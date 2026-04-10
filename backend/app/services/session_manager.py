"""
Session Manager - Manages execution sessions
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger


class SessionManager:
    """Manages execution sessions and history."""

    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._history: List[Dict[str, Any]] = []
        self._max_history = 100

    def create_session(self) -> str:
        """Create a new session and return its ID."""
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = {
            "id": session_id,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "messages": [],
        }
        logger.debug(f"Created session: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID."""
        return self._sessions.get(session_id)

    def update_session(self, session_id: str, data: Dict[str, Any]):
        """Update session data."""
        if session_id in self._sessions:
            self._sessions[session_id].update(data)

    def close_session(self, session_id: str):
        """Close and clean up a session."""
        if session_id in self._sessions:
            self._sessions[session_id]["status"] = "closed"
            self._sessions[session_id]["closed_at"] = datetime.now().isoformat()
            logger.debug(f"Closed session: {session_id}")

    def add_to_history(
        self,
        instruction: str,
        action: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        execution_time: Optional[float] = None,
    ):
        """Add an execution record to history."""
        record = {
            "id": str(uuid.uuid4()),
            "instruction": instruction,
            "parsed_action": action,
            "status": status,
            "created_at": datetime.now().isoformat(),
            "execution_time": execution_time,
            "result": result,
        }
        self._history.insert(0, record)

        # Keep history bounded
        if len(self._history) > self._max_history:
            self._history = self._history[:self._max_history]

        logger.debug(f"Added history record: {record['id']}")

    def get_history(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get execution history."""
        return self._history[offset:offset + limit]

    def clear_history(self):
        """Clear all history records."""
        self._history.clear()
        logger.info("History cleared")

    def delete_history_item(self, item_id: str) -> bool:
        """Delete a specific history item."""
        for i, item in enumerate(self._history):
            if item["id"] == item_id:
                self._history.pop(i)
                return True
        return False


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
