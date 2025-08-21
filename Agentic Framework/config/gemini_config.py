"""Gemini AI configuration and client setup."""

import asyncio
from typing import Any, Dict, List, Optional

import google.generativeai as genai
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from core.exceptions import AuthenticationError, ConfigurationError
from .settings import Settings


class GeminiConfig:
    """Gemini AI configuration and client wrapper."""

    def __init__(self, settings: Settings) -> None:
        """Initialize Gemini configuration.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.api_key = settings.gemini_api_key
        self.model_name = settings.gemini_model
        self.temperature = settings.gemini_temperature
        self.max_tokens = settings.gemini_max_tokens
        self.timeout = settings.gemini_timeout

        # Configure the Gemini client
        self._configure_client()

        # Initialize the model
        self.model: Optional[genai.GenerativeModel] = None
        self._initialize_model()

    def _configure_client(self) -> None:
        """Configure the Gemini client with API key."""
        try:
            genai.configure(api_key=self.api_key)
            logger.info("Gemini client configured successfully")
        except Exception as e:
            raise AuthenticationError(
                f"Failed to configure Gemini client: {e}", service="gemini"
            )

    def _initialize_model(self) -> None:
        """Initialize the Gemini model."""
        try:
            # Configure generation settings
            generation_config = genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
                candidate_count=1,
            )

            # Configure safety settings (optional)
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
            ]

            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=generation_config,
                safety_settings=safety_settings,
            )

            logger.info(f"Gemini model '{self.model_name}' initialized successfully")

        except Exception as e:
            raise ConfigurationError(
                f"Failed to initialize Gemini model: {e}", config_key="gemini_model"
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    async def generate_content(
        self, prompt: str, system_instruction: Optional[str] = None, **kwargs: Any
    ) -> str:
        """Generate content using Gemini model.

        Args:
            prompt: The input prompt
            system_instruction: Optional system instruction
            **kwargs: Additional generation parameters

        Returns:
            Generated content as string

        Raises:
            ConfigurationError: If model is not initialized
            Exception: If generation fails
        """
        if not self.model:
            raise ConfigurationError(
                "Gemini model not initialized", config_key="gemini_model"
            )

        try:
            # Prepare the full prompt
            if system_instruction:
                full_prompt = f"System: {system_instruction}\n\nUser: {prompt}"
            else:
                full_prompt = prompt

            # Generate content asynchronously
            response = await asyncio.to_thread(
                self.model.generate_content, full_prompt, **kwargs
            )

            if response.text:
                logger.debug(f"Generated {len(response.text)} characters")
                return response.text
            else:
                logger.warning("Empty response from Gemini")
                return ""

        except Exception as e:
            logger.error(f"Failed to generate content: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    async def generate_content_stream(
        self, prompt: str, system_instruction: Optional[str] = None, **kwargs: Any
    ) -> List[str]:
        """Generate content using streaming.

        Args:
            prompt: The input prompt
            system_instruction: Optional system instruction
            **kwargs: Additional generation parameters

        Returns:
            List of content chunks

        Raises:
            ConfigurationError: If model is not initialized
        """
        if not self.model:
            raise ConfigurationError(
                "Gemini model not initialized", config_key="gemini_model"
            )

        try:
            # Prepare the full prompt
            if system_instruction:
                full_prompt = f"System: {system_instruction}\n\nUser: {prompt}"
            else:
                full_prompt = prompt

            # Generate content with streaming
            response = await asyncio.to_thread(
                self.model.generate_content, full_prompt, stream=True, **kwargs
            )

            chunks = []
            for chunk in response:
                if chunk.text:
                    chunks.append(chunk.text)

            logger.debug(f"Generated {len(chunks)} chunks")
            return chunks

        except Exception as e:
            logger.error(f"Failed to generate streaming content: {e}")
            raise

    async def count_tokens(self, text: str) -> int:
        """Count tokens in the given text.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        if not self.model:
            raise ConfigurationError(
                "Gemini model not initialized", config_key="gemini_model"
            )

        try:
            response = await asyncio.to_thread(self.model.count_tokens, text)
            return response.total_tokens
        except Exception as e:
            logger.error(f"Failed to count tokens: {e}")
            return 0

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model.

        Returns:
            Model information dictionary
        """
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
            "initialized": self.model is not None,
        }

    def update_config(
        self,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Update model configuration.

        Args:
            temperature: New temperature value
            max_tokens: New max tokens value
            **kwargs: Additional configuration parameters
        """
        if temperature is not None:
            self.temperature = temperature
        if max_tokens is not None:
            self.max_tokens = max_tokens

        # Re-initialize model with new config
        self._initialize_model()
        logger.info("Gemini configuration updated")
