"""
Application-wide configuration loaded from environment variables.

Uses python-dotenv to read a ``.env`` file at the project root.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root (two levels up from this file)
_env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_env_path)


class Settings:
    """Centralised configuration for IntelliQuery AI."""

    # -- API Keys ------------------------------------------------------
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    DEMO_MODE: bool = False

    # ── Database ──────────────────────────────────────────────────────
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/intelliquery_db",
    )

    # ── LLM Configuration ────────────────────────────────────────────
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq").lower() # 'groq' or 'ollama'
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.1-70b-versatile")
    LLM_TEMPERATURE: float = 0.0
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # ── Paths ────────────────────────────────────────────────────────
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
    REPORTS_DIR: str = str(PROJECT_ROOT / "outputs" / "reports")
    LOGS_DIR: str = str(PROJECT_ROOT / "logs")

    # ── Limits ───────────────────────────────────────────────────────
    MAX_CONVERSATION_HISTORY: int = 10
    MAX_RETRY_ATTEMPTS: int = 3
    QUERY_TIMEOUT: int = 30  # seconds
    MAX_DISPLAY_ROWS: int = 100

    # ── Environment ──────────────────────────────────────────────────
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # ── Validation ───────────────────────────────────────────────────
    @classmethod
    def validate(cls) -> None:
        """Log warnings for missing settings and treat placeholders as empty."""
        from src.utils.logger import setup_logger
        logger = setup_logger("settings")

        if cls.LLM_PROVIDER == "ollama":
            logger.info(f"Ollama provider selected (Model: {cls.LLM_MODEL})")
            # We don't strictly validate Ollama connectivity here to avoid slow startup
        else:
            # Groq validation
            placeholders = ["your_actual_key_here", "gsk_your_key_here", "your_groq_api_key"]
            if not cls.GROQ_API_KEY or any(p in cls.GROQ_API_KEY.lower() for p in placeholders) or len(cls.GROQ_API_KEY) < 10:
                logger.warning("Valid GROQ_API_KEY not found. Falling back to DEMO MODE or checking for Local LLM.")
                cls.GROQ_API_KEY = "" # Clear placeholder
                if cls.LLM_PROVIDER == "groq":
                    cls.DEMO_MODE = True
        
        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL is required.")

    @classmethod
    def check_ollama_health(cls) -> bool:
        """Verify if the Ollama server is reachable."""
        import requests
        try:
            response = requests.get(cls.OLLAMA_BASE_URL, timeout=2)
            return response.status_code == 200
        except:
            return False

    @classmethod
    def ensure_dirs(cls) -> None:
        """Create output / log directories if they do not exist."""
        os.makedirs(cls.REPORTS_DIR, exist_ok=True)
        os.makedirs(cls.LOGS_DIR, exist_ok=True)
