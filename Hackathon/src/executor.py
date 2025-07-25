"""
The Executor is responsible for running individual tasks from the plan.
"""
from typing import Dict, Any

class Executor:
    """Executes tasks using either a tool or the LLM."""
    def __init__(self, llm_client, tools: Dict[str, Any]):
        self.llm_client = llm_client
        self.tools = tools

    def execute(self, task: Dict[str, Any]) -> str:
        """
        Executes a single task by routing it to a tool or the LLM.

        Args:
            task: The task to execute, containing a description.

        Returns:
            The result of the task's execution.
        """
        task_description = task["task"]
        
        # This simple routing logic checks if a tool's name is mentioned in the task.
        # A more advanced executor could use an LLM call to determine the best tool
        # and extract its arguments more reliably.
        for tool_name, tool_function in self.tools.items():
            if tool_name in task_description.lower():
                # A real implementation would need robust argument extraction.
                # For now, we pass the task description as a placeholder argument.
                return tool_function(task_description)
        
        # If no specific tool is found, use the LLM to "execute" the task.
        return self.llm_client.generate_text(task_description)
