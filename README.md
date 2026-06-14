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

## Getting Started

On first launch, go to **Setup** to add your equipment. The grinder form includes presets for popular grinders (Niche Zero, Comandante C40, Baratza Encore) that auto-fill the adapter profile fields. You can also enter any grinder manually.

Then head to the main screen, select a bean, and log your first shot. The app will recommend a grind adjustment and remember your settings for next time.

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

## Known Limitations

- **Estimated `step_native` values** — grinder adapter profiles use estimated step sizes. Real-world calibration may differ from the preset values.
- **Stubbed recall tiers 3-4** — approximate recall (same bean + similar equipment) is stubbed. Only exact-match (tiers 1-2) and generic fallback (tier 5) are implemented.
- **Manual entry only** — all shot data is entered manually. There is no BLE scale/machine integration.
- **Single-variable iteration** — the engine recommends one change at a time by design, which is slower but avoids confounding variables.
- **Taste subjectivity** — structured taste buttons (sour/bitter/balanced/weak/astringent) reduce ambiguity but can't eliminate it.
