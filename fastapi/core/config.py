"""
SIPARTA Backend — Centralized Configuration
=============================================
Semua environment variable yang dibutuhkan backend didefinisikan di sini
agar mudah diaudit dan divalidasi saat startup.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Pastikan .env ter-load
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_env_path)


class Settings:
    """Container untuk seluruh konfigurasi aplikasi."""

    # --- Supabase ---
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")

    # --- Google Gemini AI ---
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # --- Debug ---
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # --- Blockchain Services (path ke relay) ---
    BLOCKCHAIN_DIR: str = str(
        Path(__file__).resolve().parent.parent.parent.parent / "blockchain_services"
    )

    # --- IoT Device Authentication ---
    # X-API-Key header yang dikirim oleh Raspberry Pi saat POST /api/v1/incidents/report.
    # Jika dikosongkan, autentikasi dilewati (mode development).
    DEVICE_API_KEY: str = os.getenv("DEVICE_API_KEY", "")

    # --- Cloudinary (Opsional — fallback upload gambar jika Supabase Storage belum dikonfigurasi) ---
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")

    def validate(self) -> list[str]:
        """Validasi bahwa credential kritis tersedia. Returns list of missing keys."""
        missing = []
        if not self.SUPABASE_URL:
            missing.append("SUPABASE_URL")
        if not self.SUPABASE_ANON_KEY:
            missing.append("SUPABASE_ANON_KEY")
        if not self.SUPABASE_SERVICE_ROLE_KEY:
            missing.append("SUPABASE_SERVICE_ROLE_KEY")
        if not self.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        return missing


settings = Settings()
