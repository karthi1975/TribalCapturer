"""
Main CLI entry point for Python Function Generator.

This module orchestrates the three-phase code generation process:
1. Generate basic function code
2. Add comprehensive documentation
3. Add unittest test cases
"""

import sys
from typing import Optional, Tuple
from .conversation import Conversation
from .ai_client import AIClient, AIServiceError
from .code_extractor import CodeExtractor
from .file_writer import FileWriter


def get_user_input() -> str:
    """
    Prompt user for function description.

    Returns:
        User's function description

    Raises:
        ValueError: If user provides empty input
    """
    print("\nWhat kind of function would you like to create?")
    print("Example: 'A function that calculates the factorial of a number'")
    print("Your description: ", end='')

    description = input().strip()

    if not description:
        raise ValueError("Function description cannot be empty")

    return description


def display_code_output(code: str, title: str) -> None:
    """
    Display code with visual separation.

    Args:
        code: Code to display
        title: Section title (e.g., "Initial Function", "Documented Function")
    """
    print(f"\n=== {title} ===")
    print(code)
    print()


def develop_custom_function() -> Tuple[str, str, str]:
    """
    Execute the three-phase generation process.

    Returns:
        Tuple of (function_code, tests, filename)

    Raises:
        AIServiceError: If AI communication fails
        ValueError: If user input is invalid
    """
    # Get user input
    try:
        function_description = get_user_input()
    except EOFError:
        raise ValueError("No input provided")

    # Initialize conversation with system prompt
    conversation = Conversation(
        "You are a Python expert helping to develop a function."
    )

    # Initialize AI client
    try:
        ai_client = AIClient(
            model="openai/gpt-4",
            max_tokens=1024,
            temperature=0.7
        )
    except EnvironmentError as e:
        print(f"\nError: {e}")
        print("Please create a .env file with your OPENAI_API_KEY.")
        sys.exit(1)

    # Phase 1: Generate basic function
    print("\nGenerating basic function...")

    conversation.add_user_message(
        f"Write a Python function that {function_description}. "
        f"Output the function in a ```python code block```."
    )

    try:
        initial_response = ai_client.generate_response(conversation.get_messages())
    except AIServiceError as e:
        print(f"\nError communicating with AI service: {e}")
        print("Please check your internet connection and API key.")
        sys.exit(1)

    # Extract code from response
    try:
        initial_function = CodeExtractor.extract_code_block(initial_response)
    except ValueError as e:
        print(f"\nError extracting code: {e}")
        sys.exit(1)

    # Validate syntax
    if not CodeExtractor.validate_python_syntax(initial_function):
        print("\nWarning: Generated code may have syntax errors")

    display_code_output(initial_function, "Initial Function")

    # Add assistant response to conversation (code only, not commentary)
    conversation.add_assistant_message(f"```python\n\n{initial_function}\n\n```")

    # Phase 2: Add documentation
    print("Adding documentation...")

    conversation.add_user_message(
        "Add comprehensive documentation to this function, including description, "
        "parameters, return value, examples, and edge cases. "
        "Output the function in a ```python code block```."
    )

    try:
        doc_response = ai_client.generate_response(conversation.get_messages())
    except AIServiceError as e:
        print(f"\nError communicating with AI service: {e}")
        sys.exit(1)

    documented_function = CodeExtractor.extract_code_block(doc_response)
    display_code_output(documented_function, "Documented Function")

    # Add documentation response to conversation
    conversation.add_assistant_message(f"```python\n\n{documented_function}\n\n```")

    # Phase 3: Add test cases
    print("Adding test cases...")

    conversation.add_user_message(
        "Add unittest test cases for this function, including tests for basic "
        "functionality, edge cases, error cases, and various input scenarios. "
        "Output the code in a ```python code block```."
    )

    try:
        test_response = ai_client.generate_response(conversation.get_messages())
    except AIServiceError as e:
        print(f"\nError communicating with AI service: {e}")
        sys.exit(1)

    test_cases = CodeExtractor.extract_code_block(test_response)
    display_code_output(test_cases, "Test Cases")

    # Generate filename from description
    filename = FileWriter.generate_filename(function_description)

    # Save final version (documented function + tests)
    final_code = documented_function + '\n\n' + test_cases

    try:
        FileWriter.write_code_file(filename, final_code)
        print(f"Final code has been saved to {filename}\n")
    except (ValueError, IOError) as e:
        print(f"\nError saving file: {e}")
        print("Code was generated but not saved.")

    return documented_function, test_cases, filename


def main() -> int:
    """
    CLI entry point for function generator.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        develop_custom_function()
        return 0
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
