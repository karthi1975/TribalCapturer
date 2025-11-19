# Module Interfaces: Python Function Generator Tool

**Feature**: 001-python-function-generator
**Date**: 2025-11-16

This document defines the public interfaces (contracts) for each module in the Python Function Generator tool.

---

## 1. AIClient Interface

**Module**: `src/function_generator/ai_client.py`

**Purpose**: Wrapper for LiteLLM to communicate with AI services.

### Public Interface

```python
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

    def generate_response(self, messages: List[Dict[str, str]]) -> AIResponse:
        """
        Send messages to AI and get response.

        Args:
            messages: List of ChatML messages [{"role": "...", "content": "..."}]

        Returns:
            AIResponse object containing response and metadata

        Raises:
            AIServiceError: If API call fails (network, rate limit, etc.)
            InvalidResponseError: If response format is unexpected
        """
```

### Dependencies
- `litellm` library
- Environment: `OPENAI_API_KEY`

### Error Handling
- `AIServiceError`: Wraps litellm exceptions with user-friendly messages
- `InvalidResponseError`: When response lacks expected fields
- Retries: None (rely on litellm's built-in retry logic)

---

## 2. CodeExtractor Interface

**Module**: `src/function_generator/code_extractor.py`

**Purpose**: Extract Python code from AI responses that may include commentary.

### Public Interface

```python
class CodeExtractor:
    """Extract code from AI responses."""

    @staticmethod
    def extract_code_block(response: str) -> ExtractionResult:
        """
        Extract Python code from AI response.

        Handles multiple formats:
        - Markdown code blocks with ```python
        - Markdown code blocks with ```
        - Plain code (no delimiters)

        Args:
            response: Raw text from AI service

        Returns:
            ExtractionResult containing extracted code and metadata

        Raises:
            ExtractionError: If no code can be extracted
        """

    @staticmethod
    def validate_python_syntax(code: str) -> bool:
        """
        Check if code is syntactically valid Python.

        Args:
            code: Python source code string

        Returns:
            True if valid, False otherwise
        """
```

### Dependencies
- `re` (standard library)
- `ast` (standard library)

### Extraction Strategies (in order)
1. Find first ``` delimited block
2. Remove language identifier if present
3. Fallback to full response if no blocks found

---

## 3. Conversation Interface

**Module**: `src/function_generator/conversation.py`

**Purpose**: Manage message history for context preservation.

### Public Interface

```python
class Conversation:
    """Manage conversation history with AI service."""

    def __init__(self, system_prompt: str):
        """
        Initialize conversation with system message.

        Args:
            system_prompt: Initial message establishing AI role
        """

    def add_user_message(self, content: str) -> None:
        """
        Add user message to conversation.

        Args:
            content: User's message content

        Raises:
            ValueError: If content is empty
        """

    def add_assistant_message(self, content: str) -> None:
        """
        Add AI response to conversation.

        Args:
            content: AI's response content

        Raises:
            ValueError: If content is empty
            StateError: If no user message precedes this
        """

    def get_messages(self) -> List[Dict[str, str]]:
        """
        Get all messages in ChatML format.

        Returns:
            List of message dicts suitable for AI API
        """

    def get_message_count(self) -> int:
        """Return total number of messages."""
```

### Dependencies
- None (uses only standard library)

### Invariants
- First message is always system message
- Messages alternate user→assistant after system
- Cannot remove messages (append-only)

---

## 4. FileWriter Interface

**Module**: `src/function_generator/file_writer.py`

**Purpose**: Generate safe filenames and write code to disk.

### Public Interface

```python
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

    @staticmethod
    def write_code_file(filename: str, code: str) -> None:
        """
        Write code to file in current directory.

        Args:
            filename: Name of file to create
            code: Python code to write

        Raises:
            IOError: If file cannot be written (permissions, disk space, etc.)
            ValueError: If filename or code is empty
        """

    @staticmethod
    def check_file_exists(filename: str) -> bool:
        """
        Check if file already exists.

        Args:
            filename: File to check

        Returns:
            True if exists, False otherwise
        """
```

### Dependencies
- `os` (standard library)
- `re` (standard library)

### File Operations
- Writes to current working directory
- Overwrites existing files (user should be warned)
- Uses UTF-8 encoding

---

## 5. Main Orchestrator Interface

**Module**: `src/function_generator/main.py`

**Purpose**: CLI entry point and workflow orchestration.

### Public Interface

```python
def main() -> int:
    """
    CLI entry point for function generator.

    Workflow:
    1. Prompt user for function description
    2. Initialize conversation and AI client
    3. Phase 1: Generate basic function
    4. Phase 2: Add documentation
    5. Phase 3: Add tests
    6. Save to file
    7. Display results

    Returns:
        Exit code (0 for success, 1 for error)
    """

def develop_custom_function() -> GenerationResult:
    """
    Execute the three-phase generation process.

    This is the core orchestration function that:
    - Gets user input
    - Manages conversation through three phases
    - Displays progress at each step
    - Saves final output

    Returns:
        GenerationResult containing all artifacts and metadata

    Raises:
        AIServiceError: If AI communication fails
        ExtractionError: If code extraction fails
        IOError: If file writing fails
    """
```

### Dependencies
- All other modules (AIClient, CodeExtractor, Conversation, FileWriter)
- `sys` for exit codes
- `os` for environment checks

### User Interaction
- Prompts written to stdout
- Reads from stdin
- Progress displayed after each phase
- Final confirmation with filename

---

## 6. Data Models

**Module**: `src/function_generator/models.py` (if created)

**Purpose**: Define data classes for type safety.

### Public Interface

```python
@dataclass
class AIResponse:
    """Response from AI service."""
    raw_content: str
    model: str
    tokens_used: int
    finish_reason: str

@dataclass
class ExtractionResult:
    """Result of code extraction."""
    extracted_code: str
    had_code_blocks: bool
    had_language_identifier: bool
    extraction_method: str

@dataclass
class CodeArtifact:
    """Generated code at a specific stage."""
    code: str
    stage: Literal["basic", "documented", "tested"]
    is_valid: bool
    created_at: datetime

    def validate_syntax(self) -> bool:
        """Check if code is syntactically valid Python."""

@dataclass
class GenerationRequest:
    """User's request to generate a function."""
    description: str
    output_filename: str
    max_tokens: int = 1024
    temperature: float = 0.7

    def validate(self) -> None:
        """Validate all fields."""

    def generate_filename(self) -> str:
        """Create filename from description."""

@dataclass
class GenerationResult:
    """Complete result of generation process."""
    basic_code: Optional[CodeArtifact]
    documented_code: Optional[CodeArtifact]
    tested_code: Optional[CodeArtifact]
    filename: str
    success: bool
    error_message: Optional[str]
    execution_time: float

    def get_final_code(self) -> str:
        """Return the final tested code."""

    def display_progression(self) -> None:
        """Print all three stages to console."""
```

---

## Error Hierarchy

All custom exceptions inherit from `FunctionGeneratorError`:

```python
class FunctionGeneratorError(Exception):
    """Base exception for function generator."""

class AIServiceError(FunctionGeneratorError):
    """Error communicating with AI service."""

class ExtractionError(FunctionGeneratorError):
    """Error extracting code from response."""

class ValidationError(FunctionGeneratorError):
    """Error validating code or input."""

class FileOperationError(FunctionGeneratorError):
    """Error performing file operations."""
```

---

## Module Dependencies Graph

```
main.py
  ├─> ai_client.py
  ├─> code_extractor.py
  ├─> conversation.py
  ├─> file_writer.py
  └─> models.py (if created)

ai_client.py
  └─> litellm (external)

code_extractor.py
  ├─> re (stdlib)
  └─> ast (stdlib)

conversation.py
  └─> (no external dependencies)

file_writer.py
  ├─> os (stdlib)
  └─> re (stdlib)
```

---

## Testing Contracts

Each module should have corresponding tests:

- `test_ai_client.py`: Mock litellm responses
- `test_code_extractor.py`: Test various response formats
- `test_conversation.py`: Test message sequencing
- `test_file_writer.py`: Test filename generation and file I/O
- `test_main.py`: Integration test with mocked AI client

### Test Coverage Requirements
- Unit tests: 90%+ coverage per module
- Integration tests: Full workflow with cached responses
- Edge cases: Empty inputs, malformed responses, API failures
