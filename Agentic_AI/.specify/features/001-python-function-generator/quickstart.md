# Quickstart Guide: Python Function Generator Tool

**Feature**: 001-python-function-generator
**Date**: 2025-11-16

This guide will help you get the Python Function Generator tool running quickly.

---

## Prerequisites

- **Python**: 3.8 or higher
- **OpenAI API Key**: Get one from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Internet Connection**: Required for AI service calls

---

## Installation

### 1. Clone/Navigate to Repository

```bash
cd /Users/karthi/Agentic_AI
```

### 2. Install Dependencies

```bash
pip install litellm python-dotenv
```

**Dependencies**:
- `litellm`: AI service integration
- `python-dotenv`: Environment variable management (optional but recommended)

### 3. Set Up API Key

Create a `.env` file in the project root:

```bash
echo "OPENAI_API_KEY=your-openai-api-key-here" > .env
```

**Note**: Replace `your-openai-api-key-here` with your actual OpenAI API key. Keep this file secure and don't commit it to version control.

Alternatively, export as environment variable:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

---

## Quick Start

### Run the Tool

```bash
python -m src.function_generator.main
```

Or if installed as package:

```bash
python-function-generator
```

### Example Session

```
What kind of function would you like to create?
Example: 'A function that calculates the factorial of a number'
Your description: Calculate fibonacci sequence up to n

=== Initial Function ===
def fibonacci(n):
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    sequence = [0, 1]
    while len(sequence) < n:
        sequence.append(sequence[-1] + sequence[-2])
    return sequence

=== Documented Function ===
def fibonacci(n):
    """
    Generate a Fibonacci sequence up to n numbers.

    The Fibonacci sequence is a series where each number is the sum of the
    two preceding ones, starting from 0 and 1.

    Args:
        n (int): The number of Fibonacci numbers to generate.

    Returns:
        list: A list containing the first n Fibonacci numbers.

    Examples:
        >>> fibonacci(5)
        [0, 1, 1, 2, 3]

        >>> fibonacci(1)
        [0]

    Edge Cases:
        - Returns empty list if n <= 0
        - Returns [0] if n == 1
        - Returns [0, 1] if n == 2
    """
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    sequence = [0, 1]
    while len(sequence) < n:
        sequence.append(sequence[-1] + sequence[-2])
    return sequence

=== Test Cases ===
import unittest

class TestFibonacci(unittest.TestCase):
    def test_basic_functionality(self):
        """Test basic fibonacci sequence generation."""
        self.assertEqual(fibonacci(5), [0, 1, 1, 2, 3])
        self.assertEqual(fibonacci(7), [0, 1, 1, 2, 3, 5, 8])

    def test_edge_cases(self):
        """Test edge cases."""
        self.assertEqual(fibonacci(0), [])
        self.assertEqual(fibonacci(-5), [])
        self.assertEqual(fibonacci(1), [0])
        self.assertEqual(fibonacci(2), [0, 1])

    def test_large_input(self):
        """Test with larger input."""
        result = fibonacci(10)
        self.assertEqual(len(result), 10)
        self.assertEqual(result[-1], 21)

if __name__ == '__main__':
    unittest.main()

Final code has been saved to calculate_fibonacci_sequence_up.py
```

---

## Usage Tips

### 1. Writing Good Function Descriptions

**Good descriptions** are clear and specific:
```
✓ "Calculate the factorial of a number using recursion"
✓ "Parse a CSV file and return a list of dictionaries"
✓ "Validate email addresses using regex"
```

**Avoid vague descriptions**:
```
✗ "Do something with numbers"
✗ "Process data"
✗ "Make it work"
```

### 2. Understanding Output

The tool shows three stages:

1. **Initial Function**: Basic working code
2. **Documented Function**: Includes comprehensive docstring
3. **Test Cases**: Full unittest test suite

All three are displayed so you can see the progression.

### 3. Output Files

Generated files are saved in the **current directory** with names derived from your description:

```
"calculate factorial" → calculate_factorial.py
"parse CSV file" → parse_csv_file.py
"validate email addresses" → validate_email_addres.py  # truncated to 30 chars
```

---

## Troubleshooting

### Error: "Invalid API Key"

**Problem**: OpenAI API key is missing or invalid.

**Solution**:
1. Verify your `.env` file exists and contains `OPENAI_API_KEY=...`
2. Check that the key starts with `sk-`
3. Verify the key is valid on [OpenAI Platform](https://platform.openai.com/api-keys)

```bash
# Check if environment variable is set
echo $OPENAI_API_KEY
```

### Error: "Rate limit exceeded"

**Problem**: Too many API calls to OpenAI.

**Solution**:
1. Wait a few minutes before trying again
2. Check your OpenAI usage limits
3. Consider upgrading your OpenAI plan if needed

### Error: "No code found in response"

**Problem**: AI response didn't include properly formatted code.

**Solution**:
1. Try a more specific function description
2. Re-run the tool (AI responses can vary)
3. Check your internet connection

### Error: "Permission denied"

**Problem**: Cannot write file to current directory.

**Solution**:
1. Check directory permissions: `ls -la`
2. Try running from a directory where you have write permissions
3. Change to home directory: `cd ~`

### File Already Exists

**Behavior**: Tool will **overwrite** existing files with the same name.

**Solution**: Rename existing files before generating if you want to keep them.

---

## Advanced Usage

### Custom Model Selection

Modify `main.py` to use a different model:

```python
ai_client = AIClient(model="openai/gpt-3.5-turbo")  # Faster, cheaper
ai_client = AIClient(model="openai/gpt-4-turbo")    # Latest version
```

### Adjusting AI Parameters

```python
ai_client = AIClient(
    model="openai/gpt-4",
    max_tokens=2048,      # Longer responses
    temperature=0.3       # More deterministic (less creative)
)
```

### Using Different AI Providers

LiteLLM supports multiple providers:

```python
# Anthropic Claude
ai_client = AIClient(model="claude-3-opus-20240229")
# Set ANTHROPIC_API_KEY in .env

# Google PaLM
ai_client = AIClient(model="palm/chat-bison")
# Set PALM_API_KEY in .env
```

---

## Development Setup

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-mock black flake8

# Run all tests
pytest

# Run with coverage
pytest --cov=src/function_generator

# Run specific test file
pytest tests/unit/test_code_extractor.py
```

### Code Formatting

```bash
# Format code
black src/ tests/

# Check formatting
black --check src/ tests/
```

### Linting

```bash
flake8 src/ tests/
```

---

## Project Structure

```
Agentic_AI/
├── .env                          # API keys (create this)
├── .env.example                  # Template for API keys
├── requirements.txt              # Dependencies
├── setup.py                      # Package configuration
├── README.md                     # Project documentation
├── src/
│   └── function_generator/
│       ├── __init__.py
│       ├── main.py               # CLI entry point
│       ├── ai_client.py          # LiteLLM wrapper
│       ├── code_extractor.py     # Code parsing
│       ├── conversation.py       # Context management
│       └── file_writer.py        # File operations
└── tests/
    ├── unit/                     # Unit tests
    ├── integration/              # Integration tests
    └── fixtures/                 # Test data
```

---

## Next Steps

1. **Generate your first function**: Follow the example above
2. **Try different function types**: Math, string processing, file I/O, etc.
3. **Review generated code**: Always review before using in production
4. **Run the tests**: Execute `python <generated_file>.py` to run tests
5. **Customize prompts**: Modify `main.py` to adjust how the tool asks for documentation/tests

---

## Support

### Documentation
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Python unittest Guide](https://docs.python.org/3/library/unittest.html)

### Common Issues
- Check `.env` file exists and has valid API key
- Ensure Python 3.8+ is installed: `python --version`
- Verify internet connectivity
- Check OpenAI service status: [status.openai.com](https://status.openai.com)

---

## Example Function Descriptions to Try

1. "Convert temperature from Celsius to Fahrenheit"
2. "Check if a string is a palindrome"
3. "Find the largest number in a list"
4. "Merge two sorted lists into one sorted list"
5. "Calculate the greatest common divisor of two numbers"
6. "Reverse the words in a sentence"
7. "Check if a year is a leap year"
8. "Find all prime numbers up to n"

Each will generate a complete, documented, tested Python function!
