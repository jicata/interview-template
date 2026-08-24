# Doctrine Index — interview-template

**GENERATED.** This is a manifest over what `.claude/doctrine/` actually contains — not prose. Regenerate it when doctrine is added, removed, or renamed (`/skill-sync`). Do not hand-write rules here; they belong in a doctrine file or in `project-profile.md`.

## How anything here reaches context

**Nothing in this directory is auto-loaded.** The harness loads exactly two things by itself: `CLAUDE.md` (every session) and `.claude/rules/*.md` carrying `paths:` frontmatter (when a matching file is opened). Every other file below arrives only because something already in context told an agent to read it.

| File | How it actually arrives |
| --- | --- |
| `project-profile.md` | Named in `CLAUDE.md` and by all 4 rules — the closest thing to always-on. Read it every session. |
| `00-doctrine-index.md` | Named in `CLAUDE.md`. This file. |
| `surface-dont-chase.md` | Its imperative is **inlined in `CLAUDE.md`** (Ambient smells), so the rule applies even if this file is never read. |
| `AXES.md` | Loaded by `rules/skill-authoring.md` when anything under `.claude/**` is touched. |
| Everything else | On trigger — the table below, or a rule, or a skill that names it. |

## Load on trigger

| Trigger — what you are about to do | Load |
| --- | --- |
| Add, move, or rename a file under `backend/app/features/**` or `backend/app/api/**` | `arch-layered.md` — layer boundaries, downward-only dependencies, where queries live |
| Touch **schema, seed CSVs, queries, or anything that writes** | `relational-persistence.md` + profile → Persistence, Testing |
| Write or change **anything under `frontend/src/**`** | `arch-frontend.md` (structure) + `frontend-vue.md` (idiom) + profile → Frontend |
| Write or change **any Python** | `backend-python.md` (idiom) + `arch-layered.md` (placement) + profile → Persistence, Testing |
| **Review** a PR (Standards axis) | `fowler-smell-baseline.md` + whichever of the above match the changed paths |
| Write or edit **a skill, agent, or doctrine file** | `writing-skills.md` + `writing-skills-glossary.md` |
| Explain a change, write a teaching briefing, or justify an approach in prose | `how-to-explain.md` — loaded by `/explain-diff-html`, `/wait-what`, and any expand/log briefing |
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
