# Trader Copilot AI (EdgePilot) — Implementation Log: M0 → M7

This document records everything built and verified across milestones **M0–M7**.
It is the engineering counterpart to the four design docs in this folder (SOC,
TAD, DRD, UX Spec). The build follows the DRD's hard rule — **collect data before
intelligence** — so AI is deliberately not introduced until M9.

- **Repo:** `kuchurisatwik/EdgePilot` (branch `main`)
- **Target market (MVP):** Crypto (e.g. `BTC_USDT`), quote currency `USDT`, fractional sizing, long/short.
- **MVP boundary:** end of **M9** (AI summary). M8 (screenshots) and M9 (AI) are next.

---

## 1. Status at a glance

| Milestone | Scope | Backend tests | Migration | Commit | Status |
|---|---|---|---|---|---|
| **M0** | Foundation / scaffold / CI | health | baseline | `8b90747` | ✅ |
| **M1** | Auth + Settings | 14 | `fbd74b77dcf5` | `a24268c` | ✅ |
| **M2** | Strategies | +9 | `d7336971272c` | `0e25e50` | ✅ |
| **M3** | Trade Planner + Risk Engine | +21 | `8aa401164613` | `a11a3d2` | ✅ |
| **M4** | Rule Engine | +13 | `e71acace8103` | `f7a79a1` | ✅ |
| **M5** | Journal (lifecycle + collection) | +16 | — (reused) | `44ba01f` | ✅ |
| **M6** | Analytics (pure stats) | +19 | — (read-only) | `0deddd6` | ✅ |
| **M7** | Market Context capture | +5 | `efc2b893ff80` | `0208ce6` | ✅ |

**Test suite today:** 95 test functions (~98 cases with parametrization) — 27 unit
(pure engines) + 68 integration (API + DB). Every milestone verified with
`pytest`, `ruff`, `mypy`, Alembic drift-check, frontend `tsc`/`eslint`/`next build`,
and a live HTTP smoke. *(M4 was committed under the label "m3 done", `f7a79a1`.)*

---

## 2. Architecture & tech stack

Modular monolith — FastAPI backend + Next.js frontend + PostgreSQL (SQLite for
tests and local dev without Docker).

**Backend:** FastAPI · Python 3.12 · SQLAlchemy 2 · Pydantic v2 · Alembic · JWT ·
bcrypt. Thin routers; all business logic in services; data access in repositories.

**Frontend:** Next.js 16 (App Router) · TypeScript · Tailwind v4 (dark-mode-first) ·
TanStack Query · react-hook-form + Zod 4 · Recharts. JWT access token in memory +
httpOnly refresh cookie.

**Infra:** Docker Compose (db + backend + frontend) · GitHub Actions CI · Makefile.

### Non-negotiable invariants (enforced every milestone)
1. **AI explains, never calculates** — it will consume analytics outputs only (M9+).
2. **Risk Engine is the source of truth** — pure, `Decimal`, exhaustively unit-tested.
3. **Auto-capture over manual** — only Strategy is required input (current price is the documented MVP exception).
4. **Never fabricate confidence** — insufficient data returns the canonical string / nulls.
5. **Thin routes, logic in services; one Alembic migration per schema change; every query filtered by `user_id`.**
6. **Risk always visible** — persistent RiskStrip + always-visible Risk panel.

### Repository layout
```
backend/app/
  api/        thin routers (auth, settings, strategies, risk, trades, rules,
              journal, analytics, market_context, health)
  core/       config, database (unit-of-work get_db), security, logging, exceptions
  models/     SQLAlchemy (UUID PK + timestamp mixins, dialect-agnostic)
  schemas/    Pydantic in/out
  repositories/  user_id-scoped data access
  services/   risk_engine, rule_engine, outcome_service, analytics_engine,
              market_data/provider, *_service orchestrators
frontend/
  app/(auth)/ login, register     app/(app)/ dashboard, trade-planner, journal,
  journal/[tradeId], analytics, strategy-insights, ai-coach, settings
  components/ charts, data, feedback, layout, risk, strategies, trades, ui
  features/   auth, rules, strategies     services/  hooks/  lib/  types/
infra/docker-compose.yml · .github/workflows/ci.yml · Makefile
```

---

## 3. Data model & migrations

| Table | Milestone | Key columns |
|---|---|---|
| `users` | M1 | email (unique), password_hash (bcrypt), name, is_active |
| `user_settings` | M1 | account_size, default_risk_pct (=1.0), quote_currency (USDT), timezone — 1:1 |
| `refresh_tokens` | M1 | token_hash (sha256), jti, expires_at, revoked |
| `strategies` | M2 | name, risk_appetite enum, is_default, is_active — unique (user_id, name) |
| `trades` | M3 | inputs + **risk snapshot** (per_unit_risk, position_size, risk_amount, max_loss, rr_ratio, capital_exposure) + lifecycle (status, opened_at, closed_at) + **outcome** (exit_price, pnl, r_multiple, result) + rule_overridden |
| `risk_rules` | M4 | rule_type enum, threshold, severity enum, is_enabled — unique (user_id, rule_type) |
| `market_contexts` | M7 | atr/rsi/vwap/volume (nullable), trend/session/volatility_regime enums, timeframe, data_source, raw JSON — 1:1 trade |

**Migration chain:** `fbd74b77dcf5` → `d7336971272c` → `8aa401164613` →
`e71acace8103` → `efc2b893ff80`. (M5 and M6 added **no** migrations — the M3 trade
table already had the lifecycle/outcome columns, and analytics is read-only.)
All models use dialect-agnostic types (`Uuid`, `Numeric`, generic `JSON`,
`Enum(native_enum=False)`) so the same schema runs on PostgreSQL and SQLite.

---

## 4. API catalog

All endpoints require a Bearer access token except `/health`, `register`, `login`,
`refresh`. Cross-user access returns **404** (not 403). Errors use a consistent
`{"error": {"code", "message"}}` envelope.

| Domain | Endpoints |
|---|---|
| Health | `GET /api/health` |
| Auth (M1) | `POST /api/auth/{register,login,refresh,logout}` · `GET /api/auth/me` |
| Settings (M1) | `GET/PUT /api/settings` · `PUT /api/profile` |
| Strategies (M2) | `GET/POST /api/strategies` · `GET/PUT/DELETE /api/strategies/{id}` |
| Risk (M3/M4) | `POST /api/risk/calculate` → `{risk, rules}` |
| Trades (M3/M5) | `POST /api/trades/plan` · `GET/PUT /api/trades/{id}` · `GET /api/trades` · `POST /api/trades/{id}/{open,close,validate}` · `DELETE /api/trades/{id}` |
| Rules (M4) | `GET /api/rules` · `PUT /api/rules/{rule_type}` |
| Journal (M5) | `GET /api/journal` (filters + pagination) · `GET /api/journal/{id}` |
| Analytics (M6) | `GET /api/analytics/{summary,equity-curve,strategy,session,period,dashboard}` |
| Market Context (M7) | `GET /api/market-context/{trade_id}` · `POST /api/market-context/{trade_id}/refresh` |

---

## 5. Milestone detail

### M0 — Foundation
**Goal:** the cabinet before the furniture.
- **Backend:** `create_app()` factory; CORS + request-id/latency middleware; structured JSON logging; `AppException` hierarchy + handlers; `core/config` (pydantic-settings), `core/database` (unit-of-work `get_db`: commit-on-success/rollback-on-error), `models/base` (UUID PK + timestamp mixins); `/api/health` (DB ping); pytest with SQLite transactional fixtures.
- **Frontend:** Next.js + Tailwind v4 dark-mode tokens; protected **AppShell** (Sidebar + Topbar + always-visible RiskStrip); 7 nav routes; API client with refresh-interceptor scaffolding; shared components (`InsufficientData`, `EmptyState`, `ConfidenceBadge`, `ReasoningBlock`, `MetricTile`).
- **Infra:** docker-compose (db + backend + frontend), Dockerfiles, GitHub Actions CI (lint/type/test + Postgres migration job), `.env.example`, Makefile.

### M1 — Auth + Settings
- **Models:** `User`, `UserSettings` (account_size, default_risk_pct, quote_currency, timezone), `RefreshToken`.
- **Auth:** register (creates user + default settings in one transaction), login, **refresh with server-side rotation**, logout. Access token (15 min, in body) + refresh token (7 d, **httpOnly cookie**, sha256-tracked). `get_current_user` enforces per-user isolation.
- **Frontend:** real `AuthProvider` (bootstraps session from the refresh cookie on load), `RequireAuth` guard, `/login` + `/register` (RHF + Zod), Settings (account size, default risk %, name); Topbar shows live balance + logout; RiskStrip shows live Risk % + computed Risk Amount.
- **Tests:** register/login/refresh-rotation/logout, isolation (404), settings persist + validation.

### M2 — Strategies
- **Model:** `Strategy` (risk_appetite enum, unique per user). 6 defaults seeded per user (Breakout, Pullback, Reversal, Trend Following, Scalping, Range Trading) via idempotent `ensure_defaults` (at registration + lazily on first list).
- **Rules:** duplicate name → 422; default strategies cannot be deleted; custom delete is a **soft-delete** (preserves future trade references).
- **Frontend:** `StrategyManager` on Settings (list with risk/default badges, inline create/edit, soft-delete); reusable `StrategySelect` (used by the Trade Planner).
- **Tests:** defaults seeded + idempotent, CRUD, dup-name, default-protect, soft-delete, isolation.

### M3 — Trade Planner + Risk Engine (keystone)
- **Risk Engine** (`services/risk_engine.py`, pure `Decimal`, no I/O — the source of truth):
  `per_unit_risk=|entry−stop|`, `risk_amount=account×risk%`, `position_size=risk_amount/per_unit_risk`, `max_loss=position_size×per_unit_risk` (≡ risk_amount), `rr_ratio=|target−entry|/per_unit_risk`, `capital_exposure=position_size×entry`, exposure %. Quantized once at the boundary. **9 unit tests** (golden, shorts, fractional crypto, entry==stop raises, `max_loss == risk_amount` property).
- **Trade** model with the full lifecycle/snapshot/outcome column set (so M5/M6 need no new migration). Validation: stop/target on the correct side per direction, zero-risk, account-size required, draft-only edits.
- **Endpoints:** `POST /api/risk/calculate` (stateless live preview), `POST /api/trades/plan`, `GET/PUT /api/trades/{id}`, `GET /api/trades`.
- **Frontend — Trade Planner:** three panels — left (strategy, order type, symbol, notes), center (direction + entry/stop/target/current price), right **always-visible RiskPanel**. Live recompute via debounced `useRiskCalc` (`keepPreviousData`). AI Recommendation card is explicitly **Locked** (unlocks M9).

### M4 — Rule Engine
- **Model:** `RiskRule` + 4 defaults (max risk/trade 2% block, daily 5% block, weekly 10% block, consecutive 3 warning).
- **Rule Engine** (`services/rule_engine.py`): pure `decide()` (block > warning > pass) + `evaluate()` over max-risk, daily/weekly realized-loss-+-projected-max-loss (% of account), consecutive-loss streaks. Folded into `/api/risk/calculate` (now returns `{risk, rules}`).
- **Override-with-acknowledgment** (the chosen policy): a BLOCK without `acknowledge_override` → **409 `rule_block`**; with it → trade saved + `rule_overridden=true`. Opening a draft (M5) re-checks rules the same way.
- **Frontend:** RiskPanel shows the live **PASS / WARNING / BLOCK** verdict + violation reasons; the Plan button turns red ("Override & Save Draft") and requires explicit confirm on BLOCK; **Risk Rules** editor on Settings (threshold/severity/enabled).
- **Tests:** decide() unit tests + defaults/update/PASS/BLOCK/override + consecutive/daily-loss paths (driven by directly-inserted closed trades).

### M5 — Journal (data collection begins)
- **Lifecycle** `draft → open → closed` with transition guards (close-a-draft / re-open / delete-non-draft → 422). `outcome_service` (pure): `pnl=(exit−entry)·size·sign`, `r_multiple=pnl/risk_amount`, win/loss/breakeven (6 unit tests).
- **Journal** with filters (status, result, strategy, symbol, date range) + pagination; `TradeResponse` carries `strategy_name` (relationship) + outcome fields.
- **Frontend:** Journal table (Date/Strategy/Symbol/Dir/Risk/Result/PnL/R/Status) with colored PnL/R, pagination, inline open/close; `CloseTradeDialog`; **Trade Review** page (`/journal/[tradeId]`) with details, risk metrics, outcome, lifecycle actions, and (then-locked) Market Context / Screenshots / AI Summary cards.

### M6 — Analytics (pure statistics, no AI)
- **Analytics engine** (`services/analytics_engine.py`, pure): win rate, profit factor (None when no losses), expectancy, average R, equity curve + max/current drawdown, group-by, deterministic **Trade Score**, shared **session helper** (8 unit tests).
- **Endpoints:** `summary`, `equity-curve`, `strategy`, `session`, `period?weekly|monthly`, `dashboard`. Insufficient-data returns nulls, never fabricated.
- **Frontend:** **Analytics** screen (KPI tiles + equity-curve area chart + strategy/session/period bars & tables, Recharts) and a wired **Dashboard** (Account Balance, Today's PnL, Risk Exposure, Trade Score, Current Drawdown + equity curve + recent trades). The **AI Insights panel** shows the SOC insufficient-data string until M9; Recent Recommendations / Recent Mistakes are shown as **Locked**.

### M7 — Market Context capture
- **Model:** `MarketContext` (1:1 per trade) — atr/rsi/vwap/volume (nullable), trend/session/volatility_regime enums, timeframe, data_source, raw JSON.
- **Provider seam:** `MarketDataProvider` Protocol + `StubMarketDataProvider` — session is always derived from the timestamp (shared analytics session helper); indicators stay honestly **`unknown`**. Factory selected by `settings.MARKET_DATA_PROVIDER`; a real crypto feed (Crypto.com / Binance public REST) can swap in with **no service changes**.
- **Auto-captured on open** (`capture_for_trade` hooked into `open_trade`); idempotent refresh; ownership-checked endpoints.
- **Frontend:** **Market Context panel** in Trade Review (fingerprint cells + "unavailable" states; draft shows "captured when you open").

---

## 6. Cross-cutting concerns
- **Auth & isolation:** JWT access (15 m, in-memory) + refresh (7 d, httpOnly cookie, rotated/revocable); every repository query filtered by `user_id`; cross-user → 404; passwords bcrypt-hashed, never logged.
- **Unit of work:** `get_db` commits on success / rolls back on error; one transaction per request; multi-step seeds (user + settings + 6 strategies + 4 rules) run atomically at registration.
- **Testing:** pure engines (Risk, Rule decision, Outcome, Analytics) are exhaustively unit-tested against hand-computed fixtures; every endpoint has integration tests incl. isolation; LLM/market-data behind mockable interfaces.
- **Migrations:** one reviewed Alembic migration per schema change; CI applies + drift-checks on Postgres; timestamp defaults normalized to `func.now()` for cross-dialect parity.
- **Design system:** dark-mode-only tokens; RiskStrip + always-visible Risk panel; `InsufficientData` (UI vs AI strings); mandatory `reasoning` prop on recommendation components.

---

## 7. How to run

**Docker (Postgres):**
```bash
cp .env.example .env
docker compose -f infra/docker-compose.yml --env-file .env up --build
# API http://localhost:8000  ·  Frontend http://localhost:3000
```

**Local dev (no Docker — uses SQLite `backend/dev.db`):**
```bash
# backend
cd backend && python -m venv .venv && .venv\Scripts\activate
pip install -e ".[dev]"
$env:DATABASE_URL="sqlite+pysqlite:///./dev.db"; alembic upgrade head
uvicorn app.main:app --reload --port 8000
# frontend (new terminal)
cd frontend && npm install && npm run dev   # http://localhost:3000
```

**Verify:** `cd backend && python -m pytest -q` · `ruff check .` · `mypy app` ·
`cd frontend && npx tsc --noEmit && npm run lint && npm run build`.

---

## 8. What's next
- **M8 — Screenshots:** local file storage; entry/exit chart uploads (trade + higher timeframe) on the Trade Review (replaces the locked Screenshots card).
- **M9 — AI Foundation + Similar Trades (MVP boundary):** Anthropic Claude (`claude-opus-4-8`) behind a mockable `LLMClient`; data-sufficiency gate (≥7 days OR enough strategy history → else the canonical insufficient-data string); trade summaries; similar-trade search (deterministic scoring, LLM only narrates); unlocks the Planner AI panel, Dashboard AI Insights, and Trade Review AI Summary. **Requires the Anthropic API key.**

### Open decisions (deferred, non-blocking)
- Real crypto indicator/candle feed for the M7 provider (Crypto.com vs Binance) — MVP ships the stub.
- AI sufficiency floors (`MIN_STRATEGY_TRADES`), similarity weights/thresholds — tuned once real data exists.
- Trade Score weighting — refine post-MVP.
