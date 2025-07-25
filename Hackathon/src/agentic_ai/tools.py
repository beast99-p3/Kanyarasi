"""
Tool Registry and Base Tool Classes
Framework for creating and managing agent tools.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
import asyncio
import logging
from dataclasses import dataclass


@dataclass
class ToolDefinition:
    """Definition of a tool function."""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Callable


class BaseTool(ABC):
    """Abstract base class for agent tools."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"tool.{name}")
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get the tool schema for function calling."""
        pass


class GoogleCloudStorageTool(BaseTool):
    """Tool for Google Cloud Storage operations."""
    
    def __init__(self, project_id: str, bucket_name: str):
        super().__init__("gcs_operations", "Google Cloud Storage file operations")
        self.project_id = project_id
        self.bucket_name = bucket_name
    
    async def execute(self, operation: str, file_path: str, content: str = None) -> Any:
        """Execute GCS operation."""
        try:
            from google.cloud import storage
            
            client = storage.Client(project=self.project_id)
            bucket = client.bucket(self.bucket_name)
            
            if operation == "upload":
                blob = bucket.blob(file_path)
                blob.upload_from_string(content)
                return f"Uploaded file to gs://{self.bucket_name}/{file_path}"
            
            elif operation == "download":
                blob = bucket.blob(file_path)
                content = blob.download_as_text()
                return content
            
            elif operation == "list":
                blobs = list(bucket.list_blobs(prefix=file_path))
                return [blob.name for blob in blobs]
            
            else:
                return f"Unknown operation: {operation}"
                
        except Exception as e:
            self.logger.error(f"GCS operation failed: {e}")
            raise
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["upload", "download", "list"],
                            "description": "The operation to perform"
                        },
                        "file_path": {
                            "type": "string",
                            "description": "The file path in the bucket"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to upload (for upload operation)"
                        }
                    },
                    "required": ["operation", "file_path"]
                }
            }
        }


class WebSearchTool(BaseTool):
    """Tool for web search operations."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("web_search", "Search the web for information")
        self.api_key = api_key
    
    async def execute(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """Execute web search."""
        try:
            # Placeholder for actual web search implementation
            # You can integrate with Google Search API, Serper, etc.
            return [
                {
                    "title": f"Sample result for: {query}",
                    "url": "https://example.com",
                    "snippet": f"This is a sample search result for the query '{query}'"
                }
            ]
        except Exception as e:
            self.logger.error(f"Web search failed: {e}")
            raise
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            }
        }


class DatabaseTool(BaseTool):
    """Tool for database operations using Google Cloud Firestore."""
    
    def __init__(self, project_id: str, collection_name: str = "agent_data"):
        super().__init__("database_operations", "Database read/write operations")
        self.project_id = project_id
        self.collection_name = collection_name
    
    async def execute(self, operation: str, doc_id: str, data: Dict = None) -> Any:
        """Execute database operation."""
        try:
            from google.cloud import firestore
            
            db = firestore.Client(project=self.project_id)
            collection = db.collection(self.collection_name)
            
            if operation == "create" or operation == "update":
                doc_ref = collection.document(doc_id)
                doc_ref.set(data, merge=(operation == "update"))
                return f"Document {doc_id} {operation}d successfully"
            
            elif operation == "read":
                doc_ref = collection.document(doc_id)
                doc = doc_ref.get()
                return doc.to_dict() if doc.exists else None
            
            elif operation == "delete":
                doc_ref = collection.document(doc_id)
                doc_ref.delete()
                return f"Document {doc_id} deleted successfully"
            
            elif operation == "list":
                docs = collection.stream()
                return [{doc.id: doc.to_dict()} for doc in docs]
            
            else:
                return f"Unknown operation: {operation}"
                
        except Exception as e:
            self.logger.error(f"Database operation failed: {e}")
            raise
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["create", "read", "update", "delete", "list"],
                            "description": "The database operation to perform"
                        },
                        "doc_id": {
                            "type": "string",
                            "description": "The document ID"
                        },
                        "data": {
                            "type": "object",
                            "description": "Data for create/update operations"
                        }
                    },
                    "required": ["operation", "doc_id"]
                }
            }
        }


class ToolRegistry:
    """Registry for managing agent tools."""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.logger = logging.getLogger("tool_registry")
    
    def register_tool(self, tool: BaseTool):
        """Register a tool."""
        self.tools[tool.name] = tool
        self.logger.info(f"Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self.tools.keys())
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get schemas for all registered tools."""
        return [tool.get_schema() for tool in self.tools.values()]
    
    async def execute_tool(self, name: str, **kwargs) -> Any:
        """Execute a tool by name."""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")
        
        return await tool.execute(**kwargs)
    
    def create_default_tools(self, project_id: str, bucket_name: str = None) -> None:
        """Create and register default tools for Google Cloud."""
        if bucket_name:
            gcs_tool = GoogleCloudStorageTool(project_id, bucket_name)
            self.register_tool(gcs_tool)
        
        db_tool = DatabaseTool(project_id)
        self.register_tool(db_tool)
        
        search_tool = WebSearchTool()
        self.register_tool(search_tool)
