# Patrones Pedagogicos y Marco de Medicion — TUNI

Este documento define los patrones conductuales y pedagogicos que el bot TUNI monitorea durante el piloto de 12 semanas. Cada patron se clasifica como **fundamentado en teoria educativa** o **empirico/conductual**, y se documenta: que mide, como se captura, donde se almacena, y su significado educativo.

---

## Parte I: Patrones Fundamentados en Teoria Educativa

Estos patrones estan respaldados por marcos teoricos establecidos en ciencias de la educacion. Cada uno referencia la teoria, el autor, y como se operacionaliza en el contexto de TUNI.

### 1. Nivel Cognitivo de las Preguntas (Taxonomia de Bloom, 1956; Anderson & Krathwohl, 2001)

**Que mide:** El nivel de complejidad cognitiva de las preguntas que el estudiante formula al bot.

**Marco teorico:** La Taxonomia de Bloom revisada clasifica los procesos cognitivos en seis niveles: Recordar, Comprender, Aplicar, Analizar, Evaluar, Crear. Un estudiante que progresa de "que es una derivada?" (Recordar) a "por que este metodo no converge?" (Analizar) demuestra desarrollo cognitivo.

**Como se captura:**
- Clasificacion automatica del prompt del estudiante mediante heuristicas de palabras clave:
  - Nivel 1 (Recordar): "que es", "define", "cual es la formula"
  - Nivel 2 (Comprender): "explica", "por que", "que significa"
  - Nivel 3 (Aplicar): "resuelve", "calcula", "encuentra"
  - Nivel 4 (Analizar): "compara", "que diferencia hay", "por que falla"
  - Nivel 5 (Evaluar): "es correcto mi procedimiento", "cual metodo es mejor"
  - Nivel 6 (Crear): "como puedo plantear", "disenar", "proponer"

**Campo JSON:** `patterns.cognitive_level_progression` — array de objetos `{timestamp, level, question_snippet}`

**Significado:** Una progresion ascendente a lo largo del piloto sugiere que el estudiante esta desarrollando pensamiento critico. Una regresion puede indicar frustacion o dependencia.

---

### 2. Zona de Desarrollo Proximo y Scaffolding (Vygotsky, 1978)

**Que mide:** Si el bot esta funcionando como un "andamio" efectivo — ayudando al estudiante a resolver problemas que no podria resolver solo, pero sin hacerlo por el.

**Marco teorico:** La ZDP de Vygotsky describe la distancia entre lo que un estudiante puede hacer independientemente y lo que puede lograr con ayuda. El scaffolding efectivo opera dentro de esta zona: demasiado facil no genera aprendizaje, demasiado dificil genera frustacion.

**Como se captura:**
- **Ratio de exito asistido**: porcentaje de sesiones donde el estudiante llega a una respuesta correcta (detectado por mensajes del bot tipo "Exacto!", "Correcto", "Muy bien")
- **Iteraciones hasta resolucion**: numero de intercambios antes de que el estudiante resuelva el problema
- **Abandonos por dificultad**: sesiones donde el estudiante se va sin resolver (ultimo mensaje indica frustacion o cambio abrupto de tema)

**Campo JSON:** `patterns.scaffolding_effectiveness` — `{assisted_success_rate, avg_iterations_to_solve, difficulty_abandonments}`

**Significado:** Un ratio alto de exito asistido con iteraciones moderadas (3-7) indica scaffolding efectivo. Muchas iteraciones (>10) sugieren que el bot no esta adaptando la dificultad. Pocos intercambios (<2) sugieren que el estudiante copio la respuesta directamente.

---

### 3. Aprendizaje Autorregulado (Zimmerman, 2002)

**Que mide:** Si el estudiante demuestra capacidad de planificar, monitorear y reflexionar sobre su propio aprendizaje.

**Marco teorico:** El modelo de Zimmerman tiene tres fases: Prevision (planificacion), Ejecucion (monitoreo), y Auto-reflexion. Los estudiantes autorregulados establecen metas, monitorean su progreso, y reflexionan sobre lo que funcionó.

**Como se captura:**
- **Prevision**: El estudiante verbaliza un plan antes de resolver ("primero voy a encontrar los eigenvalores, luego los eigenvectores")
- **Monitoreo**: El estudiante corrige su propio trabajo sin que el bot lo senale ("espera, me equivoque en el signo")
- **Reflexion**: Respuestas a heartbeats semanales (autoevaluacion 1-5, reflexiones post-evaluacion)

**Campo JSON:** `patterns.self_regulation` — `{planning_instances, self_corrections, heartbeat_reflections[]}`

**Significado:** Incremento en auto-correcciones a lo largo del piloto indica desarrollo de autorregulacion. Los heartbeats capturan la dimension reflexiva explicitamente.

---

### 4. Carga Cognitiva (Sweller, 1988)

**Que mide:** Indicadores de que el estudiante esta experimentando sobrecarga cognitiva.

**Marco teorico:** La Teoria de Carga Cognitiva distingue entre carga intrinseca (complejidad del material), extrinseca (presentacion inadecuada), y germana (esfuerzo de aprendizaje productivo). La sobrecarga se manifiesta cuando la carga total excede la capacidad de la memoria de trabajo.

**Como se captura:**
- **Tiempo entre mensajes muy corto** (<10s): el estudiante no esta procesando la respuesta
- **Tiempo entre mensajes muy largo** (>5min): posible frustacion o confusion
- **Mensajes fragmentados**: multiples mensajes cortos seguidos ("no entiendo", "y?", "pero como")
- **Cambio abrupto de tema**: el estudiante abandona un problema a medio resolver

**Campo JSON:** `patterns.cognitive_load_indicators` — `{rapid_responses_count, long_pauses_count, fragmented_sequences, abrupt_topic_changes}`

**Significado:** Patrones de sobrecarga sugieren que el bot (o el material) necesita simplificar. Los indicadores se correlacionan con el horario academico — picos pre-evaluacion son esperados.

---

### 5. Dependencia de IA / Indefension Aprendida (Seligman, 1972; adaptado)

**Que mide:** Si el estudiante esta desarrollando dependencia del bot en lugar de autonomia.

**Marco teorico:** La indefension aprendida ocurre cuando un individuo deja de intentar resolver problemas por cuenta propia tras experiencias repetidas de fracaso (o exito sin esfuerzo). En el contexto de IA, esto se manifiesta como delegacion sistematica sin intento previo.

**Como se captura:**
- **Ratio de intento propio**: porcentaje de interacciones donde el estudiante muestra trabajo propio antes de pedir ayuda
- **Longitud del primer mensaje**: mensajes muy cortos ("resuelve esto") vs mensajes con contexto ("intente usar sustitucion pero me da infinito")
- **Frecuencia creciente vs decreciente**: aumento constante de uso puede indicar dependencia; uso estable o decreciente con mejores notas indica autonomia creciente

**Campo JSON:** `patterns.dependency_indicators` — `{own_attempt_ratio, avg_first_message_length, usage_trend_slope}`

**Significado:** Un indice formativo-sustitutivo alto (mas formativo) es deseable. Si el ratio de intento propio disminuye a lo largo del piloto, es una senal de alerta.

---

### 6. Dificultades Deseables (Bjork, 1994)

**Que mide:** Si el enfoque socratico del bot genera "lucha productiva" — esfuerzo que promueve retencion a largo plazo.

**Marco teorico:** Bjork demostro que condiciones de aprendizaje que hacen la tarea mas dificil a corto plazo (espaciado, intercalado, generacion) mejoran la retencion a largo plazo. El metodo socratico del bot introduce dificultad deseable al no dar respuestas directas.

**Como se captura:**
- **Abandono post-respuesta socratica**: el estudiante se va inmediatamente despues de que el bot responde con una pregunta guia (indica frustacion, no dificultad deseable)
- **Persistencia**: el estudiante responde la pregunta socratica y continua el dialogo (indica engagement con la dificultad)
- **Re-visita**: el estudiante vuelve al mismo tema dias despues (indica espaciado natural)

**Campo JSON:** `patterns.desirable_difficulty` — `{abandonment_after_socratic, persistence_rate, topic_revisit_count}`

**Significado:** Una alta persistencia con bajo abandono socratico indica que el bot esta en el "sweet spot" de dificultad. Alto abandono sugiere que el metodo socratico necesita ser menos rigido para ese estudiante.

---

### 7. Metacognicion (Flavell, 1979)

**Que mide:** El grado de conciencia del estudiante sobre su propio proceso de aprendizaje.

**Marco teorico:** La metacognicion incluye conocimiento metacognitivo (saber que se sabe y que no) y regulacion metacognitiva (planificar, monitorear, evaluar el propio aprendizaje). Se considera un predictor fuerte de exito academico.

**Como se captura:**
- **Preguntas metacognitivas explicitas**: "estoy entendiendo bien?", "me falta algo conceptual?", "deberia repasar [tema] antes?"
- **Respuestas a heartbeats**: autoevaluaciones numericas y reflexiones textuales
- **Cambio en autoevaluacion vs desempeno**: si la autoevaluacion del estudiante se acerca a su desempeno real (calibracion)

**Campo JSON:** `patterns.metacognition` — `{metacognitive_questions_count, self_assessment_history[], calibration_trend}`

**Significado:** Aumento en preguntas metacognitivas y mejor calibracion entre autoevaluacion y desempeno indica desarrollo metacognitivo.

---

### 8. Indice Formativo-Sustitutivo (marco original TUNI)

**Que mide:** Si el uso de IA por parte del estudiante es **formativo** (construye comprension) o **sustitutivo** (reemplaza el proceso de aprendizaje).

**Marco teorico:** Marco desarrollado para esta investigacion. Combina multiples indicadores para crear un indice unico [-1, +1] donde +1 es completamente formativo y -1 es completamente sustitutivo.

**Como se calcula:**
- (+) Muestra trabajo propio antes de pedir ayuda
- (+) Responde preguntas socraticas en lugar de pedir respuesta directa
- (+) Hace preguntas de comprension ("por que funciona asi?")
- (+) Re-visita temas para profundizar
- (-) Pide resoluciones completas sin intento
- (-) Mensajes tipo "dime la respuesta"
- (-) Abandona tras respuesta socratica
- (-) Uso solo previo a evaluaciones (cramming)

**Campo JSON:** `patterns.formative_substitutive_index` — float [-1, +1], recalculado semanalmente

**Significado:** Este es el indicador central de la tesis. Permite comparar entre estudiantes, entre materias, y observar la evolucion temporal.

---

## Parte II: Patrones Empiricos / Conductuales

Estos patrones son mediciones directas del comportamiento observable sin un marco teorico explicito. Son valiosos como datos descriptivos y pueden correlacionarse con los patrones teoricos.

### 9. Frecuencia y Duracion de Sesiones

**Que mide:** Con que frecuencia y por cuanto tiempo usa el estudiante el bot.

**Como se captura:** Conteo de sesiones por semana, duracion de cada sesion (timestamp_inicio a timestamp_fin o ultimo mensaje + timeout).

**Campo JSON:** `patterns.total_sessions`, `weekly_snapshots[].sessions_count`, `weekly_snapshots[].avg_session_duration_min`

---

### 10. Profundidad de Sesion

**Que mide:** Cuantos intercambios (mensajes ida y vuelta) ocurren por sesion.

**Como se captura:** Conteo de pares mensaje-respuesta por sesion.

**Campo JSON:** `patterns.avg_session_depth`

---

### 11. Tiempo Entre Mensajes

**Que mide:** Cuanto tarda el estudiante en responder despues de recibir una respuesta del bot.

**Como se captura:** Delta en segundos entre la respuesta del bot y el siguiente mensaje del estudiante.

**Campo JSON:** `patterns.avg_time_between_msgs_sec`, almacenado tambien por interaccion en `evento_interaccion.metadata_json.time_since_last_msg_seconds`

---

### 12. Evolucion de Longitud de Mensajes

**Que mide:** Si los mensajes del estudiante se hacen mas largos (mas elaborados) o mas cortos (mas concisos o mas dependientes) a lo largo del piloto.

**Como se captura:** Longitud promedio del prompt por semana.

**Campo JSON:** `weekly_snapshots[].avg_prompt_length_chars`

---

### 13. Picos de Uso Pre-Evaluacion

**Que mide:** Si el estudiante usa el bot significativamente mas antes de examenes.

**Como se captura:** Comparar uso en los 3 dias previos a una evaluacion conocida (del horario) vs uso normal. Ratio > 2x indica pico.

**Campo JSON:** `patterns.pre_eval_usage_spikes` — array de `{eval_date, subject, usage_ratio}`

**Nota:** Requiere horario del estudiante para correlacionar con fechas de evaluacion.

---

### 14. Abandono Post-Respuesta Socratica

**Que mide:** Con que frecuencia el estudiante deja de chatear inmediatamente despues de que el bot responde con una pregunta guia en lugar de una respuesta directa.

**Como se captura:** Si el ultimo mensaje de una sesion es del bot (tipo pregunta socratica) y el estudiante no responde en 30 minutos.

**Campo JSON:** `patterns.abandonment_after_socratic`

---

### 15. Patrones Horarios de Uso

**Que mide:** En que horas del dia y dias de la semana el estudiante usa el bot.

**Como se captura:** Histograma de horas de inicio de sesion.

**Campo JSON:** `patterns.usage_hours_histogram` — objeto `{hour: count}`

---

### 16. Diversidad de Materias

**Que mide:** Si el estudiante usa el bot para una o multiples materias.

**Como se captura:** Conteo de materias distintas seleccionadas.

**Campo JSON:** `subjects_used` — array de nombres de materia

---

### 17. Deteccion de Copy-Paste

**Que mide:** Si el estudiante esta copiando enunciados de problemas directamente (posible indicador de uso sustitutivo).

**Como se captura:**
- Mensajes inusualmente largos y formales (>200 caracteres, lenguaje de enunciado)
- Presencia de numeracion de ejercicios ("Ejercicio 3.2.a")
- Patrones tipicos de enunciado ("Demuestre que", "Calcule", "Sea A una matriz")

**Campo JSON:** `patterns.copy_paste_indicators` — conteo de mensajes clasificados como posible copy-paste

---

### 18. Auto-Correcciones

**Que mide:** Instancias donde el estudiante corrige su propio trabajo sin que el bot lo senale.

**Como se captura:** Deteccion de frases indicativas: "espera", "me equivoque", "no, es", "corrijo", "en realidad".

**Campo JSON:** `patterns.self_correction_count`

---

## Parte III: Datos del Horario Estudiantil

El horario semanal del estudiante (subido como foto/PDF al inicio) permite contextualizar todos los patrones anteriores:

- **Correlacion temporal**: uso del bot vs horas de clase de cada materia
- **Proximidad a evaluaciones**: detectar patrones pre/post-evaluacion
- **Carga academica**: numero de materias matematicas como variable de control
- **Horarios de estudio**: identificar si el estudiante usa el bot en horas tipicas de estudio o de ultimo minuto

**Campo JSON:** `schedule` — `{raw_text, parsed: {subjects: [{name, day, time_start, time_end}], evaluations: [{subject, date, type}]}}`

---

## Resumen de Campos JSON por Categoria

| Categoria | Campos | Tipo |
|-----------|--------|------|
| Teoria educativa | cognitive_level_progression, scaffolding_effectiveness, self_regulation, cognitive_load_indicators, dependency_indicators, desirable_difficulty, metacognition, formative_substitutive_index | Objetos complejos |
| Empiricos | total_sessions, avg_session_depth, avg_time_between_msgs_sec, abandonment_after_socratic, self_correction_count, copy_paste_indicators, usage_hours_histogram | Contadores/promedios |
| Longitudinales | weekly_snapshots, pre_eval_usage_spikes, subjects_used | Arrays temporales |
| Contextuales | schedule, consent_date | Objetos/fechas |
