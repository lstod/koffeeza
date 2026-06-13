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

## Notes

- The app runs fully **without** an LLM API key (template rationale is the default).
- Set `ANTHROPIC_API_KEY` in `.env` to enable optional LLM-phrased rationale.
