# 001. Adopt layered architecture, not VSA, Clean, or Onion

**Status:** accepted
**Date:** 2026-08-24

## Context

The skill library offers four backend architecture cores. The template had to be
matched to one, and the choice is not cosmetic: the repo's single open design
question — where data access goes, which the README leaves to the candidate — is
a *placement* question, and placement is what the architecture core governs.

The template's measured shape:

- `app/api/<feature>.py` (transport) → `app/features/<feature>/` (business logic)
  → `app/models/` + `app/db.py`. Dependencies point **downward**.
- **No ports, no interfaces, no dependency inversion, no composition root.**
- `app/models/` is imported by nothing. `app/db.py` is imported once, by
  `main.py`, purely for its import side-effect (`noqa: F401 — triggers CSV load`).
  The handler-to-database seam does not exist yet.

## Decision

Use `arch-layered`.

`arch-vsa` was rejected as directionally right but literally wrong: its instincts
(colocate by feature, no premature abstraction, no generic cross-feature
repository) fit, but its canonical slice layout places the endpoint *inside* the
slice. Followed literally it instructs an agent to move `api/hello.py` into
`features/hello/` — restructuring the interviewer's scaffold instead of doing the
task. Its slice-root census and sub-domain clustering rules also assume slices of
8+ files, where a feature here is three.

`arch-clean` and `arch-onion` were rejected despite a superficial folder-name
resemblance (`api`≈presentation, `features`≈application, `models`≈domain,
`db`≈infrastructure). Both are defined by dependencies pointing **inward** through
ports declared by the consuming layer, which this repo does not have and would
have to grow. `arch-clean` itself notes that a repo of trivial CRUD pays that cost
for nothing, and its anti-pattern #1 is the anemic domain that `models/` currently
is.

`arch-layered` did not exist when this repo was set up; it was authored in the
base library as part of this decision, since layered is the most common backend
architecture and the axis lacked a core for it.

## Consequences

- Queries live with the feature that owns them (`features/<f>/queries.py`),
  promoted to a shared module only on a second real consumer. No generic
  repository — the README leaves that open deliberately.
- The `api/` + `features/` split is **correct as-is** and must not be "fixed".
- Business logic cannot be tested without the database or a stand-in, and swapping
  the store would be invasive. Both are accepted: the store will not change, and
  the stand-in is an in-memory SQLite that costs nothing.
- **No single port/Protocol seam.** One inverted dependency in an otherwise-layered
  app buys nothing and obscures which architecture applies. If a task genuinely
  demands substitutability, invert deliberately and say so.
- If two or more of `arch-layered`'s graduation triggers appear (a second
  transport, a second store, slow rule tests, homeless cross-entity behaviour),
  revisit in favour of Clean or Onion.
