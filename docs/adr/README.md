# Architecture Decision Records

One file per decision that outlives the session: `NNN-short-slug.md`, numbered in order.

An ADR is for a decision with **live alternatives** — something a future reader would otherwise re-litigate. A fact about how the code works belongs in `../architecture.md`; a constraint with a scar belongs in `.claude/doctrine/project-profile.md`.

## Format

```markdown
# NNN. <Decision, as a statement>

**Status:** proposed | accepted | superseded by NNN
**Date:** YYYY-MM-DD

## Context
What forced a choice. The constraints, not the narrative.

## Decision
What was chosen, in the active voice.

## Consequences
What this makes easy, what it makes hard, and what it forecloses.
```

## Records

- [001. Adopt layered architecture, not VSA, Clean, or Onion](001-layered-not-vsa-or-clean.md) — why the template is layered and what that decides about data access.
- [002. Derive order-line pricing on read; round each line, then sum](002-pricing-derived-not-stored.md) — why no discount column exists, and which of the two order totals is the right one.
