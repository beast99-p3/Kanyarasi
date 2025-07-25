"""
Base Agent Implementation
Core classes for building autonomous AI agents.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Callable
import logging
from google.cloud import aiplatform
import openai


@dataclass
class AgentConfig:
    """Configuration for an AI agent."""
    name: str
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    system_prompt: str = ""
    tools: List[str] = None
    memory_enabled: bool = True
    google_cloud_project: Optional[str] = None
    
    def __post_init__(self):
        if self.tools is None:
            self.tools = []


class BaseAgent(ABC):
    """Abstract base class for AI agents."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.logger = logging.getLogger(f"agent.{config.name}")
        self.conversation_history = []
        self.tools_registry = {}
        
        # Initialize Google Cloud AI Platform if project specified
        if config.google_cloud_project:
            aiplatform.init(project=config.google_cloud_project)
    
    @abstractmethod
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process a message and return a response."""
        pass
    
    def add_tool(self, name: str, tool_func: Callable):
        """Add a tool function to the agent."""
        self.tools_registry[name] = tool_func
        if name not in self.config.tools:
            self.config.tools.append(name)
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the agent."""
        base_prompt = self.config.system_prompt or f"You are {self.config.name}, an AI agent."
        
        if self.config.tools:
            tools_info = f"\n\nAvailable tools: {', '.join(self.config.tools)}"
            base_prompt += tools_info
            
        return base_prompt
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a registered tool."""
        if tool_name not in self.tools_registry:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        try:
            return await self.tools_registry[tool_name](**kwargs)
        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {e}")
            raise


class OpenAIAgent(BaseAgent):
    """Agent implementation using OpenAI API."""
    
    def __init__(self, config: AgentConfig, api_key: Optional[str] = None):
        super().__init__(config)
        if api_key:
            openai.api_key = api_key
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process message using OpenAI API."""
        try:
            messages = [
                {"role": "system", "content": self.get_system_prompt()}
            ]
            
            # Add conversation history
            messages.extend(self.conversation_history[-10:])  # Keep last 10 messages
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            response = await openai.ChatCompletion.acreate(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            assistant_message = response.choices[0].message.content
            
            # Update conversation history
            if self.config.memory_enabled:
                self.conversation_history.extend([
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": assistant_message}
                ])
            
            return assistant_message
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return f"Sorry, I encountered an error: {str(e)}"


class VertexAIAgent(BaseAgent):
    """Agent implementation using Google Cloud Vertex AI."""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        if not config.google_cloud_project:
            raise ValueError("Google Cloud project must be specified for Vertex AI agent")
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process message using Vertex AI."""
        try:
            from vertexai.preview.generative_models import GenerativeModel
            
            model = GenerativeModel(self.config.model or "gemini-pro")
            
            # Prepare prompt with system context
            full_prompt = f"{self.get_system_prompt()}\n\nUser: {message}\nAssistant:"
            
            response = await model.generate_content_async(full_prompt)
            assistant_message = response.text
            
            # Update conversation history
            if self.config.memory_enabled:
                self.conversation_history.extend([
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": assistant_message}
                ])
            
            return assistant_message
            
        except Exception as e:
            self.logger.error(f"Error processing message with Vertex AI: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
