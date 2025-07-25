"""
Agent Orchestrator
Manages multiple agents and coordinates their interactions.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json

from .agent import BaseAgent, AgentConfig
from .memory import MemoryManager
from .tools import ToolRegistry


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Represents a task to be executed by an agent."""
    id: str
    description: str
    agent_id: str
    priority: int = 5  # 1-10, higher is more priority
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: str = None
    created_at: float = None
    started_at: float = None
    completed_at: float = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            import time
            self.created_at = time.time()
        if self.metadata is None:
            self.metadata = {}


class AgentOrchestrator:
    """Orchestrates multiple AI agents and manages task distribution."""
    
    def __init__(self, project_id: str = None):
        self.project_id = project_id
        self.agents: Dict[str, BaseAgent] = {}
        self.tool_registry = ToolRegistry()
        self.memory_managers: Dict[str, MemoryManager] = {}
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[Task] = []
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.logger = logging.getLogger("orchestrator")
        
        # Event handlers
        self.task_completed_handlers: List[Callable] = []
        self.agent_error_handlers: List[Callable] = []
        
        # Configuration
        self.max_concurrent_tasks = 5
        self.is_running = False
    
    def register_agent(self, agent: BaseAgent) -> str:
        """Register an agent with the orchestrator."""
        agent_id = agent.config.name
        self.agents[agent_id] = agent
        
        # Create memory manager for the agent
        if self.project_id:
            memory_manager = MemoryManager(
                agent_id=agent_id,
                project_id=self.project_id
            )
            self.memory_managers[agent_id] = memory_manager
        
        self.logger.info(f"Registered agent: {agent_id}")
        return agent_id
    
    def register_tool_for_agent(self, agent_id: str, tool_name: str):
        """Register a tool for a specific agent."""
        if agent_id in self.agents:
            tool = self.tool_registry.get_tool(tool_name)
            if tool:
                self.agents[agent_id].add_tool(tool_name, tool.execute)
    
    async def create_task(self, 
                         description: str, 
                         agent_id: str,
                         priority: int = 5,
                         metadata: Dict[str, Any] = None) -> str:
        """Create a new task."""
        import uuid
        task_id = str(uuid.uuid4())
        
        if agent_id not in self.agents:
            raise ValueError(f"Agent '{agent_id}' not found")
        
        task = Task(
            id=task_id,
            description=description,
            agent_id=agent_id,
            priority=priority,
            metadata=metadata or {}
        )
        
        self.tasks[task_id] = task
        self.task_queue.append(task)
        
        # Sort queue by priority
        self.task_queue.sort(key=lambda t: t.priority, reverse=True)
        
        self.logger.info(f"Created task {task_id} for agent {agent_id}")
        return task_id
    
    async def execute_task(self, task_id: str) -> Any:
        """Execute a specific task."""
        if task_id not in self.tasks:
            raise ValueError(f"Task '{task_id}' not found")
        
        task = self.tasks[task_id]
        agent = self.agents[task.agent_id]
        
        try:
            import time
            task.status = TaskStatus.RUNNING
            task.started_at = time.time()
            
            # Get memory context for the agent
            context = {}
            if task.agent_id in self.memory_managers:
                memory_manager = self.memory_managers[task.agent_id]
                recent_memories = await memory_manager.get_conversation_history(10)
                context["conversation_history"] = [
                    {"content": m.content, "timestamp": m.timestamp.isoformat()}
                    for m in recent_memories
                ]
            
            # Execute the task
            result = await agent.process_message(task.description, context)
            
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = time.time()
            
            # Store result in memory
            if task.agent_id in self.memory_managers:
                memory_manager = self.memory_managers[task.agent_id]
                await memory_manager.store_memory(
                    content=f"Task: {task.description}\nResult: {result}",
                    memory_type="procedure",
                    importance=0.7,
                    tags=["task_result"],
                    metadata={"task_id": task_id}
                )
            
            # Notify handlers
            for handler in self.task_completed_handlers:
                try:
                    await handler(task)
                except Exception as e:
                    self.logger.error(f"Error in task completion handler: {e}")
            
            self.logger.info(f"Completed task {task_id}")
            return result
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = time.time()
            
            # Notify error handlers
            for handler in self.agent_error_handlers:
                try:
                    await handler(task, e)
                except Exception as handler_error:
                    self.logger.error(f"Error in error handler: {handler_error}")
            
            self.logger.error(f"Task {task_id} failed: {e}")
            raise
    
    async def start_orchestrator(self):
        """Start the orchestrator main loop."""
        self.is_running = True
        self.logger.info("Starting orchestrator")
        
        while self.is_running:
            try:
                # Check for new tasks to execute
                if (self.task_queue and 
                    len(self.running_tasks) < self.max_concurrent_tasks):
                    
                    task = self.task_queue.pop(0)
                    
                    # Start task execution
                    async_task = asyncio.create_task(self.execute_task(task.id))
                    self.running_tasks[task.id] = async_task
                
                # Check for completed tasks
                completed_tasks = []
                for task_id, async_task in self.running_tasks.items():
                    if async_task.done():
                        completed_tasks.append(task_id)
                
                # Clean up completed tasks
                for task_id in completed_tasks:
                    del self.running_tasks[task_id]
                
                # Short delay to prevent busy waiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error in orchestrator main loop: {e}")
                await asyncio.sleep(1)
    
    def stop_orchestrator(self):
        """Stop the orchestrator."""
        self.is_running = False
        
        # Cancel running tasks
        for async_task in self.running_tasks.values():
            async_task.cancel()
        
        self.logger.info("Stopped orchestrator")
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status of a task."""
        if task_id not in self.tasks:
            raise ValueError(f"Task '{task_id}' not found")
        
        task = self.tasks[task_id]
        return {
            "id": task.id,
            "description": task.description,
            "agent_id": task.agent_id,
            "status": task.status.value,
            "priority": task.priority,
            "result": task.result,
            "error": task.error,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "metadata": task.metadata
        }
    
    async def get_agent_stats(self) -> Dict[str, Any]:
        """Get statistics about all agents."""
        stats = {}
        
        for agent_id, agent in self.agents.items():
            agent_tasks = [t for t in self.tasks.values() if t.agent_id == agent_id]
            
            stats[agent_id] = {
                "total_tasks": len(agent_tasks),
                "completed_tasks": len([t for t in agent_tasks if t.status == TaskStatus.COMPLETED]),
                "failed_tasks": len([t for t in agent_tasks if t.status == TaskStatus.FAILED]),
                "pending_tasks": len([t for t in agent_tasks if t.status == TaskStatus.PENDING]),
                "running_tasks": len([t for t in agent_tasks if t.status == TaskStatus.RUNNING]),
                "tools_available": len(agent.config.tools)
            }
            
            # Add memory stats if available
            if agent_id in self.memory_managers:
                memory_stats = await self.memory_managers[agent_id].get_memory_stats()
                stats[agent_id]["memory_stats"] = memory_stats
        
        return stats
    
    async def broadcast_message(self, message: str, agent_ids: List[str] = None) -> Dict[str, Any]:
        """Send a message to multiple agents."""
        if agent_ids is None:
            agent_ids = list(self.agents.keys())
        
        results = {}
        tasks = []
        
        for agent_id in agent_ids:
            if agent_id in self.agents:
                task_id = await self.create_task(
                    description=message,
                    agent_id=agent_id,
                    priority=7
                )
                tasks.append((agent_id, task_id))
        
        # Wait for all tasks to complete
        for agent_id, task_id in tasks:
            try:
                result = await self.execute_task(task_id)
                results[agent_id] = result
            except Exception as e:
                results[agent_id] = f"Error: {str(e)}"
        
        return results
    
    def add_task_completion_handler(self, handler: Callable):
        """Add a handler for task completion events."""
        self.task_completed_handlers.append(handler)
    
    def add_agent_error_handler(self, handler: Callable):
        """Add a handler for agent error events."""
        self.agent_error_handlers.append(handler)
