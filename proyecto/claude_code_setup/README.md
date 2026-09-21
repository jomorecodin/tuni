# Plataforma piloto de asistencia académica con telemetría

Trabajo de grado de la Escuela de Computación, Facultad de Ingeniería, Universidad Metropolitana de Caracas.

## Descripción

Sistema para investigar la incidencia académica del uso de inteligencia artificial generativa en estudiantes universitarios. La plataforma ofrece a los estudiantes un asistente basado en Google Gemini en dos modos (neutral y tutor académico), registra todas las interacciones con telemetría detallada, y alimenta un dashboard de gestión pedagógica para análisis del investigador.

## Estructura del repositorio

- `backend/` — API REST en FastAPI con integración Gemini y persistencia en PostgreSQL
- `frontend-student/` — Interfaz del estudiante (Next.js)
- `frontend-dashboard/` — Dashboard del investigador (Next.js)
- `docs/` — Documentación del proyecto (modelo de datos, encuesta, wireframes)
- `CLAUDE.md` — Contexto del proyecto para asistencia con Claude Code

## Setup local

### Prerequisitos

- Python 3.11+
- Node.js 20+
- Cuenta en Supabase (tier gratuito)
- API key de Google Gemini

### Variables de entorno

Copia `.env.example` a `.env` en cada subdirectorio y completa los valores:

```bash
# backend/.env
GEMINI_API_KEY=
SUPABASE_URL=
SUPABASE_KEY=
DATABASE_URL=
SECRET_KEY=

# frontend-student/.env.local
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=

# frontend-dashboard/.env.local
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
```

### Instalación

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head

# Frontend del estudiante
cd ../frontend-student
npm install

# Dashboard
cd ../frontend-dashboard
npm install
```

### Ejecución

```bash
# Terminal 1 - Backend
cd backend && uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend estudiante
cd frontend-student && npm run dev

# Terminal 3 - Dashboard
cd frontend-dashboard && npm run dev -- --port 3001
```

URLs locales:
- Backend API: http://localhost:8000
- Frontend estudiante: http://localhost:3000
- Dashboard: http://localhost:3001

## Privacidad y ética

Este sistema captura datos de uso de estudiantes con fines exclusivamente académicos. Todos los participantes firman consentimiento informado. La identidad real de los estudiantes se almacena en una tabla aislada con acceso restringido al investigador principal, separada de los datos analíticos. Al cierre del piloto, esta tabla será eliminada o sellada, dejando solamente datos anonimizados disponibles para el análisis posterior.

## Licencia

Uso académico. Todos los derechos reservados al autor del trabajo de grado.

## Contacto

[Datos del autor a completar]
