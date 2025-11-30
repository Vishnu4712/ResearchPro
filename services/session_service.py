"""
Session Service - Manage research sessions and conversation threads.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

class ResearchSessionService:
    """
    Manages research sessions.
    
    Features:
    - Create and manage conversation sessions
    - Track research progress
    - Support pause/resume workflows
    - Session persistence (in-memory for demo, DB for production)
    """
    
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_session(
        self,
        user_id: str,
        initial_query: str
    ) -> Dict[str, Any]:
        """Create a new research session."""
        session_id = str(uuid.uuid4())
        
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "active",  # active, paused, completed, failed
            "initial_query": initial_query,
            "messages": [],
            "context": {},
            "results": None
        }
        
        self._sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a session by ID."""
        return self._sessions.get(session_id)
    
    def update_session(
        self,
        session_id: str,
        **updates
    ) -> Dict[str, Any]:
        """Update session data."""
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self._sessions[session_id]
        session.update(updates)
        session["updated_at"] = datetime.now().isoformat()
        
        return session
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ):
        """Add a message to the session."""
        session = self.get_session(session_id)
        if session:
            session["messages"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            session["updated_at"] = datetime.now().isoformat()
    
    def pause_session(self, session_id: str, reason: str):
        """Pause a session (for long-running operations)."""
        self.update_session(
            session_id,
            status="paused",
            pause_reason=reason
        )
    
    def resume_session(self, session_id: str):
        """Resume a paused session."""
        self.update_session(session_id, status="active")
    
    def complete_session(self, session_id: str, results: Dict[str, Any]):
        """Mark session as completed with results."""
        self.update_session(
            session_id,
            status="completed",
            results=results,
            completed_at=datetime.now().isoformat()
        )


# ============================================================================
# MEMORY SERVICE
# ============================================================================