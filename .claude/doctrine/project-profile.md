# Project Profile — interview-template

**Priority:** High. Pointed at from `CLAUDE.md`, so an agent is told to read it every session — but it is **not** auto-loaded, and nothing but `CLAUDE.md` is. Constraints that must survive regardless (the catastrophic, non-discoverable few) belong *in* `CLAUDE.md`; everything else lives here and is read on the way in. This is the repo's overlay over the read-only base skill library. Base files under `.claude/skills/` and `.claude/doctrine/` install verbatim and are never edited; everything repo-specific lands here.

```yaml
stack: "Python 3.12 / FastAPI + stdlib sqlite3 (in-memory), pytest + httpx; frontend Vite 5 + Vue 3.4 + TypeScript 5.3 (no component library, no router, no store)"
architecture_core: arch-layered    # owns PLACEMENT — layer boundaries, downward dependencies, where queries live
backend_core: backend-python      # owns IDIOM — typing, async choice, error translation, pytest
frontend_core: frontend-vue       # paired with arch-frontend.md (framework-neutral structure)
architecture: "Layered with a feature-subdivided application layer — app/api/ (transport) -> app/features/<feature>/ (business logic) -> app/models/ (entities) + app/db.py (data). Dependencies point downward; no ports. Frontend src/{api,App.vue}"
tracker: "GitHub issues (jicata/interview-template) = `origin`, standard fork layout. `upstream` is prmsolutions/interview-template, read-only; see Deploy & environments"
check_commands:
  - "cd backend && .venv/Scripts/python -m pytest"       # Windows venv layout; POSIX is .venv/bin/
  - "cd frontend && npx vue-tsc --noEmit"                # the type gate
  - "cd frontend && npm run build"                       # vue-tsc + vite build
ci: none                       # no .github/workflows; nothing gates a merge but the local commands above
axis_c: off                    # no CI check-runs exist to read; see skills/_shared/axis-c.md
mode: greenfield               # a scaffold with one worked example (hello); the real task arrives live
chassis: none
legacy_oracle: none
doc_appetite: lean             # canon seeded: glossary + ADRs + architecture map
pipeline_tier: full            # HITL lane + autonomous afk lane both installed
review_identity: app           # claude-reviewer-jicata[bot] — native APPROVE / REQUEST_CHANGES
review_app_token_cmd: "GH_APP_ID=4515491 GH_APP_INSTALLATION_ID=151915759 GH_APP_PRIVATE_KEY_PATH=$HOME/.ssh/claude-reviewer-jicata.pem node $HOME/.claude/gh-app-token.js"
coder_lens:                    # how a coder run resolves "the repo's composite coder lens"
  default: coder-lens          # .claude/skills/coder-lens/SKILL.md — one lens covers both stacks here
  backend: coder-lens          # backend/app/**  -> arch-layered + backend-python + relational-persistence
  frontend: coder-lens         # frontend/src/** -> arch-frontend + frontend-vue
default_branch: main           # NOT master. The afk pipeline's prose says `origin/master` throughout; resolve the real branch
workhorse_model: sonnet
glossary: docs/UBIQUITOUS_LANGUAGE.md
smell_routing: "file a GitHub issue on jicata/interview-template; never refactor in place (see doctrine/surface-dont-chase.md)"
base_version: 69e9e33          # jicata/skills @ pluggable-doctrine-axes
```

## How to maintain this file (the fill-in convention)

- **Every constraint is: imperative + WHY + evidence pointer.** A rule with a scar attached gets obeyed; a bare imperative gets relitigated. Evidence = a commit, incident, issue, doc, or dated observation — something a skeptical future agent can check.
- **Edit in place, never append chronologically.** When reality changes, rewrite or delete the constraint. This file is a map, not a log.
- **Trigger-indexed:** constraints live under the activity that should trip them, so an agent doing persistence work reads Persistence, not everything.
- **Axis conflicts resolve one way:** the architecture core wins on **placement**, the language core wins on **idiom**, and a constraint in *this file* beats both. See `.claude/doctrine/AXES.md`.
- **Graduate at a screen:** when a section outgrows one screen, move its body to its own doctrine file (e.g. `.claude/doctrine/<topic>.md`) and leave one index line here pointing at it.

## What this repo is for

This is a **live-coding interview sandbox**, cloned from a template the interviewing company (`prmsolutions`) publishes. The actual task is handed over verbally at the start of the session and is not in the repo. The full skill pipeline is installed deliberately, as a dress rehearsal of the normal working stack — not because a throwaway repo needs it.

> **The task is unknown until the session starts — do not pre-build features.** The seed data strongly suggests a reorder/replenishment feature (each customer buys one product on a regular cadence; order 19 is an empty `draft` with no `order_date`; `pack_size` matches every historical `quantity`), but a guess that turns out wrong is worse than no code at all, because it must then be explained and deleted under time pressure. WHY: the README says only "your interviewer will share your task separately". Evidence: `README.md`; `backend/data/orders.csv` rows 1–19.

## Coder lens routing

`execute-issue`, `afk-execute-issue` and the `afk-coder` agent all implement "through the repo's composite coder lens", resolved from the `coder_lens` key above. **There is one lens here — `/coder-lens`** — because the repo is small enough that a single manifest covers both stacks; larger repos split it per stack.

> **A coder run loads `/coder-lens` before writing code, every time.** It is the only artifact that knows both axis picks, so it is what composes `arch-layered` (placement) with `backend-python` (idiom). WHY: doctrine files are not skills and are never auto-loaded — without the lens naming them, `backend-python.md` reaches context only if a path rule happens to fire. Evidence: `.claude/doctrine/00-doctrine-index.md` → "How anything here reaches context".

> **The path rules are the safety net, not the primary route.** `rules/backend-slices.md` fires automatically on `backend/app/**` and names `backend-python.md` inline along with its sharpest imperatives, so an agent working *without* invoking any skill still gets the load-bearing rules. Do not let that redundancy tempt you into thinning either one — they cover different failure modes: the rule covers ad-hoc edits, the lens covers pipeline runs.

## Architecture

**Layered, with the application layer subdivided by feature.** Three horizontal groupings — `app/api/` (transport), `app/features/<feature>/` (business logic), `app/models/` + `app/db.py` (entities and data) — with dependencies pointing **downward only**. There are no ports and no dependency inversion, which is what makes this `arch-layered` rather than `arch-clean`/`arch-onion`. Base doctrine: `.claude/doctrine/arch-layered.md`.

> **A slice is deliberately split across `api/` and `features/` — do not "fix" it by moving the route into the feature package.** The README states the pattern explicitly: "a thin API route calls a feature handler, which holds the business logic." WHY: it looks like an incomplete vertical slice and invites a helpful restructure of the interviewer's own scaffold, which spends the clock and reads as not doing the task. Evidence: `README.md` project structure; `app/api/hello.py` → `app/features/hello/handler.py`.

> **`models/` is imported by nothing and `db.py` only by `main.py`, for its import side-effect.** The `hello` slice demonstrates the routing pattern and stops short of the data pattern — the seam between a handler and the database does not exist yet. WHY: this is the deliberate hole, not an oversight; the README says "how you read and write the seeded data is your call." Evidence: verified 2026-08-24 — no module imports `app.models`; `main.py` imports `app.db` under `noqa: F401 — triggers CSV load at startup`.

> **Put a feature's queries with that feature (`app/features/<f>/queries.py`), not in a generic repository.** Promote to a shared data-access module only when a *second* feature actually needs the same query. WHY: `arch-layered` rule 4 and the README's open question point the same way, and a generic repository built for one consumer is the abstraction the interviewer left out on purpose. Evidence: `.claude/doctrine/arch-layered.md` → rules 4 and 6; `README.md`.

> **Do not introduce a single port/Protocol seam.** Either the app is layered or it is inverted; one hand-rolled interface in an otherwise-layered app buys nothing and confuses which architecture applies. If the task genuinely demands substitutability, say so out loud and invert deliberately. Evidence: `arch-layered.md` anti-pattern 9.

## Security & live-data safety

**No live or shared environments are reachable from this repo.** The database is an in-memory SQLite built fresh at process start — there is nothing to destroy that surviving a restart, and no production anything. The real hazard here is the opposite of the usual one: state is *too* cheap to lose, so a passing test can be hiding the fact that nothing was persisted.

The one outward-facing constraint:

> **`origin` is yours; `upstream` is the interviewer's and is never written to.** Standard fork layout, set 2026-08-24: `origin` = `jicata/interview-template` (writable), `upstream` = `prmsolutions/interview-template` (read-only). A bare `git push` therefore goes to your own repo. WHY: the layout was originally inverted, which meant every pipeline skill — all of which hardcode `origin` — pointed at the interviewer's repo. Swapping makes the safe thing the default instead of a rule to remember. Evidence: `git remote -v`; the whole afk lane hardcodes `origin/master`.

> **Never push, PR, or file an issue against `upstream`.** It is the repo the people evaluating you can see, and nothing there can be quietly undone. Evidence: same.

> **The default branch is `main`, but the pipeline's prose says `master` everywhere.** `/afk-execute-issue` carries the escape hatch — "where this skill says `master`, use the repo's actual default branch (resolve once: `gh repo view --json defaultBranchRef`)" — but **`/ship-issue` does not**, and its worktree setup runs `git worktree add --detach "$WORKTREE_PATH" origin/master` literally, which fails here. Substitute `origin/main` wherever a ship-* skill says `origin/master`. WHY: the inconsistency is a base-library defect, not a repo quirk; fixing it locally would edit a read-only base file. Evidence: `ship-issue/SKILL.md` line 106 vs `afk-execute-issue/SKILL.md` line 16; verified 2026-08-24 — `defaultBranchRef` is `main`.

## Persistence

One module-level `sqlite3` connection (`app/db.py::_conn`) to `:memory:`, built and seeded from `backend/data/*.csv` at **import time**. `check_same_thread=False`, with an asserted `sqlite3.threadsafety == 3`. There is no ORM, no migration tool, and **no repository layer** — the README states the data-access design is deliberately left to the candidate. Base doctrine: `.claude/doctrine/relational-persistence.md`; this section records only what is specific here.

> **Every write goes through `db.transaction()` — never `get_connection()` directly for a write.** The context manager takes a process-wide `threading.Lock`, commits on success and rolls back on error. WHY: FastAPI serves sync endpoints from a thread pool, and the implicit transaction belongs to the *shared* connection, so two concurrent writers commit or roll back each other's partial work. Evidence: commit `b0a7929` "Fix the shared-database threading bug (#1)" — this is the single bug the template authors chose to plant and then fix, which makes it the thing they are most likely to watch for.

> **Reads may use `get_connection()` directly; do not wrap them in `transaction()`.** WHY: the lock is process-wide, so wrapping reads serializes every request through one mutex for no benefit. Evidence: `app/db.py` docstring — "Use for any handler that writes".

> **A schema change means editing `_build_db()`'s `executescript` AND the matching CSV — there are no migrations.** Column order in the CSV header drives the `INSERT`, and empty string is coerced to `NULL`. WHY: the loader reads `rows[0].keys()` to build the column list, so a header/schema mismatch fails at import, which takes the whole app down at startup rather than at request time. Evidence: `app/db.py::_build_db`.

> **`unit_price` is denormalized onto `order_lines` and is the historical price — do not "fix" it by joining to `products`.** WHY: an order line records what was charged at the time; `products.unit_price` is the current price. They happen to be equal in the seed data, which makes the bug invisible in tests. Evidence: schema in `app/db.py`; `data/order_lines.csv` vs `data/products.csv`.

## Testing

`pytest` + `fastapi.testclient.TestClient`, one file per feature under `backend/tests/`. `tests/test_hello.py` is the worked template. `pytest.ini` sets `testpaths = tests`, so run pytest from `backend/`.

> **Tests share the app's single module-level connection — there is no per-test rollback.** A test that writes leaves those rows visible to every later test in the same process, and test order is therefore load-bearing unless you isolate deliberately. Fix it in the test (a fixture that wraps each test in a transaction and rolls back, or one that restores the seeded rows), never by weakening `db.py`. WHY: `_conn` is built once at import and `TestClient` imports the same `app.db` module the app does. Evidence: `app/db.py` module scope; `tests/test_hello.py` imports `app.main`.

> **The absence of a repository/data-access layer is not a test gap — do not flag it.** WHY: the README states it explicitly as a design decision left open. Evidence: `README.md` — "There is **no data-access / repository layer** — how you read and write the seeded data is your call."

## Merge gates

The `check_commands` above are the only gate. There is no CI, no branch protection, and no second human — `axis_c: off` is a statement of fact, not a deferral.

> **An agent raising "there is no CI" as a blocker is noise; suppress it.** WHY: a sandbox repo that exists for one interview session will never have CI stood up. Evidence: Q12 interview, 2026-08-24.

> **Reviews post as `claude-reviewer-jicata[bot]`, so `APPROVE` and `REQUEST_CHANGES` land natively.** App ID `4515491`, installation `151915759`, key `~/.ssh/claude-reviewer-jicata.pem`, minted by `~/.claude/gh-app-token.js`. WHY: GitHub rejects APPROVE/REQUEST_CHANGES from a PR's own author, so a self-authored review can only ever be `COMMENTED`. Evidence: verified 2026-08-24 — `GET installation/repositories` returns both `jicata/Brochures` and `jicata/interview-template`, and the minted token reaches this repo's `pulls` endpoint.

> **`reviewDecision` will still read `null` on this repo — read `latestReviews[].state` instead.** WHY: the field requires branch protection with a review requirement, which this repo does not have; a genuine App `CHANGES_REQUESTED` still leaves it null. Evidence: `setup/github-app.md` — "What it does **not** light up is the PR's `reviewDecision` field." The merge gate already reads `latestReviews`.

> **The binding verdict remains the `**Verdict:**` marker in the review body**, per `.claude/skills/_shared/review-protocol.md`. The App identity only decides whether GitHub *also* records it natively. WHY: one contract works under both identities, so a token failure degrades the audit trail, not the gate.

## Deploy & environments

Nothing deploys. Two local processes, started by hand:

```bash
cd backend && .venv/Scripts/uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev                                   # port 3000, proxies /api -> :8000
```

> **Create the venv with `py -3.12`, not bare `python`.** The default `python` on this machine is 3.11.2; the README requires 3.12+. WHY: the app runs on 3.11 today, but a version-gated syntax or stdlib change during the session would fail confusingly under time pressure. Evidence: `py -0p` on 2026-08-24 lists `-V:3.12` at `%LOCALAPPDATA%\Programs\Python\Python312`; `README.md` prerequisites.

> **Push with the `jicata` credential, not the active `gh` account.** `gh auth status` shows two logged-in accounts — `SGalovVSG` (active) and `jicata` — and the fork belongs to **jicata**. A plain `git push` resolves to the active account and fails `403 Permission denied to SGalovVSG`. Use `git push "https://x-access-token:$(gh auth token -u jicata)@github.com/jicata/interview-template.git" HEAD:<branch>`, which avoids switching the global active account and keeps the token out of `.git/config`. WHY: the failure is intermittent-looking — earlier pushes in the same session succeeded on a cached credential — so it reads as a flaky remote rather than an identity mismatch. Evidence: 403 on 2026-08-24 after several successful pushes to the same remote.

> **The `Makefile` targets are broken on Windows — invoke the commands directly.** They call `.venv/bin/uvicorn` and `.venv/bin/pytest`; a Windows venv puts binaries in `.venv/Scripts/`. WHY: `make dev-backend` fails with a path error, which reads like a broken repo rather than a platform mismatch. Evidence: `Makefile`; verified 2026-08-24. This is upstream's bug, not ours — do not "fix" it in a PR to `origin`.

> **The frontend reaches the backend only through the Vite proxy.** `client.ts` uses a relative `/api` base and `vite.config.ts` rewrites `/api/*` -> `localhost:8000/*`. A route added at `/orders` on the backend is called as `/orders` from `client.ts`. WHY: the prefix is stripped by the proxy, so mirroring `/api` into the FastAPI route path yields a 404 that looks like a routing bug. Evidence: `frontend/vite.config.ts`; `frontend/src/api/client.ts`.

## Frontend

Vue 3 `<script setup>` + TypeScript, one `App.vue`, no component library, no router, no state store, no test runner. `api/client.ts` exposes **only** `get<T>()` — a feature that writes needs a `post`/`put` added there first. Base doctrine: `.claude/doctrine/arch-frontend.md` (structure, framework-neutral) + `.claude/doctrine/frontend-vue.md` (Vue idiom).

> **Keep the typed-wrapper seam — call `client.ts`, never `fetch` from a component.** WHY: it is the only place HTTP errors are turned into thrown `Error`s, and the one seam a reviewer can see you respecting. Evidence: `frontend/src/api/client.ts`.

> **Promote out of `App.vue` on the second consumer, not the first.** WHY: this repo has no `components/` directory yet; creating one for a single-use block is structure for its own sake, and the frontend doctrine's promotion rule governs. Evidence: `.claude/doctrine/arch-frontend.md` → A2 promotion rule.

## External contracts

None. No external services, no wire-contract tooling, no Postman collection, and the app constructs no prompts and calls no models — `llm-prompt-craft.md` is deliberately **not** installed.

The one contract that exists is internal: FastAPI response models under `app/features/<feature>/schemas.py` are the wire truth, and the frontend re-declares them as TypeScript interfaces by hand (see `HelloResponse` in both). Keep the two in sync manually; there is no codegen.

## Domain language

Glossary: `docs/UBIQUITOUS_LANGUAGE.md`. One bounded context — a small order-management domain (customer, product, order, order line) with no sub-domains.

> **Use the seed data's nouns, not synonyms.** `order_line` (not "item" or "line item"), `pack_size` (not "case size"), `status` values exactly `completed` | `draft`. WHY: a `CHECK(status IN ('completed','draft'))` constraint rejects anything else at write time, and a reviewer reads renamed domain nouns as a misunderstanding of the domain. Evidence: `app/db.py` schema; `backend/data/*.csv` headers.
