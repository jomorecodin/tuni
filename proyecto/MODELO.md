# TUNI — Especificacion del Modelo LLM para el Experimento

**Fecha:** 2026-09-18
**Version:** 1.0
**Proyecto:** TUNI — Plataforma piloto de asistencia academica con telemetria
**Investigador:** Joseph Moreno, Universidad Metropolitana de Caracas

---

## 1. Modelo seleccionado

### Primario: Qwen 2.5-32B-Instruct (INT4)

| Parametro | Valor |
|---|---|
| **Modelo** | Qwen 2.5-32B-Instruct |
| **Cuantizacion** | INT4 (GPTQ o AWQ) |
| **Parametros** | 32 mil millones |
| **VRAM requerida** | ~20 GB |
| **RAM del sistema** | 64 GB recomendado |
| **GPU minima** | 1x RTX 4090 (24GB) o A100 40GB |
| **Licencia** | Apache 2.0 |
| **Soporte de espanol** | Excelente (mejor entre modelos open-source) |
| **Calidad relativa** | ~80% GPT-4 |
| **Costo por token** | $0 (local) |

### Fallback: Qwen 2.5-14B-Instruct (INT4)

Si el servidor no soporta 32B:

| Parametro | Valor |
|---|---|
| **VRAM requerida** | ~10 GB |
| **GPU minima** | 1x RTX 3060 12GB |
| **Calidad relativa** | ~70% GPT-4 |

### Plan B: DeepSeek API

Si no hay GPU disponible:

| Parametro | Valor |
|---|---|
| **Modelo** | DeepSeek-V2.5 Chat |
| **Costo estimado** | ~$0.60 para todo el piloto (60 est, 6 sem, 10 interac/sem) |
| **Nota etica** | Datos pasan por servidores externos. Documentar en consentimiento informado. |

---

## 2. Infraestructura de deployment

### Servidor de inferencia

```
┌────────────────────────────────────────────┐
│  SERVIDOR TUNI                             │
│                                            │
│  ┌──────────────┐    ┌──────────────────┐  │
│  │   Ollama     │    │   Backend TUNI   │  │
│  │  (Qwen 2.5)  │◄──│  (FastAPI/Next)   │  │
│  │   :11434     │    │     :3000        │  │
│  └──────────────┘    └──────────────────┘  │
│                             │              │
│                      ┌──────────────────┐  │
│                      │  PostgreSQL      │  │
│                      │  (telemetria)    │  │
│                      │     :5432        │  │
│                      └──────────────────┘  │
└────────────────────────────────────────────┘
```

### Comandos de deploy

```bash
# Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Descargar modelo
ollama pull qwen2.5:32b-instruct-q4_K_M

# Verificar
ollama run qwen2.5:32b-instruct-q4_K_M "Resuelve el sistema: 2x + 3y = 7, x - y = 1"

# API endpoint
# POST http://localhost:11434/api/chat
```

### Parametros de generacion

```json
{
  "model": "qwen2.5:32b-instruct-q4_K_M",
  "options": {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "repeat_penalty": 1.1,
    "num_predict": 1024,
    "stop": ["<|im_end|>"]
  },
  "stream": true
}
```

**Justificacion de parametros:**
- `temperature: 0.7` — Balancea creatividad con precision matematica. No tan bajo que sea rigido (0.3), no tan alto que genere errores (1.0).
- `top_p: 0.9` — Nucleus sampling para diversidad controlada.
- `num_predict: 1024` — Maximo ~750 palabras por respuesta. Suficiente para explicaciones matematicas sin exceso.
- `stream: true` — UX fluida, el estudiante ve la respuesta generandose.

---

## 3. Modos de operacion

### 3.1 Modo Neutral

El modelo responde como un LLM estandar, sin restricciones pedagogicas. Este modo es el **grupo control** del experimento.

```
SYSTEM PROMPT — MODO NEUTRAL
─────────────────────────────

Eres TUNI, un asistente academico de la Universidad Metropolitana de Caracas.

CONTEXTO DE LA SESION:
- Materia: {materia_nombre} ({materia_codigo})
- Profesor: {profesor_nombre}
- Semana del trimestre: {semana_actual} de 12
- Temas cubiertos hasta ahora: {temas_cubiertos}
- Proxima evaluacion: {eval_tipo} el {eval_fecha} ({eval_dias_restantes} dias)
  Temas que entran: {eval_temas}

INSTRUCCIONES:
- Responde las preguntas del estudiante de forma clara y directa.
- Usa notacion matematica cuando sea apropiado (LaTeX entre $..$ para inline, $$...$$ para bloques).
- Si el estudiante pide que resuelvas un problema, resuelvelo paso a paso.
- Si el estudiante pide que generes codigo, generalo.
- Responde en espanol.
- No menciones que tienes un "modo" ni que eres parte de un estudio.
- No agregues advertencias pedagogicas no solicitadas.
```

### 3.2 Modo Tutor

El modelo actua como tutor socratico. Este modo es la **variable experimental** — el wrapper pedagogico que Bastani et al. (REF-09) demostraron que mitiga efectos negativos.

```
SYSTEM PROMPT — MODO TUTOR
─────────────────────────────

Eres TUNI, un tutor academico de la Universidad Metropolitana de Caracas.

CONTEXTO DE LA SESION:
- Materia: {materia_nombre} ({materia_codigo})
- Profesor: {profesor_nombre}
- Semana del trimestre: {semana_actual} de 12
- Temas cubiertos hasta ahora: {temas_cubiertos}
- Proxima evaluacion: {eval_tipo} el {eval_fecha} ({eval_dias_restantes} dias)
  Temas que entran: {eval_temas}

CONTEXTO DEL ESTUDIANTE:
- Indice F-S actual: {indice_fs} (0 = totalmente formativo, 1 = totalmente sustitutivo)
- Temas donde mas pide ayuda: {temas_frecuentes}
- Consultas previas en esta sesion: {n_consultas_sesion}

ESTILO EVALUATIVO DEL PROFESOR:
- {profesor_estilo}

INSTRUCCIONES PEDAGOGICAS:
1. NUNCA des la respuesta directa a un problema matematico.
2. Usa el metodo socratico: responde con preguntas que guien al estudiante.
3. Si el estudiante pide "resuelve esto", responde: "Vamos paso a paso. ¿Que es lo primero que identificas en este problema?"
4. Si el estudiante ya intento resolver y muestra su trabajo, valida lo correcto y guia en los errores.
5. Cuando detectes un gap conceptual, regresa al fundamento antes de avanzar.
6. Adapta la dificultad de tus preguntas al nivel demostrado por el estudiante.
7. Si el estudiante insiste en que le des la respuesta (3+ intentos), ofrece una pista mas directa pero NO la solucion completa.
8. Usa notacion matematica (LaTeX) cuando sea apropiado.
9. Responde en espanol.
10. No menciones que eres parte de un estudio.

ESCALAMIENTO DE FIRMEZA:
- Si indice_fs > 0.7: Ser mas firme en no dar respuestas directas.
- Si indice_fs < 0.3: Permitir mas libertad, el estudiante ya demuestra uso formativo.
- Si proximidad_a_evaluacion < 3 dias: Ser ligeramente mas directo (el estudiante necesita prepararse).

EJEMPLO DE INTERACCION:
Estudiante: "Diagonaliza la matriz A = [[2,1],[1,2]]"
Tutor: "Bien, empecemos. Para diagonalizar una matriz, ¿cual es el primer paso que debemos hacer? ¿Que necesitamos encontrar primero?"
Estudiante: "Los valores propios"
Tutor: "Exacto. ¿Y como encontramos los valores propios de A? ¿Que ecuacion planteamos?"
```

### 3.3 Escalamiento dinamico del system prompt

El system prompt no es estatico — se reconstruye por sesion usando datos de Cronos y telemetria:

```
┌─────────────────────────────────────────────────┐
│  CONSTRUCCION DEL SYSTEM PROMPT POR SESION       │
│                                                  │
│  1. Cargar template (neutral o tutor)            │
│  2. Inyectar contexto del sujeto:                │
│     └── sujetos.syllabus_json                    │
│     └── sujetos.temas_por_semana[semana_actual]   │
│     └── evaluaciones_sujeto (proxima)            │
│  3. Inyectar contexto del profesor:              │
│     └── sujetos.profesor_estilo                  │
│  4. Inyectar contexto del estudiante (solo tutor):│
│     └── metrica_usuario_periodo.indice_fs        │
│     └── interacciones recientes (ultimas 5)      │
│  5. Calcular proximidad_a_evaluacion              │
│  6. Ajustar firmeza segun indice_fs              │
│                                                  │
│  Tokens estimados del system prompt: ~1,500      │
└─────────────────────────────────────────────────┘
```

---

## 4. Clasificacion de interacciones

### 4.1 Taxonomia

Cada interaccion se clasifica en el eje **formativo-sustitutivo**:

| Tipo | Indicadores | Indice F-S | Ejemplo |
|---|---|---|---|
| **Formativo puro** | Pregunta conceptual, muestra trabajo previo, pide verificacion | 0.0 - 0.2 | "Intente resolver det(A-λI)=0 y me da λ²-4λ+3=0, ¿esta bien?" |
| **Formativo guiado** | Pide explicacion, solicita pasos, pregunta "por que" | 0.2 - 0.4 | "No entiendo por que los vectores propios deben ser linealmente independientes" |
| **Mixto** | Pregunta parcial, combina solicitud con intento | 0.4 - 0.6 | "¿Como se diagonaliza una matriz? Dame un ejemplo con la matriz [[2,1],[1,2]]" |
| **Sustitutivo parcial** | Pide resolucion con alguna especificidad | 0.6 - 0.8 | "Resuelve este sistema de ecuaciones usando Cramer" |
| **Sustitutivo puro** | Pide respuesta directa, copia de tarea, generacion sin contexto | 0.8 - 1.0 | "Resuelve todos los ejercicios de la pagina 47" |

### 4.2 Variables del clasificador

```typescript
interface ClasificacionInteraccion {
  // Detectados automaticamente del prompt
  tiene_intento_previo: boolean;        // El estudiante muestra su trabajo
  tipo_verbo: 'pregunta' | 'solicitud' | 'imperativo';  // "¿como?" vs "hazme"
  especificidad_tematica: number;       // 0-1, que tan especifica es la pregunta
  longitud_prompt_tokens: number;
  referencias_a_material: boolean;      // Menciona clase, libro, profesor

  // Derivados del historial
  consultas_similares_previas: number;  // ¿Ya pregunto esto antes?
  modo_seleccionado: 'neutral' | 'tutor';
  cambios_de_modo_en_sesion: number;

  // Contextuales
  proximidad_a_evaluacion: number;      // Dias hasta proxima eval
  hora_del_dia: string;                 // Madrugada vs horario normal
  duracion_sesion_minutos: number;

  // Output
  indice_formativo_sustitutivo: number; // 0.0 - 1.0
  tipo_consulta: string;               // De la taxonomia
  intencion_detectada: string;         // Libre, para analisis cualitativo
}
```

### 4.3 Pipeline de clasificacion

```
Interaccion del estudiante
        │
        ▼
┌──────────────────────────────┐
│  CLASIFICADOR (post-respuesta)│
│                              │
│  Paso 1: Analisis lexico     │
│    - Detectar verbos clave   │
│    - Detectar intento previo │
│    - Medir especificidad     │
│                              │
│  Paso 2: Contexto historico  │
│    - Comparar con consultas  │
│      anteriores del mismo    │
│      estudiante/materia      │
│                              │
│  Paso 3: Scoring             │
│    - Calcular indice F-S     │
│    - Asignar tipo_consulta   │
│                              │
│  Paso 4: Registro            │
│    - INSERT en interacciones │
│    - Actualizar metricas     │
│      agregadas               │
└──────────────────────────────┘
```

**Implementacion del clasificador:**

Opcion A — **Heuristico basado en reglas** (recomendado para v1):

```python
def clasificar_interaccion(prompt: str, historial: list) -> float:
    score = 0.5  # base neutra

    # Indicadores formativos (reducen score)
    if tiene_intento_previo(prompt):
        score -= 0.2
    if contiene_pregunta_conceptual(prompt):
        score -= 0.15
    if referencia_material_clase(prompt):
        score -= 0.1
    if pide_verificacion(prompt):
        score -= 0.15

    # Indicadores sustitutivos (aumentan score)
    if verbo_imperativo(prompt):  # "resuelve", "hazme", "genera"
        score += 0.2
    if pide_respuesta_completa(prompt):
        score += 0.15
    if prompt_muy_corto(prompt, threshold=20):
        score += 0.1
    if sin_contexto_especifico(prompt):
        score += 0.1

    return max(0.0, min(1.0, score))
```

Opcion B — **LLM como clasificador** (para v2, si la heuristica es insuficiente):

Usar el mismo modelo Qwen en un segundo paso con prompt de clasificacion:

```
Clasifica la siguiente consulta de un estudiante universitario en una escala de 0 a 1,
donde 0 = uso totalmente formativo (el estudiante quiere aprender) y
1 = uso totalmente sustitutivo (el estudiante quiere que hagas el trabajo por el).

Consulta: "{prompt_estudiante}"
Responde SOLO con un numero entre 0.0 y 1.0 y una palabra clave de tipo.
```

---

## 5. Rendering matematico

### Requisito

El foco del estudio es evaluacion matematica. El modelo debe poder:
- Escribir formulas en LaTeX
- El frontend debe renderizar LaTeX correctamente

### Implementacion

```
Modelo genera:
  "Los valores propios se obtienen resolviendo $\det(A - \lambda I) = 0$"

Frontend renderiza con KaTeX:
  Los valores propios se obtienen resolviendo det(A - λI) = 0
```

**Libreria:** KaTeX (mas rapido que MathJax, ideal para streaming).

```bash
npm install katex react-katex
```

**Reglas de generacion (en system prompt):**
- Inline math: `$...$`
- Display math: `$$...$$`
- Matrices: `$\begin{pmatrix} a & b \\ c & d \end{pmatrix}$`

---

## 6. Gestion de sesiones y contexto

### Ventana de contexto

| Componente | Tokens estimados |
|---|---|
| System prompt (modo + contexto) | ~1,500 |
| Contexto de conversacion (acumulado, mid-sesion) | ~3,000 |
| Prompt del estudiante | ~200 |
| **Total input por interaccion** | **~4,700** |
| Respuesta del modelo | ~500 |

**Ventana maxima de Qwen 2.5-32B:** 128K tokens. Nunca se alcanza en una sesion.

### Manejo de sesiones

```
NUEVA SESION se crea cuando:
  - El estudiante abre la plataforma (primera interaccion del dia)
  - El estudiante cambia de materia
  - Inactividad > 30 minutos

SESION incluye:
  - id_sesion: UUID
  - id_estudiante: UUID
  - sujeto_id: UUID (materia)
  - modo_inicial: 'neutral' | 'tutor'
  - timestamp_inicio: ISO8601
  - timestamp_fin: ISO8601 (al cerrar o por inactividad)
  - dispositivo: string (user-agent)
  - total_interacciones: number
  - cambios_de_modo: number
  - indice_fs_promedio: float
```

---

## 7. Datos que se registran (telemetria completa)

### Por interaccion

| Campo | Tipo | Fuente | Proposito |
|---|---|---|---|
| id_interaccion | UUID | Auto | PK |
| id_sesion | UUID | Sesion activa | Agrupar por sesion |
| timestamp | ISO8601 | Auto | Timeline |
| modo_seleccionado | enum | UI | Variable independiente |
| prompt_estudiante | text | Input | Analisis cualitativo |
| respuesta_modelo | text | LLM output | Analisis de calidad |
| longitud_prompt_tokens | int | Tokenizer | Metrica de esfuerzo |
| longitud_respuesta_tokens | int | Tokenizer | Metrica de complejidad |
| tiempo_generacion_ms | int | Timer | Performance |
| materia_declarada | FK | Sidebar | Segmentacion |
| tipo_consulta | enum | Clasificador | Taxonomia |
| intencion_detectada | text | Clasificador | Analisis fino |
| indice_formativo_sustitutivo | float | Clasificador | Variable dependiente principal |
| proximidad_a_evaluacion | int | Calendario | Variable moderadora |
| tiene_latex | bool | Parser | Indicador de complejidad |
| contiene_codigo | bool | Parser | Tipo de consulta |

### Por evento discreto

| Evento | Datos capturados |
|---|---|
| Cambio de modo (mid-sesion) | timestamp, modo_anterior, modo_nuevo, interacciones_desde_ultimo_cambio |
| Regeneracion de respuesta | timestamp, id_interaccion_original, motivo_inferido |
| Copia al portapapeles | timestamp, id_interaccion, longitud_copiada |
| Abandono de sesion | timestamp, ultima_interaccion, duracion_total |
| Login/Logout | timestamp, dispositivo |

---

## 8. Benchmark pre-piloto

### Objetivo

Antes de activar el piloto, validar que el modelo responde adecuadamente en ambos modos para las materias foco.

### Protocolo

1. **Crear 50 problemas reales** de:
   - Algebra Lineal (15): sistemas, determinantes, valores/vectores propios, diagonalizacion, espacios vectoriales
   - Matematicas Discretas (15): logica proposicional, combinatoria, grafos, relaciones, induccion
   - Optimizacion (10): programacion lineal, simplex, dualidad
   - Otras materias (10): calculo, probabilidad, estadistica

2. **Ejecutar cada problema en ambos modos** (neutral y tutor).

3. **Evaluar:**

| Criterio | Modo Neutral | Modo Tutor |
|---|---|---|
| Precision matematica | ¿La respuesta es correcta? | ¿Las pistas llevan a la respuesta correcta? |
| Calidad de LaTeX | ¿Se renderiza bien? | ¿Se renderiza bien? |
| Adherencia al modo | ¿Responde directo? | ¿Guia sin dar respuesta? |
| Calidad pedagogica | N/A | ¿Las preguntas son utiles? ¿Escala bien? |
| Espanol | ¿Fluido y natural? | ¿Fluido y natural? |

4. **Umbral de aprobacion:**
   - Precision matematica ≥ 85% en ambos modos
   - Adherencia al modo tutor ≥ 90% (no da respuestas directas)
   - Si no pasa, escalar a Qwen 72B o refinar system prompt

---

## 9. Seguridad y etica

### Datos en el servidor

- El modelo corre localmente → **ninguna interaccion sale del servidor**.
- La BD esta en el mismo servidor → **datos nunca transitan por internet** (excepto la conexion HTTPS del estudiante al servidor).
- Compatible con el consentimiento informado: "sus datos seran almacenados en servidores de la Universidad Metropolitana y utilizados exclusivamente para fines academicos".

### Anonimizacion

- Cada estudiante tiene un `codigo_participante` (ej: `P-037`).
- El mapeo `codigo ↔ correo institucional` se almacena en tabla separada, cifrada.
- Los reportes y dashboards usan solo el codigo, nunca el nombre.
- Al finalizar el piloto, la tabla de mapeo se destruye.

### Limites del modelo

El system prompt incluye restricciones:
- No generar contenido sexual, violento o ilegal.
- No ayudar con plagio academico explicito ("escribe mi tesis", "hazme el trabajo final").
- No impersonar al profesor ni dar calificaciones.
- Si el estudiante pregunta algo fuera del ambito academico, redirigir amablemente.

---

## 10. Cronograma de implementacion del modelo

```
Semana -4   SETUP
            ├── Obtener acceso al servidor con GPU
            ├── Instalar Ollama + descargar Qwen 2.5-32B
            ├── Configurar API endpoint
            └── Verificar latencia basica

Semana -3   SYSTEM PROMPTS
            ├── Escribir prompt modo neutral (final)
            ├── Escribir prompt modo tutor (final)
            ├── Implementar inyeccion de contexto dinamico
            └── Probar con 10 consultas manuales

Semana -2   BENCHMARK
            ├── Ejecutar 50 problemas × 2 modos = 100 evaluaciones
            ├── Evaluar precision, adherencia, calidad
            ├── Refinar prompts segun resultados
            └── Decision: ¿32B es suficiente o escalar a 72B?

Semana -1   CLASIFICADOR + INTEGRACION
            ├── Implementar clasificador heuristico v1
            ├── Integrar con pipeline de telemetria
            ├── Probar end-to-end con 5 usuarios de prueba
            └── Validar que todos los campos se registran

Semana 0    PRE-PILOTO
            ├── Onboarding de participantes
            ├── Testing final con usuarios reales
            └── Activar logging completo
```

---

## Ver tambien

- [Auditoria del estado actual de la app](../../adiutor/wiki/tuni/audit-app-actual.md)
- [Reformulacion de la pregunta de investigacion](../../adiutor/wiki/tuni/reformulacion-pregunta-investigacion.md)
- [Analisis de factibilidad y ajustes](../../adiutor/wiki/tuni/analisis-factibilidad-ajustes.md)
- [Integracion Cronos-TUNI](../../adiutor/wiki/tuni/integracion-cronos-tuni.md)
- [Referencias documentadas](../../adiutor/wiki/tuni/referencias-documentadas.md)
