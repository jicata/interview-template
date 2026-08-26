# Architecture — interview-template

The map. It **positions** things; it does not describe them. For why a rule exists, see `.claude/doctrine/project-profile.md`.

## Stack

| Layer | What |
| --- | --- |
| Backend | Python 3.12, FastAPI, stdlib `sqlite3` (in-memory), pytest + httpx |
| Frontend | Vite 5, Vue 3 `<script setup>`, TypeScript 5.3 — no router, no store, no component library |
| Between them | Vite dev-server proxy: `/api/*` → `localhost:8000/*`, prefix stripped |
| Persistence | One in-memory SQLite connection, built and seeded from `backend/data/*.csv` at import. No ORM, no migrations, no repository layer |

## The request path

```
App.vue
  └─ src/api/client.ts        get<T>('/hello')  → fetch('/api/hello')
       └─ Vite proxy          /api/hello        → localhost:8000/hello
            └─ app/main.py    include_router
                 └─ app/api/hello.py            thin route: validate, call, wrap in schema
                      └─ app/features/hello/handler.py    business logic
                           └─ app/db.py         get_connection() to read
                                                transaction() to write
```

## Layers and features

**Layered**, with the application layer subdivided by feature. Dependencies point downward only: `api` → `features` → `models`/`db`. No ports, no inversion.

A feature is a route module in `api/` plus a package in `features/`. Adding one means adding a row here.

| Feature | Route (transport) | Handler (application) | Schemas |
| --- | --- | --- | --- |
| `hello` | `app/api/hello.py` — `GET /hello?name=` | `app/features/hello/handler.py` | `app/features/hello/schemas.py` |
| `reorder` | `app/api/reorder.py` — `GET /customers/{customer_id}/reorder-suggestions?as_of=` | `app/features/reorder/handler.py` → pure deep module `app/features/reorder/cadence.py` (no db import) | `app/features/reorder/schemas.py` |

## Data

Four tables, seeded from CSV of the same name. Entity dataclasses in `app/models/` mirror them but are **not** wired to the database — nothing maps rows to them automatically.

```
customers ──< orders ──< order_lines >── products
```

- `orders.status` — `CHECK(status IN ('completed','draft'))`
- `orders.order_date` — nullable; empty for drafts
- `order_lines.unit_price` — the price charged at the time, denormalized from `products.unit_price`

Seed shape: 3 customers, 5 products, 19 orders (18 completed, 1 draft), 18 order lines — one per completed order.

## What is deliberately absent

No repository/data-access layer (the README leaves the design open), no migrations, no auth, no CI, no deployment, no frontend test runner. Their absence is a decision, not a gap — do not flag it as one.
