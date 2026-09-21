import type { SurveyDefinition } from "./survey-types"

export const studentSurvey: SurveyDefinition = {
  id: "estudiante",
  title: "Encuesta Pre-Tesis para Estudiantes",
  description: "Proyecto TUNI — Plataforma piloto de asistencia academica con telemetria",
  instructions:
    "Esta encuesta forma parte de un trabajo de grado sobre como los estudiantes universitarios usan herramientas de inteligencia artificial para estudiar y resolver evaluaciones matematicas. Tu participacion es voluntaria y anonima. No hay respuestas correctas ni incorrectas. La encuesta toma aproximadamente 12-15 minutos.",
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
        {
          id: "s1_5",
          type: "number",
          label:
            "Cuantas evaluaciones (parciales, quizzes, entregas) tienes este trimestre en total?",
          placeholder: "Ej: 12",
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
          type: "checkbox",
          label: "Para que usas IA generativa en tus materias? (Marca todas las que apliquen)",
          options: [
            "Entender un concepto que no me quedo claro en clase",
            "Resolver ejercicios o problemas de practica",
            "Verificar si mi solucion a un problema esta correcta",
            "Generar codigo para tareas de programacion",
            "Preparar resumenes o apuntes",
            "Resolver tareas o entregas directamente",
            "Preparar para evaluaciones (practicar tipos de preguntas)",
            "Buscar informacion que no encuentro en el material de clase",
          ],
          hasOther: true,
        },
        {
          id: "s2_4",
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
          id: "s2_5",
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
              text: "Si la IA no existiera, me esforzaria mas en resolver problemas yo mismo",
            },
            {
              id: "e",
              text: "Creo que saber usar IA es una habilidad importante para mi carrera profesional",
            },
            {
              id: "f",
              text: "Siento que aprendo mas cuando intento resolver un problema antes de consultar IA",
            },
            {
              id: "g",
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
        {
          id: "s3_3",
          type: "radio",
          label:
            'Alguna vez has sentido que la IA te "arruino" una oportunidad de aprender algo por ti mismo?',
          options: ["Si, varias veces", "Si, alguna vez", "No, nunca", "No estoy seguro"],
        },
      ],
    },
    {
      id: "s4",
      title: "Autoevaluacion de competencias matematicas",
      description: "Evaluacion subjetiva de tus habilidades actuales.",
      questions: [
        {
          id: "s4_1",
          type: "likert",
          label: "Como calificarias tu nivel actual en las siguientes areas?",
          scale: ["Muy debil", "Debil", "Regular", "Bueno", "Muy bueno"],
          statements: [
            { id: "a", text: "Resolver sistemas de ecuaciones" },
            { id: "b", text: "Demostraciones matematicas formales" },
            { id: "c", text: "Razonamiento logico / logica proposicional" },
            { id: "d", text: "Calculo (derivadas, integrales)" },
            { id: "e", text: "Algebra de matrices y espacios vectoriales" },
            { id: "f", text: "Probabilidad y estadistica" },
            { id: "g", text: "Modelado matematico (plantear problemas reales)" },
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
        {
          id: "s4_3",
          type: "radio",
          label: "Cuantas horas a la semana dedicas a estudiar matematica fuera de clase?",
          options: [
            "Menos de 2 horas",
            "2-4 horas",
            "5-8 horas",
            "9-12 horas",
            "Mas de 12 horas",
          ],
        },
      ],
    },
    {
      id: "s5",
      title: "Expectativas ante un asistente de IA academico",
      description: "Tu opinion sobre una herramienta como TUNI.",
      questions: [
        {
          id: "s5_1",
          type: "radio",
          label:
            "Imagina que tu universidad te ofrece un asistente de IA disenado especificamente para tus materias — que conoce tu syllabus, tus proximas evaluaciones, y los temas que ya viste en clase. Que tan interesado estarias en usarlo?",
          options: [
            "Muy interesado, lo usaria activamente",
            "Algo interesado, lo probaria",
            "Neutral",
            "Poco interesado",
            "Nada interesado",
          ],
          required: true,
        },
        {
          id: "s5_2",
          type: "radio",
          label:
            "Este asistente tendria dos modos: Modo libre (responde directamente, como ChatGPT) y Modo tutor (te guia paso a paso sin darte la respuesta). Cual modo crees que usarias mas?",
          options: [
            "Modo libre la mayoria del tiempo",
            "Modo tutor la mayoria del tiempo",
            "Ambos por igual, dependiendo de la situacion",
            "No sabria hasta probarlo",
          ],
        },
        {
          id: "s5_3",
          type: "checkbox",
          label: "En que situaciones usarias el modo tutor (guia sin respuesta directa)?",
          options: [
            "Cuando estudio para entender un tema nuevo",
            "Cuando quiero verificar mi razonamiento",
            "Antes de un parcial, para practicar",
            "Nunca, prefiero obtener la respuesta directa",
          ],
          hasOther: true,
        },
        {
          id: "s5_4",
          type: "checkbox",
          label: "En que situaciones usarias el modo libre (respuesta directa)?",
          options: [
            "Cuando tengo una tarea con deadline cercano",
            "Cuando necesito un ejemplo resuelto para entender el patron",
            "Cuando estoy verificando una respuesta que ya obtuve",
            "Cuando el tema es demasiado dificil y necesito ver la solucion",
          ],
          hasOther: true,
        },
        {
          id: "s5_5",
          type: "radio",
          label:
            'Si el asistente te mostrara un resumen de tus patrones de uso (ej: "Esta semana el 70% de tus consultas fueron pedir respuestas directas"), te resultaria util?',
          options: [
            "Si, me ayudaria a ser mas consciente de como estudio",
            "Tal vez, pero no se si cambiaria mi comportamiento",
            "No, no me interesaria",
            "Me incomodaria que me monitoreen",
          ],
        },
        {
          id: "s5_6",
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
            { id: "a", text: "Preferiria un tutor IA que me guie a uno que me de la respuesta" },
            {
              id: "b",
              text: "Un asistente que conoce mi materia seria mas util que ChatGPT generico",
            },
            { id: "c", text: "Me preocuparia que la universidad vea como uso IA" },
            {
              id: "d",
              text: "Si los datos son anonimos, no me molesta que se estudie mi uso",
            },
            {
              id: "e",
              text: "Usaria mas IA si fuera parte oficial de mis herramientas de estudio",
            },
          ],
        },
      ],
    },
    {
      id: "s6",
      title: "Privacidad y consentimiento",
      description: "Tus expectativas sobre privacidad en un sistema como este.",
      questions: [
        {
          id: "s6_1",
          type: "radio",
          label:
            "Que nivel de anonimato esperarias en un sistema de asistencia academica con telemetria?",
          options: [
            "Totalmente anonimo (nadie puede identificarme, ni el investigador)",
            "Pseudo-anonimo (el investigador tiene un codigo, pero mis profesores no me identifican)",
            "No me importa si saben quien soy, siempre que los datos sean para investigacion",
            "No usaria el sistema si se recolectan datos",
          ],
          required: true,
        },
        {
          id: "s6_2",
          type: "checkbox",
          label: "Que datos te sentirias comodo compartiendo? (Marca todas las que apliquen)",
          options: [
            "Mis preguntas al asistente (anonimizadas)",
            "La frecuencia con la que uso el sistema",
            "Las materias en las que pido mas ayuda",
            "Mi patron de uso (formativo vs sustitutivo)",
            "Mi rendimiento academico (notas) para correlacionar",
            "Ninguno de los anteriores",
          ],
        },
        {
          id: "s6_3",
          type: "checkbox",
          label: "Que te haria sentir mas comodo con la recoleccion de datos?",
          options: [
            "Saber que los datos nunca salen del servidor de la universidad",
            "Poder ver mis propios datos en tiempo real",
            "Saber que el profesor solo ve datos agregados, no individuales",
            "Poder borrar mis datos al final del estudio",
          ],
        },
      ],
    },
    {
      id: "s7",
      title: "Comentarios abiertos",
      questions: [
        {
          id: "s7_1",
          type: "text",
          label:
            "Hay algo sobre tu experiencia usando IA para estudiar que crees que los profesores o la universidad no entienden?",
          multiline: true,
          placeholder: "Escribe tu respuesta aqui...",
        },
        {
          id: "s7_2",
          type: "text",
          label:
            "Que feature o caracteristica te gustaria ver en un asistente de IA disenado para tus materias?",
          multiline: true,
          placeholder: "Escribe tu respuesta aqui...",
        },
        {
          id: "s7_3",
          type: "radio",
          label:
            "Estarias interesado(a) en participar en el piloto de TUNI (6 semanas, uso libre de la plataforma)?",
          options: ["Si, me interesa", "Tal vez, necesito mas informacion", "No por el momento"],
        },
        {
          id: "s7_4",
          type: "text",
          label:
            'Si respondiste "si" o "tal vez", proporciona tu correo institucional (no se asociara a tus respuestas):',
          placeholder: "tucorreo@correo.unimet.edu.ve",
        },
      ],
    },
  ],
}
