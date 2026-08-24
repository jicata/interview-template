# interview-template

Python 3.12 · FastAPI · stdlib `sqlite3` (in-memory, seeded from CSV at import) · pytest.
Frontend: Vite · Vue 3 `<script setup>` · TypeScript. No ORM, no migrations, no component library.
**Feature-sliced backend** — `app/api/<feature>.py` is a thin route that calls `app/features/<feature>/handler.py`. The `hello` slice is the worked example and the shape of record.

This repo is a **live-coding interview sandbox**. The task is handed over verbally when the session starts; it is not in the repo.

## Where the rules actually live

- **`.claude/doctrine/project-profile.md`** — this repo's constraints, each with its evidence. Read it before persistence, testing, merge or review work. It is the only writable skill surface; base files under `.claude/skills/` and `.claude/doctrine/` install verbatim.
- **`.claude/doctrine/00-doctrine-index.md`** — which doctrine governs which activity.
- **`.claude/rules/`** — path-scoped; the right doctrine loads automatically when a matching file is opened.
- **`/ask-interview`** — the router over the installed skill stack when you don't remember what fits.

## Canon — three durable documents

- **`docs/architecture.md`** — the map: stack, slice table, request path. Positions things; does not describe them.
- **`docs/UBIQUITOUS_LANGUAGE.md`** — domain terms. Use these names in code, tests and PRs.
- **`docs/adr/`** — decisions that outlive the session, one file each.

## Checks — all three must pass before a PR

```bash
cd backend && .venv/Scripts/python -m pytest
cd frontend && npx vue-tsc --noEmit
cd frontend && npm run build
```

There is no CI. These are the only gate — an agent raising "there is no CI" as a blocker is noise. `npm run dev` does **not** typecheck; `vue-tsc` is a separate, mandatory gate.

## Never

- **Never push to `origin`.** `origin` is `prmsolutions/interview-template` — the interviewer's repo, read-only to you. Push to `fork` (`jicata/interview-template`). A stray branch or PR on their repo is visible to the people evaluating you and cannot be quietly undone.
- **Never write to the database outside `db.transaction()`.** There is one process-wide `sqlite3` connection, so the implicit transaction is shared: two concurrent writers commit and roll back each other's partial work. Reads use `get_connection()` directly — `transaction()` holds a global lock. This is the one bug the template authors planted and then fixed (`b0a7929`), so assume it is the thing being watched.
- **Never assume a test starts from the seeded state.** Tests import the same module-level connection the app uses and there is no per-test rollback, so a test that writes leaks rows into every later test in the process. Isolate in the test, never by weakening `db.py`.
- **Never pre-build the feature you think is coming.** The seed data hints loudly at a reorder/replenishment feature, but a wrong guess has to be explained and deleted on the clock. Wait for the task.
