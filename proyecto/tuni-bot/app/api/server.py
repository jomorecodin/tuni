"""FastAPI server for the supervisor dashboard API.

Run alongside the bot:
    uvicorn app.api.server:app --port 8001 --reload
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.bot.services.cronograma_service import load_all_cronogramas
from app.api.routes import analysis, health, ai_query

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

app = FastAPI(
    title="TUNI Supervisor API",
    description="API for the TUNI research supervisor dashboard",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load cronogramas on startup
@app.on_event("startup")
async def startup():
    load_all_cronogramas()

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(ai_query.router, prefix="/api/ai", tags=["ai"])
