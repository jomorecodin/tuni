# ANTEPROYECTO DE TRABAJO DE GRADO
## Escuela de Ingeniería de Sistemas — Universidad Metropolitana de Caracas

**Autor:** Joseph Moreno
**Tutor (Ingeniería de Sistemas):** [Por definir]
**Tutor (Educación):** [Por definir]
**Fecha:** Septiembre 2026

---

## a) Objetivos de Desarrollo Sostenible (ODS)

**ODS 4 — Educación de calidad.**
Este proyecto contribuye a la meta 4.4 (aumentar las competencias técnicas y profesionales para acceder al empleo) al investigar cómo integrar herramientas de inteligencia artificial generativa de forma pedagógicamente responsable en la educación universitaria. El sistema de telemetría propuesto genera datos que permiten a las instituciones tomar decisiones basadas en evidencia sobre políticas de uso de IA en el aula, promoviendo una educación de calidad adaptada a las realidades tecnológicas actuales.

**ODS 9 — Industria, innovación e infraestructura.**
El diseño e implementación de una plataforma de instrumentación pedagógica con arquitectura de microservicios, procesamiento de lenguaje natural y analítica en tiempo real constituye una contribución a la infraestructura tecnológica educativa, aplicando técnicas de ingeniería de software a un problema emergente en la educación superior.

---

## b) Título

**Diseño e implementación de un sistema de telemetría e instrumentación pedagógica para caracterizar patrones de interacción estudiante-IA en materias con componente matemático de la Universidad Metropolitana de Caracas**

---

## c) Planteamiento del problema

La adopción masiva de herramientas de inteligencia artificial generativa (IAG) como ChatGPT, Gemini y Claude por parte de estudiantes universitarios ha transformado las dinámicas de estudio y resolución de evaluaciones. Investigaciones recientes documentan que entre el 55% y el 86% de estudiantes universitarios utilizan estas herramientas regularmente (Chan y Hu, 2023; Shoufan, 2023), pero las instituciones carecen de visibilidad sobre cómo, cuándo y con qué propósito ocurre ese uso.

El problema central es la ausencia de instrumentos de medición que permitan distinguir entre uso formativo de la IAG —donde el estudiante utiliza la herramienta para profundizar su comprensión— y uso sustitutivo —donde la herramienta reemplaza el esfuerzo cognitivo del estudiante—. Esta distinción, identificada por Bastani et al. (2024) como determinante del impacto académico, no puede observarse con los métodos tradicionales de evaluación educativa.

Desde la perspectiva de ingeniería de sistemas, el desafío consiste en diseñar una arquitectura de software capaz de: (1) proveer una interfaz conversacional con un modelo de lenguaje grande que opere en dos modos diferenciados (neutral y tutor pedagógico), (2) capturar telemetría detallada de cada interacción sin comprometer la privacidad del estudiante, (3) clasificar automáticamente las interacciones en el eje formativo-sustitutivo mediante procesamiento de lenguaje natural, y (4) presentar los datos recopilados en un dashboard analítico que habilite la toma de decisiones pedagógicas basada en evidencia.

No existe actualmente una plataforma de código abierto que integre estos cuatro componentes en un sistema unificado diseñado para el contexto universitario latinoamericano.

---

## d) Delimitación y alcance

El sistema se desplegará como piloto en la Universidad Metropolitana de Caracas durante un periodo de 12 semanas, con una muestra de aproximadamente 60 estudiantes cursantes de materias con componente matemático (Álgebra Lineal, Matemáticas Discretas, Cálculo, Optimización, entre otras). La interfaz del estudiante será un bot de Telegram que se conecta a un modelo de lenguaje grande servido localmente. El alcance de ingeniería comprende: diseño de la arquitectura del sistema, implementación del backend con telemetría de cinco capas, desarrollo del clasificador formativo-sustitutivo, implementación del dashboard de analítica pedagógica, y documentación técnica completa. No se incluyen en este alcance el análisis estadístico de los resultados pedagógicos ni la validación del impacto educativo, los cuales corresponden al componente de Educación del trabajo de grado conjunto.

---

## e) Objetivos

### Objetivo general

Diseñar e implementar una plataforma de software con telemetría integrada que permita caracterizar los patrones de interacción entre estudiantes universitarios y un modelo de lenguaje grande en dos modalidades de asistencia (neutral y tutor pedagógico), generando datos estructurados para el análisis de la incidencia académica de la inteligencia artificial generativa.

### Objetivos específicos

1. Diseñar la arquitectura de un sistema distribuido que integre una interfaz conversacional vía Telegram, un backend de orquestación de modelos de lenguaje, un módulo de telemetría de cinco capas y un dashboard analítico, cumpliendo con principios de anonimización por diseño e inmutabilidad de registros.

2. Implementar un módulo de orquestación que inyecte dinámicamente system prompts diferenciados (modo neutral y modo tutor) al modelo de lenguaje, incorporando contexto académico del estudiante (materia, cronograma de evaluaciones, historial de interacciones) para personalizar las respuestas.

3. Desarrollar un clasificador de interacciones que asigne a cada consulta un índice formativo-sustitutivo en escala continua [0, 1], implementado en dos etapas: (a) un clasificador heurístico basado en reglas léxicas que detecta indicadores en el texto del prompt del estudiante (presencia de trabajo previo, tipo de verbo —interrogativo vs. imperativo—, especificidad temática, referencias a material de clase) y calcula un puntaje compuesto; y (b) un clasificador LLM-as-judge que utiliza el mismo modelo de lenguaje del sistema (Gemini o Qwen) con un prompt de clasificación dedicado para asignar el índice en casos donde la heurística resulte ambigua. No se emplean modelos de embeddings ni arquitecturas RAG; el clasificador opera directamente sobre el texto de cada interacción sin requerir entrenamiento previo ni bases de datos vectoriales.

4. Implementar un pipeline de telemetría que capture, almacene y exponga métricas en cinco capas: identificación y contexto, consulta del estudiante, respuesta del modelo, comportamiento e interacción, y variables derivadas.

5. Desarrollar un dashboard de analítica pedagógica que presente visualizaciones de los patrones de uso agregados por materia, estudiante y periodo temporal, incluyendo un módulo de detección de brechas académicas y una interfaz de consulta asistida por IA para el investigador.

6. Validar el sistema mediante pruebas de integración end-to-end y un benchmark pre-piloto de 100 evaluaciones (50 problemas × 2 modos) que verifique precisión matemática ≥ 85% y adherencia al modo tutor ≥ 90%.

---

## f) Justificación

La investigación sobre el impacto de la IAG en el aprendizaje universitario requiere herramientas de medición que las plataformas comerciales (ChatGPT, Gemini) no proveen: telemetría granular, clasificación formativo-sustitutiva y correlación con el calendario académico. Desde la ingeniería de sistemas, este trabajo contribuye con una arquitectura de referencia replicable para instrumentación pedagógica de interacciones estudiante-IA. La plataforma integra técnicas de procesamiento de lenguaje natural, diseño de APIs REST, gestión de datos sensibles con anonimización por diseño y desarrollo de dashboards analíticos —competencias centrales del perfil del ingeniero de sistemas. El proyecto genera además un conjunto de datos estructurado y anonimizado que podrá ser utilizado por investigadores en educación y en inteligencia artificial.

---

## g) Metodología preliminar

Se adopta una metodología iterativa incremental organizada en seis fases, alineada con prácticas de ingeniería de software ágil.

### Fase 1 — Análisis y diseño arquitectónico (Semanas 1-3)

- Levantamiento de requisitos funcionales y no funcionales mediante entrevistas con el tutor de educación y revisión de literatura.
- Diseño del modelo de datos relacional (PostgreSQL) con 14 entidades organizadas en bloques: identidad y privacidad, académico institucional, interacción con el modelo, parametrización, y análisis derivado.
- Diseño de la arquitectura de microservicios: bot de Telegram (python-telegram-bot), backend API (FastAPI), servidor de inferencia (Ollama), base de datos (Supabase/PostgreSQL), frontend dashboard (Next.js).
- Especificación de las cinco capas de telemetría y definición del esquema de clasificación formativo-sustitutivo.
- Diseño del protocolo de anonimización y consentimiento informado.

**Entregable:** Documento de arquitectura, modelo de datos, diagramas de secuencia.

### Fase 2 — Implementación del núcleo (Semanas 4-7)

- Desarrollo del bot de Telegram con flujo conversacional: onboarding, selección de materia, chat con persistencia de historial por materia, cambio de materia mediante teclado de respuesta.
- Implementación del módulo de orquestación del modelo de lenguaje: carga dinámica de system prompts, inyección de contexto académico (cronograma, evaluaciones, temas cubiertos), gestión de sesiones con timeout por inactividad.
- Desarrollo del pipeline de telemetría: registro de interacciones, eventos discretos, y metadatos contextuales en PostgreSQL.
- Implementación del clasificador formativo-sustitutivo en dos etapas: (1) clasificador heurístico v1 basado en reglas léxicas que analiza el prompt del estudiante buscando indicadores formativos (muestra trabajo previo, formula preguntas conceptuales, pide verificación, referencia material de clase) e indicadores sustitutivos (verbos imperativos como "resuelve"/"hazme", solicitud de respuesta completa, prompts cortos sin contexto) para calcular un puntaje compuesto en [0, 1]; (2) clasificador v2 LLM-as-judge que reutiliza el mismo modelo de lenguaje del sistema (MaaS — Gemini en nube u Ollama local) con un prompt de meta-clasificación dedicado, invocado como segundo paso post-respuesta para los casos donde la heurística arroja un puntaje en la zona ambigua [0.35, 0.65]. Este enfoque no requiere modelos de embeddings, búsqueda semántica, RAG ni entrenamiento de modelos propios.
- Desarrollo del sistema de cronogramas por materia (YAML) y scheduler de recordatorios.

**Entregable:** Sistema funcional end-to-end (bot → modelo → telemetría → base de datos).

### Fase 3 — Dashboard y analítica (Semanas 8-10)

- Desarrollo de la API del supervisor (FastAPI, puerto 8001) con endpoints de análisis, reportes semanales y consulta asistida por IA.
- Implementación del motor de análisis de brechas: correlación de puntos oscuros reportados en check-ins, brechas percibidas en reflexiones, y brechas docentes.
- Desarrollo del frontend del dashboard (Next.js + Recharts) con vistas: panorámica del piloto, análisis de brechas por materia, tabla de estudiantes, y chat de consulta con IA.
- Integración de métricas derivadas: índice formativo-sustitutivo promedio, intensidad de uso pre-evaluación, diversidad temática, patrones temporales.

**Entregable:** Dashboard funcional con datos en tiempo real.

### Fase 4 — Validación y benchmark (Semanas 11-12)

- Ejecución del benchmark pre-piloto: 50 problemas matemáticos reales evaluados en ambos modos.
- Pruebas de integración end-to-end: flujo completo desde registro hasta visualización en dashboard.
- Pruebas de carga: simulación de 60 usuarios concurrentes con interacciones típicas.
- Validación del clasificador formativo-sustitutivo contra clasificación manual de 100 interacciones de prueba.
- Corrección de defectos y optimización de rendimiento.

**Entregable:** Informe de validación, sistema listo para piloto.

### Fase 5 — Despliegue y piloto (Semanas 13-24)

- Configuración del servidor de producción (Proxmox VM, Ollama, servicios como daemons).
- Onboarding de participantes: consentimiento informado, registro en el bot, configuración de materias y evaluaciones.
- Monitoreo continuo del sistema durante las 12 semanas del piloto.
- Generación de reportes semanales automáticos que identifican: (a) brechas académicas —temas donde los estudiantes concentran consultas repetidas sin progresión, temas reportados como "no entendidos" en check-ins post-clase, y discrepancias entre lo cubierto en clase y lo consultado al asistente—; y (b) patrones de uso —uso predominantemente sustitutivo (índice F-S > 0.7, indicando delegación del esfuerzo cognitivo), uso formativo complementario (índice F-S < 0.3, donde el estudiante usa la herramienta para verificar intentos propios o profundizar comprensión), picos de uso pre-evaluación (incremento de consultas en los 3 días previos a un parcial), y abandono post-socrático (el estudiante deja la sesión cuando el modo tutor responde con preguntas guía en lugar de respuestas directas)—.
- Soporte técnico a participantes.

**Entregable:** Datos del piloto recopilados, sistema en producción estable.

### Fase 6 — Documentación y cierre (Semanas 25-28)

- Exportación y anonimización definitiva de datos del piloto.
- Redacción del documento de trabajo de grado (componente de ingeniería de sistemas).
- Documentación técnica: manual de despliegue, API reference, guía de mantenimiento.
- Preparación de la defensa.

**Entregable:** Documento de trabajo de grado, código fuente documentado, datos anonimizados.

---

## h) Referencias

Bastani, H., Bastani, O., Sungu, A., Ge, H., Kabakcı, Ö., y Mariman, R. (2024). Generative AI Can Harm Learning. *Wharton School Research Paper*. https://doi.org/10.2139/ssrn.4895486

Chan, C. K. Y. y Hu, W. (2023). Students' voices on generative AI: perceptions, benefits, and challenges in higher education. *International Journal of Educational Technology in Higher Education*, 20(43). https://doi.org/10.1186/s41239-023-00411-8

Denny, P., Leinonen, J., Prather, J., Luxton-Reilly, A., Amarouche, T., Becker, B. A. y Reeves, B. N. (2024). Prompt Problems: A New Programming Exercise for the Generative AI Era. *Proceedings of the 55th ACM Technical Symposium on Computer Science Education*. https://doi.org/10.1145/3626252.3630909

Ju, Y. (2024). The impact of AI-powered tools on student academic achievement: Evidence from a meta-analysis and a randomized experiment. *Education and Information Technologies*. https://doi.org/10.1007/s10639-024-12894-7

Kasneci, E., Sessler, K., Küchemann, S., Bannert, M., Dementieva, D., Fischer, F., ... y Kasneci, G. (2023). ChatGPT for good? On opportunities and challenges of large language models for education. *Learning and Individual Differences*, 103, 102274. https://doi.org/10.1016/j.lindif.2023.102274

Liang, W., Yuksekgonul, M., Mao, Y., Wu, E. y Zou, J. (2023). GPT detectors are biased against non-native English writers. *Patterns*, 4(7). https://doi.org/10.1016/j.patter.2023.100779

Mollick, E. R. y Mollick, L. (2023). Using AI to Implement Effective Teaching Strategies in Classrooms: Five Strategies, Including Prompts. *The Wharton School Research Paper*. https://doi.org/10.2139/ssrn.4391243

Prather, J., Denny, P., Leinonen, J., Becker, B. A., Estey, A., Finnie-Ansley, J., ... y Reeves, B. N. (2024). Interactions with Generative AI Chatbots in Computing Education. *ACM Computing Surveys*. https://doi.org/10.1145/3706598

Shoufan, A. (2023). Exploring Students' Perceptions of ChatGPT: Thematic Analysis and Follow-Up Survey. *IEEE Access*, 11, 38805-38818. https://doi.org/10.1109/ACCESS.2023.3268224

Wardat, Y., Tashtoush, M. A., AlAli, R. y Jarrah, A. M. (2023). ChatGPT: A revolutionary tool for teaching and learning mathematics. *Eurasia Journal of Mathematics, Science and Technology Education*, 19(7), em2286. https://doi.org/10.29333/ejmste/13272

---

## i) Plan de trabajo y cronograma

| Fase | Actividad | Semanas | Duración |
|------|-----------|---------|----------|
| 1 | Análisis y diseño arquitectónico | 1–3 | 3 semanas |
| 2 | Implementación del núcleo (bot, orquestación, telemetría) | 4–7 | 4 semanas |
| 3 | Dashboard y analítica | 8–10 | 3 semanas |
| 4 | Validación y benchmark | 11–12 | 2 semanas |
| 5 | Despliegue y piloto (12 semanas de recopilación) | 13–24 | 12 semanas |
| 6 | Documentación y cierre | 25–28 | 4 semanas |
| **Total** | | | **28 semanas (~7 meses)** |

### Diagrama de Gantt simplificado

```
Semana:  1  2  3  4  5  6  7  8  9  10 11 12 13 14 ... 24 25 26 27 28
Fase 1:  ████████████
Fase 2:              ████████████████
Fase 3:                                ████████████
Fase 4:                                            ████████
Fase 5:                                                     ████████████████████████████████████████████████
Fase 6:                                                                                                     ████████████████
```

---

## j) Planificación de inscripción en trimestres futuros

| Trimestre | Periodo estimado | Actividades del trabajo de grado |
|-----------|-----------------|----------------------------------|
| Actual (inscripción TG) | Sep–Dic 2026 | Aprobación del anteproyecto. Fases 1-3: diseño, implementación del núcleo y dashboard. |
| Siguiente | Ene–Mar 2027 | Fase 4: validación. Fase 5: inicio del piloto (primeras 8 semanas). |
| Siguiente +1 | Abr–Jul 2027 | Fase 5: cierre del piloto. Fase 6: análisis, documentación y defensa. |

**Nota:** La planificación asume que la inscripción del trabajo de grado se formaliza en el trimestre Sep–Dic 2026 y que el piloto se ejecuta durante un trimestre académico completo para capturar un ciclo completo de evaluaciones.

---

## Anexos técnicos (referencia)

Los siguientes documentos complementan este anteproyecto y están disponibles en el repositorio del proyecto:

- **Modelo de datos completo:** `docs/modelo_de_datos.md` — 14 entidades, principios de diseño, esquema SQL.
- **Especificación del modelo LLM:** `MODELO.md` — System prompts, taxonomía formativo-sustitutiva, pipeline de clasificación, benchmark pre-piloto.
- **Encuesta pre-tesis estudiantes:** `ENCUESTA_ESTUDIANTE.md` — 7 secciones, 30 ítems, escalas Likert.
- **Encuesta pre-tesis profesores:** `ENCUESTA_PROFESOR.md` — 6 secciones, instrumento de percepción docente.
- **Documentación de despliegue:** `DESPLIEGUE.md` — Arquitectura de producción, configuración de VM, servicios.
