"""
Executor
Logic for calling LLMs or tools.
"""

from typing import Dict, Any

class Executor:
    def __init__(self, llm_client, tools: Dict[str, Any]):
        self.llm_client = llm_client
        self.tools = tools

    def execute(self, task: Dict[str, Any]) -> str:
        """
        Executes a single task.

        Args:
            task: The task to execute.

        Returns:
            The result of the task.
        """
        task_description = task["task"]
        
        # Simple logic to decide whether to use a tool or the LLM
        # A more advanced executor would have more sophisticated routing.
        tool_to_use = None
        for tool_name in self.tools.keys():
            if tool_name in task_description.lower():
                tool_to_use = tool_name
                break

        if tool_to_use:
            # Extract arguments for the tool (this is a simplified example)
            # A real implementation would need more robust argument parsing.
            return self.tools[tool_to_use]()
        else:
            return self.llm_client.generate_text(task_description)
