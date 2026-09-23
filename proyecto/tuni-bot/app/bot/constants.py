from enum import IntEnum


class State(IntEnum):
    """ConversationHandler states."""
    AWAITING_CONSENT = 0
    UPLOAD_SCHEDULE = 1
    SELECTING_CAREER = 2
    SELECTING_TRIMESTER = 3
    SELECTING_SUBJECT = 4
    CHATTING = 5
    # Class check-in (between subject selection and chatting)
    CLASS_CHECKIN_ATTENDANCE = 6
    CLASS_CHECKIN_TOPIC = 7
    CLASS_CHECKIN_UNCLEAR = 8
    # Post-exam reflection (separate ConversationHandler, group=1)
    REFLECTION_SELF_ASSESSMENT = 9
    REFLECTION_GAPS = 10
    REFLECTION_TEACHING = 11


# Available careers for the pilot
CAREERS = [
    {"id": "ing_sistemas", "name": "Ingenieria de Sistemas"},
]

# Available trimesters per career
TRIMESTERS = {
    "ing_sistemas": [3, 4, 5],
}


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
        "La informacion que te pido a continuacion (horario, carrera, trimestre) "
        "solo se solicita una vez. Queda guardada para que cada vez mis "
        "respuestas sean mas precisas y contextualizadas a tu situacion academica."
    ),
    "consent_accept": "Acepto participar",
    "consent_decline": "No deseo participar",
    "consent_declined": "Entendido. Si cambias de opinion, escribe /start.",
    "schedule_prompt": (
        "Para personalizar tu experiencia, sube una foto o PDF de tu "
        "horario semanal (el que genera el sistema de la universidad).\n\n"
        "Si prefieres saltarte este paso, escribe /saltar"
    ),
    "schedule_received": "Horario recibido!",
    "schedule_skipped": "Sin problema! Puedes subirlo despues con /horario",
    "select_career": "Cual es tu carrera?",
    "select_trimester": "En que trimestre estas?",
    "select_subject": "Selecciona la materia con la que necesitas ayuda:",
    "subject_selected": (
        "Perfecto! Estamos en *{subject}*.\n\n"
        "Como puedo ayudarte?\n"
        "- Escribe el *tema* que necesitas repasar\n"
        "- Enviame un *problema* que quieras resolver\n"
        "- O hazme una *pregunta concreta* sobre la materia\n\n"
        "Mientras mas especifica tu consulta, mejor te puedo guiar."
    ),
    "general_selected": (
        "Modo *Consulta General*.\n\n"
        "Puedes preguntarme sobre procesos, informacion y tramites "
        "de la Universidad Metropolitana. Escribe tu consulta."
    ),
    "thinking": "Pensando...",
    "error": "Lo siento, ocurrio un error. Intenta de nuevo.",
    "session_timeout": "Tu sesion anterior expiro. Selecciona una materia para continuar.",
    "help": (
        "*Comandos disponibles:*\n\n"
        "/start - Iniciar el bot\n"
        "/materia - Cambiar de materia\n"
        "/nueva - Nueva sesion\n"
        "/horario - Subir tu horario\n"
        "/estado - Ver tu progreso\n"
        "/ayuda - Ver estos comandos"
    ),
    "new_session": "Sesion cerrada. Selecciona una materia para continuar.",
    "subject_switched": "Perfecto, cambiamos a *{subject}*! Escribe tu pregunta.",
    "switch_ambiguous": "Quieres cambiar de materia? Selecciona una:",
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
        "Gracias por tu reflexion! Esto me ayuda a entender mejor como apoyarte. "
        "Si necesitas repasar algo, puedes seleccionar una materia cuando quieras."
    ),
    "status": (
        "*Tu progreso con TUNI:*\n\n"
        "Sesiones totales: {total_sessions}\n"
        "Interacciones: {total_interactions}\n"
        "Materias usadas: {subjects_used}\n"
        "Profundidad promedio: {avg_depth} mensajes/sesion"
    ),
}
