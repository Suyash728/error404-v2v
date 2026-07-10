# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Arohi is a women's wellness PWA built around a companion persona, "Sakhi". It is a monorepo:

- `/web` — Next.js 14 (App Router), TypeScript, Tailwind, Framer Motion
- `/api` — FastAPI, Python 3.12

This is a hackathon build with a 36-hour budget and 2 developers. Optimize for boring, readable code over abstraction. Do not build for hypothetical future requirements — if a helper is only used once, inline it.

## Commands

### web (`/web`)
- `npm run dev` — start the Next.js dev server
- `npm run build` — production build
- `npm run lint` — lint
- Run a single test the same way the test runner configured in `web/package.json` supports (e.g. `npx jest <path>` or `npx vitest run <path>`) — check `package.json` scripts before assuming which one is wired up.

### api (`/api`)
- `uvicorn main:app --reload` (or the equivalent entrypoint under `api/`) — run the dev server
- `pytest` — run all tests
- `pytest api/tests/test_rule_engine.py -k <name>` — run a single test
- Tests are **required** (not optional) for:
  - `services/rule_engine.py`
  - `services/prediction.py`
  - `services/gamification.py`

Check for a `Makefile`, `package.json`, or `pyproject.toml` at the relevant root before assuming a command name — this list reflects the intended structure, not a verified script inventory.

## Architecture

### web
- Server components are the default. Only mark a component `"use client"` when it genuinely needs interactivity (state, effects, event handlers, browser APIs, Framer Motion animation).
- All API calls go through `web/lib/api.ts`. Do not call `fetch` against the API directly from components — route it through this module, which is responsible for attaching the Supabase JWT to outgoing requests. If `api.ts` doesn't support a needed pattern yet, extend it there rather than bypassing it.
- Design tokens come **only** from `tailwind.config.ts` and CSS variables. Never hardcode colors, spacing, or other design values in component code. The palette is a pink base plus 4 phase-specific palettes (cycle-phase theming) — new UI must pull from these, not introduce new ad hoc colors.
- Accessibility is a graded requirement, not a nice-to-have, for every UI change: semantic HTML, aria labels where semantics aren't enough, full keyboard navigation, `prefers-reduced-motion` handling for any Framer Motion animation, and WCAG-AA contrast. Treat these as non-negotiable acceptance criteria for UI work, not follow-up polish.

### api
- Structure: `routers/` (HTTP layer) → `services/` (business logic) → `models/`. Keep routers thin; put logic in services.
- Auth: every endpoint requires Supabase JWT verification except `/health`. Uses `supabase-py`.
- LLM access is centralized: `services/llm_client.py` is the **only** module allowed to call an LLM. Primary model is Gemini 2.5 Flash, with Groq as fallback. Any feature needing LLM calls goes through this client rather than calling a provider SDK directly — this keeps provider swaps and fallback logic in one place.

## Color usage rules
Phase and brand colors have three tiers — never use them interchangeably:
- `phase-X` / `brand-primary` (raw accent): decorative fills only — icons, wheel segments, badges, gradient stops. NEVER as text, NEVER as a solid button background with text on top.
- `phase-X-soft`: tinted card/chip backgrounds, paired with default `--foreground` text.
- `phase-X-text` / `phase-ovulatory-accent-text`: the ONLY tokens allowed when a phase color is used AS text color on `--background`/`--surface`.
- `--on-accent` (#000) / `--on-deep` (#FFFFFF): the ONLY tokens allowed as text color on top of a solid `--accent`/`--brand-deep` fill (e.g. primary buttons). Never assume `--foreground` or white is safe on a colored fill without checking TOKENS.md's contrast table.

Every screen-conversion prompt must follow this without being reminded.

## Database invariants
- A trigger on `auth.users` creates a `public.profiles` and `public.gamification` row (with defaults) for every user at signup. All backend code MUST assume these rows already exist: use `UPDATE` or upsert, never a plain `INSERT` that assumes the row is absent.
- Onboarding UPDATEs the existing profile with the user's cycle data — it does not INSERT a new profile.
- RAG retrieval MUST use cosine distance (the `<=>` operator) to match the HNSW `vector_cosine_ops` index.
- Every user table cascades from `auth.users`, so account deletion = delete the auth user and let cascades handle the rest.

## Conventions
- No premature abstraction: prefer duplication over a shared helper until a third use case actually appears.
- Keep changes readable over clever, given the compressed timeline and two-person team.

### After Each Prompt
- Tell me what steps to do manually.