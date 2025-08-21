"""AI Agent Framework - Agent module."""

from .agent_factory import AgentFactory
from .research_agent import ResearchAgent
from .synthesis_agent import SynthesisAgent

__all__ = ["AgentFactory", "ResearchAgent", "SynthesisAgent"]