"""AI orchestration. AI explains pre-computed numbers; it never calculates risk
or analytics, and never speaks below the data-sufficiency gate."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.ai_insight import (
    AIConfidence,
    AIInsight,
    AIInsightType,
    Recommendation,
)
from app.models.trade import Trade, TradeResult, TradeStatus
from app.repositories import ai_insight_repo, trade_repo, user_repo
from app.schemas.ai import AIInsightResponse, AISimilarRequest, SimilarTradeAnalysis
from app.services import analytics_engine, analytics_service, strategy_service, trade_service
from app.services.ai import prompt_builder, similarity, sufficiency
from app.services.ai.llm_client import get_llm_client
from app.services.ai.similarity import SimTrade
from app.services.risk_engine import ZeroRiskError, compute_breakdown


def _closed_count(db: Session, user_id: uuid.UUID) -> int:
    return len(trade_repo.list_closed(db, user_id))


def _currency(db: Session, user_id: uuid.UUID) -> str:
    s = user_repo.get_settings(db, user_id)
    return s.quote_currency if s else "USDT"


def _narrate(system: str, prompt: str, fallback: str) -> str:
    llm = get_llm_client()
    if llm is not None:
        try:
            text = llm.complete(system=system, prompt=prompt)
            if text:
                return text
        except Exception:  # noqa: BLE001 - never let a flaky LLM break the response
            return fallback
    return fallback


def _confidence_for(count: int) -> AIConfidence:
    if count >= 15:
        return AIConfidence.high
    if count >= 8:
        return AIConfidence.medium
    if count >= settings.ai_min_matches:
        return AIConfidence.low
    return AIConfidence.insufficient


def _insufficient(insight_type: AIInsightType) -> AIInsightResponse:
    return AIInsightResponse(
        insight_type=insight_type,
        content=sufficiency.INSUFFICIENT_DATA,
        confidence=AIConfidence.insufficient,
    )


def get_trade_summary(db: Session, user_id: uuid.UUID, trade_id: uuid.UUID) -> AIInsightResponse:
    user = user_repo.get_by_id(db, user_id)
    trade = trade_service.get_trade(db, user_id, trade_id)  # 404 if not the user's
    if user is None or not sufficiency.has_sufficient_data(user, _closed_count(db, user_id)):
        return _insufficient(AIInsightType.trade_summary)

    if trade.status != TradeStatus.closed:
        return AIInsightResponse(
            insight_type=AIInsightType.trade_summary,
            content=(
                f"This {trade.direction} {trade.symbol} trade is still {trade.status}; "
                "a full summary appears once it closes."
            ),
            confidence=AIConfidence.low,
        )

    cached = ai_insight_repo.get_for_trade(db, user_id, trade_id, AIInsightType.trade_summary)
    if cached is not None:
        return AIInsightResponse(
            insight_type=AIInsightType.trade_summary,
            content=cached.content,
            confidence=cached.confidence,
        )

    currency = _currency(db, user_id)
    system, prompt = prompt_builder.trade_summary_prompt(
        symbol=trade.symbol,
        direction=trade.direction,
        result=trade.result,
        pnl=trade.pnl,
        r_multiple=trade.r_multiple,
        strategy=trade.strategy.name,
        currency=currency,
    )
    fallback = prompt_builder.trade_summary_fallback(
        symbol=trade.symbol,
        direction=trade.direction,
        result=trade.result,
        pnl=trade.pnl,
        r_multiple=trade.r_multiple,
        currency=currency,
    )
    content = _narrate(system, prompt, fallback)

    ai_insight_repo.add(
        db,
        AIInsight(
            user_id=user_id,
            trade_id=trade_id,
            insight_type=AIInsightType.trade_summary,
            content=content,
            confidence=AIConfidence.medium,
            inputs_snapshot={
                "result": str(trade.result),
                "pnl": str(trade.pnl),
                "r_multiple": str(trade.r_multiple),
            },
            model=settings.ai_model if settings.anthropic_api_key else "fallback",
        ),
    )
    return AIInsightResponse(
        insight_type=AIInsightType.trade_summary,
        content=content,
        confidence=AIConfidence.medium,
    )


def get_performance(db: Session, user_id: uuid.UUID) -> AIInsightResponse:
    user = user_repo.get_by_id(db, user_id)
    closed_count = _closed_count(db, user_id)
    if user is None or not sufficiency.has_sufficient_data(user, closed_count) or closed_count == 0:
        return _insufficient(AIInsightType.performance)

    summary = analytics_service.get_summary(db, user_id)
    currency = _currency(db, user_id)
    system, prompt = prompt_builder.performance_prompt(
        summary={
            "trade_count": summary.trade_count,
            "win_rate": str(summary.win_rate),
            "profit_factor": str(summary.profit_factor),
            "expectancy": str(summary.expectancy),
            "average_r": str(summary.average_r),
            "max_drawdown": str(summary.max_drawdown),
        }
    )
    fallback = prompt_builder.performance_fallback(
        trade_count=summary.trade_count,
        win_rate=summary.win_rate,
        expectancy=summary.expectancy,
        average_r=summary.average_r,
        currency=currency,
    )
    return AIInsightResponse(
        insight_type=AIInsightType.performance,
        content=_narrate(system, prompt, fallback),
        confidence=_confidence_for(summary.trade_count),
    )


def _to_simtrade(trade: Trade) -> SimTrade:
    when = trade.opened_at or trade.closed_at or trade.created_at
    return SimTrade(
        trade_id=str(trade.id),
        strategy_id=str(trade.strategy_id),
        direction=trade.direction.value,
        rr_ratio=trade.rr_ratio,
        risk_pct=trade.risk_pct,
        session=analytics_engine.derive_session(when),
        r_multiple=trade.r_multiple,
        is_win=trade.result == TradeResult.win,
    )


def get_similar(
    db: Session, user_id: uuid.UUID, payload: AISimilarRequest
) -> SimilarTradeAnalysis:
    user = user_repo.get_by_id(db, user_id)
    strategy = strategy_service.get_strategy(db, user_id, payload.strategy_id)  # 404 if not theirs
    settings_row = user_repo.get_settings(db, user_id)
    risk_pct = payload.risk_pct or (settings_row.default_risk_pct if settings_row else Decimal(1))

    try:
        breakdown = compute_breakdown(
            account_size=settings_row.account_size if settings_row else Decimal(1),
            risk_pct=risk_pct,
            entry=payload.entry_price,
            stop=payload.stop_loss,
            target=payload.take_profit,
        )
        rr = breakdown.rr_ratio
    except ZeroRiskError:
        rr = None

    insufficient = SimilarTradeAnalysis(
        match_count=0,
        avg_similarity=None,
        historical_win_rate=None,
        historical_avg_r=None,
        recommendation=Recommendation.insufficient,
        reasoning=sufficiency.INSUFFICIENT_DATA,
        confidence=AIConfidence.insufficient,
    )
    if user is None or not sufficiency.has_sufficient_data(user, _closed_count(db, user_id)):
        return insufficient

    target = SimTrade(
        trade_id="target",
        strategy_id=str(strategy.id),
        direction=payload.direction.value,
        rr_ratio=rr,
        risk_pct=risk_pct,
        session=analytics_engine.derive_session(datetime.now(UTC)),
    )
    candidates = [
        _to_simtrade(t)
        for t in trade_repo.list_closed(db, user_id)
        if t.strategy_id == strategy.id and t.direction == payload.direction
    ]
    matches = similarity.find_similar(
        target,
        candidates,
        min_similarity=Decimal(str(settings.ai_min_similarity)),
    )
    stats = similarity.cohort_stats(matches)
    recommendation = similarity.recommend(stats, min_matches=settings.ai_min_matches)

    fallback = prompt_builder.similar_fallback(
        strategy=strategy.name,
        direction=payload.direction.value,
        match_count=stats.count,
        win_rate=stats.win_rate,
        avg_r=stats.avg_r,
        recommendation=recommendation,
    )
    if recommendation == Recommendation.insufficient:
        reasoning = fallback
    else:
        system, prompt = prompt_builder.similar_prompt(
            strategy=strategy.name,
            direction=payload.direction.value,
            match_count=stats.count,
            win_rate=stats.win_rate,
            avg_r=stats.avg_r,
            recommendation=recommendation,
        )
        reasoning = _narrate(system, prompt, fallback)

    return SimilarTradeAnalysis(
        match_count=stats.count,
        avg_similarity=stats.avg_similarity,
        historical_win_rate=stats.win_rate,
        historical_avg_r=stats.avg_r,
        recommendation=recommendation,
        reasoning=reasoning,
        confidence=_confidence_for(stats.count),
    )
