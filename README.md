# Interview Template

A small full-stack app you'll extend during the interview — **FastAPI + SQLite**
backend, **Vue 3 + Vite + TypeScript** frontend. Your interviewer will share your
task separately.

## Prerequisites

- Python 3.12+
- Node 20+
- [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) installed

## Setup

1. **Clone this repo** and `cd` into it.

2. **Set the API key your interviewer gave you** — in each terminal where you'll run `claude`:
   ```shell
   export ANTHROPIC_API_KEY=<the key your interviewer gave you>
   ```

3. **Backend** (terminal 1, port 8000):
   ```shell
   cd backend
   python3 -m venv .venv && . .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

4. **Frontend** (terminal 2, port 3000):
   ```shell
   cd frontend
   npm install
   npm run dev
   ```

5. Open <http://localhost:3000> — you should see the example greeting from the backend.
   The data resets to a known state every time the backend restarts.

> Shortcuts once the backend venv exists: `make dev-backend`, `make dev-frontend`, `make test`.

## Tests

```shell
cd backend && . .venv/bin/activate
pytest        # runs the example hello test; add your own as you go
```

`tests/test_hello.py` shows how the harness works — use it as a template.

## Project structure

The backend is layered: a thin API route calls a feature handler, which holds the
business logic. The `hello` endpoint is a worked example of that pattern.

```
backend/
  app/
    api/          # Thin route handlers — validate input, call a feature handler
    features/     # Business logic per feature (hello/ is the worked example)
    models/       # Entity dataclasses (Customer, Product, Order, OrderLine)
    db.py         # get_connection() — in-memory SQLite seeded from CSV
    main.py       # FastAPI app
  data/           # CSV seed files
  tests/          # test_hello.py is a template for your own tests
frontend/
  src/
    api/client.ts # Typed fetch wrapper
    App.vue       # Main component
```

There is **no data-access / repository layer** — how you read and write the seeded
data is your call.
