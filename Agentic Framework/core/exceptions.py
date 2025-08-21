"""Custom exceptions for the AI Agent Framework."""

from typing import Any, Dict, Optional


class AgentError(Exception):
    """Base exception for all agent-related errors."""

    def __init__(
        self,
        message: str,
        agent_id: Optional[str] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.agent_id = agent_id
        self.error_code = error_code
        self.context = context or {}

    def __str__(self) -> str:
        parts = [self.message]
        if self.agent_id:
            parts.append(f"Agent: {self.agent_id}")
        if self.error_code:
            parts.append(f"Code: {self.error_code}")
        return " | ".join(parts)


class CommunicationError(AgentError):
    """Exception raised for communication-related errors."""

    def __init__(
        self,
        message: str,
        from_agent: Optional[str] = None,
        to_agent: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.from_agent = from_agent
        self.to_agent = to_agent


class ConfigurationError(AgentError):
    """Exception raised for configuration-related errors."""

    def __init__(
        self, message: str, config_key: Optional[str] = None, **kwargs: Any
    ) -> None:
        super().__init__(message, **kwargs)
        self.config_key = config_key


class MemoryError(AgentError):
    """Exception raised for memory-related errors."""

    def __init__(
        self, message: str, memory_type: Optional[str] = None, **kwargs: Any
    ) -> None:
        super().__init__(message, **kwargs)
        self.memory_type = memory_type


class ProcessingError(AgentError):
    """Exception raised for processing-related errors."""

    def __init__(
        self, message: str, input_id: Optional[str] = None, **kwargs: Any
    ) -> None:
        super().__init__(message, **kwargs)
        self.input_id = input_id


class TimeoutError(AgentError):
    """Exception raised when operations timeout."""

    def __init__(
        self, message: str, timeout_duration: Optional[float] = None, **kwargs: Any
    ) -> None:
        super().__init__(message, **kwargs)
        self.timeout_duration = timeout_duration


class AuthenticationError(AgentError):
    """Exception raised for authentication-related errors."""

    def __init__(
        self, message: str, service: Optional[str] = None, **kwargs: Any
    ) -> None:
        super().__init__(message, **kwargs)
        self.service = service


class ValidationError(AgentError):
    """Exception raised for validation-related errors."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.field = field
        self.value = value
