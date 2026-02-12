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

    # ── API Keys ──────────────────────────────────────────────────────
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # ── Database ──────────────────────────────────────────────────────
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/intelliquery_db",
    )

    # ── LLM Model ────────────────────────────────────────────────────
    LLM_MODEL: str = "llama-3.1-70b-versatile"
    LLM_TEMPERATURE: float = 0.0  # deterministic SQL generation

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
        """Raise ``ValueError`` if required settings are missing."""
        missing: list[str] = []
        if not cls.GROQ_API_KEY:
            missing.append("GROQ_API_KEY")
        if not cls.DATABASE_URL:
            missing.append("DATABASE_URL")
        if missing:
            raise ValueError(
                f"Missing required environment variable(s): {', '.join(missing)}. "
                "Please set them in a .env file or export them."
            )

    @classmethod
    def ensure_dirs(cls) -> None:
        """Create output / log directories if they do not exist."""
        os.makedirs(cls.REPORTS_DIR, exist_ok=True)
        os.makedirs(cls.LOGS_DIR, exist_ok=True)
