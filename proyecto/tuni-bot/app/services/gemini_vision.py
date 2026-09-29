"""Gemini multimodal document processing.

Used for:
- Cronograma extraction during onboarding (PDF/photo → structured JSON)
- Exam photo / document analysis during chat
- Professor document uploads

Always uses Gemini regardless of llm_provider setting.
"""

import base64
import json
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

CRONOGRAMA_PROMPT = """\
Analiza esta imagen/documento de un cronograma universitario.
Extrae la siguiente informacion en formato JSON:

{
  "materias": [
    {
      "nombre": "nombre de la materia",
      "evaluaciones": [
        {
          "tipo": "parcial|quiz|proyecto|final|tarea",
          "fecha": "YYYY-MM-DD",
          "temas": ["tema1", "tema2"],
          "peso": "porcentaje si esta visible"
        }
      ]
    }
  ],
  "notas": "cualquier observacion relevante"
}

Reglas:
- Si no puedes leer una fecha claramente, usa null.
- Si no hay temas listados para una evaluacion, deja el array vacio.
- Incluye TODAS las materias visibles en el documento.
- Responde SOLO con el JSON, sin texto adicional.
"""


async def process_document(
    file_bytes: bytes,
    mime_type: str,
    prompt: str,
) -> str:
    """Send a document/image to Gemini for multimodal analysis.

    Args:
        file_bytes: Raw bytes of the file (image or PDF).
        mime_type: MIME type (e.g. "image/jpeg", "application/pdf").
        prompt: Text prompt describing what to extract.

    Returns:
        Gemini's text response.
    """
    b64_data = base64.b64encode(file_bytes).decode("utf-8")

    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": b64_data,
                        }
                    },
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 4096,
        },
    }

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:generateContent"
        f"?key={settings.gemini_api_key}"
    )

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=body)
        response.raise_for_status()
        result = response.json()

    candidates = result.get("candidates", [])
    if not candidates:
        raise ValueError("Gemini returned no candidates")

    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(p.get("text", "") for p in parts)
    return text


async def extract_cronograma(file_bytes: bytes, mime_type: str) -> dict | None:
    """Extract structured cronograma data from a document/image.

    Returns parsed JSON dict or None if extraction fails.
    """
    try:
        raw = await process_document(file_bytes, mime_type, CRONOGRAMA_PROMPT)
        # Strip markdown code fences if Gemini wraps the JSON
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
        return json.loads(cleaned)
    except (json.JSONDecodeError, ValueError) as e:
        logger.error("Cronograma extraction failed: %s", e)
        return None
    except httpx.HTTPStatusError as e:
        logger.error("Gemini API error during cronograma extraction: %s", e)
        return None


async def analyze_document(
    file_bytes: bytes,
    mime_type: str,
    context: str = "",
) -> str:
    """Analyze a document/image in the context of a student conversation.

    Used for mid-chat document uploads (exam photos, problem sets, etc.).
    """
    prompt = (
        "El estudiante ha enviado este documento/imagen durante una sesion de estudio.\n"
    )
    if context:
        prompt += f"Contexto de la conversacion: {context}\n\n"
    prompt += (
        "Analiza el contenido. Si es un problema matematico o ejercicio, "
        "NO des la respuesta directa — identifica los conceptos involucrados "
        "y guia al estudiante con preguntas socraticas.\n"
        "Si es material informativo (cronograma, notas, etc.), resume el contenido."
    )
    return await process_document(file_bytes, mime_type, prompt)
