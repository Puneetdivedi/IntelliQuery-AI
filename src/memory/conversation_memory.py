"""
Conversation Memory module for storing and retrieving chat history.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, List, Dict

from src.config.settings import Settings
from src.utils.logger import setup_logger

logger = setup_logger("memory")


class ConversationMemory:
    """
    Manages conversation history for context-aware interactions.
    Persists history to JSON (optional) and keeps last N turns in memory.
    """

    def __init__(self, session_id: str = "default"):
        """
        Initialize memory for a specific session.
        
        Args:
           session_id: Unique identifier for the user session.
        """
        self.session_id = session_id
        self.history: List[Dict[str, Any]] = []
        self.max_history = Settings.MAX_CONVERSATION_HISTORY
        
        # Ensure memory directory exists if we strictly wanted persistence
        # For this app, we'll mostly rely on in-memory list per session (Streamlit state)
        # But here is stub for file backing if needed later.

    def add_interaction(self, question: str, sql: str, summary: str):
        """Add a completed interaction to history."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "sql_query": sql,
            "summary": summary
        }
        self.history.append(entry)
        
        # Trim history
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def get_history(self) -> List[Dict[str, Any]]:
        """Return current conversation history."""
        return self.history

    def clear(self):
        """Clear all history."""
        self.history = []

    def save_to_file(self):
        """Save history to local JSON file (optional persistence)."""
        try:
            path = os.path.join(Settings.LOGS_DIR, f"memory_{self.session_id}.json")
            with open(path, "w") as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")

    def load_from_file(self):
        """Load history from local JSON file."""
        try:
            path = os.path.join(Settings.LOGS_DIR, f"memory_{self.session_id}.json")
            if os.path.exists(path):
                with open(path, "r") as f:
                    self.history = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load memory: {e}")
