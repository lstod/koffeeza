.PHONY: lint test up down backend-lint backend-test frontend-lint frontend-test

# --- Aggregate targets ---

lint: backend-lint frontend-lint

test: backend-test frontend-test

up:
	docker compose up --build

down:
	docker compose down

# --- Backend ---

backend-lint:
	cd backend && ruff check app/ && ruff format --check app/

backend-test:
	cd backend && pytest --cov=app --cov-report=term-missing

# --- Frontend ---

frontend-lint:
	cd frontend && npm run lint

frontend-test:
	cd frontend && npm test
