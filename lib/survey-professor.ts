import type { SurveyDefinition } from "./survey-types"

export const professorSurvey: SurveyDefinition = {
  id: "profesor",
  title: "Encuesta Pre-Tesis para Profesores",
  description: "Proyecto TUNI — Plataforma piloto de asistencia academica con telemetria",
  instructions:
    "Esta encuesta forma parte del trabajo de grado titulado \"Diseno de un sistema de telemetria e instrumentacion pedagogica para caracterizar patrones de interaccion estudiante-IA en un entorno universitario\". Su participacion es voluntaria y anonima. Las respuestas seran utilizadas exclusivamente para fines academicos. No hay respuestas correctas o incorrectas.",
  tableName: "respuesta_encuesta_profesor",
  sections: [
    {
      id: "s1",
      title: "Datos del docente",
      description: "Datos demograficos y contextuales. Anonimizados en el analisis.",
      questions: [
        {
          id: "s1_1",
          type: "radio",
          label: "Facultad a la que pertenece:",
          options: ["Ingenieria", "Ciencias y Artes", "Ciencias Economicas y Sociales"],
          hasOther: true,
          required: true,
        },
        {
          id: "s1_2",
          type: "radio",
          label: "Area disciplinar principal:",
          options: [
            "Matematica pura (Algebra, Calculo, Ecuaciones Diferenciales)",
            "Matematica aplicada (Optimizacion, Estadistica, Probabilidad)",
            "Computacion / Sistemas",
            "Fisica / Ciencias",
          ],
          hasOther: true,
          required: true,
        },
        {
          id: "s1_3",
          type: "checkbox",
          label: "Materias que dicta actualmente (marque todas las que apliquen):",
          options: [
            "Algebra Lineal",
            "Matematicas Discretas",
            "Calculo I / II / III",
            "Optimizacion",
            "Estadistica / Probabilidad",
            "Ecuaciones Diferenciales",
            "Simulacion",
          ],
          hasOther: true,
        },
        {
          id: "s1_4",
          type: "radio",
          label: "Anos de experiencia docente universitaria:",
          options: [
            "Menos de 3 anos",
            "3 a 7 anos",
            "8 a 15 anos",
            "Mas de 15 anos",
          ],
          required: true,
        },
        {
          id: "s1_5",
          type: "number",
          label: "Numero aproximado de estudiantes que atiende este trimestre:",
          placeholder: "Ej: 90",
        },
      ],
    },
    {
      id: "s2",
      title: "Percepcion sobre IA generativa en la academia",
      description:
        "Como percibe usted el impacto de herramientas como ChatGPT, Gemini, etc. en el aprendizaje universitario.",
      questions: [
        {
          id: "s2_1",
          type: "likert",
          label:
            "Con que frecuencia cree que sus estudiantes usan herramientas de IA generativa para las siguientes actividades?",
          scale: ["Nunca", "Raramente", "A veces", "Frecuentemente", "Casi siempre"],
          statements: [
            { id: "a", text: "Para estudiar/comprender temas" },
            { id: "b", text: "Para resolver tareas/ejercicios" },
            { id: "c", text: "Para preparar evaluaciones" },
            { id: "d", text: "Para generar informes/trabajos escritos" },
          ],
        },
        {
          id: "s2_2",
          type: "radio",
          label:
            "En su opinion, el uso de IA generativa por parte de los estudiantes es principalmente...",
          options: [
            "Positivo para el aprendizaje",
            "Negativo para el aprendizaje",
            "Depende de como se use",
            "No tengo opinion formada",
          ],
          hasOther: true,
        },
        {
          id: "s2_3",
          type: "radio",
          label:
            "Ha detectado casos donde sospecha que un estudiante uso IA para completar una evaluacion o entrega?",
          options: [
            "Si, multiples veces",
            "Si, alguna vez",
            "No, pero creo que ocurre",
            "No",
            "No sabria como detectarlo",
          ],
        },
        {
          id: "s2_4",
          type: "likert",
          label: "Que tan de acuerdo esta con las siguientes afirmaciones?",
          scale: [
            "Muy en desacuerdo",
            "En desacuerdo",
            "Neutral",
            "De acuerdo",
            "Muy de acuerdo",
          ],
          statements: [
            {
              id: "a",
              text: "Los estudiantes que usan IA generativa aprenden menos que los que no la usan",
            },
            {
              id: "b",
              text: "La IA generativa puede ser una herramienta pedagogica valiosa si se usa correctamente",
            },
            {
              id: "c",
              text: "La universidad deberia prohibir el uso de IA en evaluaciones",
            },
            {
              id: "d",
              text: "La universidad deberia ensenar a los estudiantes a usar IA productivamente",
            },
            {
              id: "e",
              text: "Me preocupa que la IA reemplace habilidades fundamentales en mis estudiantes",
            },
            {
              id: "f",
              text: "No tengo las herramientas para evaluar si un estudiante uso IA indebidamente",
            },
          ],
          required: true,
        },
      ],
    },
    {
      id: "s3",
      title: "Evaluacion y metodos actuales",
      description: "Como evalua usted actualmente y que relacion tiene con el uso de IA.",
      questions: [
        {
          id: "s3_1",
          type: "checkbox",
          label: "Que tipos de evaluacion utiliza actualmente? (Marque todas las que apliquen)",
          options: [
            "Examenes presenciales escritos (sin tecnologia)",
            "Examenes con consulta de material",
            "Tareas para la casa (problemas, ejercicios)",
            "Proyectos o trabajos de investigacion",
            "Quizzes cortos en clase",
            "Evaluaciones orales",
            "Portafolios o entregas progresivas",
          ],
          hasOther: true,
        },
        {
          id: "s3_2",
          type: "radio",
          label: "Que porcentaje de su evaluacion es presencial sin acceso a tecnologia?",
          options: ["0-25%", "26-50%", "51-75%", "76-100%"],
        },
        {
          id: "s3_3",
          type: "radio",
          label:
            "Ha modificado sus metodos de evaluacion en respuesta a la existencia de IA generativa?",
          options: [
            "Si, significativamente",
            "Si, algo",
            "No, pero lo estoy considerando",
            "No, no lo considero necesario",
            "No estaba al tanto del tema",
          ],
        },
        {
          id: "s3_4",
          type: "checkbox",
          label: "Si respondio 'si' a la pregunta anterior, que cambios ha implementado?",
          options: [
            "Mas evaluaciones presenciales",
            "Preguntas que requieren razonamiento original (no solo respuesta)",
            "Evaluaciones orales",
            "Preguntas mas complejas o contextualizadas",
            "Uso de herramientas de deteccion de IA",
          ],
          hasOther: true,
        },
        {
          id: "s3_5",
          type: "radio",
          label: "En sus evaluaciones de matematica, que tipo de pregunta predomina?",
          options: [
            "Resolucion de problemas con procedimiento paso a paso",
            "Demostraciones formales",
            "Seleccion multiple / verdadero-falso",
            "Problemas aplicados (modelado, casos reales)",
            "Combinacion de varios tipos",
          ],
        },
      ],
    },
    {
      id: "s4",
      title: "Disposicion ante una plataforma con telemetria",
      description: "Evaluar la receptividad docente ante un sistema como TUNI.",
      questions: [
        {
          id: "s4_1",
          type: "radio",
          label:
            "Si existiera una plataforma donde sus estudiantes pudieran consultar un asistente de IA para estudiar su materia, y usted pudiera ver datos agregados y anonimizados sobre como la usan, le resultaria util?",
          options: ["Muy util", "Algo util", "Neutral", "Poco util", "Nada util"],
          required: true,
        },
        {
          id: "s4_2",
          type: "likert",
          label:
            "Que tan valiosa le resultaria la siguiente informacion de un sistema asi? (1 = Nada valiosa, 5 = Muy valiosa)",
          scale: ["Nada valiosa", "Poco valiosa", "Neutral", "Valiosa", "Muy valiosa"],
          statements: [
            { id: "a", text: "Temas que generan mas consultas" },
            {
              id: "b",
              text: "Proporcion de uso formativo vs sustitutivo (piden ayuda vs piden respuestas)",
            },
            { id: "c", text: "Picos de uso en relacion a fechas de evaluacion" },
            { id: "d", text: "Comparativa entre secciones o carreras" },
            {
              id: "e",
              text: "Alertas cuando un tema genera uso excesivamente delegativo",
            },
          ],
        },
        {
          id: "s4_3",
          type: "radio",
          label:
            "Estaria dispuesto(a) a compartir el programa, cronograma de evaluacion y estilo evaluativo de su materia para alimentar el contexto del asistente de IA?",
          options: [
            "Si, sin inconveniente",
            "Si, si se usa solo para el piloto",
            "Tal vez, necesitaria mas informacion",
            "No",
          ],
        },
        {
          id: "s4_4",
          type: "likert",
          label:
            'Que tan de acuerdo esta con las siguientes afirmaciones sobre un asistente de IA con modo "tutor"?',
          scale: [
            "Muy en desacuerdo",
            "En desacuerdo",
            "Neutral",
            "De acuerdo",
            "Muy de acuerdo",
          ],
          statements: [
            { id: "a", text: "Un tutor IA podria complementar mi labor docente" },
            {
              id: "b",
              text: "Prefiero que los estudiantes no usen ningun tipo de IA",
            },
            {
              id: "c",
              text: "Un tutor que guia sin dar respuestas me parece mejor que un chatbot abierto",
            },
            {
              id: "d",
              text: "Los datos de uso me ayudarian a ajustar mis evaluaciones",
            },
            {
              id: "e",
              text: "Me preocupa la privacidad de los datos de mis estudiantes",
            },
          ],
          required: true,
        },
      ],
    },
    {
      id: "s5",
      title: "Contexto institucional",
      description: "Percepcion sobre la posicion de la Unimet ante la IA.",
      questions: [
        {
          id: "s5_1",
          type: "radio",
          label:
            "Conoce alguna politica o lineamiento de la Universidad Metropolitana sobre el uso de IA por parte de estudiantes?",
          options: [
            "Si, conozco lineamientos formales",
            "He escuchado algo, pero no lineamientos formales",
            "No existe ninguno que yo sepa",
            "No estoy seguro(a)",
          ],
        },
        {
          id: "s5_2",
          type: "radio",
          label:
            "Cree que la universidad necesita una politica institucional clara sobre IA en la evaluacion?",
          options: [
            "Si, urgentemente",
            "Si, seria deseable",
            "No necesariamente",
            "No, cada profesor deberia decidir",
            "No tengo opinion",
          ],
        },
        {
          id: "s5_3",
          type: "radio",
          label:
            "Si pudiera disenar la politica de IA de la Unimet para su materia, cual seria su enfoque?",
          options: [
            "Prohibicion total en evaluaciones",
            "Permitido con restricciones (ej: solo para estudio, no para evaluaciones)",
            "Permitido con transparencia (el estudiante declara cuando uso IA)",
            "Integracion activa (ensenar a usarla como herramienta profesional)",
          ],
          hasOther: true,
        },
      ],
    },
    {
      id: "s6",
      title: "Comentarios abiertos",
      questions: [
        {
          id: "s6_1",
          type: "text",
          label:
            "Tiene algun comentario, preocupacion o sugerencia sobre el uso de IA generativa en la educacion matematica universitaria?",
          multiline: true,
          placeholder: "Escribe su respuesta aqui...",
        },
        {
          id: "s6_2",
          type: "radio",
          label:
            "Estaria dispuesto(a) a participar en el piloto como profesor colaborador (proporcionando material de su materia y recibiendo reportes agregados de uso)?",
          options: ["Si, me interesa", "Tal vez, necesito mas informacion", "No por el momento"],
        },
        {
          id: "s6_3",
          type: "text",
          label:
            'Si respondio "si" o "tal vez", proporcione un correo de contacto (opcional):',
          placeholder: "correo@unimet.edu.ve",
        },
      ],
    },
  ],
}
