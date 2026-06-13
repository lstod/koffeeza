# Koffeeza

Espresso extraction optimization tool. Logs espresso shots and recommends grind adjustments to dial in a balanced cup, with per-bean/grinder/machine memory so switching bags gives a good starting point.

## Quick Start

### With Docker (recommended)

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

### Local Development

**Backend:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install ".[dev]"
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

## Commands

| Command | Description |
|---------|-------------|
| `make up` | Build and start all services |
| `make down` | Stop all services |
| `make test` | Run all tests (backend + frontend) |
| `make lint` | Run all linters (backend + frontend) |

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy, SQLite
- **Frontend:** React, TypeScript, Vite, Tailwind CSS, shadcn/ui
- **Infrastructure:** Docker, GitHub Actions CI/CD

## LLM Rationale (Optional)

The app runs fully without an LLM API key — template rationale is the default. To enable conversational rephrasing of shot rationale via Anthropic:

```bash
# in .env
ENABLE_LLM_RATIONALE=true
ANTHROPIC_API_KEY=sk-ant-...
```

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_LLM_RATIONALE` | `false` | Feature flag — must be `true` to activate |
| `ANTHROPIC_API_KEY` | — | Required when enabled |
| `LLM_RATIONALE_MODEL` | `claude-haiku-4-20250414` | Anthropic model to use |
| `LLM_RATIONALE_TIMEOUT` | `5.0` | Timeout in seconds; falls back to template on failure |

If the LLM call fails for any reason (timeout, missing key, API error), the response silently falls back to the template. The `rationale_source` field in the shot response indicates which path was used (`"template"` or `"llm"`).
