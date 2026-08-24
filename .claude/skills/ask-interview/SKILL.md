---
name: ask-interview
description: Ask which skill or flow fits your situation. A router over this repo's skill stack.
disable-model-invocation: true
---

# Ask — interview-template

You don't remember every skill, so ask. This router names the flows and the edges between skills — it gists and routes, it never restates a skill's contents.

**Maintenance rule:** any skill add / rename / behavior change triggers a re-check of this file. A new skill it never mentions, or a stale one it still routes to, is a router that lies.

A **flow** is a path through the skills. Most work travels the main flow; on-ramps merge onto it.

> **Repo note:** `origin` is **your fork**, `jicata/interview-template` — every skill below that files an issue or opens a PR targets it correctly. `upstream` is the interviewer's repo and is never written to. The default branch is `main`, not the `master` the ship-* skills name in their prose.

## The main flow

0. Too big to hold in one session, and the unknowns are *decisions* rather than build slices → `/wayfinder`. Charts the work as a map of decision tickets and works them one at a time until the route is clear, then hands off to the spec-authoring skill. It never builds. Skip this step when you already know what you're building.
1. Sharpen the idea by interview — `/grill-with-docs` when it should leave a paper trail in the glossary or an ADR; `/grill-me` for a plan that doesn't touch the doc set.
2. `/write-a-prd` — interview → codebase exploration → module design → files a `PRD:` issue.
3. `/prd-to-issues` — slices the PRD into child issues as tracer-bullet vertical slices, with `Blocked by` edges. Prints the execution order.
4. Build — two lanes. **HITL** (default): `/expand-issue` → `/execute-issue` → `/review-pr` → `/address-pr` → `/merge-pr`, running ahead on expands while the coder builds. **Autonomous:** `/ship-feature <prd>` loops the coder + reviewer subagents over every child and never halts.
5. Finalize — `/execute-issue` on the all-merged path, or `/ship-feature`, merges the base branch to `main` and closes the PRD.

**In a timed session, most work will not travel this whole flow.** A single task from the interviewer is one issue, not a PRD: go straight to the on-ramp below.

## On-ramps

- Something feels off and you can't name it yet → `/triage`. Comes back with what's actually going on and no fix attached, then exits to `/log-issue`, `/write-a-prd`, `/diagnosing-bugs`, or nothing-to-file.
- A bug or small enhancement you *can* name → `/log-issue` → `/ship-issue <n>` (autonomous) or the HITL lane off `main`. Outgrows one PR → `/write-a-prd`. A bug that *resists* drops into `/diagnosing-bugs`.
- A PR someone (or some agent) else wrote → `/review-pr <n>`; fixes via `/address-pr <n>`; merge via `/merge-pr <n>`.
- Only Axis-B threads left after max iterations → `/concede-pr` files the tech-debt issue and approves.
- A mid-flight merge or rebase conflict → `/resolving-merge-conflicts`.
- A `[ship-cleanup]` issue accumulated residue → `/drain-cleanup`.
- A run's **Execution conformance** block flagged a review-identity mismatch, or a review posted as the PR author instead of the App → `/fix-review-identity`. Reviews should post as `claude-reviewer-jicata[bot]`; a review appearing under your own account means the token command failed and the gate silently fell back to comment-only.

## Understanding the system

- `/flow-map` — visual, incremental: grow a runtime-flow diagram step-by-step as you reason, each block grounded in the real handler. Needs the Miro MCP.
- `/miro-diagram` — visual, one-shot: you already understand it; this draws it in a single pass. Needs the Miro MCP.
- `/prototype` — a throwaway spike answering ONE design question; the verdict lands on the issue, the code never merges.
- `/lab` — a hunch turned into a *measured* verdict, with the decision rule written before the run. Where `/prototype` answers a design question by feel, `/lab` answers an empirical one with numbers.
- `/explain-diff-html` — a change explained as a self-contained HTML document for a reader who wasn't in the room.
- `/wait-what` — the last answer didn't land; stop and re-pitch it in plain language using this repo's own glossary.

## Codebase health

- Ambient smell while working → surface, don't chase: one line, offer to log it as an issue on the fork. **Sharper here than usual** — this is a timed repo and an unasked refactor spends the clock.
- Structural drift worth a real diagnosis → `/improve-codebase-architecture <area>`.
- Working-diff quality → `/code-review` (bugs) or `/simplify`.

## Vocabulary & doctrine underneath

- `/karpathy-guidelines` — behavioural guidelines targeting common LLM coding pitfalls. Loaded by `/coder-lens` on every coder run; you rarely type it.
- `/codebase-design` — deep-module vocabulary; `/tdd` and `/improve-codebase-architecture` speak it.
- `/tdd` + `/coder-lens` — the implementation lenses. `coder-lens` is this repo's generated composite: what to load before writing code, and the two mistakes this repo punishes. Coders load these; you rarely type them.
- `/code-reviewer-persona` — the persona the review skills adopt.
- `/ubiquitous-language` — extracts domain terms from the conversation into `docs/UBIQUITOUS_LANGUAGE.md`.
- `.claude/doctrine/00-doctrine-index.md` — the load-on-demand doctrine table.

## Never type these

Orchestrator internals, dispatched by `/ship-feature` / `/ship-issue`: `afk-execute-issue`, `afk-address-pr`, `afk-review-pr`, `afk-merge-pr`, `afk-concede-thread`, and the `afk-coder` / `afk-reviewer` agents. Use the human-driven equivalents in the main flow.
