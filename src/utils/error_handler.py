"""
Custom exception classes and a user-friendly error formatter.
"""

from __future__ import annotations


# ── Custom Exceptions ────────────────────────────────────────────────────────

class DatabaseError(Exception):
    """Raised when a database operation fails."""


class QueryGenerationError(Exception):
    """Raised when the LLM fails to generate a valid SQL query."""


class VisualizationError(Exception):
    """Raised when chart creation fails."""


class ReportGenerationError(Exception):
    """Raised when PDF/DOCX report generation fails."""


class APIError(Exception):
    """Raised when an external API call (e.g. Groq) fails."""


# ── Error-to-message mapper ─────────────────────────────────────────────────

_USER_MESSAGES: dict[type, str] = {
    DatabaseError: (
        "⚠️ Unable to reach the database. Please check your connection settings."
    ),
    QueryGenerationError: (
        "⚠️ I couldn't generate a valid SQL query for that question. "
        "Try rephrasing or simplifying your question."
    ),
    VisualizationError: (
        "⚠️ Something went wrong while creating the chart. "
        "The data may not support the requested visualisation."
    ),
    ReportGenerationError: (
        "⚠️ Report generation failed. Please try again."
    ),
    APIError: (
        "⚠️ The AI service is temporarily unavailable. Please try again in a moment."
    ),
}


def handle_error(error: Exception, context: str = "") -> str:
    """Convert a technical exception into a user-friendly message."""
    # Use custom message if the exception provides one (useful for APIError)
    if isinstance(error, (APIError, DatabaseError, QueryGenerationError)) and str(error):
        user_msg = str(error)
        if not user_msg.startswith("⚠️"):
            user_msg = f"⚠️ {user_msg}"
    else:
        user_msg = _USER_MESSAGES.get(
            type(error),
            "⚠️ An unexpected error occurred. Please try again.",
        )
    
    # Append context if provided
    if context:
        user_msg = f"[{context}] {user_msg}"
    return user_msg
