import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db.client import get_supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


class CreateSessionRequest(BaseModel):
    user_id: str
    mode: str  # "neutral" | "tutor"
    materia_id: str | None = None


@router.post("/sessions")
async def create_session(req: CreateSessionRequest):
    # Ensure the user exists, create if not
    sb = get_supabase()
    user_result = sb.table("usuario").select("user_id").eq("user_id", req.user_id).execute()
    if not user_result.data:
        sb.table("usuario").insert({"user_id": req.user_id}).execute()

    # Create session
    session_data: dict = {
        "user_id": req.user_id,
        "modo_inicial": req.mode,
    }
    if req.materia_id:
        session_data["materia_declarada"] = req.materia_id

    result = sb.table("sesion").insert(session_data).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create session")

    return {"id_sesion": result.data[0]["id_sesion"]}


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: str):
    result = (
        get_supabase()
        .table("interaccion")
        .select("prompt_estudiante, respuesta_modelo, timestamp, modo_seleccionado")
        .eq("id_sesion", session_id)
        .order("timestamp", desc=False)
        .execute()
    )

    messages = []
    for row in result.data:
        messages.append({
            "role": "user",
            "content": row["prompt_estudiante"],
            "timestamp": row["timestamp"],
        })
        if row["respuesta_modelo"]:
            messages.append({
                "role": "assistant",
                "content": row["respuesta_modelo"],
                "timestamp": row["timestamp"],
            })

    return {"messages": messages}
