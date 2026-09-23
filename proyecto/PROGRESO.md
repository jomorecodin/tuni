# TUNI — Registro de Progreso del Proyecto

**Proyecto:** Investigacion sobre el impacto de la IA generativa en el aprendizaje universitario
**Autor:** Joseph Moreno — Universidad Metropolitana de Caracas
**Trabajo de grado — Ingenieria de Sistemas**
**Ultima actualizacion:** 2026-09-22

---

## 1. Reformulacion del Proyecto

### Modelo original (web)
El proyecto inicio como una plataforma web con dos modos de asistencia:
- **Modo neutral:** LLM sin restricciones pedagogicas (respuestas directas)
- **Modo tutor:** LLM con metodo socratico (guia con preguntas)

La arquitectura era:
- Frontend: Next.js 16 + React 19 (chat web)
- Backend: FastAPI + Ollama (Qwen 2.5 7B)
- Base de datos: PostgreSQL via Supabase

### Decision de pivotar a Telegram
Se identificaron problemas con el modelo web:
- **Friccion de adopcion:** los estudiantes no visitaran voluntariamente una plataforma web para estudiar
- **Engagement bajo:** requiere que el estudiante abra un navegador, vaya a la URL, inicie sesion
- **Fuera del flujo natural:** los estudiantes ya viven en Telegram/WhatsApp

**Solucion:** Migrar a un **bot de Telegram** como interfaz principal. Ventajas:
- Cero friccion — acceso via QR code o link directo (t.me/tuni_bot)
- Notificaciones nativas del telefono
- El estudiante ya tiene Telegram instalado
- Permite recoleccion de patrones conductuales naturales (horarios, frecuencia, tiempos de respuesta)

### Simplificacion del modo
Se elimino el **modo neutral**. El piloto usa unicamente el modo **asistente academico** (tutor socratico). Razon: un solo modo simplifica el analisis comparativo y se enfoca en la pregunta de investigacion central — si el metodo socratico via IA promueve aprendizaje formativo vs sustitutivo.

---

## 2. Sistema de Encuestas (completado)

### Descripcion
Se construyo un sistema de encuestas desplegado en Vercel como primer contacto con los participantes del piloto.

### Componentes
- **Encuesta estudiante** (`/encuestas/estudiante`): 6 secciones, ~20 preguntas, 5-7 minutos
  - Datos demograficos, uso previo de IA, percepcion, autoevaluacion academica, interes en asistente academico, comentarios
- **Encuesta profesor** (`/encuestas/profesor`): encuesta para docentes sobre percepcion de IA en educacion
- **Panel administrativo** (`/encuestas/admin`): dashboard protegido con clave de acceso para visualizar respuestas con graficos (Recharts)

### Tecnologias
- Next.js 16 + React 19 + TailwindCSS v4
- Supabase (tablas `respuesta_encuesta_estudiante`, `respuesta_encuesta_profesor`)
- Desplegado en Vercel: https://tuni-ten.vercel.app

### Estado
- Funcional y desplegado
- Repositorio: https://github.com/jomorecodin/tuni

---

## 3. Diseno del Bot de Telegram

### Arquitectura
El bot es un proceso Python standalone que importa directamente los modulos del backend existente (no pasa por HTTP/SSE). Componentes clave:

| Componente | Tecnologia |
|------------|-----------|
| Libreria Telegram | `python-telegram-bot` v21 (async) |
| LLM (desarrollo) | Gemini 2.5 Flash (API) |
| LLM (produccion) | Qwen3-8B via Ollama (CPU) |
| Base de datos | Supabase (PostgreSQL) |
| Tracking local | Archivos JSON por estudiante |
| Deployment | Docker Compose + PM2 en VM Proxmox |

### Seleccion de modelo para produccion
La VM de produccion tiene 32GB RAM, sin GPU (CPU only). Despues de evaluar multiples modelos:

| Modelo | Tamano | tok/s CPU | Espanol | Matematicas |
|--------|--------|-----------|---------|-------------|
| **Qwen3-8B** | ~5GB | 8-15 | Excelente | Excelente |
| Qwen2.5:7B | ~4.5GB | 8-12 | Muy bueno | Bueno |
| Llama 3.1:8B | ~4.7GB | 8-12 | Regular | Bueno |
| Mistral:7B | ~4.1GB | 8-12 | Bueno | Moderado |

**Eleccion: Qwen3-8B** — mejor balance de velocidad, soporte en espanol y capacidad matematica. Modo dual thinking/non-thinking ideal para tutoria socratica.

### Flujo de conversacion
```
/start → Consentimiento → Subir horario (opcional) → Seleccionar materia → Chat con IA
```

El bot incluye:
- **ConversationHandler** con 4 estados: AWAITING_CONSENT, UPLOAD_SCHEDULE, SELECTING_SUBJECT, CHATTING
- **Streaming progresivo**: edita el mensaje cada ~1.5s mientras genera la respuesta
- **Timeout de sesion**: 30 minutos de inactividad
- **Protocolo de heartbeat**: check-ins semanales, pre/post-evaluacion, re-engagement por inactividad

---

## 4. Marco de Medicion Pedagogica

Se definieron 18 patrones de medicion divididos en dos categorias (documentados en `proyecto/tuni-bot/docs/patrones_pedagogicos.md`):

### Fundamentados en teoria educativa (8 patrones)

| # | Patron | Teoria | Autor |
|---|--------|--------|-------|
| 1 | Nivel cognitivo de preguntas | Taxonomia de Bloom | Anderson & Krathwohl, 2001 |
| 2 | Efectividad del scaffolding | Zona de Desarrollo Proximo | Vygotsky, 1978 |
| 3 | Autorregulacion del aprendizaje | Self-Regulated Learning | Zimmerman, 2002 |
| 4 | Indicadores de sobrecarga | Carga Cognitiva | Sweller, 1988 |
| 5 | Dependencia de IA | Indefension Aprendida | Seligman, 1972 (adaptado) |
| 6 | Lucha productiva | Dificultades Deseables | Bjork, 1994 |
| 7 | Conciencia metacognitiva | Metacognicion | Flavell, 1979 |
| 8 | Indice formativo-sustitutivo | Marco original TUNI | Moreno, 2026 |

### Empiricos / conductuales (10 patrones)

| # | Patron | Que mide |
|---|--------|----------|
| 9 | Frecuencia y duracion de sesiones | Con que frecuencia y por cuanto tiempo se usa el bot |
| 10 | Profundidad de sesion | Intercambios por sesion |
| 11 | Tiempo entre mensajes | Velocidad de respuesta del estudiante |
| 12 | Evolucion de longitud de mensajes | Si los mensajes se elaboran mas o menos |
| 13 | Picos pre-evaluacion | Uso intensivo antes de examenes |
| 14 | Abandono post-socratico | Desercion cuando el bot no da respuesta directa |
| 15 | Patrones horarios | Horas y dias de uso |
| 16 | Diversidad de materias | Cuantas materias consulta |
| 17 | Deteccion de copy-paste | Indicador de uso sustitutivo |
| 18 | Auto-correcciones | Instancias de correccion propia sin guia del bot |

### Indicador central: Indice Formativo-Sustitutivo
Escala [-1, +1] donde:
- **+1 (formativo):** el estudiante usa la IA para construir comprension
- **-1 (sustitutivo):** el estudiante usa la IA para reemplazar el proceso de aprendizaje

---

## 5. Tracking por Estudiante

Cada estudiante tiene un archivo JSON (`data/students/{telegram_id}.json`) que se actualiza en tiempo real con:
- Fecha de consentimiento
- Horario semanal (subido como foto/PDF)
- Materias usadas
- Todos los patrones pedagogicos (teoria + empiricos)
- Snapshots semanales para datos longitudinales

Esto complementa la telemetria en Supabase, que almacena las interacciones individuales.

---

## 6. Implementacion del Bot — Estado Actual

### Estructura del proyecto
El bot vive en `proyecto/tuni-bot/` como carpeta autocontenida para comprimir y mover a la VM.

### Fases completadas

**Fase 0: Setup del proyecto** ✅
- Estructura de carpetas creada
- Modulos reutilizables copiados y adaptados
- `patrones_pedagogicos.md` documentado (18 patrones)
- `llm_client.py` con soporte dual Gemini/Ollama

**Fase 1: Fundacion del bot** ✅
- `constants.py` — 4 estados de conversacion, strings UI en espanol
- `keyboards.py` — teclados inline para consentimiento y materias
- `user_manager.py` — mapeo Telegram → usuario en Supabase
- `student_tracker.py` — gestion de archivos JSON por estudiante (escritura atomica)
- `session_manager.py` — dataclass UserSession, crear/cerrar sesiones
- `start.py` — flujo /start → consentimiento → subir horario
- `subject_selection.py` — seleccion de materia via botones
- `commands.py` — /ayuda, /materia, /nueva, /estado, /horario
- `main.py` — ConversationHandler con PicklePersistence
- `config.py` — Pydantic Settings con provider dual
- Migracion 003 aplicada en Supabase

**Fase 2: Chat handler con streaming** ✅
- `streaming.py` — edicion progresiva de mensajes con debounce 1.5s
- `chat.py` — handler completo: sesion check → LLM → streaming → telemetria diferida
- `llm_client.py` — streaming async para Gemini (dev) y Ollama (produccion)

**Fase 2.5: Telemetria diferida** ✅
- Arquitectura refactorizada: cero I/O de disco durante conversaciones activas
- Interacciones se bufferean en memoria en el objeto `UserSession`
- Al cerrar sesion (timeout 30min, /materia, /nueva) se hace un unico flush:
  - Actualizacion batch del JSON del estudiante (una sola lectura+escritura)
  - Generacion de log de conversacion en `data/conversations/{session_id}.json`
- Supabase inserts se mantienen por mensaje (network calls non-blocking post-respuesta)
- Resultado: tiempo de respuesta del bot no se degrada con el tracking

**Fase 3: Rendering LaTeX** ⬜ Pendiente

**Fase 4: Heartbeat + comandos avanzados** ⬜ Pendiente

**Fase 5: Docker + PM2 deployment** ⬜ Pendiente

### Base de datos
- Migracion 003 aplicada: columna `telegram_id` en `usuario`, tabla `evento_interaccion`
- RLS policies configuradas para operacion con anon key
- 8 materias cargadas en tabla `materia`
- Todas las operaciones DB verificadas: insert usuario, sesion, interaccion, evento_interaccion

### Dependencias instaladas
```
python-telegram-bot==21.6
supabase==2.9.1
pydantic-settings==2.5.2
httpx==0.27.2
matplotlib==3.9.2
apscheduler==3.10.4
```

---

## 7. Infraestructura

| Componente | Servicio | Estado |
|------------|----------|--------|
| Encuestas web | Vercel (Next.js) | ✅ Desplegado |
| Base de datos | Supabase (free tier) | ✅ Operativo |
| Repositorio | GitHub (jomorecodin/tuni) | ✅ Activo |
| Bot Telegram | Local (dev) → VM Proxmox (prod) | 🔧 En desarrollo |
| LLM dev | Gemini 2.5 Flash API | ✅ Configurado |
| LLM prod | Ollama + Qwen3-8B | ⬜ Pendiente (VM) |

### VM Proxmox (produccion)
- 32GB RAM, sin GPU, hasta 250GB storage
- Docker Compose: contenedor Ollama + contenedor bot
- PM2 para auto-restart y log rotation
- Long-polling (sin necesidad de dominio/HTTPS)

---

## 8. Proximos Pasos

1. **Probar el bot** con Gemini como LLM de prueba
2. **Fase 3**: Rendering LaTeX (Unicode + matplotlib PNG)
3. **Fase 4**: Heartbeat scheduler (APScheduler)
4. **Fase 5**: Dockerizar para la VM Proxmox
5. **Crear bot en BotFather** y definir nombre/descripcion publica
6. **Generar QR code** de acceso para distribuir a estudiantes
7. **Piloto**: 12 semanas con ~60 estudiantes

---

## Archivos Clave

| Archivo | Descripcion |
|---------|-------------|
| `proyecto/tuni-bot/` | Carpeta autocontenida del bot |
| `proyecto/tuni-bot/docs/patrones_pedagogicos.md` | Marco de medicion (18 patrones) |
| `proyecto/tuni-bot/app/bot/main.py` | Entry point del bot |
| `proyecto/tuni-bot/app/services/llm_client.py` | Cliente dual Gemini/Ollama |
| `proyecto/tuni-bot/migrations/003_telegram_support.sql` | Migracion DB |
| `proyecto/PROGRESO.md` | Este documento |
| `CLAUDE.md` | Instrucciones para Claude Code |
