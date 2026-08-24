# Doctrine Index — interview-template

**GENERATED.** This is a manifest over what `.claude/doctrine/` actually contains — not prose. Regenerate it when doctrine is added, removed, or renamed (`/skill-sync`). Do not hand-write rules here; they belong in a doctrine file or in `project-profile.md`.

## Always on

Loaded every session, no trigger needed.

| File | Why it's always on |
| --- | --- |
| `project-profile.md` | The overlay: machine-readable repo facts + this repo's scar tissue. Every other file defers to it for repo specifics. |
| `documentation-first.md` | Consult docs before code. The canon here is the full lean three — glossary, ADRs, architecture map — all seeded under `docs/`. |
| `AXES.md` | The composition contract: which core owns placement vs idiom, and how the two resolve when they disagree. |
| `surface-dont-chase.md` | A smell noticed in already-loaded context gets one line and an offer to log it — never an unasked refactor. Sharper than usual here: this is a timed interview repo, and an unasked refactor spends the clock. |

## Load on trigger

| Trigger — what you are about to do | Load |
| --- | --- |
| Add, move, or rename a file under `backend/app/features/**` or `backend/app/api/**` | `arch-layered.md` — layer boundaries, downward-only dependencies, where queries live |
| Touch **schema, seed CSVs, queries, or anything that writes** | `relational-persistence.md` + profile → Persistence, Testing |
| Write or change **anything under `frontend/src/**`** | `arch-frontend.md` (structure) + `frontend-vue.md` (idiom) + profile → Frontend |
| Write or change **any Python** | `backend-python.md` (idiom) + `arch-layered.md` (placement) + profile → Persistence, Testing |
| **Review** a PR (Standards axis) | `fowler-smell-baseline.md` + whichever of the above match the changed paths |
| Write or edit **a skill, agent, or doctrine file** | `writing-skills.md` + `writing-skills-glossary.md` |
| Explain a change, write a teaching briefing, or justify an approach in prose | `how-to-explain.md` |
| Name a domain concept, or argue about what something should be called | profile → Domain language + `docs/UBIQUITOUS_LANGUAGE.md` |
| Record a decision that outlives the session | `docs/adr/` + `documentation-first.md` |

## Routing by changed path (for the review skills)

> **This table is also enforced natively.** `.claude/rules/*.md` carry `paths:` frontmatter, so Claude Code loads the matching rule — which names the governing doctrine and its sharpest constraints — the moment it reads a file in that path. The table below stays as the reviewer's explicit checklist and as the source of truth if the two ever disagree; the rules are the automatic half, not a replacement.

| Path | Doctrine | Rule file |
| --- | --- | --- |
| `backend/app/api/**`, `backend/app/features/**`, `backend/app/models/**` | `arch-layered.md`, `backend-python.md` | `rules/backend-slices.md` |
| `backend/app/db.py`, `backend/data/**` | `relational-persistence.md` | `rules/persistence.md` |
| `backend/tests/**` | profile → Testing | `rules/persistence.md` |
| `frontend/src/**` | `arch-frontend.md`, `frontend-vue.md` | `rules/frontend.md` |
| `.claude/**` | `writing-skills.md` | `rules/skill-authoring.md` |

## Axes

Doctrine cores plug in along independent axes (`.claude/doctrine/AXES.md`). This repo's picks:

| Axis | Core | Owns |
| --- | --- | --- |
| Backend architecture | `arch-layered.md` | placement — layer boundaries, downward-only dependencies, where queries live |
| Backend language | `backend-python.md` | idiom — typing, async choice, error translation, pytest |
| Frontend architecture | `arch-frontend.md` | placement — page/component boundary, promotion |
| Frontend framework | `frontend-vue.md` | idiom — `ref` vs `reactive`, composables, the type gate |

**When two disagree:** architecture wins on placement, language wins on idiom, and `project-profile.md` beats both.
