---
name: coder-lens
description: The composite lens every coder run loads before writing code in this repo — routing from changed paths to the doctrine and skills that govern them. Use when implementing any change to Python, the frontend, the SQLite schema, or the seed CSVs.
---

# Coder lens — interview-template

**GENERATED.** This is a manifest: which installed files a coder run loads, and when. It holds no rules of its own. Rules live in `.claude/doctrine/`; repo facts and scars live in `.claude/doctrine/project-profile.md`. Regenerate via `/skill-sync` when the installed set changes.

## Always load, before any code

1. `.claude/doctrine/project-profile.md` — repo facts, `check_commands`, and the constraints that override everything below.
2. `.claude/doctrine/00-doctrine-index.md` — the routing table this lens mirrors.
3. `.claude/skills/karpathy-guidelines/SKILL.md` — general coding approach.
4. `.claude/skills/tdd/SKILL.md` + `tests.md` + `mocking.md` + `refactoring.md` — the red-green loop.
5. `.claude/skills/codebase-design/SKILL.md` — module depth and testable seams.

## Then load by what you are changing

| Changing | Also load |
| --- | --- |
| Any Python under `backend/app/**` | `.claude/doctrine/backend-python.md` — typing, the `def` vs `async def` choice, context managers, exception chaining, error translation at the route boundary, pytest discipline |
| A new or changed feature slice — `app/api/<f>.py` + `app/features/<f>/**` | `.claude/doctrine/arch-vsa.md` + profile → What this repo is for |
| `app/db.py`, `data/*.csv`, or any handler that writes | `.claude/doctrine/relational-persistence.md` + profile → Persistence |
| Anything under `backend/tests/**` | profile → Testing — shared-connection state leaks across tests |
| Anything under `frontend/src/**` | `.claude/doctrine/arch-frontend.md` (structure) + `.claude/doctrine/frontend-vue.md` (idiom) + profile → Frontend |
| A response schema and its TypeScript twin | profile → External contracts — hand-synced, no codegen |

## The two things this repo will punish

Ahead of any general doctrine, because both are invisible in a green test run:

1. **A write that does not go through `db.transaction()`.** One shared connection, one implicit transaction. See profile → Persistence.
2. **A test that leaves rows behind.** No per-test rollback exists; the next test inherits your writes. See profile → Testing.

## Conflict resolution

- **Profile beats doctrine.** A constraint in `project-profile.md` is this repo's recorded reality; a base doctrine file is the generic default.
- **Architecture wins on placement, language wins on idiom.** Where a file goes and what may import it: `arch-vsa.md` / `arch-frontend.md`. What it is called and how it is written: `backend-python.md` / `frontend-vue.md`. See `.claude/doctrine/AXES.md`.
- **Behaviour beats implementation.** For test design, TDD's behaviour-driven approach wins — test user-visible behaviour, not internals.
- **The worked example beats inference.** Where both are silent, match `app/api/hello.py` + `app/features/hello/`. Consistency with the template's own shape is what a reviewer reads as fluency.

## Definition of done

Every command in the profile's `check_commands` exits 0:

```bash
cd backend && .venv/Scripts/python -m pytest
cd frontend && npx vue-tsc --noEmit
cd frontend && npm run build
```

Green backend tests alone are **not** done — the frontend type gate is separate, and nothing in `npm run dev` typechecks.
