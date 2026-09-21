from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.sessions import router as sessions_router
from app.api.subjects import router as subjects_router
from app.core.config import settings

app = FastAPI(
    title="Plataforma Piloto Académica",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(sessions_router)
app.include_router(subjects_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
