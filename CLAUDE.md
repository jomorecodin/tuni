# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TUNI is a pilot platform for investigating how generative AI impacts university student learning, developed as a bachelor's thesis at Universidad Metropolitana de Caracas. It provides students and professors with a single agentic LLM assistant via Telegram bot, collects detailed telemetry on interactions, and feeds a pedagogical analytics dashboard.

The active codebase is in `proyecto/tuni-bot/`. The `tuni/` and `proyecto/claude_code_setup/` directories are older prototypes and should be ignored.

## Critical Design Decisions (September 2026)

1. **Single agentic model** — NO more dual modes (tutor/neutral). The bot is one unified agent that manages interactions, adapts its behavior based on context, and handles all user types.

2. **Two user roles via tokens:**
   - **Students** — default role. The agent knows their subjects from the cronograma, assists with academics, tracks telemetry.
   - **Professors** — authenticated via pre-generated tokens. They get access to aggregated analytics of their subjects, gap reports, usage patterns. They do NOT see individual student conversations (privacy). Professors can also update cronogramas and provide context about their teaching.

3. **No button-based subject selection** — The agent infers the subject from conversation context. The cronograma already defines what subjects exist. Students don't need to manually select career → trimester → subject.

4. **Local knowledge bank** — The bot must NOT depend on web searches. Each subject has a `context/` folder with curriculum content (.md files) that the agent uses as reference. These need to be populated with real content: key concepts, formulas, common problems, syllabus topics.

5. **Supabase as primary data layer** — Both for telemetry storage AND for the AI consultation module (text-to-SQL exploratory analysis on raw empirical data).

6. **Deployment** — CT (LXC container) on Proxmox with Ubuntu, Ollama for local inference (qwen3:8b), systemd services. Dashboard on Vercel, API exposed via Cloudflare tunnel.

## Repository Structure

```
proyecto/claude_code_setup/
├── backend/              # Python FastAPI API server
│   ├── app/
│   │   ├── main.py       # FastAPI app entry point
│   │   ├── api/          # Route handlers
│   │   ├── core/         # Config, Gemini client, prompt loading
│   │   ├── db/           # Database models and session
│   │   └── services/     # Business logic (classifier, telemetry, metrics)
│   ├── prompts/          # System prompt markdown files (modo_neutral.md, modo_tutor.md)
│   ├── migrations/       # Alembic SQL migrations
│   └── requirements.txt
├── frontend-student/     # Next.js 16 + React 19 student chat interface
│   ├── app/              # App router (layout.tsx, page.tsx)
│   └── components/       # ChatInterface, ChatLayout, ModeSelector, Sidebar
├── frontend-dashboard/   # Next.js dashboard for researcher (not yet implemented)
└── docs/                 # Data model, onboarding survey, wireframes
```

## Build & Run Commands

All commands run from `proyecto/claude_code_setup/`.

### Backend (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend Student (Next.js 16)
```bash
cd frontend-student
npm install
npm run dev       # Dev server on http://localhost:3000
npm run build     # Production build
npm run lint      # ESLint
```

### Frontend Dashboard (Next.js)
```bash
cd frontend-dashboard
npm install
npm run dev -- --port 3001  # Dev server on http://localhost:3001
```

### Health Check
- Backend: `GET http://localhost:8000/health`

## Architecture

### Three-Service Architecture
- **Backend** (port 8000): FastAPI REST API. Wraps the Google Gemini API (`gemini-2.5-flash` by default), manages sessions, records telemetry to PostgreSQL via Supabase.
- **Frontend Student** (port 3000): Next.js 16 with React 19, TailwindCSS v4, lucide-react icons. Chat interface with mode selection (neutral / tutor).
- **Frontend Dashboard** (port 3001): Next.js with Recharts. Researcher-facing analytics views.

### Key Data Flow
1. Student selects mode (neutral or tutor) → starts session
2. Each message goes to `POST /api/chat` with `{user_id, modo, mensaje, sesion_id}`
3. Backend injects corresponding system prompt from `prompts/` markdown files via Gemini API
4. Response + telemetry (5 layers) recorded to PostgreSQL
5. Dashboard reads aggregated data via `GET /api/dashboard/*` endpoints

### Telemetry Layers
1. Identification/context (user, subject, timing, proximity to evaluation)
2. Student query (prompt length, type, specificity, academic context)
3. Model response (length, type, completeness, generation time)
4. Behavior (iterations, timing between messages, regenerations, abandonment)
5. Derived metrics (formative-substitutive index, usage intensity, thematic diversity)

### Privacy Design
- Real student identity lives only in `estudiante` table (restricted access)
- All other tables use opaque `user_id` via the `usuario` table
- Interactions are immutable once recorded

## Code Conventions

- **Language**: Code, comments, and variable names in English. UI strings in Spanish.
- **Python**: PEP 8, type hints on public functions. Use pydantic-settings for config.
- **TypeScript**: Strict mode, avoid `any`. Functional components only.
- **Commits**: Descriptive messages in Spanish, format `tipo(alcance): descripción`.
- **No localStorage in frontend**: Use React state or backend for persistence.

## Important Notes

- **Next.js 16 breaking changes**: The `frontend-student` uses Next.js 16 with React 19. Read docs in `node_modules/next/dist/docs/` before writing code — APIs and conventions differ from Next.js 14/15.
- **LLM model**: Default is `gemini-2.5-flash`. Do not switch to Pro without explicit approval.
- **SQL migrations**: Must be reversible (include DOWN migration).
- **Gemini integration**: Use latest Google SDK (`google-generativeai`), implement exponential backoff for network errors.
- **Dashboard priority**: Clarity over aesthetics — the user is a researcher, not a consumer.
- **Database**: PostgreSQL via Supabase (free tier). Auth via Supabase Auth.

## Environment Variables

Backend `.env`:
```
GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_ROLE_KEY,
GEMINI_MODEL (default: gemini-2.5-flash), APP_ENV, APP_PORT, CORS_ORIGINS
```

Frontend `.env.local`:
```
NEXT_PUBLIC_API_URL, NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY
```

## Key Documentation Files

- `proyecto/claude_code_setup/CLAUDE.md` — Full project specification and data model
- `proyecto/claude_code_setup/docs/modelo_de_datos.md` — Complete database schema
- `proyecto/claude_code_setup/docs/encuesta_onboarding.md` — Onboarding survey spec
- `proyecto/claude_code_setup/docs/wireframe_dashboard.md` — Dashboard wireframes
- `MODELO.md` — LLM model specs, system prompts, and telemetry schema (Qwen/Ollama alternative)
- `ENCUESTA_ESTUDIANTE.md` / `ENCUESTA_PROFESOR.md` — Survey instruments
