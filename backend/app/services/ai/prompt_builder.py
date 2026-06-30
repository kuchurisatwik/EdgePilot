"""Prompt construction + deterministic fallback narration.

AI explains, never calculates: prompts interpolate ALREADY-computed numbers,
forbid fabrication, and require citing trade counts. The fallback templates
produce honest, data-derived prose when no LLM is configured.
"""

from decimal import Decimal

_SYSTEM = (
    "You are a trading-performance analyst for a risk-management platform. "
    "You ONLY explain the pre-computed statistics provided. Never invent numbers, "
    "never fabricate confidence, always cite the trade counts you were given, and "
    "keep it to 2-3 plain sentences. You never tell the user to override their risk rules."
)


def _sanitize(text: str | None, limit: int = 500) -> str:
    if not text:
        return ""
    # Strip control chars / template markers before embedding user text in prompts.
    cleaned = "".join(ch for ch in text if ch.isprintable())
    return cleaned[:limit]


def _pct(value: Decimal | None) -> str:
    return "n/a" if value is None else f"{(value * 100):.1f}%"


def trade_summary_prompt(
    *, symbol, direction, result, pnl, r_multiple, strategy, currency
) -> tuple[str, str]:
    prompt = (
        f"Summarize this closed trade for the trader.\n"
        f"- Strategy: {strategy}\n- Symbol: {symbol}\n- Direction: {direction}\n"
        f"- Result: {result}\n- PnL: {pnl} {currency}\n- R-multiple: {r_multiple}\n"
        f"Explain what the outcome means relative to the risk taken. Do not invent context."
    )
    return _SYSTEM, prompt


def trade_summary_fallback(*, symbol, direction, result, pnl, r_multiple, currency) -> str:
    return (
        f"This {direction} {symbol} trade closed {result} with {pnl} {currency} "
        f"({r_multiple}R relative to the risk taken)."
    )


def performance_prompt(*, summary: dict) -> tuple[str, str]:
    prompt = (
        "Explain this trader's performance in plain language using ONLY these "
        f"pre-computed statistics:\n{summary}\n"
        "Mention the trade count, win rate and expectancy. Do not invent anything."
    )
    return _SYSTEM, prompt


def performance_fallback(*, trade_count, win_rate, expectancy, average_r, currency) -> str:
    return (
        f"Across {trade_count} closed trades your win rate is {_pct(win_rate)} with an "
        f"expectancy of {expectancy} {currency} per trade and an average of {average_r}R."
    )


def similar_prompt(
    *, strategy, direction, match_count, win_rate, avg_r, recommendation
) -> tuple[str, str]:
    prompt = (
        "Explain a trade recommendation using ONLY these pre-computed numbers from "
        f"historically similar trades:\n- Strategy: {strategy}\n- Direction: {direction}\n"
        f"- Similar trades: {match_count}\n- Historical win rate: {_pct(win_rate)}\n"
        f"- Average R: {avg_r}\n- Recommendation: {recommendation}\n"
        "Justify the recommendation by citing the win rate and the number of similar trades."
    )
    return _SYSTEM, prompt


def similar_fallback(*, strategy, direction, match_count, win_rate, avg_r, recommendation) -> str:
    if match_count == 0:
        return "No closely similar historical trades yet for this setup."
    verb = {
        "take": "supports taking",
        "reduce": "suggests reducing size on",
        "avoid": "warns against",
    }
    lead = verb.get(str(recommendation), "is inconclusive for")
    return (
        f"History {lead} this trade: similar {strategy} {direction} setups won "
        f"{_pct(win_rate)} over {match_count} trades at an average of {avg_r}R."
    )
