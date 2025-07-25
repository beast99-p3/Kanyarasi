"""
The Planner breaks down a high-level goal into a sequence of actionable sub-tasks.
"""
from typing import List, Dict, Any

class Planner:
    """Uses an LLM to generate a step-by-step plan."""
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def plan(self, goal: str) -> List[Dict[str, Any]]:
        """
        Generates a structured plan to achieve the user's goal.

        Args:
            goal: The user's high-level objective.

        Returns:
            A list of dictionaries, where each dictionary represents a sub-task.
        """
        # This simple prompt-based planning is effective for many cases.
        # More complex scenarios might benefit from a ReAct or Tree-of-Thoughts pattern.
        prompt = (
            f"Create a concise, step-by-step plan to achieve this goal: '{goal}'. "
            "Each step must be a clear, actionable instruction. "
            "Return the plan as a numbered list, with each step on a new line."
        )
        
        response = self.llm_client.generate_text(prompt)
        
        # Parse the numbered list response into a list of task dictionaries
        tasks = [
            {"task": line.strip().split('. ', 1)[-1], "completed": False}
            for line in response.split('\n')
            if line.strip()
        ]
        
        return tasks
