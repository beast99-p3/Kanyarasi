"""
Memory Management for AI Agents
Handles conversation history and logging.
"""

import datetime

class MemoryManager:
    """Manages agent memory for logging."""
    
    def __init__(self, log_file: str = "agent_log.txt"):
        self.log_file = log_file
    
    def add_log(self, message: str):
        """
        Adds a message to the log file.

        Args:
            message: The message to log.
        """
        timestamp = datetime.datetime.now().isoformat()
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
