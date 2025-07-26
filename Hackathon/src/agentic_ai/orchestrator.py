from typing import Dict, Any
from .agent import Agent
from .llm_client import GeminiClient

class Orchestrator:
    def __init__(self, api_key: str):
        self.llm = GeminiClient(api_key)
        self.agent = Agent(self.llm)
    
    async def process_request(self, goal: str) -> Dict[str, Any]:
        try:
            result = await self.agent.process_goal(goal)
            return {
                "status": "success",
                "data": result
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "data": None
            }
    
    def get_agent_state(self) -> Dict[str, Any]:
        return {
            "recent_memory": self.agent.memory.get_recent_interactions(),
            "available_tools": self.agent.tools.list_tools()
        }
