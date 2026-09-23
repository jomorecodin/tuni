"""
LLM client abstraction — supports Gemini (dev/test) and Ollama (production).
Provides a unified async generator interface for streaming chat completions.
"""

import json
import time
from typing import AsyncGenerator

import httpx

from app.core.config import settings
from app.services.prompt_loader import build_system_prompt


async def stream_chat(
    messages: list[dict[str, str]],
    mode: str,
    materia_nombre: str = "General",
    carrera: str | None = None,
    trimestre: int | None = None,
) -> AsyncGenerator[dict, None]:
    """Stream a chat completion, yielding token chunks.

    Yields dicts with either:
      {"done": False, "content": "token_text"}
      {"done": True, "total_tokens": N, "elapsed_ms": M}
    """
    if settings.llm_provider == "gemini":
        async for chunk in _stream_gemini(messages, mode, materia_nombre, carrera, trimestre):
            yield chunk
    else:
        async for chunk in _stream_ollama(messages, mode, materia_nombre, carrera, trimestre):
            yield chunk


async def _stream_gemini(
    messages: list[dict[str, str]],
    mode: str,
    materia_nombre: str,
    carrera: str | None = None,
    trimestre: int | None = None,
) -> AsyncGenerator[dict, None]:
    """Stream from Gemini API using REST endpoint."""
    system_prompt = build_system_prompt(mode, materia_nombre, carrera, trimestre)

    # Build Gemini contents format
    contents = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})

    body = {
        "contents": contents,
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.9,
            "topK": 40,
            "maxOutputTokens": 2048,
        },
    }

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:streamGenerateContent"
        f"?alt=sse&key={settings.gemini_api_key}"
    )

    start_time = time.monotonic()
    total_tokens = 0

    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream("POST", url, json=body) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data = line[6:]
                if not data.strip():
                    continue
                try:
                    chunk = json.loads(data)
                except json.JSONDecodeError:
                    continue

                candidates = chunk.get("candidates", [])
                if not candidates:
                    continue

                parts = candidates[0].get("content", {}).get("parts", [])
                for part in parts:
                    text = part.get("text", "")
                    if text:
                        total_tokens += len(text.split())
                        yield {"done": False, "content": text}

    elapsed_ms = int((time.monotonic() - start_time) * 1000)
    yield {"done": True, "total_tokens": total_tokens, "elapsed_ms": elapsed_ms}


async def _stream_ollama(
    messages: list[dict[str, str]],
    mode: str,
    materia_nombre: str,
    carrera: str | None = None,
    trimestre: int | None = None,
) -> AsyncGenerator[dict, None]:
    """Stream from Ollama local API."""
    system_prompt = build_system_prompt(mode, materia_nombre, carrera, trimestre)

    ollama_messages = [
        {"role": "system", "content": system_prompt},
        *messages,
    ]

    body = {
        "model": settings.ollama_model,
        "messages": ollama_messages,
        "stream": True,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.1,
            "num_predict": 1024,
        },
    }

    start_time = time.monotonic()
    total_tokens = 0

    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            "POST",
            f"{settings.ollama_base_url}/api/chat",
            json=body,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line:
                    continue
                chunk = json.loads(line)
                if chunk.get("done"):
                    elapsed_ms = int((time.monotonic() - start_time) * 1000)
                    eval_count = chunk.get("eval_count", total_tokens)
                    yield {
                        "done": True,
                        "total_tokens": eval_count,
                        "elapsed_ms": elapsed_ms,
                    }
                else:
                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        total_tokens += 1
                        yield {"done": False, "content": token}
