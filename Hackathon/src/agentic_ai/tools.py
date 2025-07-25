from typing import List, Dict, Any

class AgentTools:
    def __init__(self):
        self.tools = {
            "search": self.search,
            "calculate": self.calculate,
            "summarize": self.summarize
        }
    
    def list_tools(self) -> List[str]:
        return list(self.tools.keys())
    
    def execute_step(self, step: str, llm) -> str:
        for tool_name, tool_fn in self.tools.items():
            if tool_name.lower() in step.lower():
                return tool_fn(step, llm)
        return self.default_action(step, llm)
    
    def search(self, query: str, llm) -> str:
        prompt = f"Simulate web search for: {query}"
        return llm.generate_text(prompt)
    
    def calculate(self, expression: str, llm) -> str:
        prompt = f"Solve this calculation: {expression}"
        return llm.generate_text(prompt)
    
    def summarize(self, text: str, llm) -> str:
        prompt = f"Summarize this text: {text}"
        return llm.generate_text(prompt)
    
    def default_action(self, step: str, llm) -> str:
        return llm.generate_text(step)
