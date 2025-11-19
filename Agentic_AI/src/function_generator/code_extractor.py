"""
Code extraction utilities for parsing AI responses.

This module provides functions to extract Python code from AI responses that
may include commentary, markdown formatting, or other non-code text.
"""

import re
import ast


class CodeExtractor:
    """Extract code from AI responses."""

    @staticmethod
    def extract_code_block(response: str) -> str:
        """
        Extract Python code from AI response.

        Handles multiple formats:
        - Markdown code blocks with ```python
        - Markdown code blocks with ```
        - Plain code (no delimiters)

        Args:
            response: Raw text from AI service

        Returns:
            Extracted Python code as string

        Raises:
            ValueError: If response is empty
        """
        if not response or not response.strip():
            raise ValueError("Response cannot be empty")

        response = response.strip()

        # Try to find code blocks with triple backticks
        if '```' in response:
            # Split by code block delimiters
            parts = response.split('```')

            if len(parts) >= 3:
                # Get the first code block (index 1)
                code_block = parts[1].strip()

                # Remove language identifier if present
                lines = code_block.split('\n')
                if lines and lines[0].strip().lower() in ['python', 'py']:
                    # Remove first line (language identifier)
                    code_block = '\n'.join(lines[1:]).strip()

                return code_block

        # Fallback: assume entire response is code
        return response

    @staticmethod
    def validate_python_syntax(code: str) -> bool:
        """
        Check if code is syntactically valid Python.

        Args:
            code: Python source code string

        Returns:
            True if valid Python syntax, False otherwise
        """
        if not code or not code.strip():
            return False

        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False
