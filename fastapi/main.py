import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env dari root web-backend sebelum import apapun yang butuh env vars
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import incidents
from core.config import settings

logger = logging.getLogger("siparta")

app = FastAPI(
    title="SIPARTA Backend API",
    description="Backend services for SIPARTA Real-Time Gas Detection and Web3 Logging",
    version="1.0.0"
)

# Konfigurasi CORS agar frontend (Next.js) bisa mengakses API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Dalam produksi ganti dengan origin Vercel/Railway
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mounting router dari module api
app.include_router(incidents.router, prefix="/api/v1")


@app.on_event("startup")
def validate_environment():
    """Validasi credential kritis saat server startup."""
    missing = settings.validate()
    if missing:
        logger.warning(f"[STARTUP] ⚠️  Missing env vars: {', '.join(missing)}")
    else:
        logger.info("[STARTUP] ✅ Semua environment variable tervalidasi.")
    logger.info(f"[STARTUP] Supabase URL: {settings.SUPABASE_URL}")
    logger.info(f"[STARTUP] Blockchain Dir: {settings.BLOCKCHAIN_DIR}")


@app.get("/")
def read_root():
    return {
        "status": "Online",
        "message": "Welcome to SIPARTA Backend API! Engine is running.",
        "services": ["Supabase", "Gemini AI", "Thirdweb Blockchain"]
    }

