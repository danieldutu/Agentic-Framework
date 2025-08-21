"""Simplified memory store interface for easier usage."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from loguru import logger

from core.agent_types import MemoryEntry
from .memory_handler import MemoryHandler, RedisMemoryHandler


class MemoryStore:
    """Simplified memory store interface for agents."""

    def __init__(self, agent_id: str, handler: Optional[MemoryHandler] = None) -> None:
        """Initialize memory store for an agent.

        Args:
            agent_id: Agent identifier
            handler: Memory handler instance (defaults to Redis)
        """
        self.agent_id = agent_id
        self.handler = handler or RedisMemoryHandler()
        self.logger = logger.bind(component="memory_store", agent_id=agent_id)

    async def remember(
        self,
        content: Any,
        memory_type: str = "episodic",
        tags: Optional[List[str]] = None,
        importance: float = 0.5,
    ) -> UUID:
        """Store a memory entry.

        Args:
            content: Content to remember
            memory_type: Type of memory (episodic, semantic, procedural)
            tags: Tags for categorization
            importance: Importance score (0.0-1.0)

        Returns:
            Memory entry ID
        """
        memory = MemoryEntry(
            agent_id=self.agent_id,
            content=content,
            memory_type=memory_type,
            tags=tags or [],
            importance=importance,
        )

        await self.handler.store(memory)
        self.logger.debug(f"Stored memory {memory.id} of type {memory_type}")
        return memory.id

    async def recall(self, memory_id: UUID) -> Optional[Any]:
        """Recall a specific memory by ID.

        Args:
            memory_id: Memory entry ID

        Returns:
            Memory content if found, None otherwise
        """
        memory = await self.handler.retrieve(memory_id)
        if memory:
            self.logger.debug(f"Recalled memory {memory_id}")
            return memory.content
        return None

    async def search_memories(
        self,
        query: Optional[str] = None,
        memory_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search for memories.

        Args:
            query: Text query to search for
            memory_type: Filter by memory type
            tags: Filter by tags
            limit: Maximum number of results

        Returns:
            List of memory information dictionaries
        """
        memories = await self.handler.search(
            agent_id=self.agent_id,
            query=query,
            memory_type=memory_type,
            tags=tags,
            limit=limit,
        )

        results = []
        for memory in memories:
            results.append(
                {
                    "id": memory.id,
                    "content": memory.content,
                    "type": memory.memory_type,
                    "tags": memory.tags,
                    "importance": memory.importance,
                    "timestamp": memory.timestamp,
                    "accessed_count": memory.accessed_count,
                    "last_accessed": memory.last_accessed,
                }
            )

        self.logger.debug(f"Found {len(results)} memories for query: {query}")
        return results

    async def forget(self, memory_id: UUID) -> bool:
        """Forget a specific memory.

        Args:
            memory_id: Memory entry ID

        Returns:
            True if memory was deleted, False if not found
        """
        deleted = await self.handler.delete(memory_id)
        if deleted:
            self.logger.debug(f"Forgot memory {memory_id}")
        return deleted

    async def remember_conversation(
        self,
        conversation: List[Dict[str, str]],
        context: Optional[str] = None,
        importance: float = 0.7,
    ) -> UUID:
        """Remember a conversation.

        Args:
            conversation: List of message dictionaries with 'role' and 'content'
            context: Optional context about the conversation
            importance: Importance score

        Returns:
            Memory entry ID
        """
        content = {
            "type": "conversation",
            "messages": conversation,
            "context": context,
            "participant_count": len(
                set(msg.get("role", "unknown") for msg in conversation)
            ),
            "message_count": len(conversation),
        }

        tags = ["conversation"]
        if context:
            tags.append("contextual")

        return await self.remember(
            content=content, memory_type="episodic", tags=tags, importance=importance
        )

    async def remember_fact(
        self,
        fact: str,
        source: Optional[str] = None,
        confidence: float = 1.0,
        importance: float = 0.8,
    ) -> UUID:
        """Remember a factual piece of information.

        Args:
            fact: The factual information
            source: Source of the information
            confidence: Confidence in the fact (0.0-1.0)
            importance: Importance score

        Returns:
            Memory entry ID
        """
        content = {
            "type": "fact",
            "fact": fact,
            "source": source,
            "confidence": confidence,
        }

        tags = ["fact", "knowledge"]
        if source:
            tags.append("sourced")

        return await self.remember(
            content=content, memory_type="semantic", tags=tags, importance=importance
        )

    async def remember_procedure(
        self,
        procedure_name: str,
        steps: List[str],
        context: Optional[str] = None,
        importance: float = 0.9,
    ) -> UUID:
        """Remember a procedure or process.

        Args:
            procedure_name: Name of the procedure
            steps: List of steps in the procedure
            context: Optional context about when to use this procedure
            importance: Importance score

        Returns:
            Memory entry ID
        """
        content = {
            "type": "procedure",
            "name": procedure_name,
            "steps": steps,
            "context": context,
            "step_count": len(steps),
        }

        tags = ["procedure", "process", "how-to"]
        if context:
            tags.append("contextual")

        return await self.remember(
            content=content, memory_type="procedural", tags=tags, importance=importance
        )

    async def get_recent_memories(
        self, memory_type: Optional[str] = None, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get recent memories.

        Args:
            memory_type: Filter by memory type
            limit: Maximum number of results

        Returns:
            List of recent memory information
        """
        return await self.search_memories(memory_type=memory_type, limit=limit)

    async def get_important_memories(
        self, min_importance: float = 0.7, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get memories above a certain importance threshold.

        Args:
            min_importance: Minimum importance score
            limit: Maximum number of results

        Returns:
            List of important memories
        """
        all_memories = await self.search_memories(limit=1000)  # Get many memories

        # Filter by importance
        important_memories = [
            memory for memory in all_memories if memory["importance"] >= min_importance
        ]

        # Sort by importance (descending)
        important_memories.sort(key=lambda m: m["importance"], reverse=True)

        return important_memories[:limit]

    async def get_memories_by_tag(
        self, tag: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get memories with a specific tag.

        Args:
            tag: Tag to search for
            limit: Maximum number of results

        Returns:
            List of memories with the tag
        """
        return await self.search_memories(tags=[tag], limit=limit)

    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics for this agent.

        Returns:
            Memory statistics
        """
        if hasattr(self.handler, "get_agent_memory_stats"):
            return await self.handler.get_agent_memory_stats(self.agent_id)

        # Fallback: basic stats
        memories = await self.search_memories(limit=1000)
        type_counts: Dict[str, int] = {}

        for memory in memories:
            memory_type = memory["type"]
            type_counts[memory_type] = type_counts.get(memory_type, 0) + 1

        return {
            "agent_id": self.agent_id,
            "total_memories": len(memories),
            "memory_types": type_counts,
        }

    async def cleanup_old_memories(self) -> int:
        """Clean up old or expired memories.

        Returns:
            Number of memories cleaned up
        """
        if hasattr(self.handler, "cleanup_expired"):
            return await self.handler.cleanup_expired()
        return 0

    async def export_memories(self) -> List[Dict[str, Any]]:
        """Export all memories for this agent.

        Returns:
            List of all memory data
        """
        return await self.search_memories(limit=10000)  # Large limit to get all

    async def import_memories(self, memories_data: List[Dict[str, Any]]) -> int:
        """Import memories from data.

        Args:
            memories_data: List of memory data dictionaries

        Returns:
            Number of memories imported
        """
        imported_count = 0

        for memory_data in memories_data:
            try:
                await self.remember(
                    content=memory_data.get("content"),
                    memory_type=memory_data.get("type", "episodic"),
                    tags=memory_data.get("tags", []),
                    importance=memory_data.get("importance", 0.5),
                )
                imported_count += 1
            except Exception as e:
                self.logger.error(f"Failed to import memory: {e}")

        self.logger.info(f"Imported {imported_count} memories")
        return imported_count
