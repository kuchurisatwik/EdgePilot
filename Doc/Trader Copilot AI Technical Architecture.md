## Trader Copilot AI 

## Technical Architecture Document (TAD) 

Version 1.0 

## 1. Purpose 

This document defines the technical architecture, system boundaries, technology stack, database design principles, API domains, and implementation structure for Trader Copilot AI. 

This document should be used together with the SOC (System Overview & Control) document. 

## 2. Product Summary 

Trader Copilot AI is a SaaS platform that helps traders improve: 

- Risk Management 

- Position Sizing 

- Trade Selection 

- Strategy Validation 

- Behavioral Discipline 

The platform is NOT: 

- Auto Trading Software 

- Signal Generator 

- Trade Execution Engine 

The platform IS: 

- Decision Support System 

- Trading Intelligence Platform 

- Risk Management Assistant 

- AI Trading Coach 

## 3. Technology Stack 

Frontend 

Framework: 

- Next.js 

Language: 

- TypeScript 

Styling: 

- Tailwind CSS 

UI Components: 

- shadcn/ui 

Charts: 

- TradingView Lightweight Charts 

- Recharts 

Authentication: 

- JWT 

Backend 

Framework: 

- FastAPI 

Language: 

- Python 3.12+ 

ORM: 

- SQLAlchemy 

Validation: 

- Pydantic 

Authentication: 

- JWT 

Migrations: 

- Alembic 

## Database 

Primary Database: 

- PostgreSQL 

Purpose: 

- Users 

- Trades 

- Strategies 

- Analytics 

- Market Context 

- AI Insights 

## Storage 

MVP: 

- Local File Storage 

Future: 

- AWS S3 

Used For: 

- Chart Screenshots 

- Generated Reports 

## Future Components 

Not MVP: 

- Redis 

- Celery 

- Kafka 

- Kubernetes 

- Microservices 

## 4. High-Level Architecture 

Next.js Frontend | | REST APIs | | FastAPI Backend | 

| | | | | uth Trades Risk Analytics AI odule Module Engine Engine Module | | PostgreSQL | | Screenshot Store 

## 5. Architecture Principles 

## Principle 1 

Use Modular Monolith Architecture. 

Do NOT use microservices. 

## Principle 2 

Business Logic must remain in Services. 

API Routes should remain thin. 

## Principle 3 

AI must never perform calculations. 

AI only consumes analytics outputs. 

## Principle 4 

Risk Engine is the source of truth. 

AI cannot override risk rules. 

## Principle 5 

Auto-capture wherever possible. 

Reduce manual user input. 

## 6. Module Boundaries 

## Auth Module 

Responsibilities: 

- Register 

- Login 

- Refresh Tokens 

- Profile 

Owns: 

- Users 

## Strategy Module 

Responsibilities: 

- Create Strategy 

- Edit Strategy 

- Delete Strategy 

Owns: 

- Strategy Definitions 

- Risk Preferences 

## Trade Module 

Responsibilities: 

- Create Trade 

- Update Trade 

- Close Trade 

- Trade Lifecycle 

## Owns: 

- Trades 

- Trade Journal 

## Risk Engine 

Responsibilities: 

- Position Sizing 

- Risk Calculations 

- Exposure Calculations 

## Outputs: 

- Risk Amount 

- Position Size 

- Reward Risk Ratio 

## Rule Engine 

Responsibilities: 

- Validate Trades 

- Apply Risk Constraints 

Outputs: 

- PASS 

- WARNING 

- BLOCK 

## Market Context Module 

Responsibilities: 

Capture: 

- ATR 

- RSI 

- VWAP 

- Volume 

- Trend 

- Session 

Purpose: 

Create market fingerprints. 

## Analytics Module 

Responsibilities: 

Generate: 

- Win Rate 

- Profit Factor 

- Drawdown 

- Expectancy 

- Strategy Performance 

No AI logic. 

## AI Module 

Responsibilities: 

Generate: 

- Trade Validation 

- Similar Trade Analysis 

- Behavioral Coaching 

- Strategy Intelligence 

Consumes: 

- Analytics Data 

- Market Context 

- Trade History 

## 7. Backend Folder Structure 

backend/ 

- ├── app/ 

│ ── api/├ 

│ │ ── auth/├ 

│ │ ── strategies/├ 

│ │ ── trades/├ 

│ │ ── risk/├ 

│ │ ── analytics/├ 

- │ │ ── ai/├ 

│ │ └── market_context/ 

│ │ 

│ ── core/├ 

│ │ ── config.py├ 

│ │ ── database.py├ 

│ │ └── security.py 

│ │ 

│ ── models/├ 

- │ ── schemas/├ 

│ ── repositories/├ 

│ ── services/├ 

│ └── main.py 

## 8. Frontend Structure 

frontend/ 

├── app/ 

├── components/ 

- ├── features/ 

- │ ── dashboard/├ 

- │ ── trades/├ 

- │ ── risk/├ 

- │ ── analytics/├ 

- │ ── journal/├ 

- │ └── ai/ 

- ├── services/ 

- ├── hooks/ 

├── types/ 

└── utils/ 

## 9. Core API Domains 

## Authentication 

/api/auth 

Responsibilities: 

- Register 

- Login 

- Logout 

## Strategies 

/api/strategies 

Responsibilities: 

- CRUD 

## Trades 

/api/trades 

Responsibilities: 

- Trade Lifecycle 

## Risk 

/api/risk 

Responsibilities: 

- Risk Calculations 

- Validation 

## Analytics 

/api/analytics 

Responsibilities: 

- Performance Metrics 

## Market Context 

/api/market-context 

Responsibilities: 

- Market Fingerprints 

## AI 

/api/ai 

Responsibilities: 

- Recommendations 

- Insights 

## 10. Data Flow 

User Selects Strategy |  Trade Creation |  Risk Engine |  Rule Engine |  Market Context ▼ ▼ ▼ ▼ Capture |  Store Trade |  Analytics Engine |  AI Analysis |  Dashboard Output▼ ▼ ▼ ▼ 

## 11. Screenshot Architecture 

For every trade: 

Capture: 

Entry: 

- Trade Timeframe 

- Higher Timeframe 

Exit: 

- Trade Timeframe 

- Higher Timeframe 

Store: 

- File Path 

- Trade ID 

- Timestamp 

Future AI Vision: 

- Pattern Recognition 

- Trend Classification 

- Setup Similarity 

## 12. AI Architecture 

AI Input Sources: 

1. Trade History 

2. Market Context 

3. Risk Metrics 

4. Behavioral Data 

5. Analytics Outputs 

AI Must Not Consume Raw Data Directly. 

Pipeline: 

Raw Data |  Analytics Engine |  Feature Extraction |  AI Layer |  Recommendation▼ ▼ ▼ ▼ 

## 13. Frontend Pages 

Dashboard 

Purpose: Overall account health 

New Trade 

Purpose: Trade planning 

Trade Review 

Purpose: Trade validation 

Journal 

Purpose: Historical trades 

Analytics 

Purpose: Performance analysis 

Strategy Insights 

Purpose: Strategy intelligence 

AI Coach 

Purpose: Recommendations and coaching 

Settings 

Purpose: User configuration 

## 14. MVP Deliverables 

Phase 1 

- Authentication 

- Trade Entry 

- Risk Engine 

Phase 2 

- Rule Engine 

- Journal 

- Analytics 

Phase 3 

- Market Context Capture 

- Screenshot Storage 

Phase 4 

- AI Insights 

- Similar Trade Analysis 

Phase 5 

- Broker Integrations 

Phase 6 

- Live Updates 

## 15. Non-Functional Requirements 

Performance: 

- API Response < 300ms 

## Security: 

- JWT Authentication 

- Password Hashing 

Scalability: 

- Modular Architecture 

Maintainability: 

- Service Layer Pattern 

Reliability: 

 Transaction-safe database operations 

Observability: 

 Structured Logging 

## 16. Success Criteria 

The platform successfully helps traders answer: 

- What should I risk? 

- Is this trade valid? 

- Has this setup worked before? 

- Is my position size correct? 

- What mistakes am I repeating? 

- How can I improve my strategy performance? 

without becoming an automated trading system. 

