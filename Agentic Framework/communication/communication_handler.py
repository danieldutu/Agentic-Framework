"""Communication handler for managing agent-to-agent messaging."""

import asyncio
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID

from loguru import logger

from core.agent_types import AgentMessage
from core.exceptions import CommunicationError
from .message_broker import MessageBroker, RedisMessageBroker


class CommunicationHandler:
    """Handles communication between agents using message brokers."""

    def __init__(self, broker: Optional[MessageBroker] = None) -> None:
        """Initialize communication handler.

        Args:
            broker: Message broker instance (defaults to Redis)
        """
        self.broker = broker or RedisMessageBroker()
        self.agent_handlers: Dict[str, Callable[[AgentMessage], None]] = {}
        self.message_history: List[AgentMessage] = []
        self.pending_responses: Dict[UUID, asyncio.Future] = {}
        self.logger = logger.bind(component="communication_handler")

    async def initialize(self) -> None:
        """Initialize the communication handler."""
        try:
            if hasattr(self.broker, "connect"):
                await self.broker.connect()
            self.logger.info("Communication handler initialized")
        except Exception as e:
            raise CommunicationError(
                f"Failed to initialize communication handler: {e}",
                error_code="initialization_failed",
            )

    async def register_agent(
        self, agent_id: str, handler: Callable[[AgentMessage], None]
    ) -> None:
        """Register an agent for receiving messages.

        Args:
            agent_id: Unique agent identifier
            handler: Function to handle incoming messages
        """
        try:
            # Store the handler
            self.agent_handlers[agent_id] = handler

            # Subscribe to agent's channel
            channel = self._get_agent_channel(agent_id)
            await self.broker.subscribe(channel, self._handle_message)

            self.logger.info(f"Registered agent {agent_id}")

        except Exception as e:
            raise CommunicationError(
                f"Failed to register agent {agent_id}: {e}",
                error_code="agent_registration_failed",
            )

    async def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from receiving messages.

        Args:
            agent_id: Agent identifier to unregister
        """
        try:
            # Unsubscribe from agent's channel
            channel = self._get_agent_channel(agent_id)
            await self.broker.unsubscribe(channel)

            # Remove handler
            if agent_id in self.agent_handlers:
                del self.agent_handlers[agent_id]

            self.logger.info(f"Unregistered agent {agent_id}")

        except Exception as e:
            self.logger.error(f"Failed to unregister agent {agent_id}: {e}")

    async def send_message(self, target_agent: str, message: AgentMessage) -> None:
        """Send a message to a target agent.

        Args:
            target_agent: ID of the target agent
            message: Message to send
        """
        try:
            # Set the target agent in the message
            message.to_agent = target_agent

            # Get the target channel
            channel = self._get_agent_channel(target_agent)

            # Publish the message
            await self.broker.publish(channel, message)

            # Store in history
            self.message_history.append(message)

            # Limit history size
            if len(self.message_history) > 1000:
                self.message_history = self.message_history[-500:]

            self.logger.debug(
                f"Sent message {message.id} from {message.from_agent} to {target_agent}"
            )

        except Exception as e:
            raise CommunicationError(
                f"Failed to send message to {target_agent}: {e}",
                from_agent=message.from_agent,
                to_agent=target_agent,
                error_code="send_failed",
            )

    async def send_request(
        self, target_agent: str, message: AgentMessage, timeout: float = 30.0
    ) -> AgentMessage:
        """Send a request message and wait for response.

        Args:
            target_agent: ID of the target agent
            message: Request message to send
            timeout: Maximum time to wait for response

        Returns:
            Response message

        Raises:
            CommunicationError: If request fails or times out
        """
        try:
            # Create a future for the response
            response_future: asyncio.Future[AgentMessage] = asyncio.Future()
            self.pending_responses[message.id] = response_future

            # Set message type to request
            message.message_type = "request"

            # Send the message
            await self.send_message(target_agent, message)

            # Wait for response
            try:
                response = await asyncio.wait_for(response_future, timeout=timeout)
                return response
            except asyncio.TimeoutError:
                raise CommunicationError(
                    f"Request to {target_agent} timed out after {timeout}s",
                    from_agent=message.from_agent,
                    to_agent=target_agent,
                    error_code="request_timeout",
                )
            finally:
                # Clean up
                if message.id in self.pending_responses:
                    del self.pending_responses[message.id]

        except Exception as e:
            if isinstance(e, CommunicationError):
                raise
            raise CommunicationError(
                f"Failed to send request to {target_agent}: {e}",
                from_agent=message.from_agent,
                to_agent=target_agent,
                error_code="request_failed",
            )

    async def send_response(
        self, request_message: AgentMessage, response_message: AgentMessage
    ) -> None:
        """Send a response to a request message.

        Args:
            request_message: Original request message
            response_message: Response message to send
        """
        try:
            # Set response properties
            response_message.message_type = "response"
            response_message.correlation_id = request_message.id
            response_message.to_agent = request_message.from_agent

            # Send the response
            await self.send_message(request_message.from_agent, response_message)

            self.logger.debug(
                f"Sent response {response_message.id} for request {request_message.id}"
            )

        except Exception as e:
            raise CommunicationError(
                f"Failed to send response: {e}",
                from_agent=response_message.from_agent,
                to_agent=request_message.from_agent,
                error_code="response_failed",
            )

    async def broadcast_message(
        self, message: AgentMessage, target_agents: Optional[List[str]] = None
    ) -> None:
        """Broadcast a message to multiple agents.

        Args:
            message: Message to broadcast
            target_agents: List of target agent IDs (None for all registered agents)
        """
        if target_agents is None:
            target_agents = list(self.agent_handlers.keys())

        # Send to each target agent
        tasks = []
        for agent_id in target_agents:
            if agent_id != message.from_agent:  # Don't send to sender
                task = self.send_message(agent_id, message)
                tasks.append(task)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        self.logger.debug(f"Broadcasted message {message.id} to {len(tasks)} agents")

    async def _handle_message(self, message: AgentMessage) -> None:
        """Internal message handler for incoming messages.

        Args:
            message: Incoming message
        """
        try:
            # Check if this is a response to a pending request
            if (
                message.message_type == "response"
                and message.correlation_id
                and message.correlation_id in self.pending_responses
            ):

                # Complete the pending request
                future = self.pending_responses[message.correlation_id]
                if not future.done():
                    future.set_result(message)
                return

            # Route to agent handler
            target_agent = message.to_agent
            if target_agent and target_agent in self.agent_handlers:
                handler = self.agent_handlers[target_agent]

                # Call handler safely
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(message)
                    else:
                        handler(message)
                except Exception as e:
                    self.logger.error(f"Agent handler failed for {target_agent}: {e}")
            else:
                self.logger.warning(f"No handler found for agent {target_agent}")

        except Exception as e:
            self.logger.error(f"Failed to handle message {message.id}: {e}")

    def _get_agent_channel(self, agent_id: str) -> str:
        """Get the channel name for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Channel name
        """
        return f"agent:{agent_id}"

    async def get_message_history(
        self, agent_id: Optional[str] = None, limit: int = 100
    ) -> List[AgentMessage]:
        """Get message history.

        Args:
            agent_id: Filter by agent ID (None for all)
            limit: Maximum number of messages

        Returns:
            List of messages
        """
        messages = self.message_history

        if agent_id:
            messages = [
                msg
                for msg in messages
                if msg.from_agent == agent_id or msg.to_agent == agent_id
            ]

        return messages[-limit:]

    async def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get status information for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Status information
        """
        channel = self._get_agent_channel(agent_id)

        # Get channel info from broker
        if hasattr(self.broker, "get_channel_info"):
            channel_info = await self.broker.get_channel_info(channel)
        else:
            channel_info = {}

        return {
            "agent_id": agent_id,
            "registered": agent_id in self.agent_handlers,
            "channel": channel,
            "channel_info": channel_info,
        }

    async def shutdown(self) -> None:
        """Shutdown the communication handler."""
        try:
            # Cancel pending responses
            for future in self.pending_responses.values():
                if not future.done():
                    future.cancel()
            self.pending_responses.clear()

            # Unregister all agents
            agent_ids = list(self.agent_handlers.keys())
            for agent_id in agent_ids:
                await self.unregister_agent(agent_id)

            # Disconnect broker
            await self.broker.disconnect()

            self.logger.info("Communication handler shutdown complete")

        except Exception as e:
            self.logger.error(f"Error during communication handler shutdown: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get overall status of the communication handler.

        Returns:
            Status information
        """
        broker_status = {}
        if hasattr(self.broker, "get_status"):
            broker_status = self.broker.get_status()

        return {
            "registered_agents": list(self.agent_handlers.keys()),
            "message_history_size": len(self.message_history),
            "pending_responses": len(self.pending_responses),
            "broker_status": broker_status,
        }
