"""Configuration centralisée (variables d'environnement / .env)."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
GENERATED_DIR = DATA_DIR / "generated"
DB_PATH = DATA_DIR / "shop.db"
for _d in (UPLOAD_DIR, GENERATED_DIR):
    _d.mkdir(parents=True, exist_ok=True)


class Settings:
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    MAX_STEPS: int = int(os.getenv("AGENT_MAX_STEPS", "8"))
    IMAGE_PROVIDER: str = os.getenv("IMAGE_PROVIDER", "pollinations")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    MAX_UPLOAD_MB: int = 25

    @property
    def is_local(self) -> bool:
        return "localhost" in self.LLM_BASE_URL or "127.0.0.1" in self.LLM_BASE_URL

    @property
    def configured(self) -> bool:
        key = self.LLM_API_KEY.strip()
        return (bool(key) and key != "colle_ta_cle_ici") or self.is_local


settings = Settings()
