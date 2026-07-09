### Project Title: Arohi (Sanskrit: "ascending / rising / a progressive musical tune")

### The Idea
Arohi is a women's wellness PWA centered on cycle tracking and holistic health insight. It pairs the user with an in-app companion persona, "Sakhi", who surfaces phase-aware guidance, predictions, and gentle nudges instead of raw data dumps.

### Important Links
 ●  Live Deployment Link: [Insert URL here]
 ●  Demo Video Link: [Insert YouTube/Drive URL here]

### Features
 ●  Phase-aware theming: pink base palette plus 4 distinct phase palettes that drive the entire UI
 ●  Sakhi companion: conversational guidance backed by an LLM (Gemini 2.5 Flash primary, Groq fallback)
 ●  Rule-based + predictive cycle insights (`services/rule_engine.py`, `services/prediction.py`)
 ●  Gamification to encourage consistent logging (`services/gamification.py`)
 ●  Installable, accessible PWA experience (WCAG-AA, full keyboard navigation, `prefers-reduced-motion` support)

### Tech Stack & Tools
 ●  Web: Next.js 14 (App Router), TypeScript, Tailwind CSS, Framer Motion
 ●  API: FastAPI, Python 3.12, supabase-py
 ●  Auth/DB: Supabase (JWT-based auth on every endpoint except `/health`)
 ●  LLM: Gemini 2.5 Flash (primary), Groq (fallback) — routed through a single `services/llm_client.py`

### Getting Started

**web**
```
cd web
cp .env.example .env.local   # fill in Supabase URL/anon key + API URL
npm install
npm run dev                  # http://localhost:3000
```

**api**
```
cd api
cp .env.example .env         # fill in Supabase + LLM keys, then export them
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload    # http://localhost:8000
```

### Documentation
See [CLAUDE.md](./CLAUDE.md) for repository structure, conventions, and commands used during development.
