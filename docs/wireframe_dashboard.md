# Wireframe del dashboard de gestión pedagógica

Arquitectura de información del dashboard. No incluye decisiones de diseño visual.

## Principios de diseño

- **De lo general a lo particular.** Drill-down natural desde vista panorámica hasta interacción individual.
- **Filtros persistentes.** Los filtros aplicados se mantienen al cambiar de vista cuando es analíticamente coherente.
- **Vistas guardadas.** Conjuntos predefinidos de filtros invocables con un clic.
- **Exportabilidad.** Cualquier tabla o gráfico debe poder exportarse a CSV o imagen.
- **Latencia tolerable.** Cálculos pesados sobre tablas precalculadas, no sobre tablas crudas.

## Estructura de navegación

Menú lateral fijo con seis vistas principales:

1. Vista Panorámica — overview general del piloto
2. Vista por Estudiante — un estudiante a la vez
3. Vista por Carrera — comparativo entre las 6 carreras
4. Vista por Materia — uso de IA por contenido académico
5. Vista Temporal — patrones a lo largo del tiempo
6. Vista de Interacciones — tabla cruda navegable

Y configuración: vistas guardadas, exportar, parametrizaciones del modelo.

## Filtros globales

Persistente en la parte superior. Los filtros se aplican simultáneamente a toda la información mostrada.

### Filtros de segmentación primaria

- **Carrera:** selección múltiple entre las seis carreras del piloto.
- **Trimestre del estudiante:** rangos (1-4, 5-8, 9-12) o selección puntual.
- **Modo seleccionado:** neutral, tutor académico, o ambos.
- **Periodo temporal:** presets o rango personalizado.

### Filtros de exploración (contextuales)

- Estudiante individual.
- Materia específica.
- Tipo de consulta.
- Banda de proximidad a evaluación.
- Momento del día.

### Filtros de análisis derivado

- Rango del índice formativo-sustitutivo (slider 0-1).
- Intensidad de uso (baja, media, alta, muy alta).
- Patrón temporal (constante, picos pre-evaluación, esporádico).

## Vistas detalladas

### 1. Vista Panorámica

Métricas principales (cards superiores):

- Estudiantes activos en el periodo.
- Interacciones totales.
- Porcentaje de uso del modo tutor.
- Índice formativo-sustitutivo promedio.

Gráficos resumen:

- Línea temporal: interacciones por día.
- Barras: distribución entre modo neutral y modo tutor.
- Heatmap: día de la semana × hora del día.

Panel de alertas:

- Estudiantes inactivos por más de N días.
- Picos anómalos de actividad.
- Interacciones flagged como altamente sustitutivas.

### 2. Vista por Estudiante

- Selector de estudiante con búsqueda por user_id anónimo.
- Tarjeta de perfil con métricas individuales.
- Listado de materias inscritas con métricas por materia.
- Línea temporal con marcas en fechas de evaluaciones.
- Distribución de tipos de consulta del estudiante.
- Acceso al historial completo de interacciones.

### 3. Vista por Carrera

- Tabla comparativa: una fila por carrera, columnas con métricas clave.
- Gráfico de radar comparando perfiles de uso.
- Distribución del índice formativo-sustitutivo por carrera (boxplot).
- Ranking de tipos de consulta más frecuentes por carrera.

### 4. Vista por Materia

- Listado de materias con número de estudiantes activos y métricas resumen.
- Expansión al seleccionar materia.
- Comparativo entre materias del mismo trimestre teórico.
- Análisis de proximidad a evaluación específico por materia.

### 5. Vista Temporal

- Línea temporal multivariable.
- Comparación semana a semana.
- Identificación de eventos anómalos.
- Cruce con eventos académicos masivos.

### 6. Vista de Interacciones

- Tabla paginada con todas las columnas relevantes.
- Filtros de columna en cada encabezado.
- Búsqueda por contenido del prompt o respuesta.
- Marcado manual para revisión cualitativa.
- Exportación a CSV.

## Vistas guardadas predefinidas

| Perspectiva | Configuración |
|---|---|
| Patrones críticos | Estudiantes con índice formativo-sustitutivo alto (>0.7) en última semana |
| Pre-evaluación | Interacciones a menos de 3 días de evaluación, todas las carreras |
| Comparativo de modos | Vista por carrera con foco en ratio neutral vs tutor |
| Estudiantes inactivos | Lista de estudiantes sin actividad en últimos 7 días |
| Humanidades vs Ingeniería | Comparativo agregado entre los dos bloques disciplinares |
| Reporte semanal | Vista temporal con foco en última semana, todas las métricas |

## Stack técnico tentativo

- **Backend:** Python con FastAPI.
- **Frontend del dashboard:** Next.js (React) con TypeScript y Tailwind. Recharts para visualizaciones.
- **Base de datos:** PostgreSQL via Supabase.
- **Despliegue:** Vercel para frontend, Railway/Render para backend.

## Decisiones pendientes

- Confirmación de los seis tipos de vista propuestos.
- Niveles de acceso al dashboard.
- Política de cálculo de métricas (tiempo real con caché vs batch nocturno).
- Necesidad de exportación automatizada de reportes.
- Diseño visual y branding.
