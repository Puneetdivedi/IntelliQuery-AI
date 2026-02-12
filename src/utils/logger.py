"""
Logging utilities for IntelliQuery AI.

Provides a ``setup_logger`` factory that creates module-specific loggers
with both file and console handlers.
"""

import logging
import os
from datetime import datetime
from src.config.settings import Settings


def setup_logger(name: str) -> logging.Logger:
    """Create and return a logger with file and console handlers.

    Args:
        name: Logger name (typically ``__name__`` of the calling module).

    Returns:
        Configured ``logging.Logger`` instance.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers when called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # ── Ensure log directory exists ──────────────────────────────────
    os.makedirs(Settings.LOGS_DIR, exist_ok=True)

    # ── File handler (INFO and above) ────────────────────────────────
    log_filename = os.path.join(
        Settings.LOGS_DIR,
        f"{name}_{datetime.now().strftime('%Y%m%d')}.log",
    )
    fh = logging.FileHandler(log_filename, encoding="utf-8")
    fh.setLevel(logging.INFO)

    # ── Console handler (WARNING and above) ──────────────────────────
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)

    # ── Formatter ────────────────────────────────────────────────────
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
