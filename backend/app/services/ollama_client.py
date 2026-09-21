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
) -> AsyncGenerator[dict, None]:
    """Stream a chat completion from Ollama, yielding token chunks."""
    system_prompt = build_system_prompt(mode, materia_nombre)

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
