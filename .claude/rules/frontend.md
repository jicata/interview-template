---
paths:
  - "frontend/src/**"
  - "frontend/vite.config.ts"
---

# Vue frontend

Full doctrine: `.claude/doctrine/arch-frontend.md` (structure, framework-neutral) + `.claude/doctrine/frontend-vue.md` (Vue idiom), plus `project-profile.md` → Frontend.

- **All HTTP goes through `src/api/client.ts`** — never `fetch` in a component. It is the only place a non-2xx becomes a thrown `Error`. `client.ts` currently exposes `get<T>()` only; a feature that writes adds `post<T>` there first.
- **Call backend routes without the `/api` prefix in the path you pass** — `get('/orders')` hits `localhost:8000/orders`. The prefix belongs to `BASE`, and Vite rewrites it away.
- **Response types are hand-mirrored from the backend's Pydantic schemas.** No codegen — change one, change the other in the same commit.
- **Promote out of `App.vue` on the second consumer, not the first.** There is no `components/` directory yet; creating one for a single-use block is structure for its own sake.
- **`npm run dev` does not typecheck.** `npx vue-tsc --noEmit` is a separate, mandatory gate.
- **`ref` by default, and `.value` in script.** A `ref` read without `.value` is an always-truthy object — the most common Vue bug, and it raises no error.
