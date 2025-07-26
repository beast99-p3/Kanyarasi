from typing import List, Dict, Any
from datetime import datetime

class AgentMemory:
    def __init__(self, max_history: int = 100):
        self.interactions = []
        self.max_history = max_history
    
    def add_interaction(self, role: str, content: str) -> None:
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content
        }
        self.interactions.append(interaction)
        if len(self.interactions) > self.max_history:
            self.interactions.pop(0)
    
    def get_recent_interactions(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.interactions[-limit:]
    
    def search_memory(self, query: str) -> List[Dict[str, Any]]:
        return [
            interaction for interaction in self.interactions
            if query.lower() in interaction["content"].lower()
        ]
    
    def clear_memory(self) -> None:
        self.interactions = []
