import type { SurveyDefinition } from "./survey-types"

export const studentSurvey: SurveyDefinition = {
  id: "estudiante",
  title: "Encuesta Pre-Tesis para Estudiantes",
  description: "Proyecto TUNI — Universidad Metropolitana de Caracas",
  instructions:
    "Esta encuesta forma parte de un trabajo de grado sobre como los estudiantes universitarios usan herramientas de inteligencia artificial para estudiar. Tu participacion es voluntaria y anonima. No hay respuestas correctas ni incorrectas. Toma aproximadamente 5-7 minutos.",
  tableName: "respuesta_encuesta_estudiante",
  sections: [
    {
      id: "s1",
      title: "Datos del estudiante",
      description: "Informacion demografica basica. Sera anonimizada en el analisis.",
      questions: [
        {
          id: "s1_1",
          type: "radio",
          label: "Carrera que cursas actualmente:",
          options: [
            "Ingenieria de Sistemas / Computacion",
            "Ingenieria Mecanica",
            "Ingenieria Quimica",
            "Ingenieria Electrica",
            "Educacion",
          ],
          hasOther: true,
          required: true,
        },
        {
          id: "s1_2",
          type: "radio",
          label: "Facultad:",
          options: ["Ingenieria", "Ciencias y Artes", "Ciencias Economicas y Sociales"],
          required: true,
        },
        {
          id: "s1_3",
          type: "radio",
          label: "Trimestre que cursas (aproximado):",
          options: [
            "1-3 (primer ano)",
            "4-6 (segundo ano)",
            "7-9 (tercer ano)",
            "10+ (cuarto ano en adelante)",
          ],
          required: true,
        },
        {
          id: "s1_4",
          type: "checkbox",
          label:
            "Materias con componente matematico que cursas este trimestre (marca todas las que apliquen):",
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
      ],
    },
    {
      id: "s2",
      title: "Uso actual de IA generativa",
      description: "Queremos entender como usas herramientas de IA hoy, sin juicio.",
      questions: [
        {
          id: "s2_1",
          type: "checkbox",
          label:
            "Que herramientas de IA generativa has usado en los ultimos 3 meses? (Marca todas las que apliquen)",
          options: [
            "ChatGPT (OpenAI)",
            "Gemini (Google)",
            "Claude (Anthropic)",
            "Copilot (Microsoft/GitHub)",
            "Perplexity",
            "No he usado ninguna",
          ],
          hasOther: true,
        },
        {
          id: "s2_2",
          type: "radio",
          label: "Con que frecuencia usas IA generativa para actividades academicas?",
          options: [
            "Todos los dias",
            "Varias veces por semana",
            "Una vez por semana",
            "Algunas veces al mes",
            "Raramente",
          ],
        },
        {
          id: "s2_3",
          type: "radio",
          label:
            "Cuando usas IA para un problema matematico, cual de estas describe mejor lo que haces normalmente?",
          options: [
            "Le pido que me resuelva el problema completo y copio/adapto la respuesta",
            "Le pido que me resuelva el problema y luego estudio la solucion para entender",
            "Le muestro mi intento y le pido que me diga donde me equivoque",
            "Le pido que me explique el concepto y luego intento resolver yo",
            "Le pido pistas o pasos sin la respuesta completa",
            "Varia mucho dependiendo de la situacion",
          ],
        },
        {
          id: "s2_4",
          type: "radio",
          label: "Tu uso de IA cambia cuando se acerca una evaluacion?",
          options: [
            "Uso IA mas cuando se acerca un parcial/quiz",
            "Uso IA menos cuando se acerca un parcial/quiz (prefiero estudiar solo)",
            "No cambia significativamente",
            "No he notado un patron",
          ],
        },
      ],
    },
    {
      id: "s3",
      title: "Percepcion sobre IA y aprendizaje",
      description: "Tu opinion sobre como la IA afecta tu proceso de aprendizaje.",
      questions: [
        {
          id: "s3_1",
          type: "likert",
          label: "Que tan de acuerdo estas con las siguientes afirmaciones?",
          scale: [
            "Muy en desacuerdo",
            "En desacuerdo",
            "Neutral",
            "De acuerdo",
            "Muy de acuerdo",
          ],
          statements: [
            { id: "a", text: "Usar IA me ayuda a aprender mejor los temas de mis materias" },
            {
              id: "b",
              text: "A veces uso IA para completar tareas sin realmente entender lo que entrego",
            },
            {
              id: "c",
              text: "Me preocupa que depender de IA me haga menos capaz de resolver problemas por mi cuenta",
            },
            {
              id: "d",
              text: "Siento que aprendo mas cuando intento resolver un problema antes de consultar IA",
            },
            {
              id: "e",
              text: "La universidad deberia ensenarme a usar IA productivamente, no prohibirla",
            },
          ],
          required: true,
        },
        {
          id: "s3_2",
          type: "radio",
          label:
            "Piensa en la ultima vez que usaste IA para una tarea de matematica. Que tan bien entendiste el tema DESPUES de usar IA?",
          options: [
            "Lo entendi completamente, podria explicarlo a alguien mas",
            "Lo entendi en general, pero no los detalles finos",
            "Entendi el resultado pero no estoy seguro del proceso",
            "No lo entendi mucho mejor que antes",
            "No aplica / no recuerdo",
          ],
        },
      ],
    },
    {
      id: "s4",
      title: "Autoevaluacion de competencias matematicas",
      questions: [
        {
          id: "s4_1",
          type: "likert",
          label: "Como calificarias tu nivel actual en las siguientes areas?",
          scale: ["Muy debil", "Debil", "Regular", "Bueno", "Muy bueno"],
          statements: [
            { id: "a", text: "Resolver sistemas de ecuaciones" },
            { id: "b", text: "Razonamiento logico / demostraciones" },
            { id: "c", text: "Calculo (derivadas, integrales)" },
            { id: "d", text: "Algebra de matrices y espacios vectoriales" },
            { id: "e", text: "Probabilidad y estadistica" },
          ],
          required: true,
        },
        {
          id: "s4_2",
          type: "radio",
          label:
            "Cuando te enfrentas a un problema matematico que no sabes resolver, cual es tu primera reaccion?",
          options: [
            "Intentar resolverlo por mi cuenta (releer apuntes, probar enfoques)",
            "Buscar en internet / YouTube",
            "Preguntarle a un companero",
            "Preguntarle a una IA",
            "Preguntarle al profesor / preparador",
            "Dejarlo para despues y esperar que se aclare",
          ],
        },
      ],
    },
    {
      id: "s5",
      title: "Asistente academico",
      description: "Tu opinion sobre un asistente de IA disenado para tus materias.",
      questions: [
        {
          id: "s5_1",
          type: "radio",
          label:
            "Te gustaria contar con un asistente academico de IA que tenga la informacion exacta de las materias que cursas (syllabus, temas, evaluaciones)?",
          options: [
            "Si, lo usaria activamente",
            "Tal vez, lo probaria",
            "No me interesa",
          ],
          required: true,
        },
        {
          id: "s5_2",
          type: "radio",
          label:
            "Si este asistente estuviera disponible por Telegram, lo usarias?",
          options: [
            "Si, me parece mas practico que una pagina web",
            "Si, pero preferiria una pagina web",
            "No uso Telegram",
            "No me interesa",
          ],
        },
      ],
    },
    {
      id: "s6",
      title: "Comentarios finales",
      questions: [
        {
          id: "s6_1",
          type: "text",
          label:
            "Hay algo sobre tu experiencia usando IA para estudiar que crees que los profesores o la universidad no entienden?",
          multiline: true,
          placeholder: "Escribe tu respuesta aqui (opcional)...",
        },
        {
          id: "s6_2",
          type: "radio",
          label:
            "Estarias interesado(a) en participar en el piloto de TUNI (6 semanas, uso libre)?",
          options: ["Si, me interesa", "Tal vez, necesito mas informacion", "No por el momento"],
        },
        {
          id: "s6_3",
          type: "text",
          label:
            'Si respondiste "si" o "tal vez", proporciona tu correo institucional (no se asociara a tus respuestas):',
          placeholder: "tucorreo@correo.unimet.edu.ve",
        },
      ],
    },
  ],
}
