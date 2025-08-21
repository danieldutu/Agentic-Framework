"""Message broker implementations for agent communication."""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional

import redis.asyncio as redis
from loguru import logger

from core.agent_types import AgentMessage
from core.exceptions import CommunicationError


class MessageBroker(ABC):
    """Abstract base class for message brokers."""

    @abstractmethod
    async def publish(self, channel: str, message: AgentMessage) -> None:
        """Publish a message to a channel.

        Args:
            channel: Channel name
            message: Message to publish
        """

    @abstractmethod
    async def subscribe(
        self, channel: str, handler: Callable[[AgentMessage], None]
    ) -> None:
        """Subscribe to a channel.

        Args:
            channel: Channel name
            handler: Message handler function
        """

    @abstractmethod
    async def unsubscribe(self, channel: str) -> None:
        """Unsubscribe from a channel.

        Args:
            channel: Channel name
        """

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the message broker."""


class RedisMessageBroker(MessageBroker):
    """Redis-based message broker implementation."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0") -> None:
        """Initialize Redis message broker.

        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self.subscribers: Dict[str, Callable[[AgentMessage], None]] = {}
        self.listen_task: Optional[asyncio.Task] = None
        self.logger = logger.bind(component="redis_broker")

    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self.redis_client = redis.from_url(
                self.redis_url, encoding="utf-8", decode_responses=True
            )

            # Test connection
            await self.redis_client.ping()

            self.pubsub = self.redis_client.pubsub()
            self.logger.info("Connected to Redis message broker")

        except Exception as e:
            raise CommunicationError(
                f"Failed to connect to Redis: {e}", error_code="redis_connection_failed"
            )

    async def publish(self, channel: str, message: AgentMessage) -> None:
        """Publish a message to a Redis channel.

        Args:
            channel: Channel name
            message: Message to publish
        """
        if not self.redis_client:
            await self.connect()

        try:
            # Serialize message to JSON
            message_data = message.model_dump_json()

            # Publish to Redis
            await self.redis_client.publish(channel, message_data)

            self.logger.debug(f"Published message {message.id} to channel {channel}")

        except Exception as e:
            raise CommunicationError(
                f"Failed to publish message to channel {channel}: {e}",
                error_code="publish_failed",
            )

    async def subscribe(
        self, channel: str, handler: Callable[[AgentMessage], None]
    ) -> None:
        """Subscribe to a Redis channel.

        Args:
            channel: Channel name
            handler: Message handler function
        """
        if not self.pubsub:
            await self.connect()

        try:
            # Subscribe to channel
            await self.pubsub.subscribe(channel)

            # Store handler
            self.subscribers[channel] = handler

            # Start listening if not already started
            if not self.listen_task:
                self.listen_task = asyncio.create_task(self._listen_for_messages())

            self.logger.info(f"Subscribed to channel {channel}")

        except Exception as e:
            raise CommunicationError(
                f"Failed to subscribe to channel {channel}: {e}",
                error_code="subscribe_failed",
            )

    async def unsubscribe(self, channel: str) -> None:
        """Unsubscribe from a Redis channel.

        Args:
            channel: Channel name
        """
        if not self.pubsub:
            return

        try:
            # Unsubscribe from channel
            await self.pubsub.unsubscribe(channel)

            # Remove handler
            if channel in self.subscribers:
                del self.subscribers[channel]

            # Stop listening if no more subscriptions
            if not self.subscribers and self.listen_task:
                self.listen_task.cancel()
                self.listen_task = None

            self.logger.info(f"Unsubscribed from channel {channel}")

        except Exception as e:
            self.logger.error(f"Failed to unsubscribe from channel {channel}: {e}")

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        try:
            # Cancel listening task
            if self.listen_task:
                self.listen_task.cancel()
                self.listen_task = None

            # Close pubsub
            if self.pubsub:
                await self.pubsub.close()
                self.pubsub = None

            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
                self.redis_client = None

            # Clear subscribers
            self.subscribers.clear()

            self.logger.info("Disconnected from Redis message broker")

        except Exception as e:
            self.logger.error(f"Error during Redis disconnect: {e}")

    async def _listen_for_messages(self) -> None:
        """Listen for messages from Redis channels."""
        if not self.pubsub:
            return

        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    channel = message["channel"]
                    data = message["data"]

                    # Get handler for this channel
                    handler = self.subscribers.get(channel)
                    if not handler:
                        continue

                    try:
                        # Parse message
                        agent_message = AgentMessage.model_validate_json(data)

                        # Call handler
                        await asyncio.create_task(
                            self._safe_handle_message(handler, agent_message)
                        )

                    except Exception as e:
                        self.logger.error(
                            f"Failed to process message from channel {channel}: {e}"
                        )

        except asyncio.CancelledError:
            self.logger.debug("Message listening task cancelled")
        except Exception as e:
            self.logger.error(f"Error in message listening loop: {e}")

    async def _safe_handle_message(
        self, handler: Callable[[AgentMessage], None], message: AgentMessage
    ) -> None:
        """Safely handle a message with error catching.

        Args:
            handler: Message handler function
            message: Message to handle
        """
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(message)
            else:
                handler(message)
        except Exception as e:
            self.logger.error(f"Message handler failed: {e}")

    async def get_channel_info(self, channel: str) -> Dict[str, Any]:
        """Get information about a channel.

        Args:
            channel: Channel name

        Returns:
            Channel information
        """
        if not self.redis_client:
            return {"subscribed": False, "subscribers": 0}

        try:
            # Get number of subscribers for the channel
            pubsub_channels = await self.redis_client.pubsub_channels(pattern=channel)
            subscribers_count = await self.redis_client.pubsub_numsub(channel)

            return {
                "subscribed": channel in self.subscribers,
                "exists": channel in pubsub_channels,
                "subscribers": subscribers_count[0][1] if subscribers_count else 0,
            }

        except Exception as e:
            self.logger.error(f"Failed to get channel info for {channel}: {e}")
            return {"subscribed": False, "subscribers": 0}

    def get_status(self) -> Dict[str, Any]:
        """Get broker status information.

        Returns:
            Status information
        """
        return {
            "connected": self.redis_client is not None,
            "subscribed_channels": list(self.subscribers.keys()),
            "listening": self.listen_task is not None and not self.listen_task.done(),
        }
