from enum import IntEnum


class State(IntEnum):
    """ConversationHandler states."""
    AWAITING_CONSENT = 0
    UPLOAD_SCHEDULE = 1
    CHATTING = 2
    CLASS_CHECKIN_ATTENDANCE = 3
    CLASS_CHECKIN_TOPIC = 4
    CLASS_CHECKIN_UNCLEAR = 5
    # Post-exam reflection (separate ConversationHandler, group=1)
    REFLECTION_SELF_ASSESSMENT = 6
    REFLECTION_GAPS = 7
    REFLECTION_TEACHING = 8
    PROFESSOR_AUTH = 9


# Spanish UI strings
STRINGS = {
    "welcome": (
        "Hola {name}! Soy TUNI, tu asistente academico de la "
        "Universidad Metropolitana de Caracas.\n\n"
        "Formo parte de un proyecto de investigacion sobre como los "
        "estudiantes usan herramientas de IA para estudiar."
    ),
    "consent_prompt": (
        "Al continuar, aceptas:\n"
        "- El registro automatico de tus interacciones\n"
        "- El uso anonimizado de los datos con fines academicos\n\n"
        "Tu identidad esta protegida y separada de tus interacciones."
    ),
    "onboarding_disclaimer": (
        "La informacion que te pido a continuacion solo se solicita una vez. "
        "Queda guardada para que mis respuestas sean mas precisas y "
        "contextualizadas a tu situacion academica."
    ),
    "consent_accept": "Acepto participar",
    "consent_decline": "No deseo participar",
    "consent_declined": "Entendido. Si cambias de opinion, escribe /start.",
    "schedule_prompt": (
        "Para personalizar tu experiencia, sube una foto o PDF de tu "
        "cronograma de evaluaciones.\n\n"
        "Con esto puedo saber que materias cursas, tus fechas de "
        "evaluacion, y darte mejor asistencia.\n\n"
        "Si prefieres saltarte este paso, escribe /saltar"
    ),
    "schedule_received": (
        "Cronograma recibido! Procesando...\n"
        "Esto puede tardar unos segundos."
    ),
    "schedule_processed": (
        "Listo! Ya tengo tu cronograma. Veo que cursas:\n{subjects}\n\n"
        "Preguntame lo que necesites — puedo ayudarte con cualquiera "
        "de tus materias, fechas de evaluacion, o consultas generales."
    ),
    "schedule_process_error": (
        "No pude procesar el cronograma automaticamente. "
        "No te preocupes, puedes usarme normalmente y subir "
        "otro cronograma despues con /horario.\n\n"
        "Preguntame lo que necesites!"
    ),
    "schedule_skipped": (
        "Sin problema! Puedes subirlo despues con /horario.\n\n"
        "Preguntame lo que necesites — puedo ayudarte con materias, "
        "tramites universitarios, o consultas generales."
    ),
    "thinking": "Pensando...",
    "error": "Lo siento, ocurrio un error. Intenta de nuevo.",
    "session_timeout": (
        "Tu sesion anterior expiro. Escribe tu pregunta para continuar."
    ),
    "help": (
        "*Como usar TUNI:*\n\n"
        "Simplemente escribe tu pregunta o duda. Puedo ayudarte con:\n"
        "- Materias academicas (matematica, teoria, ejercicios)\n"
        "- Fechas y cronograma de evaluaciones\n"
        "- Informacion y tramites de la universidad\n\n"
        "*Comandos:*\n"
        "/horario - Subir tu cronograma\n"
        "/estado - Ver tu progreso\n"
        "/ayuda - Ver esta ayuda"
    ),
    # Class check-in strings
    "checkin_attendance_eval": (
        "Antes de empezar, cuentame un poco sobre {materia}. "
        "Tienes {eval_name} en {days} dia{plural}. "
        "Fuiste a la ultima clase?"
    ),
    "checkin_attendance_normal": (
        "Antes de arrancar con {materia}, cuentame rapido: "
        "fuiste a la ultima clase?"
    ),
    "checkin_topic_attended": "Que fue lo ultimo que vieron en clase? (En pocas palabras)",
    "checkin_topic_missed": "Entendido. Sabes que tema vieron en la ultima clase?",
    "checkin_unclear": "Hay algo que no te quedo claro o que quieras repasar hoy?",
    "checkin_transition_unclear": (
        "Perfecto, empecemos por ahi. Cuentame mas sobre lo que no entendiste de *{topic}*."
    ),
    # Post-exam reflection strings
    "reflection_prompt": (
        "Hola! Ayer tuviste *{eval_name}* de *{materia}*.\n\n"
        "Los temas que entraban eran: _{topics}_.\n\n"
        "Como te fue? (1 = muy mal, 5 = excelente)"
    ),
    "reflection_followup_low": "En que temas sientes que te falto estudio o preparacion?",
    "reflection_followup_high": "Bien! Hubo algun tema que te costara mas de lo esperado?",
    "reflection_teaching": (
        "Ultima pregunta: sientes que hubo temas de {materia} que "
        "el profesor no explico bien o que no se cubrieron lo suficiente "
        "en clase{topics_hint}?\n\n"
        "(Escribe 'no' si no tienes comentarios sobre eso)"
    ),
    "reflection_thanks": (
        "Gracias por tu reflexion! Esto me ayuda a entender mejor como apoyarte."
    ),
    "status": (
        "*Tu progreso con TUNI:*\n\n"
        "Sesiones totales: {total_sessions}\n"
        "Interacciones: {total_interactions}\n"
        "Materias usadas: {subjects_used}\n"
        "Profundidad promedio: {avg_depth} mensajes/sesion"
    ),
    # Professor strings
    "professor_prompt": "Ingresa la clave de acceso para el modo profesor:",
    "professor_auth_success": (
        "Acceso concedido. Modo profesor activado.\n\n"
        "Puedes hacerme preguntas sobre los datos del piloto, "
        "brechas detectadas, patrones de uso, o subir material."
    ),
    "professor_auth_fail": "Clave incorrecta. Intenta de nuevo o escribe /start para volver.",
    "professor_welcome_back": (
        "Bienvenido de vuelta, profesor. Escribe su consulta."
    ),
}
