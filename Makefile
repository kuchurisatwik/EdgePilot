# Trader Copilot AI — developer shortcuts
# Usage: make <target>   (on Windows, run via `make` from Git Bash, or run the
# underlying commands manually / via the scripts noted in README.md)

.PHONY: help up down logs migrate revision test test-backend lint fmt backend frontend

help:
	@echo "Targets:"
	@echo "  up            docker compose up (db + backend + frontend)"
	@echo "  down          docker compose down"
	@echo "  logs          tail compose logs"
	@echo "  migrate       alembic upgrade head (in backend container)"
	@echo "  revision m=.. autogenerate an alembic migration"
	@echo "  test          run backend test suite"
	@echo "  lint          ruff + mypy (backend), eslint (frontend)"
	@echo "  backend       run backend dev server on the host"
	@echo "  frontend      run frontend dev server on the host"

up:
	docker compose -f infra/docker-compose.yml --env-file .env up --build

down:
	docker compose -f infra/docker-compose.yml down

logs:
	docker compose -f infra/docker-compose.yml logs -f

migrate:
	docker compose -f infra/docker-compose.yml exec backend alembic upgrade head

revision:
	docker compose -f infra/docker-compose.yml exec backend alembic revision --autogenerate -m "$(m)"

test test-backend:
	cd backend && python -m pytest -q

lint:
	cd backend && ruff check . && mypy app
	cd frontend && npm run lint

fmt:
	cd backend && ruff format .

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev
