"""
Agentic AI Package
A modular framework for building AI agents with planning, memory, and tool capabilities.
"""

from .agent import Agent
from .memory import AgentMemory
from .tools import AgentTools
from .orchestrator import Orchestrator

__version__ = "0.1.0"
__author__ = "Agentic AI Hackathon Team"

# Export main components for easy access
__all__ = [
    "Agent",
    "AgentMemory",
    "AgentTools",
    "Orchestrator"
]
