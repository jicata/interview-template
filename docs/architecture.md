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

The writing path, which `hello` does not demonstrate:

```
App.vue
  └─ src/api/client.ts        post<Order>('/orders/19/lines', body)
       └─ Vite proxy          /api/orders/19/lines → localhost:8000/orders/19/lines
            └─ app/api/orders.py                   thin route; maps OrderError → status
                 └─ app/features/orders/handler.py  guards, then writes in one transaction
                      ├─ app/features/orders/queries.py  the SQL
                      └─ app/features/orders/pricing.py  pure: discount + rounding
```

## Layers and features

**Layered**, with the application layer subdivided by feature. Dependencies point downward only: `api` → `features` → `models`/`db`. No ports, no inversion.

A feature is a route module in `api/` plus a package in `features/`. Adding one means adding a row here.

| Feature | Route (transport) | Handler (application) | Schemas | Queries |
| --- | --- | --- | --- | --- |
| `hello` | `app/api/hello.py` — `GET /hello?name=` | `app/features/hello/handler.py` | `app/features/hello/schemas.py` | — |
| `products` | `app/api/products.py` — `GET /products` | `app/features/products/handler.py` | `app/features/products/schemas.py` | `app/features/products/queries.py` |
| `orders` | `app/api/orders.py` — `POST /orders`, `GET /orders/{id}`, `POST /orders/{id}/lines`, `DELETE /orders/{id}/lines/{line_id}` | `app/features/orders/handler.py` + `pricing.py` | `app/features/orders/schemas.py` | `app/features/orders/queries.py` |

Two things about the `orders` feature are worth positioning rather than leaving to
be discovered:

- **`app/features/orders/pricing.py` imports nothing from `app.db`.** The volume
  discount and the rounding policy live there, and they are testable with no
  database at all (`tests/test_pricing.py` uses no fixture). See ADR 002.
- **`app/api/orders.py` owns the domain-error-to-status mapping** in one table,
  registered on the app in `main.py` as an exception handler. The handler layer
  raises `OrderError` subclasses and never imports `HTTPException`.

## Data

Four tables, seeded from CSV of the same name. Entity dataclasses in `app/models/` mirror them but are **not** wired to the database — nothing maps rows to them automatically. The one exception is `OrderStatus` in `app/models/order.py`, a `StrEnum` naming the same two values as the `status` `CHECK` constraint; the orders feature imports it rather than repeating string literals.

```
customers ──< orders ──< order_lines >── products
```

- `orders.status` — `CHECK(status IN ('completed','draft'))`
- `orders.order_date` — nullable; empty for drafts
- `order_lines.unit_price` — the price charged at the time, denormalized from `products.unit_price`
- **No discount or line-total column.** Pricing is derived on every read, not stored — ADR 002.

Seed shape: 3 customers, 5 products, 19 orders (18 completed, 1 draft), 18 order lines — one per completed order.

## What is deliberately absent

No repository/data-access layer (the README leaves the design open), no migrations, no auth, no CI, no deployment, no frontend test runner. Their absence is a decision, not a gap — do not flag it as one.
