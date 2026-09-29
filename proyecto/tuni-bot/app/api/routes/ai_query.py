"""AI consultation endpoints — pattern analysis + text-to-SQL exploratory queries."""

import json
import re
import time
import logging

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import settings
from app.bot.services.analysis_engine import build_ai_context
from app.db.client import get_supabase

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


# --- Text-to-SQL endpoint ---

SQL_SCHEMA_PROMPT = """\
You are a SQL query generator for a PostgreSQL database (Supabase).
The user asks questions in Spanish about pilot study data.
Generate a SELECT query that answers their question.

SCHEMA:
- usuario(user_id UUID PK, telegram_id BIGINT, estado_participacion TEXT, created_at TIMESTAMPTZ)
- sesion(id_sesion UUID PK, user_id UUID FK, modo_inicial TEXT, dispositivo TEXT, materia_declarada UUID, timestamp_fin TIMESTAMPTZ, created_at TIMESTAMPTZ)
- interaccion(id_interaccion UUID PK, id_sesion UUID FK, modo_seleccionado TEXT, prompt_estudiante TEXT, respuesta_modelo TEXT, longitud_prompt_tokens INT, longitud_respuesta_tokens INT, tiempo_generacion_ms INT, created_at TIMESTAMPTZ)
- materia(id_materia UUID PK, nombre TEXT, carrera TEXT, trimestre INT, codigo TEXT)
- evento_interaccion(id_evento UUID PK, id_interaccion UUID FK, id_sesion UUID FK, tipo_evento TEXT, timestamp TIMESTAMPTZ, metadata_json JSONB)
- reflexion_post_evaluacion(id_reflexion UUID PK, telegram_id BIGINT, materia TEXT, eval_tipo TEXT, eval_fecha DATE, self_assessment INT, perceived_gaps TEXT, teaching_gaps TEXT, response_delay_hours NUMERIC, timestamp TIMESTAMPTZ)

RULES:
1. ONLY generate SELECT queries. Never INSERT, UPDATE, DELETE, DROP, etc.
2. Return ONLY the SQL query, no explanation. Do not wrap in markdown code blocks.
3. Use appropriate aggregations (COUNT, AVG, SUM, etc.)
4. Limit results to 100 rows max.
5. Use table aliases for readability.
"""

INTERPRET_PROMPT = """\
Eres un asistente de investigacion. El usuario hizo una pregunta sobre datos de un piloto universitario.
Se genero una consulta SQL y estos son los resultados.

Pregunta del usuario: {question}
SQL ejecutado: {sql}
Resultados: {results}

Interpreta los resultados de forma clara y concisa en espanol.
Si los resultados estan vacios, explicalo.
Sugiere insights pedagogicos relevantes si aplica.
"""


class SqlQueryRequest(BaseModel):
    question: str


class SqlQueryResponse(BaseModel):
    answer: str
    sql: str
    elapsed_ms: int


@router.post("/sql-query", response_model=SqlQueryResponse)
async def sql_query(req: SqlQueryRequest):
    """Generate SQL from natural language, execute it, and interpret results."""
    start = time.monotonic()

    # Step 1: Generate SQL from question using Gemini
    sql_body = {
        "contents": [{"role": "user", "parts": [{"text": req.question}]}],
        "systemInstruction": {"parts": [{"text": SQL_SCHEMA_PROMPT}]},
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1024},
    }

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:generateContent"
        f"?key={settings.gemini_api_key}"
    )

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, json=sql_body)
        resp.raise_for_status()
        data = resp.json()

    candidates = data.get("candidates", [])
    sql = ""
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        sql = "".join(p.get("text", "") for p in parts).strip()

    # Clean up markdown code fences if present
    if sql.startswith("```"):
        sql = sql.split("\n", 1)[1] if "\n" in sql else sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]
        sql = sql.strip()

    if not sql:
        raise HTTPException(status_code=400, detail="Could not generate SQL query")

    # Safety: only allow SELECT queries
    sql_upper = sql.upper().strip()
    if not sql_upper.startswith("SELECT"):
        raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")

    # Block dangerous keywords
    dangerous = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE", "GRANT", "REVOKE"]
    for kw in dangerous:
        if re.search(rf'\b{kw}\b', sql_upper):
            raise HTTPException(status_code=400, detail=f"Forbidden SQL keyword: {kw}")

    # Step 2: Execute SQL against Supabase
    try:
        sb = get_supabase()
        result = sb.rpc("", {}).execute()  # Not using RPC — use raw SQL via postgrest
        # Supabase Python client doesn't support raw SQL directly
        # Use the REST API instead
        import httpx as httpx_sync
        headers = {
            "apikey": settings.supabase_key,
            "Authorization": f"Bearer {settings.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        # Use Supabase's PostgREST doesn't support raw SQL
        # Instead, we'll use the pg_net extension or just return the SQL for now
        # For a clean implementation, use supabase-py's rpc with a server function
        # Fallback: execute via a Supabase Edge Function or rpc

        # Simple approach: create a Supabase function for arbitrary SELECT
        # For now, we'll try using the Supabase REST API with a custom RPC
        rpc_result = sb.rpc("execute_readonly_query", {"query_text": sql}).execute()
        results = rpc_result.data if rpc_result.data else []
    except Exception as e:
        logger.error("SQL execution failed: %s", e)
        # If RPC doesn't exist yet, return the SQL with instructions
        results = []
        elapsed_ms = int((time.monotonic() - start) * 1000)
        return SqlQueryResponse(
            answer=(
                f"SQL generado correctamente pero no se pudo ejecutar automaticamente.\n\n"
                f"Puedes ejecutar esta consulta directamente en el SQL Editor de Supabase:\n\n"
                f"```sql\n{sql}\n```\n\n"
                f"Para habilitar la ejecucion automatica, crea esta funcion en Supabase:\n\n"
                f"```sql\n"
                f"CREATE OR REPLACE FUNCTION execute_readonly_query(query_text TEXT)\n"
                f"RETURNS JSON AS $$\n"
                f"BEGIN\n"
                f"  RETURN (SELECT json_agg(row_to_json(t)) FROM (\n"
                f"    EXECUTE query_text\n"
                f"  ) t);\n"
                f"END;\n"
                f"$$ LANGUAGE plpgsql SECURITY DEFINER;\n"
                f"```"
            ),
            sql=sql,
            elapsed_ms=elapsed_ms,
        )

    # Step 3: Interpret results using Gemini
    interpret_body = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": INTERPRET_PROMPT.format(
                            question=req.question,
                            sql=sql,
                            results=json.dumps(results[:50], ensure_ascii=False, default=str),
                        )
                    }
                ],
            }
        ],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2048},
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, json=interpret_body)
        resp.raise_for_status()
        data = resp.json()

    answer = ""
    candidates = data.get("candidates", [])
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        answer = "".join(p.get("text", "") for p in parts)

    if not answer:
        answer = f"Resultados de la consulta:\n{json.dumps(results[:20], indent=2, ensure_ascii=False, default=str)}"

    elapsed_ms = int((time.monotonic() - start) * 1000)
    return SqlQueryResponse(answer=answer, sql=sql, elapsed_ms=elapsed_ms)
