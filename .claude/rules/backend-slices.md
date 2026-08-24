---
paths:
  - "backend/app/api/**"
  - "backend/app/features/**"
  - "backend/app/models/**"
  - "backend/app/main.py"
---

# Backend feature slices

Full doctrine: `.claude/doctrine/arch-layered.md` (placement) + `.claude/doctrine/backend-python.md` (idiom), plus `project-profile.md` → Architecture. When they disagree, architecture wins on placement and language wins on idiom.

- **A feature spans two layers, deliberately:** `app/api/<feature>.py` (thin route — validate, call, wrap) and `app/features/<feature>/{handler,schemas}.py` (business logic + response models). **Do not move the route into the feature package** — the split is the template's stated pattern, not an unfinished slice. Business logic in the route file is the single most visible deviation from the README.
- **Dependencies point downward only.** `api` → `features` → `models`/`db`. A data-access module importing a handler, or `models/` importing anything above it, is always a bug.
- **A feature's queries live with the feature** (`app/features/<f>/queries.py`), promoted to a shared module only on a second real consumer. Do not build a generic repository — the README leaves that open deliberately.
- **Register the router in `main.py`** — `app.include_router(<feature>.router)`. A handler nobody mounts is a silent 404.
- **Route paths carry no `/api` prefix.** Vite strips it in the proxy; mirroring it here yields a 404 that reads like a routing bug.
- **`app/models/` dataclasses are entities, not ORM rows.** Nothing maps `sqlite3.Row` to them automatically — if a slice wants one, it constructs it. Adding a generic mapper is a design decision, not a refactor.
- **Do not create a shared/ or common/ dumping ground for a single caller.** Isolate between slices; duplicate before you couple.
