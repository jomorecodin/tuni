# Encuesta de onboarding

Instrumento de captura inicial aplicado a estudiantes participantes antes de su primer uso de la plataforma.

## Funciones

1. Obtener consentimiento informado.
2. Capturar datos de identificación y contexto académico.
3. Registrar materias e instancias evaluativas del trimestre.
4. Caracterizar el conocimiento previo del estudiante sobre IA generativa.

Tiempo estimado de llenado: 10-15 minutos.

## Sección 1 — Consentimiento informado

Bloque inicial obligatorio. Sin consentimiento no se puede avanzar.

### Información para el participante

Se presenta al estudiante una explicación del estudio que incluye:
- Título y propósito del estudio.
- En qué consiste la participación.
- Qué datos serán capturados.

### Tratamiento de los datos

- Anonimización: identidad real sustituida por user_id anónimo.
- Confidencialidad: resultados reportados de forma agregada.
- Uso académico exclusivo.
- Derecho a retirarse en cualquier momento.
- Riesgos: el estudio no implica riesgos físicos.

### Casillas de consentimiento

1. He leído y comprendido la información presentada arriba. [Sí / No]
2. Acepto participar voluntariamente en el estudio. [Sí / No]
3. Autorizo el registro automático de mis interacciones. [Sí / No]
4. Autorizo el uso anonimizado de los datos en publicaciones académicas. [Sí / No]

## Sección 2 — Datos de identificación

Información que vive en la tabla `estudiante` (aislada).

5. Nombre completo. [texto]
6. Cédula de identidad. [texto]
7. Correo electrónico institucional. [email]
8. Número de teléfono o WhatsApp. [teléfono]

## Sección 3 — Contexto académico

9. Carrera que cursa actualmente. [opción única]
   - Ingeniería de Computación / Sistemas
   - Ingeniería Mecánica
   - Ingeniería Civil
   - Ingeniería de Producción
   - Ingeniería Química
   - Educación
   - Comunicación Social
   - Psicología
   - Otra (especificar)

10. Trimestre que está cursando. [número 1-12]
11. Año de ingreso a la Unimet. [número]
12. Programa especial (doble carrera, intercambio). [texto opcional]

## Sección 4 — Materias del trimestre actual

Por cada materia que el estudiante está cursando, capturar:

### Datos de la materia

13. Nombre de la materia. [texto]
14. Código institucional. [texto opcional]
15. Sección. [texto]
16. Profesor que dicta la materia. [texto]
17. Tipo de materia. [opción única: obligatoria, electiva, servicio comunitario, no estoy seguro]

### Evaluaciones programadas

Por cada evaluación que tenga fecha conocida:

18. Tipo de evaluación. [opción única: parcial, final, quiz, entrega, presentación, laboratorio, otra]
19. Fecha programada. [fecha]
20. Peso porcentual. [número opcional]
21. Descripción breve. [texto opcional]

El estudiante podrá actualizar este calendario semanalmente desde la plataforma.

## Sección 5 — Línea base sobre uso previo de IA

22. ¿Ha utilizado herramientas de IA generativa antes?
    - No, nunca
    - Sí, ocasionalmente (menos de una vez por semana)
    - Sí, regularmente (varias veces por semana)
    - Sí, intensivamente (a diario o casi a diario)

23. ¿Para qué fines ha utilizado IA generativa? [selección múltiple]
    - Realización de tareas y entregas académicas
    - Estudio y comprensión de temas
    - Resumen de textos
    - Generación de código
    - Redacción de textos
    - Traducción
    - Conversación general / curiosidad
    - Trabajo o emprendimientos personales
    - No la he usado

24. En una escala de 1 a 5, ¿qué tan cómodo se siente formulando preguntas a una IA? [1-5]

25. ¿Algún profesor le ha dado lineamientos sobre el uso de IA?
    - Sí, varios profesores tienen reglas claras
    - Sí, algún profesor ha mencionado el tema
    - No, no se ha tratado el tema
    - No estoy seguro

26. ¿Considera que la Unimet debería tener una política institucional sobre IA?
    - Sí, definitivamente
    - Probablemente sí
    - Indiferente
    - Probablemente no
    - No

## Sección 6 — Logística del piloto

27. Dispositivo principal. [opción única: laptop, desktop, tablet, móvil, combinación]
28. ¿Tiene conexión a internet estable? [opción única: siempre, mayoría del tiempo, a veces, problemas frecuentes]
29. ¿En qué momento del día estudia con mayor frecuencia? [opción única: mañana, tarde, noche, madrugada, variable]
30. Comentarios adicionales. [texto opcional]

## Cierre

Al finalizar:

- Resumen de materias y evaluaciones registradas, editable.
- Generación automática del `user_id` anónimo.
- Información sobre la plataforma y los modos disponibles.
- Recordatorio sobre actualización semanal del calendario.
- Datos de contacto del investigador.

## Decisiones pendientes

- Validación del consentimiento informado por la coordinación académica de la Unimet.
- Plataforma técnica del formulario (Google Forms, Typeform, formulario embebido).
- Flujo de actualización del calendario académico durante el piloto.
- Política de manejo de retiro/agregado de materias después del onboarding.
- Eventual encuesta de cierre al finalizar el piloto.
