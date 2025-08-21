"""Agent factory for creating and managing agents."""

from typing import Any, Dict, Optional, Type

from loguru import logger

from core.agent_types import AgentCapability, AgentConfig
from core.base_agent import BaseAgent
from core.exceptions import ConfigurationError
from .research_agent import ResearchAgent
from .synthesis_agent import SynthesisAgent


class AgentFactory:
    """Factory class for creating and managing agents."""

    _agent_types: Dict[str, Type[BaseAgent]] = {
        "research": ResearchAgent,
        "synthesis": SynthesisAgent,
    }

    _default_configs: Dict[str, Dict[str, Any]] = {
        "research": {
            "max_search_results": 10,
            "search_timeout": 30,
            "research_depth": "medium",
            "enable_web_search": False,
        },
        "synthesis": {
            "synthesis_style": "comprehensive",
            "max_sources": 20,
            "analysis_depth": "deep",
        },
    }

    @classmethod
    def create_agent(
        cls,
        agent_type: str,
        agent_id: str,
        custom_config: Optional[Dict[str, Any]] = None,
    ) -> BaseAgent:
        """Create an agent of the specified type.

        Args:
            agent_type: Type of agent to create (research, synthesis)
            agent_id: Unique identifier for the agent
            custom_config: Custom configuration overrides

        Returns:
            Created agent instance

        Raises:
            ConfigurationError: If agent type is not supported
        """
        if agent_type not in cls._agent_types:
            raise ConfigurationError(
                f"Unsupported agent type: {agent_type}. "
                f"Supported types: {list(cls._agent_types.keys())}",
                config_key="agent_type",
            )

        # Get default config for this agent type
        default_config = cls._default_configs.get(agent_type, {})

        # Merge with custom config
        final_config = default_config.copy()
        if custom_config:
            final_config.update(custom_config)

        # Determine capabilities based on agent type
        capabilities = cls._get_agent_capabilities(agent_type)

        # Create agent configuration
        config = AgentConfig(
            agent_id=agent_id,
            agent_type=agent_type,
            capabilities=capabilities,
            custom_config=final_config,
        )

        # Create and return the agent
        agent_class = cls._agent_types[agent_type]
        agent = agent_class(config)

        logger.info(f"Created {agent_type} agent with ID: {agent_id}")
        return agent

    @classmethod
    def create_research_agent(
        cls,
        agent_id: str,
        research_depth: str = "medium",
        enable_web_search: bool = False,
        max_search_results: int = 10,
        **kwargs: Any,
    ) -> ResearchAgent:
        """Create a research agent with specific configuration.

        Args:
            agent_id: Unique identifier for the agent
            research_depth: Depth of research (light, medium, deep)
            enable_web_search: Whether to enable web search
            max_search_results: Maximum search results to process
            **kwargs: Additional configuration parameters

        Returns:
            Research agent instance
        """
        custom_config = {
            "research_depth": research_depth,
            "enable_web_search": enable_web_search,
            "max_search_results": max_search_results,
            **kwargs,
        }

        agent = cls.create_agent("research", agent_id, custom_config)
        return agent  # type: ignore

    @classmethod
    def create_synthesis_agent(
        cls,
        agent_id: str,
        synthesis_style: str = "comprehensive",
        analysis_depth: str = "deep",
        max_sources: int = 20,
        **kwargs: Any,
    ) -> SynthesisAgent:
        """Create a synthesis agent with specific configuration.

        Args:
            agent_id: Unique identifier for the agent
            synthesis_style: Style of synthesis (comprehensive, concise, academic, etc.)
            analysis_depth: Depth of analysis (light, medium, deep)
            max_sources: Maximum sources to analyze
            **kwargs: Additional configuration parameters

        Returns:
            Synthesis agent instance
        """
        custom_config = {
            "synthesis_style": synthesis_style,
            "analysis_depth": analysis_depth,
            "max_sources": max_sources,
            **kwargs,
        }

        agent = cls.create_agent("synthesis", agent_id, custom_config)
        return agent  # type: ignore

    @classmethod
    def create_agent_pair(
        cls,
        base_id: str = "agent",
        research_config: Optional[Dict[str, Any]] = None,
        synthesis_config: Optional[Dict[str, Any]] = None,
    ) -> tuple[ResearchAgent, SynthesisAgent]:
        """Create a complementary pair of research and synthesis agents.

        Args:
            base_id: Base identifier for the agents
            research_config: Configuration for research agent
            synthesis_config: Configuration for synthesis agent

        Returns:
            Tuple of (research_agent, synthesis_agent)
        """
        research_agent = cls.create_agent(
            "research", f"{base_id}_research", research_config
        )

        synthesis_agent = cls.create_agent(
            "synthesis", f"{base_id}_synthesis", synthesis_config
        )

        logger.info(f"Created agent pair: {base_id}_research and {base_id}_synthesis")
        return research_agent, synthesis_agent  # type: ignore

    @classmethod
    def _get_agent_capabilities(cls, agent_type: str) -> list[AgentCapability]:
        """Get default capabilities for an agent type.

        Args:
            agent_type: Type of agent

        Returns:
            List of capabilities
        """
        capability_map = {
            "research": [
                AgentCapability.RESEARCH,
                AgentCapability.ANALYSIS,
                AgentCapability.MEMORY,
                AgentCapability.COMMUNICATION,
            ],
            "synthesis": [
                AgentCapability.SYNTHESIS,
                AgentCapability.ANALYSIS,
                AgentCapability.REASONING,
                AgentCapability.MEMORY,
                AgentCapability.COMMUNICATION,
            ],
        }

        return capability_map.get(agent_type, [])

    @classmethod
    def get_supported_agent_types(cls) -> list[str]:
        """Get list of supported agent types.

        Returns:
            List of supported agent type names
        """
        return list(cls._agent_types.keys())

    @classmethod
    def get_agent_type_info(cls, agent_type: str) -> Dict[str, Any]:
        """Get information about a specific agent type.

        Args:
            agent_type: Type of agent to get info for

        Returns:
            Information about the agent type

        Raises:
            ConfigurationError: If agent type is not supported
        """
        if agent_type not in cls._agent_types:
            raise ConfigurationError(
                f"Unsupported agent type: {agent_type}", config_key="agent_type"
            )

        agent_class = cls._agent_types[agent_type]
        default_config = cls._default_configs.get(agent_type, {})
        capabilities = cls._get_agent_capabilities(agent_type)

        return {
            "agent_type": agent_type,
            "class_name": agent_class.__name__,
            "capabilities": [cap.value for cap in capabilities],
            "default_config": default_config,
            "description": agent_class.__doc__ or "No description available",
        }

    @classmethod
    def register_agent_type(
        cls,
        agent_type: str,
        agent_class: Type[BaseAgent],
        default_config: Optional[Dict[str, Any]] = None,
        capabilities: Optional[list[AgentCapability]] = None,
    ) -> None:
        """Register a new agent type.

        Args:
            agent_type: Name of the agent type
            agent_class: Agent class to register
            default_config: Default configuration for this agent type
            capabilities: Default capabilities for this agent type
        """
        cls._agent_types[agent_type] = agent_class

        if default_config:
            cls._default_configs[agent_type] = default_config

        logger.info(f"Registered new agent type: {agent_type}")

    @classmethod
    def validate_agent_config(cls, agent_type: str, config: Dict[str, Any]) -> bool:
        """Validate configuration for an agent type.

        Args:
            agent_type: Type of agent
            config: Configuration to validate

        Returns:
            True if valid, False otherwise
        """
        if agent_type not in cls._agent_types:
            return False

        # Basic validation - could be extended with specific rules
        required_fields = ["agent_id", "agent_type"]
        for field in required_fields:
            if field not in config:
                return False

        return True

    @classmethod
    def create_from_config(cls, config_dict: Dict[str, Any]) -> BaseAgent:
        """Create an agent from a configuration dictionary.

        Args:
            config_dict: Complete configuration dictionary

        Returns:
            Created agent instance

        Raises:
            ConfigurationError: If configuration is invalid
        """
        agent_type = config_dict.get("agent_type")
        agent_id = config_dict.get("agent_id")

        if not agent_type or not agent_id:
            raise ConfigurationError(
                "agent_type and agent_id are required in configuration",
                config_key="basic_config",
            )

        custom_config = config_dict.get("custom_config", {})

        return cls.create_agent(agent_type, agent_id, custom_config)
