---
paths:
  - "backend/app/api/**"
  - "backend/app/features/**"
  - "backend/app/models/**"
  - "backend/app/main.py"
---

# Backend feature slices

Full doctrine: `.claude/doctrine/arch-vsa.md` (placement) + `.claude/doctrine/backend-python.md` (idiom), plus `project-profile.md`. When they disagree, architecture wins on placement and language wins on idiom.

- **A slice is three files, and they stay together:** `app/api/<feature>.py` (thin route — validate, call, wrap), `app/features/<feature>/handler.py` (all business logic), `app/features/<feature>/schemas.py` (Pydantic response models). Business logic in the route file is the single most visible deviation from the template's own README.
- **Register the router in `main.py`** — `app.include_router(<feature>.router)`. A handler nobody mounts is a silent 404.
- **Route paths carry no `/api` prefix.** Vite strips it in the proxy; mirroring it here yields a 404 that reads like a routing bug.
- **`app/models/` dataclasses are entities, not ORM rows.** Nothing maps `sqlite3.Row` to them automatically — if a slice wants one, it constructs it. Adding a generic mapper is a design decision, not a refactor.
- **Do not create a shared/ or common/ dumping ground for a single caller.** Isolate between slices; duplicate before you couple.
