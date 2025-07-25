"""
Planner
Breaks down user goals into sub-tasks.
"""

from typing import List, Dict, Any

class Planner:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def plan(self, goal: str) -> List[Dict[str, Any]]:
        """
        Generates a plan to achieve the user's goal.

        Args:
            goal: The user's high-level goal.

        Returns:
            A list of sub-tasks.
        """
        # This is a simple implementation. A more advanced planner could use
        # a ReAct or BabyAGI pattern.
        prompt = f"Create a step-by-step plan to achieve this goal: {goal}. Each step should be a clear action. Return the plan as a numbered list."
        
        response = self.llm_client.generate_text(prompt)
        
        tasks = []
        for line in response.split('\n'):
            if line.strip():
                tasks.append({"task": line.strip(), "completed": False})
        
        return tasks
