"""
Memory Management for AI Agents
Handles conversation history, context, and long-term memory storage.
"""

from typing import Dict, List, Any, Optional
import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from google.cloud import firestore


@dataclass
class MemoryEntry:
    """A single memory entry."""
    id: str
    content: str
    timestamp: datetime
    memory_type: str  # "conversation", "fact", "procedure", "context"
    importance: float = 0.5  # 0.0 to 1.0
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}


class MemoryManager:
    """Manages agent memory storage and retrieval."""
    
    def __init__(self, 
                 agent_id: str, 
                 project_id: str = None,
                 use_cloud_storage: bool = True,
                 max_local_memories: int = 1000):
        self.agent_id = agent_id
        self.project_id = project_id
        self.use_cloud_storage = use_cloud_storage
        self.max_local_memories = max_local_memories
        self.logger = logging.getLogger(f"memory.{agent_id}")
        
        # Local memory storage
        self.memories: List[MemoryEntry] = []
        self.memory_index: Dict[str, MemoryEntry] = {}
        
        # Cloud storage client
        if use_cloud_storage and project_id:
            self.db = firestore.Client(project=project_id)
            self.collection_name = f"agent_memories_{agent_id}"
        else:
            self.db = None
    
    async def store_memory(self, 
                          content: str, 
                          memory_type: str = "conversation",
                          importance: float = 0.5,
                          tags: List[str] = None,
                          metadata: Dict[str, Any] = None) -> str:
        """Store a new memory entry."""
        memory_id = f"{self.agent_id}_{datetime.now().timestamp()}"
        
        memory = MemoryEntry(
            id=memory_id,
            content=content,
            timestamp=datetime.now(),
            memory_type=memory_type,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # Store locally
        self.memories.append(memory)
        self.memory_index[memory_id] = memory
        
        # Manage local memory size
        if len(self.memories) > self.max_local_memories:
            # Remove oldest, least important memories
            self.memories.sort(key=lambda m: (m.importance, m.timestamp))
            removed = self.memories.pop(0)
            del self.memory_index[removed.id]
        
        # Store in cloud if enabled
        if self.db:
            try:
                doc_ref = self.db.collection(self.collection_name).document(memory_id)
                memory_dict = asdict(memory)
                memory_dict['timestamp'] = memory.timestamp.isoformat()
                doc_ref.set(memory_dict)
            except Exception as e:
                self.logger.error(f"Failed to store memory in cloud: {e}")
        
        self.logger.debug(f"Stored memory: {memory_id}")
        return memory_id
    
    async def retrieve_memories(self, 
                               query: str = None,
                               memory_type: str = None,
                               tags: List[str] = None,
                               limit: int = 10,
                               min_importance: float = 0.0) -> List[MemoryEntry]:
        """Retrieve memories based on criteria."""
        memories = list(self.memories)
        
        # Load from cloud if needed
        if self.db and len(memories) < limit:
            try:
                cloud_memories = await self._load_from_cloud(limit * 2)
                # Merge with local memories, avoiding duplicates
                cloud_ids = {m.id for m in cloud_memories}
                local_ids = {m.id for m in memories}
                new_memories = [m for m in cloud_memories if m.id not in local_ids]
                memories.extend(new_memories)
            except Exception as e:
                self.logger.error(f"Failed to load memories from cloud: {e}")
        
        # Apply filters
        filtered_memories = []
        for memory in memories:
            # Filter by type
            if memory_type and memory.memory_type != memory_type:
                continue
            
            # Filter by importance
            if memory.importance < min_importance:
                continue
            
            # Filter by tags
            if tags and not any(tag in memory.tags for tag in tags):
                continue
            
            # Simple text search
            if query and query.lower() not in memory.content.lower():
                continue
            
            filtered_memories.append(memory)
        
        # Sort by relevance (importance + recency)
        filtered_memories.sort(
            key=lambda m: (m.importance, m.timestamp), 
            reverse=True
        )
        
        return filtered_memories[:limit]
    
    async def get_conversation_history(self, limit: int = 20) -> List[MemoryEntry]:
        """Get recent conversation history."""
        return await self.retrieve_memories(
            memory_type="conversation",
            limit=limit
        )
    
    async def get_context_memories(self, context_keys: List[str]) -> List[MemoryEntry]:
        """Get memories relevant to specific context."""
        return await self.retrieve_memories(
            tags=context_keys,
            memory_type="context",
            limit=50
        )
    
    async def update_memory_importance(self, memory_id: str, new_importance: float):
        """Update the importance score of a memory."""
        if memory_id in self.memory_index:
            self.memory_index[memory_id].importance = new_importance
            
            # Update in cloud storage
            if self.db:
                try:
                    doc_ref = self.db.collection(self.collection_name).document(memory_id)
                    doc_ref.update({"importance": new_importance})
                except Exception as e:
                    self.logger.error(f"Failed to update memory importance in cloud: {e}")
    
    async def delete_memory(self, memory_id: str):
        """Delete a memory entry."""
        if memory_id in self.memory_index:
            memory = self.memory_index[memory_id]
            self.memories.remove(memory)
            del self.memory_index[memory_id]
            
            # Delete from cloud storage
            if self.db:
                try:
                    doc_ref = self.db.collection(self.collection_name).document(memory_id)
                    doc_ref.delete()
                except Exception as e:
                    self.logger.error(f"Failed to delete memory from cloud: {e}")
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about stored memories."""
        total_memories = len(self.memories)
        if total_memories == 0:
            return {"total": 0}
        
        by_type = {}
        avg_importance = 0
        oldest_date = min(m.timestamp for m in self.memories)
        newest_date = max(m.timestamp for m in self.memories)
        
        for memory in self.memories:
            by_type[memory.memory_type] = by_type.get(memory.memory_type, 0) + 1
            avg_importance += memory.importance
        
        avg_importance /= total_memories
        
        return {
            "total": total_memories,
            "by_type": by_type,
            "average_importance": avg_importance,
            "date_range": {
                "oldest": oldest_date.isoformat(),
                "newest": newest_date.isoformat()
            }
        }
    
    async def _load_from_cloud(self, limit: int) -> List[MemoryEntry]:
        """Load memories from cloud storage."""
        if not self.db:
            return []
        
        try:
            docs = (self.db.collection(self.collection_name)
                   .order_by("timestamp", direction=firestore.Query.DESCENDING)
                   .limit(limit)
                   .stream())
            
            memories = []
            for doc in docs:
                data = doc.to_dict()
                data['timestamp'] = datetime.fromisoformat(data['timestamp'])
                memory = MemoryEntry(**data)
                memories.append(memory)
            
            return memories
        except Exception as e:
            self.logger.error(f"Failed to load memories from cloud: {e}")
            return []
    
    async def cleanup_old_memories(self, days_old: int = 30, min_importance: float = 0.3):
        """Clean up old, unimportant memories."""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        memories_to_remove = [
            memory for memory in self.memories
            if memory.timestamp < cutoff_date and memory.importance < min_importance
        ]
        
        for memory in memories_to_remove:
            await self.delete_memory(memory.id)
        
        self.logger.info(f"Cleaned up {len(memories_to_remove)} old memories")
