"""Memory handler for agent memory management."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

import redis.asyncio as redis
from loguru import logger

from core.agent_types import MemoryEntry
from core.exceptions import MemoryError


class MemoryHandler(ABC):
    """Abstract base class for memory handlers."""

    @abstractmethod
    async def store(self, memory: MemoryEntry) -> None:
        """Store a memory entry.

        Args:
            memory: Memory entry to store
        """

    @abstractmethod
    async def retrieve(self, memory_id: UUID) -> Optional[MemoryEntry]:
        """Retrieve a memory entry by ID.

        Args:
            memory_id: Memory entry ID

        Returns:
            Memory entry if found, None otherwise
        """

    @abstractmethod
    async def search(
        self,
        agent_id: str,
        query: Optional[str] = None,
        memory_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[MemoryEntry]:
        """Search for memory entries.

        Args:
            agent_id: Agent ID to search for
            query: Text query (optional)
            memory_type: Memory type filter (optional)
            tags: Tags to filter by (optional)
            limit: Maximum number of results

        Returns:
            List of matching memory entries
        """

    @abstractmethod
    async def delete(self, memory_id: UUID) -> bool:
        """Delete a memory entry.

        Args:
            memory_id: Memory entry ID

        Returns:
            True if deleted, False if not found
        """

    @abstractmethod
    async def cleanup_expired(self) -> int:
        """Clean up expired memory entries.

        Returns:
            Number of entries cleaned up
        """


class RedisMemoryHandler(MemoryHandler):
    """Redis-based memory handler implementation."""

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        ttl_seconds: int = 3600,
        max_entries_per_agent: int = 1000,
    ) -> None:
        """Initialize Redis memory handler.

        Args:
            redis_url: Redis connection URL
            ttl_seconds: Time-to-live for memory entries in seconds
            max_entries_per_agent: Maximum memory entries per agent
        """
        self.redis_url = redis_url
        self.ttl_seconds = ttl_seconds
        self.max_entries_per_agent = max_entries_per_agent
        self.redis_client: Optional[redis.Redis] = None
        self.logger = logger.bind(component="redis_memory")

    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self.redis_client = redis.from_url(
                self.redis_url, encoding="utf-8", decode_responses=True
            )

            # Test connection
            await self.redis_client.ping()
            self.logger.info("Connected to Redis memory handler")

        except Exception as e:
            raise MemoryError(
                f"Failed to connect to Redis: {e}", memory_type="redis_connection"
            )

    async def store(self, memory: MemoryEntry) -> None:
        """Store a memory entry in Redis.

        Args:
            memory: Memory entry to store
        """
        if not self.redis_client:
            await self.connect()

        try:
            # Update access information
            memory.accessed_count = 0
            memory.last_accessed = None

            # Serialize memory entry
            memory_data = memory.model_dump_json()

            # Store in Redis with TTL
            key = self._get_memory_key(memory.id)
            await self.redis_client.setex(key, self.ttl_seconds, memory_data)

            # Add to agent's memory index
            agent_key = self._get_agent_memories_key(memory.agent_id)
            await self.redis_client.zadd(
                agent_key, {str(memory.id): memory.timestamp.timestamp()}
            )

            # Add to type index
            type_key = self._get_type_memories_key(memory.memory_type)
            await self.redis_client.zadd(
                type_key, {str(memory.id): memory.timestamp.timestamp()}
            )

            # Add to tag indices
            for tag in memory.tags:
                tag_key = self._get_tag_memories_key(tag)
                await self.redis_client.zadd(
                    tag_key, {str(memory.id): memory.timestamp.timestamp()}
                )

            # Enforce memory limits per agent
            await self._enforce_memory_limits(memory.agent_id)

            self.logger.debug(f"Stored memory {memory.id} for agent {memory.agent_id}")

        except Exception as e:
            raise MemoryError(
                f"Failed to store memory {memory.id}: {e}", memory_type="store_failed"
            )

    async def retrieve(self, memory_id: UUID) -> Optional[MemoryEntry]:
        """Retrieve a memory entry by ID from Redis.

        Args:
            memory_id: Memory entry ID

        Returns:
            Memory entry if found, None otherwise
        """
        if not self.redis_client:
            await self.connect()

        try:
            key = self._get_memory_key(memory_id)
            memory_data = await self.redis_client.get(key)

            if not memory_data:
                return None

            # Parse memory entry
            memory = MemoryEntry.model_validate_json(memory_data)

            # Update access information
            memory.accessed_count += 1
            memory.last_accessed = datetime.utcnow()

            # Update in Redis
            updated_data = memory.model_dump_json()
            await self.redis_client.setex(key, self.ttl_seconds, updated_data)

            self.logger.debug(f"Retrieved memory {memory_id}")
            return memory

        except Exception as e:
            self.logger.error(f"Failed to retrieve memory {memory_id}: {e}")
            return None

    async def search(
        self,
        agent_id: str,
        query: Optional[str] = None,
        memory_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[MemoryEntry]:
        """Search for memory entries in Redis.

        Args:
            agent_id: Agent ID to search for
            query: Text query (optional)
            memory_type: Memory type filter (optional)
            tags: Tags to filter by (optional)
            limit: Maximum number of results

        Returns:
            List of matching memory entries
        """
        if not self.redis_client:
            await self.connect()

        try:
            # Start with agent's memories
            agent_key = self._get_agent_memories_key(agent_id)
            memory_ids = await self.redis_client.zrevrange(agent_key, 0, -1)

            # Apply filters
            filtered_ids = []
            for memory_id_str in memory_ids:
                memory_id = UUID(memory_id_str)
                memory = await self.retrieve(memory_id)

                if not memory:
                    continue

                # Filter by memory type
                if memory_type and memory.memory_type != memory_type:
                    continue

                # Filter by tags
                if tags and not any(tag in memory.tags for tag in tags):
                    continue

                # Filter by query (simple text search)
                if query and query.lower() not in str(memory.content).lower():
                    continue

                filtered_ids.append(memory)

                if len(filtered_ids) >= limit:
                    break

            # Sort by importance and recency
            filtered_ids.sort(
                key=lambda m: (m.importance, m.timestamp.timestamp()), reverse=True
            )

            self.logger.debug(
                f"Found {len(filtered_ids)} memories for agent {agent_id}"
            )
            return filtered_ids[:limit]

        except Exception as e:
            self.logger.error(f"Failed to search memories for agent {agent_id}: {e}")
            return []

    async def delete(self, memory_id: UUID) -> bool:
        """Delete a memory entry from Redis.

        Args:
            memory_id: Memory entry ID

        Returns:
            True if deleted, False if not found
        """
        if not self.redis_client:
            await self.connect()

        try:
            # First get the memory to access its metadata
            memory = await self.retrieve(memory_id)
            if not memory:
                return False

            # Delete from main storage
            key = self._get_memory_key(memory_id)
            deleted = await self.redis_client.delete(key)

            if deleted:
                # Remove from indices
                agent_key = self._get_agent_memories_key(memory.agent_id)
                await self.redis_client.zrem(agent_key, str(memory_id))

                type_key = self._get_type_memories_key(memory.memory_type)
                await self.redis_client.zrem(type_key, str(memory_id))

                for tag in memory.tags:
                    tag_key = self._get_tag_memories_key(tag)
                    await self.redis_client.zrem(tag_key, str(memory_id))

                self.logger.debug(f"Deleted memory {memory_id}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False

    async def cleanup_expired(self) -> int:
        """Clean up expired memory entries.

        Returns:
            Number of entries cleaned up
        """
        if not self.redis_client:
            await self.connect()

        try:
            # Redis automatically handles TTL, but we can clean up indices
            cleaned_count = 0

            # Get all agent keys and clean up broken references
            agent_pattern = self._get_agent_memories_key("*")
            agent_keys = await self.redis_client.keys(agent_pattern)

            for agent_key in agent_keys:
                memory_ids = await self.redis_client.zrange(agent_key, 0, -1)

                for memory_id_str in memory_ids:
                    memory_key = self._get_memory_key(UUID(memory_id_str))
                    exists = await self.redis_client.exists(memory_key)

                    if not exists:
                        # Remove from agent index
                        await self.redis_client.zrem(agent_key, memory_id_str)
                        cleaned_count += 1

            if cleaned_count > 0:
                self.logger.info(
                    f"Cleaned up {cleaned_count} expired memory references"
                )

            return cleaned_count

        except Exception as e:
            self.logger.error(f"Failed to cleanup expired memories: {e}")
            return 0

    async def _enforce_memory_limits(self, agent_id: str) -> None:
        """Enforce memory limits per agent.

        Args:
            agent_id: Agent ID to enforce limits for
        """
        try:
            agent_key = self._get_agent_memories_key(agent_id)

            # Get current count
            count = await self.redis_client.zcard(agent_key)

            if count > self.max_entries_per_agent:
                # Remove oldest entries
                excess = count - self.max_entries_per_agent
                oldest_ids = await self.redis_client.zrange(agent_key, 0, excess - 1)

                for memory_id_str in oldest_ids:
                    memory_id = UUID(memory_id_str)
                    await self.delete(memory_id)

                self.logger.debug(
                    f"Removed {len(oldest_ids)} old memories for agent {agent_id}"
                )

        except Exception as e:
            self.logger.error(f"Failed to enforce memory limits for {agent_id}: {e}")

    def _get_memory_key(self, memory_id: UUID) -> str:
        """Get Redis key for a memory entry.

        Args:
            memory_id: Memory entry ID

        Returns:
            Redis key
        """
        return f"memory:{memory_id}"

    def _get_agent_memories_key(self, agent_id: str) -> str:
        """Get Redis key for agent's memory index.

        Args:
            agent_id: Agent ID

        Returns:
            Redis key
        """
        return f"agent_memories:{agent_id}"

    def _get_type_memories_key(self, memory_type: str) -> str:
        """Get Redis key for memory type index.

        Args:
            memory_type: Memory type

        Returns:
            Redis key
        """
        return f"type_memories:{memory_type}"

    def _get_tag_memories_key(self, tag: str) -> str:
        """Get Redis key for tag index.

        Args:
            tag: Tag name

        Returns:
            Redis key
        """
        return f"tag_memories:{tag}"

    async def get_agent_memory_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get memory statistics for an agent.

        Args:
            agent_id: Agent ID

        Returns:
            Memory statistics
        """
        if not self.redis_client:
            await self.connect()

        try:
            agent_key = self._get_agent_memories_key(agent_id)

            # Get total count
            total_count = await self.redis_client.zcard(agent_key)

            # Get memory types distribution
            memory_ids = await self.redis_client.zrange(agent_key, 0, -1)
            type_counts: Dict[str, int] = {}

            for memory_id_str in memory_ids:
                memory = await self.retrieve(UUID(memory_id_str))
                if memory:
                    type_counts[memory.memory_type] = (
                        type_counts.get(memory.memory_type, 0) + 1
                    )

            return {
                "agent_id": agent_id,
                "total_memories": total_count,
                "memory_types": type_counts,
                "max_entries": self.max_entries_per_agent,
                "ttl_seconds": self.ttl_seconds,
            }

        except Exception as e:
            self.logger.error(f"Failed to get memory stats for {agent_id}: {e}")
            return {
                "agent_id": agent_id,
                "total_memories": 0,
                "memory_types": {},
                "max_entries": self.max_entries_per_agent,
                "ttl_seconds": self.ttl_seconds,
            }

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        try:
            if self.redis_client:
                await self.redis_client.close()
                self.redis_client = None
            self.logger.info("Disconnected from Redis memory handler")
        except Exception as e:
            self.logger.error(f"Error during Redis disconnect: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get memory handler status.

        Returns:
            Status information
        """
        return {
            "connected": self.redis_client is not None,
            "ttl_seconds": self.ttl_seconds,
            "max_entries_per_agent": self.max_entries_per_agent,
        }
