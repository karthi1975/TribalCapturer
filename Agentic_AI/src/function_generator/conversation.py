"""
Conversation management for maintaining context across AI interactions.

This module provides the Conversation class which manages the message history
for ChatML-formatted conversations with AI services.
"""

from typing import List, Dict


class Conversation:
    """
    Manage conversation history with AI service.

    Maintains an ordered sequence of messages in ChatML format (role + content)
    to preserve context across multiple AI requests.
    """

    def __init__(self, system_prompt: str):
        """
        Initialize conversation with system message.

        Args:
            system_prompt: Initial message establishing AI role and behavior

        Raises:
            ValueError: If system_prompt is empty
        """
        if not system_prompt or not system_prompt.strip():
            raise ValueError("System prompt cannot be empty")

        self._messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt.strip()}
        ]

    def add_user_message(self, content: str) -> None:
        """
        Add user message to conversation.

        Args:
            content: User's message content

        Raises:
            ValueError: If content is empty
        """
        if not content or not content.strip():
            raise ValueError("Message content cannot be empty")

        self._messages.append({
            "role": "user",
            "content": content.strip()
        })

    def add_assistant_message(self, content: str) -> None:
        """
        Add AI response to conversation.

        Args:
            content: AI's response content

        Raises:
            ValueError: If content is empty
        """
        if not content or not content.strip():
            raise ValueError("Message content cannot be empty")

        self._messages.append({
            "role": "assistant",
            "content": content.strip()
        })

    def get_messages(self) -> List[Dict[str, str]]:
        """
        Get all messages in ChatML format.

        Returns:
            List of message dicts suitable for AI API calls
        """
        return self._messages.copy()

    def get_message_count(self) -> int:
        """
        Return total number of messages.

        Returns:
            Count of messages in conversation
        """
        return len(self._messages)
