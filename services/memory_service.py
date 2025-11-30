"""
Memory Service - Manage long-term memory across sessions.
"""
from typing import Dict, Any, List
from datetime import datetime
import uuid

class ResearchMemoryService:
    """Manages long-term memory across sessions."""
    
    def __init__(self, use_vertex: bool = False):
        self.use_vertex = use_vertex
        self._memories: Dict[str, List[Dict[str, Any]]] = {}
    
    async def store_memory(self, user_id: str, memory_data: Dict[str, Any]):
        """Store a memory for a user."""
        if user_id not in self._memories:
            self._memories[user_id] = []
        memory = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "data": memory_data
        }
        self._memories[user_id].append(memory)
    
    async def search_memories(self, user_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search memories for relevant information."""
        user_memories = self._memories.get(user_id, [])
        query_terms = set(query.lower().split())
        scored = []
        for memory in user_memories:
            text = str(memory["data"]).lower()
            score = sum(1 for term in query_terms if term in text) / len(query_terms) if query_terms else 0
            if score > 0:
                scored.append((score, memory))
        scored.sort(reverse=True, key=lambda x: x[0])
        return [m for _, m in scored[:limit]]
