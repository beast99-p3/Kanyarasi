from typing import List, Dict, Any
from .memory import AgentMemory
from .tools import AgentTools

class Agent:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.memory = AgentMemory()
        self.tools = AgentTools()
        
    async def process_goal(self, goal: str) -> Dict[str, Any]:
        self.memory.add_interaction("user", goal)
        
        planning_prompt = f"""Given this goal: '{goal}'
        1. Analyze what information or tools you need
        2. Break it down into sequential steps
        3. Consider what could go wrong
        Create a plan using available tools: {self.tools.list_tools()}
        """
        
        plan = self.llm.generate_text(planning_prompt)
        self.memory.add_interaction("agent", f"Generated plan: {plan}")
        
        steps = [step.strip() for step in plan.split('\n') if step.strip()]
        results = []
        
        for step in steps:
            tool_result = await self.tools.execute_step(step, self.llm)
            results.append(tool_result)
            self.memory.add_interaction("tool", f"Step: {step}\nResult: {tool_result}")
        
        summary_prompt = f"Based on:\nGoal: {goal}\nResults: {results}\nProvide a clear, comprehensive answer."
        final_response = self.llm.generate_text(summary_prompt)
        self.memory.add_interaction("agent", final_response)
        
        return {
            "goal": goal,
            "plan": steps,
            "results": results,
            "response": final_response,
            "memory": self.memory.get_recent_interactions()
        }
