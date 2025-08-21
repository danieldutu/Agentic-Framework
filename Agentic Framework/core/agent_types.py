"""Core data types and models for the AI Agent Framework."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    """Agent status enumeration."""

    IDLE = "idle"
    PROCESSING = "processing"
    COMMUNICATING = "communicating"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class AgentCapability(str, Enum):
    """Agent capability enumeration."""

    RESEARCH = "research"
    SYNTHESIS = "synthesis"
    ANALYSIS = "analysis"
    COMMUNICATION = "communication"
    MEMORY = "memory"
    REASONING = "reasoning"


class AgentInput(BaseModel):
    """Input data structure for agent processing."""

    id: UUID = Field(
        default_factory=uuid4, description="Unique identifier for the input"
    )
    content: Union[str, Dict[str, Any]] = Field(..., description="The input content")
    source_agent: Optional[str] = Field(
        None, description="ID of the agent that sent this input"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp of input creation"
    )
    priority: int = Field(
        default=5, description="Priority level (1-10, 10 being highest)"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)}


class AgentOutput(BaseModel):
    """Output data structure from agent processing."""

    id: UUID = Field(
        default_factory=uuid4, description="Unique identifier for the output"
    )
    content: Union[str, Dict[str, Any]] = Field(..., description="The output content")
    source_agent: str = Field(
        ..., description="ID of the agent that produced this output"
    )
    target_agent: Optional[str] = Field(
        None, description="ID of the target agent (if any)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp of output creation"
    )
    confidence: float = Field(default=1.0, description="Confidence score (0.0-1.0)")
    processing_time: Optional[float] = Field(
        None, description="Time taken to process in seconds"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)}


class AgentMessage(BaseModel):
    """Message structure for inter-agent communication."""

    id: UUID = Field(
        default_factory=uuid4, description="Unique identifier for the message"
    )
    from_agent: str = Field(..., description="ID of the sending agent")
    to_agent: str = Field(..., description="ID of the receiving agent")
    message_type: str = Field(
        ..., description="Type of message (request, response, notification)"
    )
    payload: Union[AgentInput, AgentOutput, Dict[str, Any]] = Field(
        ..., description="Message payload"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp of message creation"
    )
    correlation_id: Optional[UUID] = Field(
        None, description="ID to correlate request/response pairs"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)}


class AgentConfig(BaseModel):
    """Configuration model for agents."""

    agent_id: str = Field(..., description="Unique identifier for the agent")
    agent_type: str = Field(
        ..., description="Type of agent (research, synthesis, etc.)"
    )
    capabilities: List[AgentCapability] = Field(
        default_factory=list, description="Agent capabilities"
    )
    max_concurrent_tasks: int = Field(default=5, description="Maximum concurrent tasks")
    timeout_seconds: int = Field(default=30, description="Task timeout in seconds")
    retry_attempts: int = Field(default=3, description="Number of retry attempts")
    memory_enabled: bool = Field(default=True, description="Whether memory is enabled")
    logging_level: str = Field(default="INFO", description="Logging level")
    custom_config: Dict[str, Any] = Field(
        default_factory=dict, description="Custom configuration"
    )


class MemoryEntry(BaseModel):
    """Memory entry structure."""

    id: UUID = Field(
        default_factory=uuid4, description="Unique identifier for the memory entry"
    )
    agent_id: str = Field(..., description="ID of the agent that created this memory")
    content: Union[str, Dict[str, Any]] = Field(..., description="Memory content")
    memory_type: str = Field(
        ..., description="Type of memory (short_term, long_term, episodic)"
    )
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp of memory creation"
    )
    importance: float = Field(default=0.5, description="Importance score (0.0-1.0)")
    accessed_count: int = Field(default=0, description="Number of times accessed")
    last_accessed: Optional[datetime] = Field(None, description="Last access timestamp")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)}


class SystemMetrics(BaseModel):
    """System metrics for monitoring."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    active_agents: int = Field(default=0)
    total_messages: int = Field(default=0)
    average_response_time: float = Field(default=0.0)
    error_rate: float = Field(default=0.0)
    memory_usage: Dict[str, float] = Field(default_factory=dict)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
