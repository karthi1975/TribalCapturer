"""
AI service client for code generation.

This module provides a wrapper around LiteLLM for communicating with AI services
like OpenAI GPT-4.
"""

import os
from typing import List, Dict
from litellm import completion


class AIServiceError(Exception):
    """Error communicating with AI service."""
    pass


class AIClient:
    """Client for interacting with AI services via LiteLLM."""

    def __init__(self, model: str = "openai/gpt-4", max_tokens: int = 1024, temperature: float = 0.7):
        """
        Initialize AI client.

        Args:
            model: LiteLLM model identifier (e.g., "openai/gpt-4")
            max_tokens: Maximum tokens in response
            temperature: Creativity parameter (0.0-2.0)

        Raises:
            ValueError: If parameters are invalid
            EnvironmentError: If required API keys not set
        """
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")

        if not (0.0 <= temperature <= 2.0):
            raise ValueError("temperature must be between 0.0 and 2.0")

        # Check for API key
        if not os.getenv("OPENAI_API_KEY"):
            raise EnvironmentError(
                "OPENAI_API_KEY environment variable not set. "
                "Please set it in your .env file or environment."
            )

        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Send messages to AI and get response.

        Args:
            messages: List of ChatML messages [{"role": "...", "content": "..."}]

        Returns:
            Response content as string

        Raises:
            AIServiceError: If API call fails
            ValueError: If messages is empty
        """
        if not messages:
            raise ValueError("Messages list cannot be empty")

        try:
            response = completion(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            # Extract content from response
            content = response.choices[0].message.content

            if not content:
                raise AIServiceError("AI returned empty response")

            return content

        except Exception as e:
            # Wrap all exceptions as AIServiceError for cleaner error handling
            if isinstance(e, (ValueError, AIServiceError)):
                raise

            raise AIServiceError(f"AI service error: {str(e)}")
