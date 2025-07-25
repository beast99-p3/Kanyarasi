from typing import List, Dict, Any

class Planner:
    def __init__(self, llm_client):
        self.llm_client = llm_client
    def plan(self, goal: str) -> List[Dict[str, Any]]:
        prompt = (
            f"Create a concise, step-by-step plan to achieve this goal: '{goal}'. "
            "Each step must be a clear, actionable instruction. "
            "Return the plan as a numbered list, with each step on a new line."
        )
        response = self.llm_client.generate_text(prompt)
        return [
            {"task": line.strip().split('. ', 1)[-1], "completed": False}
            for line in response.split('\n') if line.strip()
        ]
