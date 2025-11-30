"""
State Manager - Manage shared state between agents.
"""
from typing import Dict, Any
from datetime import datetime

class ResearchStateManager:
    """Manages shared state between agents."""
    
    def __init__(self):
        self._state: Dict[str, Any] = {}
    
    def set_state(self, key: str, value: Any):
        """Set a state value."""
        self._state[key] = {"value": value, "updated_at": datetime.now().isoformat()}
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get a state value."""
        entry = self._state.get(key)
        return entry["value"] if entry else default
    
    def get_all_state(self) -> Dict[str, Any]:
        """Get all current state."""
        return {k: v["value"] for k, v in self._state.items()}
