"""AI consultation endpoint — lets the supervisor ask questions about pilot data."""

import json
import time
import logging

import httpx
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings
from app.bot.services.analysis_engine import build_ai_context

logger = logging.getLogger(__name__)

router = APIRouter()

SUPERVISOR_SYSTEM_PROMPT = """\
Eres un asistente de investigacion para el proyecto TUNI de la Universidad Metropolitana de Caracas.

Tu rol es ayudar al supervisor del trabajo de grado a interpretar los datos recopilados del piloto.
El piloto estudia como la IA complementa las carencias en la preparacion estudiantil universitaria.

Tienes acceso a datos reales del piloto a continuacion. Responde SIEMPRE en espanol.
Basa tus respuestas exclusivamente en los datos proporcionados.
Si no hay suficientes datos para responder, dilo claramente.

Cuando identifiques patrones, explica su significado pedagogico.
Sugiere acciones concretas cuando sea pertinente.
"""


class AiQueryRequest(BaseModel):
    question: str
    include_context: bool = True


class AiQueryResponse(BaseModel):
    answer: str
    elapsed_ms: int
    context_length: int


@router.post("/query", response_model=AiQueryResponse)
async def ai_query(req: AiQueryRequest):
    """Send a question about pilot data to the LLM with full context."""
    context = build_ai_context() if req.include_context else ""

    system = SUPERVISOR_SYSTEM_PROMPT
    if context:
        system += f"\n\n--- DATOS DEL PILOTO ---\n{context}"

    # Build Gemini request
    contents = [{"role": "user", "parts": [{"text": req.question}]}]
    body = {
        "contents": contents,
        "systemInstruction": {"parts": [{"text": system}]},
        "generationConfig": {
            "temperature": 0.4,
            "topP": 0.9,
            "maxOutputTokens": 4096,
        },
    }

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:generateContent"
        f"?key={settings.gemini_api_key}"
    )

    start = time.monotonic()
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(url, json=body)
        resp.raise_for_status()
        data = resp.json()

    elapsed_ms = int((time.monotonic() - start) * 1000)

    # Extract response text
    candidates = data.get("candidates", [])
    answer = ""
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        answer = "".join(p.get("text", "") for p in parts)

    if not answer:
        answer = "No se pudo generar una respuesta. Verifica que hay datos suficientes en el piloto."

    return AiQueryResponse(
        answer=answer,
        elapsed_ms=elapsed_ms,
        context_length=len(context),
    )
