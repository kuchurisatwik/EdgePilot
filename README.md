# Trader Copilot AI

A risk-management, trading-intelligence and AI-coaching platform for traders.
It is **not** a broker, terminal, or signal service — the trader stays responsible
for execution; the platform provides risk validation, a journal, analytics, and
(once enough data exists) AI explanations.

> Built phase-by-phase. See the implementation plan for the full roadmap and the
> design docs under [`Doc/`](Doc/). Current target market: **crypto** (e.g.
> `BTC_USDT`). MVP ships at milestone **M9** (AI summary layer).

## Architecture

Modular monolith — a FastAPI backend + Next.js frontend + PostgreSQL.

```
backend/    FastAPI + SQLAlchemy + Alembic (api / core / models / schemas /
            repositories / services). All business logic lives in services;
            routes stay thin. Risk Engine is the deterministic source of truth.
frontend/   Next.js (App Router) + TypeScript + Tailwind + shadcn/ui.
            Dark-mode-first; risk metrics always visible.
infra/      docker-compose (db + backend + frontend).
Doc/        Product/design source-of-truth documents.
```

## Quick start (Docker — recommended)

```bash
cp .env.example .env
docker compose -f infra/docker-compose.yml --env-file .env up --build
```

- API:      http://localhost:8000  (health: http://localhost:8000/api/health)
- API docs: http://localhost:8000/docs
- Frontend: http://localhost:3000

## Local development (without Docker)

**Backend**
```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate     |  macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
# point DATABASE_URL at a local postgres, then:
alembic upgrade head
uvicorn app.main:app --reload --port 8000
python -m pytest -q
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

## Milestones

| # | Milestone | Status |
|---|-----------|--------|
| M0 | Foundation (scaffold, health, CI, dark shell) | in progress |
| M1 | Auth + Settings | planned |
| M2 | Strategies | planned |
| M3 | Trade Planner + Risk Engine | planned |
| M4 | Rule Engine | planned |
| M5 | Journal | planned |
| M6 | Analytics | planned |
| M7 | Market Context | planned |
| M8 | Screenshots | planned |
| M9 | AI Foundation + Similar Trades (**MVP**) | planned |
| M10 | Behavioral + Strategy Intelligence | planned |
| M11 | Broker integration | deferred |
| M12 | Real-time | deferred |

Each milestone is completed, tested, and approved before the next begins.
**Data must exist before intelligence** — AI is introduced only at M9.
