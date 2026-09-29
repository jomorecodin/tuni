"""Lightweight keyword-based subject classifier for telemetry tagging.

No LLM call — uses keyword matching to tag which subject an interaction
is most likely about. Used for analytics only, not for routing.
"""

import re

# Subject keywords: each list contains terms strongly associated with that subject
SUBJECT_KEYWORDS: dict[str, list[str]] = {
    "Algebra Lineal": [
        "matriz", "matrices", "vector", "vectores", "espacio vectorial",
        "transformacion lineal", "determinante", "eigenvalor", "autovalor",
        "diagonalizar", "rango", "nucleo", "base", "dimension",
        "producto punto", "producto cruz", "sistema de ecuaciones",
        "gauss", "jordan", "inversa", "ortogonal",
    ],
    "Matematicas Discretas": [
        "grafo", "grafos", "arbol", "combinatoria", "permutacion",
        "logica", "proposicion", "induccion", "recursion", "relacion",
        "conjunto", "funcion biyectiva", "inyectiva", "sobreyectiva",
        "modular", "congruencia", "teorema de euler", "algoritmo",
    ],
    "Calculo I": [
        "limite", "derivada", "integral", "continuidad", "funcion",
        "regla de la cadena", "maximos", "minimos", "area bajo la curva",
        "teorema fundamental", "antiderivada", "serie de taylor",
    ],
    "Calculo II": [
        "integral doble", "integral triple", "coordenadas polares",
        "parametrizacion", "superficie", "volumen", "jacobiano",
        "campo vectorial", "gradiente", "divergencia", "rotacional",
    ],
    "Calculo III": [
        "ecuacion diferencial", "laplace", "fourier", "serie de potencias",
        "ecuacion de calor", "ecuacion de onda", "condiciones de frontera",
    ],
    "Estadistica": [
        "probabilidad", "distribucion", "media", "varianza", "desviacion",
        "hipotesis", "intervalo de confianza", "regresion", "correlacion",
        "muestra", "poblacion", "binomial", "normal", "poisson",
    ],
    "Optimizacion": [
        "optimizar", "programacion lineal", "simplex", "restriccion",
        "funcion objetivo", "maximizar", "minimizar", "dual",
        "gradiente descendente", "convexo", "lagrange",
    ],
}


def classify_subject(text: str) -> str | None:
    """Classify which subject a message is most likely about.

    Returns subject name or None if no strong match.
    """
    lower = text.lower()
    scores: dict[str, int] = {}

    for subject, keywords in SUBJECT_KEYWORDS.items():
        count = 0
        for kw in keywords:
            if kw in lower:
                count += 1
        if count > 0:
            scores[subject] = count

    if not scores:
        return None

    # Return the subject with the highest keyword match count
    return max(scores, key=scores.get)
