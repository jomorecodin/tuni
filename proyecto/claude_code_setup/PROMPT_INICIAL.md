# PROMPT INICIAL PARA CLAUDE CODE

Este es el prompt que debes copiar y pegar en Claude Code después de haber colocado los archivos en el directorio del proyecto. Léelo completo antes de pegarlo, y ajusta lo que esté entre [corchetes] según tus preferencias.

---

## PROMPT (copiar a partir de aquí):

Hola Claude. Soy estudiante de Ingeniería de Computación en la Universidad Metropolitana de Caracas, y estoy desarrollando el MVP de mi trabajo de grado. Antes de hacer cualquier cosa, lee el archivo `CLAUDE.md` en la raíz del proyecto y los archivos en `docs/`. Ahí está todo el contexto del proyecto.

Mi objetivo en esta sesión es construir un MVP funcional end-to-end. No busco un producto pulido, busco demostrar que la arquitectura propuesta funciona y que puedo desplegar algo a estudiantes reales en las próximas semanas.

### Plan de trabajo propuesto

Quiero que trabajemos en este orden, y que me consultes antes de tomar decisiones importantes:

**Fase 1 — Setup inicial (hoy)**
1. Crear la estructura de directorios completa según lo descrito en `CLAUDE.md`.
2. Inicializar `requirements.txt` para el backend con dependencias mínimas: fastapi, uvicorn, supabase, google-generativeai, sqlalchemy, alembic, python-dotenv, pydantic.
3. Inicializar los dos proyectos Next.js (frontend-student y frontend-dashboard) con TypeScript y Tailwind.
4. Crear los archivos `.env.example` con todas las variables necesarias documentadas.
5. Escribir las migraciones SQL iniciales para Supabase con todas las tablas del modelo de datos.

**Fase 2 — Backend mínimo**
1. Implementar el cliente de Gemini con carga de prompts desde Markdown (`backend/app/core/gemini_client.py` y `prompt_loader.py`).
2. Crear los archivos `prompts/modo_neutral.md` y `prompts/modo_tutor.md` con un primer borrador del system prompt para cada modo. Para el modo tutor, prioriza la guía socrática sobre la respuesta directa, pero sin ser molesto.
3. Implementar el endpoint `POST /api/chat` que reciba `{user_id, modo, mensaje, sesion_id}` y devuelva la respuesta del modelo, registrando todo en la base de datos.
4. Implementar el endpoint `POST /api/onboarding` que reciba la encuesta inicial (ver `docs/encuesta_onboarding.md`) y cree el estudiante, las inscripciones y las evaluaciones.
5. Implementar endpoints básicos del dashboard: `GET /api/dashboard/overview`, `GET /api/dashboard/students`, `GET /api/dashboard/students/{id}`.

**Fase 3 — Frontend del estudiante**
1. Pantalla de login (Supabase Auth con email).
2. Flujo de onboarding multi-paso con la encuesta.
3. Interfaz de chat con selector de modo (neutral / tutor) y conversación clara y limpia.
4. Persistencia de la sesión activa.

**Fase 4 — Dashboard mínimo**
1. Vista panorámica con las cuatro métricas principales (estudiantes activos, interacciones totales, % uso modo tutor, índice formativo-sustitutivo promedio).
2. Vista por estudiante con perfil individual.
3. Filtros globales (carrera, trimestre, modo, periodo).
4. Tabla cruda de interacciones con búsqueda.

### Consideraciones importantes

- **Costos:** uso `gemini-2.5-flash` por defecto. Si necesitas escalar a Pro para algo específico, pregúntame primero.
- **Privacidad:** la tabla `estudiante` (identidad real) debe quedar aislada desde el inicio. Todo el resto del sistema debe usar `user_id` opaco.
- **Convenciones:** código y comentarios en inglés, UI en español. Type hints en Python, modo estricto en TypeScript.
- **Cuando tengas dudas, pregunta.** Prefiero invertir 30 segundos respondiendo que rehacer una hora de código.

### Información que necesitarás de mí

Voy a ir proporcionándote a medida que avancemos:
- API key de Gemini (la cargaré yo en `.env`)
- Credenciales de Supabase (las cargaré yo en `.env`)
- Listado real de carreras y materias del piloto (después de validar con mi tutor)

### Empecemos

Por favor empieza leyendo `CLAUDE.md` y los documentos en `docs/`, y luego propón un plan detallado de la Fase 1 antes de escribir código. Quiero validar contigo el plan antes de que ejecutes.

---

## Notas de uso

1. **Antes de pegar el prompt**, asegúrate de tener en el directorio:
   - `CLAUDE.md`
   - `README.md`
   - `docs/modelo_de_datos.md` (puedes copiar el contenido del .docx que generé y pegarlo en formato Markdown)
   - `docs/encuesta_onboarding.md` (idem)
   - `docs/wireframe_dashboard.md` (idem)

2. **Comando para ejecutar Claude Code en el directorio:**
   ```bash
   cd ruta/al/proyecto
   claude
   ```

3. **Si Claude Code te pregunta por permisos:** dale acceso completo al directorio del proyecto. No le des acceso al sistema completo.

4. **Sesiones recomendadas:** divide el trabajo en sesiones de 1-2 horas por fase. No intentes hacer todo en una sola sesión, perderás contexto y calidad.

5. **Versionado:** crea un repositorio Git desde el inicio y commitea después de cada fase. Si algo sale mal, puedes revertir.

## Archivos que aún te falta crear o convertir

Antes de iniciar Claude Code, conviene que tengas los siguientes archivos en el directorio:

- `CLAUDE.md` — ya lo tienes
- `README.md` — ya lo tienes
- `docs/modelo_de_datos.md` — necesitas convertir el .docx a Markdown
- `docs/encuesta_onboarding.md` — necesitas convertir el .docx a Markdown
- `docs/wireframe_dashboard.md` — necesitas convertir el .docx a Markdown
- `.gitignore` — para no commitear `.env` ni `node_modules`

Si quieres, puedo generarte los tres documentos directamente en Markdown para que los pongas en `docs/` sin necesidad de convertirlos. También puedo generarte un `.gitignore` apropiado.
