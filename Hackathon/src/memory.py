"""
A simple memory system for the agent to log its actions.
"""
import datetime

class MemoryManager:
    """Handles the agent's memory by logging actions to a file."""
    
    def __init__(self, log_file: str = "agent_log.txt"):
        """Initializes the memory manager with a specified log file."""
        self.log_file = log_file
    
    def add_log(self, message: str):
        """
        Appends a timestamped message to the agent's log file.

        Args:
            message: The action or result to be logged.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
