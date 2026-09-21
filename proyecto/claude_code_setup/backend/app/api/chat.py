import json
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.db.client import get_supabase
from app.services.ollama_client import stream_chat

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    mode: str  # "neutral" | "tutor"
    message: str
    materia_id: str | None = None
    history: list[dict[str, str]] = []


@router.post("/chat")
async def chat(req: ChatRequest):
    if req.mode not in ("neutral", "tutor"):
        raise HTTPException(status_code=400, detail="mode must be 'neutral' or 'tutor'")

    # Look up materia name
    materia_nombre = "General"
    if req.materia_id:
        try:
            result = (
                get_supabase()
                .table("materia")
                .select("nombre")
                .eq("id_materia", req.materia_id)
                .single()
                .execute()
            )
            materia_nombre = result.data["nombre"]
        except Exception:
            logger.warning("Could not fetch materia %s, using 'General'", req.materia_id)

    # Build conversation messages for Ollama
    messages = [{"role": m["role"], "content": m["content"]} for m in req.history]
    messages.append({"role": "user", "content": req.message})

    async def event_stream():
        full_response = ""
        elapsed_ms = 0
        total_tokens = 0

        try:
            async for chunk in stream_chat(messages, req.mode, materia_nombre):
                if chunk["done"]:
                    elapsed_ms = chunk["elapsed_ms"]
                    total_tokens = chunk["total_tokens"]
                    yield f"data: {json.dumps(chunk)}\n\n"
                else:
                    full_response += chunk["content"]
                    yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            logger.error("Ollama streaming error: %s", e)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return

        # Record interaction in Supabase
        try:
            get_supabase().table("interaccion").insert({
                "id_sesion": req.session_id,
                "modo_seleccionado": req.mode,
                "prompt_estudiante": req.message,
                "respuesta_modelo": full_response,
                "longitud_prompt_tokens": len(req.message.split()),
                "longitud_respuesta_tokens": total_tokens,
                "tiempo_generacion_ms": elapsed_ms,
            }).execute()
        except Exception as e:
            logger.error("Failed to record interaction: %s", e)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
