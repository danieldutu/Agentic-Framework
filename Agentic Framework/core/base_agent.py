"""Base agent class for the AI Agent Framework."""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from .agent_types import (
    AgentCapability,
    AgentConfig,
    AgentInput,
    AgentMessage,
    AgentOutput,
    AgentStatus,
)
from .exceptions import AgentError, ProcessingError, TimeoutError


class BaseAgent(ABC):
    """Abstract base class for all agents in the framework."""

    def __init__(self, config: AgentConfig) -> None:
        """Initialize the base agent.

        Args:
            config: Agent configuration
        """
        self.config = config
        self.agent_id = config.agent_id
        self.agent_type = config.agent_type
        self.capabilities = config.capabilities
        self.status = AgentStatus.IDLE
        self._task_queue: asyncio.Queue[AgentInput] = asyncio.Queue()
        self._running_tasks: Dict[UUID, asyncio.Task[AgentOutput]] = {}
        self._communication_handler: Optional[Any] = None
        self._memory_handler: Optional[Any] = None
        self._metrics: Dict[str, Any] = {
            "tasks_processed": 0,
            "tasks_failed": 0,
            "total_processing_time": 0.0,
            "last_activity": datetime.utcnow(),
        }

        # Configure logging
        self.logger = logger.bind(agent_id=self.agent_id, agent_type=self.agent_type)

        # Initialize components
        self._setup_components()

    def _setup_components(self) -> None:
        """Setup agent components like memory and communication handlers."""
        # Will be implemented when handlers are injected

    @abstractmethod
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process input data and return output.

        Args:
            input_data: The input to process

        Returns:
            The processed output

        Raises:
            ProcessingError: If processing fails
        """

    @abstractmethod
    def get_capabilities(self) -> List[AgentCapability]:
        """Get the capabilities of this agent.

        Returns:
            List of agent capabilities
        """

    async def start(self) -> None:
        """Start the agent and begin processing tasks."""
        self.logger.info("Starting agent")
        self.status = AgentStatus.IDLE

        # Start the task processing loop
        asyncio.create_task(self._process_task_queue())

    async def stop(self) -> None:
        """Stop the agent and cleanup resources."""
        self.logger.info("Stopping agent")
        self.status = AgentStatus.SHUTDOWN

        # Cancel all running tasks
        for task in self._running_tasks.values():
            task.cancel()

        # Wait for tasks to complete or timeout
        if self._running_tasks:
            await asyncio.wait(self._running_tasks.values(), timeout=30.0)

    async def submit_task(self, input_data: AgentInput) -> UUID:
        """Submit a task for processing.

        Args:
            input_data: The input to process

        Returns:
            Task ID for tracking
        """
        # Create a future to track when the task is picked up
        future = asyncio.Future()
        self._pending_tasks = getattr(self, '_pending_tasks', {})
        self._pending_tasks[input_data.id] = future
        
        await self._task_queue.put(input_data)
        self.logger.debug(f"Task submitted: {input_data.id}")
        return input_data.id

    async def get_task_result(
        self, task_id: UUID, timeout: float = 30.0
    ) -> AgentOutput:
        """Get the result of a submitted task.

        Args:
            task_id: The task ID to get results for
            timeout: Maximum time to wait for result

        Returns:
            The task output

        Raises:
            TimeoutError: If task doesn't complete within timeout
        """
        # Wait for task to be picked up from queue if it's still pending
        pending_tasks = getattr(self, '_pending_tasks', {})
        if task_id in pending_tasks:
            try:
                # Wait for the task to be picked up (with a small timeout)
                await asyncio.wait_for(pending_tasks[task_id], timeout=min(5.0, timeout))
            except asyncio.TimeoutError:
                raise AgentError(f"Task {task_id} was not picked up from queue", agent_id=self.agent_id)
        
        if task_id not in self._running_tasks:
            raise AgentError(f"Task {task_id} not found", agent_id=self.agent_id)

        try:
            return await asyncio.wait_for(self._running_tasks[task_id], timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"Task {task_id} timed out after {timeout} seconds",
                agent_id=self.agent_id,
                timeout_duration=timeout,
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    async def communicate(self, target_agent: str, message: AgentMessage) -> None:
        """Send a message to another agent.

        Args:
            target_agent: The ID of the target agent
            message: The message to send

        Raises:
            CommunicationError: If communication fails
        """
        if not self._communication_handler:
            raise AgentError(
                "Communication handler not initialized", agent_id=self.agent_id
            )

        self.status = AgentStatus.COMMUNICATING
        try:
            await self._communication_handler.send_message(target_agent, message)
            self.logger.debug(f"Message sent to {target_agent}: {message.id}")
        finally:
            self.status = AgentStatus.IDLE

    def get_status(self) -> AgentStatus:
        """Get the current status of the agent.

        Returns:
            Current agent status
        """
        return self.status

    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics.

        Returns:
            Dictionary of metrics
        """
        return self._metrics.copy()

    def set_communication_handler(self, handler: Any) -> None:
        """Set the communication handler for this agent.

        Args:
            handler: The communication handler instance
        """
        self._communication_handler = handler
        self.logger.debug("Communication handler set")

    def set_memory_handler(self, handler: Any) -> None:
        """Set the memory handler for this agent.

        Args:
            handler: The memory handler instance
        """
        self._memory_handler = handler
        self.logger.debug("Memory handler set")

    async def _process_task_queue(self) -> None:
        """Process tasks from the queue continuously."""
        while self.status != AgentStatus.SHUTDOWN:
            try:
                # Wait for a task with timeout to allow shutdown
                input_data = await asyncio.wait_for(self._task_queue.get(), timeout=1.0)

                # Create a task to process the input
                task = asyncio.create_task(
                    self._process_with_error_handling(input_data)
                )
                self._running_tasks[input_data.id] = task
                
                # Mark task as picked up
                pending_tasks = getattr(self, '_pending_tasks', {})
                if input_data.id in pending_tasks:
                    pending_tasks[input_data.id].set_result(True)
                    del pending_tasks[input_data.id]

                # Clean up completed tasks
                await self._cleanup_completed_tasks()

            except asyncio.TimeoutError:
                # No task received, continue loop
                continue
            except Exception as e:
                self.logger.error(f"Error in task queue processing: {e}")

    async def _process_with_error_handling(self, input_data: AgentInput) -> AgentOutput:
        """Process input with comprehensive error handling.

        Args:
            input_data: The input to process

        Returns:
            The processed output
        """
        start_time = datetime.utcnow()
        self.status = AgentStatus.PROCESSING

        try:
            self.logger.debug(f"Processing task: {input_data.id}")
            output = await self.process(input_data)

            # Update metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._metrics["tasks_processed"] += 1
            self._metrics["total_processing_time"] += processing_time
            self._metrics["last_activity"] = datetime.utcnow()

            output.processing_time = processing_time
            output.source_agent = self.agent_id

            self.logger.debug(
                f"Task completed: {input_data.id} in {processing_time:.2f}s"
            )
            return output

        except Exception as e:
            self._metrics["tasks_failed"] += 1
            self.logger.error(f"Task failed: {input_data.id} - {e}")

            # Create error output
            error_output = AgentOutput(
                content={"error": str(e), "type": type(e).__name__},
                source_agent=self.agent_id,
                confidence=0.0,
                processing_time=(datetime.utcnow() - start_time).total_seconds(),
                metadata={"error": True, "original_input_id": str(input_data.id)},
            )

            raise ProcessingError(
                f"Failed to process task {input_data.id}: {e}",
                agent_id=self.agent_id,
                input_id=str(input_data.id),
            )
        finally:
            self.status = AgentStatus.IDLE

    async def _cleanup_completed_tasks(self) -> None:
        """Clean up completed tasks from the running tasks dictionary."""
        completed_tasks = [
            task_id for task_id, task in self._running_tasks.items() if task.done()
        ]

        for task_id in completed_tasks:
            del self._running_tasks[task_id]

    async def handle_message(self, message: AgentMessage) -> None:
        """Handle incoming messages from other agents.
        
        Args:
            message: The incoming message
            
        Note:
            Subclasses should override this method to handle specific message types
        """
        self.logger.debug(f"Received message: {message.message_type} from {message.from_agent}")
        # Default implementation - subclasses can override
        pass

    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(id={self.agent_id}, status={self.status})"
