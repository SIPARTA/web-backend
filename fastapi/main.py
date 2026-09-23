import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env dari root web-backend sebelum import apapun yang butuh env vars
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from api import incidents
from core.config import settings

logger = logging.getLogger("siparta")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Validasi credential kritis saat server startup."""
    missing = settings.validate()
    if missing:
        logger.warning(f"[STARTUP] ⚠️  Missing env vars: {', '.join(missing)}")
    else:
        logger.info("[STARTUP] ✅ Semua environment variable tervalidasi.")
    logger.info(f"[STARTUP] Supabase URL: {settings.SUPABASE_URL}")
    logger.info(f"[STARTUP] Blockchain Dir: {settings.BLOCKCHAIN_DIR}")
    yield
    logger.info("[SHUTDOWN] SIPARTA Backend shutting down.")

app = FastAPI(
    title="SIPARTA Backend API",
    description="Backend services for SIPARTA Real-Time Gas Detection and Web3 Logging",
    version="1.0.0",
    lifespan=lifespan
)

# Konfigurasi CORS agar frontend (Next.js) bisa mengakses API
allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if allowed_origins_env:
    allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
else:
    allowed_origins = [
        "https://siparta.id",
        "https://www.siparta.id",
        "https://siparta.vercel.app",
        "http://localhost:3000"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mounting router dari module api
app.include_router(incidents.router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {
        "status": "Online",
        "message": "Welcome to SIPARTA Backend API! Engine is running.",
        "services": ["Supabase", "Gemini AI", "Thirdweb Blockchain"]
    }


@app.get("/health")
def health_check(response: Response):
    """Health check untuk deployment platform (Render)."""
    health_status = {
        "status": "ok",
        "components": {
            "supabase": "ok" if settings.SUPABASE_URL else "missing_config",
            "gemini": "ok" if os.getenv("GEMINI_API_KEY") else "missing_config",
            "blockchain": "ok" if os.getenv("DEVICE_API_KEY") else "missing_config"
        }
    }
    
    if any(v == "missing_config" for v in health_status["components"].values()):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        health_status["status"] = "degraded"
        
    return health_status

