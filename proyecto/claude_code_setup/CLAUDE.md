# Proyecto: Plataforma piloto de asistencia académica con telemetría

## Contexto del proyecto

Este repositorio contiene el MVP (Minimum Viable Product) de una plataforma piloto desarrollada como parte de un trabajo de grado de la Escuela de Computación de la Universidad Metropolitana de Caracas. El estudio investiga la incidencia académica del uso de inteligencia artificial generativa en estudiantes universitarios.

La plataforma será desplegada a una muestra de aproximadamente 60 estudiantes durante 12 semanas, registrará todas sus interacciones con un modelo de lenguaje basado en Google Gemini, y alimentará un dashboard de gestión pedagógica que permita al investigador analizar patrones de uso.

## Objetivos del MVP

El MVP debe demostrar que es técnicamente viable:

1. Capturar interacciones de estudiantes con un LLM en dos modos diferenciados (neutral y tutor académico).
2. Registrar telemetría detallada de cada interacción.
3. Almacenar datos académicos del estudiante (carrera, materias, evaluaciones).
4. Visualizar patrones de uso a través de un dashboard analítico.

NO se busca todavía un producto pulido visualmente, sino un sistema funcional end-to-end que pueda evolucionar a producción.

## Arquitectura tentativa

### Stack tecnológico recomendado

- **Backend:** Python con FastAPI. Razón: integración natural con la API de Gemini, librerías estadísticas robustas para los cálculos derivados, y rapidez de desarrollo.
- **Frontend del estudiante:** Next.js (React) con TailwindCSS para la interfaz conversacional.
- **Frontend del dashboard:** Next.js con Recharts para visualizaciones.
- **Base de datos:** PostgreSQL via Supabase (free tier).
- **Autenticación:** Supabase Auth.
- **LLM:** Google Gemini API (modelo `gemini-2.5-flash` por defecto, con routing opcional a Pro).
- **Despliegue:** Railway o Render para el backend, Vercel para los frontends.

### Capas funcionales

1. **Capa de interacción:** interfaz conversacional accesible desde web. El estudiante elige entre modo neutral y modo tutor académico al inicio de cada sesión.
2. **Capa de orquestación del modelo:** wrapper sobre la API de Gemini que inyecta como system prompt el archivo de parametrización pedagógica correspondiente al modo seleccionado.
3. **Capa de telemetría:** módulo que captura las variables definidas, las almacena en PostgreSQL y las expone vía API REST.
4. **Capa de dashboard:** frontend separado para el investigador, con seis vistas principales (panorámica, por estudiante, por carrera, por materia, temporal, interacciones).

## Modelo de datos

El modelo completo está documentado en el archivo `docs/modelo_de_datos.md`. Resumen de entidades principales:

- `estudiante` — tabla aislada de identidad real (acceso restringido)
- `usuario` — identidad operativa anonimizada
- `carrera`, `materia`, `pensum_carrera`, `inscripcion`, `evaluacion`, `historial_evaluacion` — bloque académico
- `sesion`, `interaccion`, `clasificacion_interaccion`, `evento_interaccion` — bloque de interacción
- `parametrizacion_modelo` — versionado del system prompt
- `metrica_usuario_periodo`, `metrica_materia_periodo` — agregaciones precalculadas

## Variables de telemetría (las cinco capas)

### Capa 1 — Identificación y contexto
`user_id`, `carrera`, `trimestre_cursado`, `materia_asociada`, `timestamp_inicio`, `timestamp_fin`, `duracion_sesion`, `dispositivo`, `momento_del_dia`, `dia_semana`, `proximidad_a_evaluacion`.

### Capa 2 — Consulta del estudiante
`longitud_prompt`, `tipo_consulta`, `nivel_especificidad`, `presencia_de_contexto_academico`, `idioma_consulta`, `consulta_contiene_enunciado_textual`, `contiene_codigo`, `contiene_pregunta_explicita_vs_imperativa`.

### Capa 3 — Respuesta del modelo
`longitud_respuesta`, `tipo_respuesta`, `nivel_de_completitud`, `tokens_generados`, `tiempo_de_generacion`.

### Capa 4 — Comportamiento e interacción
`numero_de_iteraciones_en_sesion`, `tiempo_entre_mensajes`, `regenero_respuesta`, `pidio_explicacion_adicional`, `pidio_simplificacion`, `pidio_ejemplos`, `pidio_correccion_de_su_intento`, `abandono_sesion_tras_primera_respuesta`.

### Capa 5 — Variables derivadas
`indice_formativo_sustitutivo`, `intensidad_de_uso_semanal`, `patron_temporal`, `diversidad_tematica`, `profundidad_de_interaccion`.

## Parametrización del modelo

El comportamiento del modelo se controla mediante archivos Markdown que se inyectan como system prompt. Existen dos archivos principales:

- `prompts/modo_neutral.md` — replica comportamiento estándar de un asistente general
- `prompts/modo_tutor.md` — política pedagógica que prioriza guía sobre respuesta directa

Los archivos están versionados en la tabla `parametrizacion_modelo`. Cada interacción registra qué versión del prompt se usó.

## Restricciones de diseño

- **Anonimización por diseño:** la identidad real del estudiante vive solo en la tabla `estudiante`. Todo el resto del sistema usa `user_id` opaco.
- **Inmutabilidad de interacciones:** una vez registrada, una interacción no se modifica.
- **Costos controlados:** el modelo por defecto es Flash. Solo escalar a Pro bajo criterios definidos.
- **Sin localStorage en frontend:** usar estado de React o backend para persistencia.

## Estructura de directorios sugerida

```
/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── chat.py
│   │   │   ├── telemetry.py
│   │   │   ├── students.py
│   │   │   └── dashboard.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── gemini_client.py
│   │   │   └── prompt_loader.py
│   │   ├── db/
│   │   │   ├── models.py
│   │   │   └── session.py
│   │   └── services/
│   │       ├── classifier.py
│   │       ├── metrics_calculator.py
│   │       └── telemetry_service.py
│   ├── prompts/
│   │   ├── modo_neutral.md
│   │   └── modo_tutor.md
│   ├── migrations/
│   ├── requirements.txt
│   └── .env.example
├── frontend-student/
│   ├── pages/
│   │   ├── index.tsx
│   │   ├── login.tsx
│   │   ├── onboarding.tsx
│   │   └── chat.tsx
│   ├── components/
│   │   ├── ChatInterface.tsx
│   │   ├── ModeSelector.tsx
│   │   └── OnboardingForm.tsx
│   ├── lib/
│   └── package.json
├── frontend-dashboard/
│   ├── pages/
│   │   ├── index.tsx
│   │   ├── student/[id].tsx
│   │   ├── career/[id].tsx
│   │   ├── subject/[id].tsx
│   │   ├── temporal.tsx
│   │   └── interactions.tsx
│   ├── components/
│   │   ├── FilterBar.tsx
│   │   ├── MetricCard.tsx
│   │   └── charts/
│   ├── lib/
│   └── package.json
├── docs/
│   ├── modelo_de_datos.md
│   ├── encuesta_onboarding.md
│   └── wireframe_dashboard.md
├── README.md
└── CLAUDE.md (este archivo)
```

## Prioridades de desarrollo

Si necesitas tomar decisiones sobre qué desarrollar primero:

1. **Crítico para MVP:**
   - Esquema de base de datos en Supabase (migraciones SQL)
   - Backend con endpoints `/chat`, `/onboarding`, `/dashboard`
   - Wrapper de Gemini con carga de prompts desde Markdown
   - Frontend del estudiante: login, onboarding, chat
   - Dashboard: vista panorámica + vista por estudiante

2. **Importante pero diferible:**
   - Clasificador automático de interacciones (puede empezar con reglas heurísticas, después ML)
   - Vistas avanzadas del dashboard (por carrera, por materia, temporal)
   - Cálculo de métricas derivadas
   - Sistema de notificaciones

3. **No prioritario para MVP:**
   - Diseño visual pulido
   - Tests automatizados exhaustivos
   - Optimizaciones de rendimiento
   - Internacionalización

## Convenciones de código

- **Idioma:** comentarios y nombres de variables en inglés. Strings de UI en español.
- **Estilo Python:** PEP 8, type hints obligatorios en funciones públicas.
- **Estilo TypeScript:** modo estricto, no usar `any`.
- **Commits:** mensajes descriptivos en español, formato `tipo(alcance): descripción`.

## Decisiones pendientes

- Confirmación final del modelo Gemini a usar (`gemini-2.5-flash` vs `gemini-2.5-pro`).
- Implementación del clasificador formativo-sustitutivo (reglas vs ML).
- Política de actualización del calendario académico durante el piloto.
- Estrategia de respaldo y exportación de datos al cierre del piloto.

## Notas para Claude Code

- Cuando generes código, asume que el desarrollador es estudiante de ingeniería de sistemas con conocimiento medio. Explica decisiones técnicas no obvias.
- Cuando crees migraciones SQL, hazlas reversibles (incluye `DOWN`).
- Cuando integres con la API de Gemini, usa la última versión del SDK oficial de Google y maneja errores de red con reintentos exponenciales.
- Cuando construyas el dashboard, prioriza claridad sobre estética: el usuario es el investigador, no un usuario final masivo.
- Si encuentras ambigüedades en este documento, pregunta antes de asumir.
