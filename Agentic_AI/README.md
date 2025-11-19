# Python Function Generator Tool

AI-powered CLI tool that generates Python functions with comprehensive documentation and test cases.

## Features

- 🤖 **AI-Powered Generation**: Uses GPT-4 to generate Python code from natural language descriptions
- 📝 **Automatic Documentation**: Adds comprehensive docstrings following PEP 257 conventions
- ✅ **Test Generation**: Creates unittest test cases covering basic functionality, edge cases, and errors
- 💾 **File Saving**: Automatically saves generated code to properly named Python files
- 🔄 **Context Preservation**: Maintains conversation context across the three-phase generation process

## Quick Start

### Installation

1. Clone the repository:
```bash
cd /Users/karthi/Agentic_AI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### Usage

Run the tool:
```bash
python -m src.function_generator.main
```

Or after installation:
```bash
python-function-generator
```

### Example

```
What kind of function would you like to create?
Example: 'A function that calculates the factorial of a number'
Your description: Calculate fibonacci sequence up to n

=== Initial Function ===
[Basic Python code generated]

=== Documented Function ===
[Code with comprehensive docstrings]

=== Test Cases ===
[Complete unittest test suite]

Final code has been saved to calculate_fibonacci_sequence_up.py
```

## How It Works

The tool uses a three-phase process:

1. **Phase 1 - Basic Code**: Generates working Python code from your description
2. **Phase 2 - Documentation**: Adds comprehensive docstrings with examples and edge cases
3. **Phase 3 - Testing**: Creates unittest test cases for thorough coverage

Each phase builds on the previous one, maintaining full context throughout the process.

## Requirements

- Python 3.8+
- OpenAI API key
- Internet connection

## Project Structure

```
src/function_generator/
├── __init__.py           # Package metadata
├── main.py              # CLI entry point
├── ai_client.py         # LiteLLM wrapper
├── code_extractor.py    # Code parsing
├── conversation.py      # Context management
└── file_writer.py       # File operations

tests/
├── unit/               # Unit tests
├── integration/        # Integration tests
└── fixtures/           # Test data
```

## Development

Install development dependencies:
```bash
pip install -e ".[dev]"
```

Run tests:
```bash
pytest
```

Format code:
```bash
black src/ tests/
```

Lint code:
```bash
flake8 src/ tests/
```

## Configuration

The tool uses the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (required)

## License

MIT License

## Credits

Built with:
- [LiteLLM](https://github.com/BerriAI/litellm) - Unified LLM API interface
- [OpenAI GPT-4](https://openai.com/) - AI model for code generation
