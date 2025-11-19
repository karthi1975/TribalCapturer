"""
File operations for saving generated code.

This module provides utilities for generating safe filenames and writing
code to disk.
"""

import os
import re


class FileWriter:
    """Handle file operations for generated code."""

    @staticmethod
    def generate_filename(description: str, max_length: int = 30) -> str:
        """
        Create safe filename from user description.

        Transforms description into valid cross-platform filename:
        - Lowercase
        - Alphanumeric and underscores only
        - Limited length
        - .py extension

        Args:
            description: User's function description
            max_length: Maximum length of name (excluding .py)

        Returns:
            Safe filename string (e.g., "calculate_fibonacci.py")
        """
        if not description or not description.strip():
            return "generated_function.py"

        # Lowercase and remove non-alphanumeric except spaces
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', description.lower())

        # Replace spaces with underscores
        cleaned = cleaned.replace(' ', '_')

        # Remove multiple consecutive underscores
        cleaned = re.sub(r'_+', '_', cleaned)

        # Strip leading/trailing underscores
        cleaned = cleaned.strip('_')

        # Limit length
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length]

        # Handle empty case after cleaning
        if not cleaned:
            cleaned = "generated_function"

        return f"{cleaned}.py"

    @staticmethod
    def write_code_file(filename: str, code: str) -> None:
        """
        Write code to file in current directory.

        Args:
            filename: Name of file to create
            code: Python code to write

        Raises:
            ValueError: If filename or code is empty
            IOError: If file cannot be written
        """
        if not filename or not filename.strip():
            raise ValueError("Filename cannot be empty")

        if not code or not code.strip():
            raise ValueError("Code cannot be empty")

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(code)
        except IOError as e:
            raise IOError(f"Failed to write file '{filename}': {str(e)}")

    @staticmethod
    def check_file_exists(filename: str) -> bool:
        """
        Check if file already exists.

        Args:
            filename: File to check

        Returns:
            True if exists, False otherwise
        """
        return os.path.exists(filename)
