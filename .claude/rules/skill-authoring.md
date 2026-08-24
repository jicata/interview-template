---
paths:
  - ".claude/**"
---

# Editing skills, doctrine and rules

Full doctrine: `.claude/doctrine/writing-skills.md` + `writing-skills-glossary.md`.

- **Base files install verbatim and are read-only.** Everything under `.claude/skills/` and `.claude/doctrine/` — except `project-profile.md`, `00-doctrine-index.md` and `skills/coder-lens/` — is a copy of `jicata/skills`. A repo-specific edit to one breaks upgrades, which are file copies.
- **Repo-specific truth goes in `project-profile.md`**, as imperative + WHY + evidence pointer. It is this repo's only writable skill surface.
- **A generic improvement born here goes upstream, not into the local copy** — `/skill-sync` classifies and moves it.
- **Every new `.claude/rules/*.md` MUST carry `paths:` frontmatter.** Without it the file loads in every session forever, at CLAUDE.md priority.
- **Verify a new glob matches real files.** A rule matching nothing looks like coverage and provides none.
