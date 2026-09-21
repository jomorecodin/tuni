# Modelo de datos

Documento técnico de referencia para la plataforma piloto.

## Principios de diseño

- **Anonimización por diseño.** La identidad real del estudiante vive en una sola tabla aislada. Todas las demás tablas referencian al estudiante mediante un identificador anonimizado.
- **Inmutabilidad de las interacciones.** Una vez registrada una interacción con el modelo, no se modifica ni se borra.
- **Separación entre datos crudos y datos derivados.** Las variables de Capa 5 se calculan en tablas derivadas o vistas materializadas.
- **Auditoría de cambios.** Las entidades que pueden cambiar registran historial de cambios con timestamp.
- **Coherencia con el módulo de telemetría unificado.** El modo seleccionado se almacena como atributo de la interacción.

## Entidades

### Bloque de identidad y privacidad

#### `estudiante`
Tabla aislada con identidad real. Acceso restringido al investigador principal.

```sql
estudiante (
  id_estudiante PK,
  nombre,
  apellido,
  cedula,
  correo,
  telefono,
  fecha_consentimiento,
  user_id_anonimo FK → usuario
)
```

#### `usuario`
Identidad operativa anonimizada. Toda la lógica del sistema referencia esta entidad.

```sql
usuario (
  user_id PK,                -- UUID opaco
  fecha_alta,
  carrera_id FK,
  trimestre_actual,
  estado_participacion
)
```

### Bloque académico institucional

#### `carrera`
Catálogo de carreras incluidas en el piloto.

```sql
carrera (id_carrera PK, nombre, facultad, codigo_institucional)
```

#### `materia`
Catálogo de materias.

```sql
materia (id_materia PK, nombre, codigo, descripcion_breve, area_disciplinar)
```

#### `pensum_carrera`
Relación muchos a muchos entre carreras y materias.

```sql
pensum_carrera (
  id_carrera FK,
  id_materia FK,
  trimestre_teorico,
  obligatoria_o_electiva
)
```

#### `inscripcion`
Materias que cada usuario cursa en el periodo del piloto.

```sql
inscripcion (
  id_inscripcion PK,
  user_id FK,
  id_materia FK,
  trimestre_periodo,
  seccion,
  profesor_declarado
)
```

#### `evaluacion`
Eventos evaluativos declarados.

```sql
evaluacion (
  id_evaluacion PK,
  id_inscripcion FK,
  tipo_evaluacion,
  fecha_programada,
  peso_porcentual,
  descripcion_breve,
  fecha_actualizacion
)
```

#### `historial_evaluacion`
Registro inmutable de cambios en fechas de evaluación.

```sql
historial_evaluacion (
  id_historial PK,
  id_evaluacion FK,
  fecha_anterior,
  fecha_nueva,
  timestamp_cambio
)
```

### Bloque de interacción con el modelo

#### `sesion`
Agrupa interacciones de un periodo continuo.

```sql
sesion (
  id_sesion PK,
  user_id FK,
  timestamp_inicio,
  timestamp_fin,
  dispositivo,
  modo_inicial,
  materia_declarada FK → materia (opcional)
)
```

#### `interaccion`
Registro central del módulo de telemetría.

```sql
interaccion (
  id_interaccion PK,
  id_sesion FK,
  timestamp,
  modo_seleccionado,
  prompt_estudiante TEXT,
  respuesta_modelo TEXT,
  longitud_prompt_tokens,
  longitud_respuesta_tokens,
  tiempo_generacion_ms,
  id_parametrizacion FK
)
```

#### `clasificacion_interaccion`
Clasificaciones aplicadas a cada interacción.

```sql
clasificacion_interaccion (
  id_clasificacion PK,
  id_interaccion FK,
  clasificador,
  tipo_consulta,
  intencion_detectada,
  indice_formativo_sustitutivo,
  confianza,
  timestamp_clasificacion
)
```

#### `evento_interaccion`
Eventos discretos durante una interacción.

```sql
evento_interaccion (
  id_evento PK,
  id_interaccion FK (opcional),
  id_sesion FK,
  tipo_evento,
  timestamp,
  metadata_json
)
```

### Bloque de parametrización del modelo

#### `parametrizacion_modelo`
Versiona los archivos Markdown de parametrización.

```sql
parametrizacion_modelo (
  id_parametrizacion PK,
  modo,                  -- 'neutral' | 'tutor'
  version,
  contenido_md TEXT,
  fecha_activacion,
  fecha_desactivacion,
  autor
)
```

### Bloque de análisis derivado

#### `metrica_usuario_periodo`
Tabla de agregación por usuario y ventana temporal.

```sql
metrica_usuario_periodo (
  id_metrica PK,
  user_id FK,
  periodo_inicio,
  periodo_fin,
  total_sesiones,
  total_interacciones,
  ratio_modo_tutor,
  indice_formativo_sustitutivo_promedio,
  intensidad_pre_evaluacion
)
```

#### `metrica_materia_periodo`
Equivalente agregada por materia.

```sql
metrica_materia_periodo (
  id_metrica PK,
  id_materia FK,
  periodo_inicio,
  periodo_fin,
  total_interacciones,
  ratio_modo_tutor,
  indice_formativo_sustitutivo_promedio
)
```

## Cálculo de proximidad a evaluación

```sql
proximidad = MIN(evaluacion.fecha_programada - interaccion.timestamp)
            WHERE evaluacion.id_inscripcion IN (inscripciones del usuario)
            AND evaluacion.fecha_programada >= interaccion.timestamp
```

Categorización en bandas: más de 7 días, entre 3 y 7 días, menos de 3 días, día de la evaluación.

**Importante:** el cálculo debe usar la fecha vigente en el momento de la interacción, no la fecha actual. Para esto existe `historial_evaluacion`.

## Consideraciones técnicas

- **Volumen estimado:** 60 estudiantes × 12 semanas × 5 interacciones/semana ≈ 3.600 interacciones totales.
- **Almacenamiento de prompts:** tipo TEXT en PostgreSQL.
- **Índices:** `user_id` y `timestamp` en `sesion` e `interaccion`. `id_evaluacion` y `fecha_programada` en `evaluacion`.
- **Backups:** automáticos diarios durante todo el piloto.
- **Anonimización al cierre:** la tabla `estudiante` debe ser eliminada o sellada al finalizar el piloto.

## Decisiones pendientes

- Confirmación del motor de base de datos (PostgreSQL via Supabase recomendado).
- Decisión sobre dónde se ejecuta la clasificación de interacciones.
- Política de actualización del calendario de evaluaciones por el estudiante.
- Estrategia de migración de la tabla `estudiante` al cierre del piloto.
- Definición del umbral de inactividad para cierre automático de sesión (30 minutos sugerido).
