from typing import Dict, Any

class Executor:
    def __init__(self, llm_client, tools: Dict[str, Any]):
        self.llm_client = llm_client
        self.tools = tools
    def execute(self, task: Dict[str, Any]) -> str:
        desc = task["task"]
        for name, fn in self.tools.items():
            if name in desc.lower():
                return fn(desc)
        return self.llm_client.generate_text(desc)
