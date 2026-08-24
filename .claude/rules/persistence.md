---
paths:
  - "backend/app/db.py"
  - "backend/data/**"
  - "backend/tests/**"
---

# SQLite, seed data and test state

Full doctrine: `.claude/doctrine/relational-persistence.md`, plus `project-profile.md` → Persistence and Testing. Read them before changing the schema or writing a test that writes.

- **Every write goes through `db.transaction()`; never `get_connection()` for a write.** One shared connection means the implicit transaction is shared too, so concurrent writers commit each other's partial work. This is the bug the template authors planted and fixed in commit `b0a7929` — assume it is watched.
- **Reads use `get_connection()` directly.** `transaction()` holds a process-wide lock; wrapping reads serializes every request for nothing.
- **There are no migrations.** A schema change is `_build_db()`'s `executescript` **and** the matching CSV header, in the same commit. The loader derives columns from `rows[0].keys()`, so a mismatch fails at import and takes the app down at startup.
- **Tests share the app's connection — there is no per-test rollback.** A test that writes pollutes every later test in the process. Isolate in the test (wrap-and-rollback fixture, or restore the seeded rows); never weaken `db.py` to make a test pass.
- **`order_lines.unit_price` is the historical price.** Do not "normalize" it away by joining to `products.unit_price` — they are equal in the seed data, so the bug is invisible in tests.
