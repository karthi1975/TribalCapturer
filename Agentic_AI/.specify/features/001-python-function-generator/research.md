# Research: Python Function Generator Tool

**Feature**: 001-python-function-generator
**Date**: 2025-11-16
**Status**: Complete

## Research Areas

### 1. LiteLLM Library Integration

**Decision**: Use LiteLLM's `completion()` function with ChatML message format

**Rationale**:
- LiteLLM provides a unified interface across multiple LLM providers (OpenAI, Anthropic, etc.)
- Supports the standard ChatML message format with roles (system, user, assistant)
- Handles API key management through environment variables
- Provides built-in retry logic and error handling
- Allows easy switching between models without code changes

**Alternatives Considered**:
- **OpenAI SDK directly**: Would lock us to OpenAI only, no provider flexibility
- **LangChain**: Too heavyweight for this simple use case, adds unnecessary complexity
- **Raw HTTP requests**: Would require implementing retry logic, error handling, and message formatting manually

**Best Practices**:
- Set reasonable timeout values (default: 120 seconds for completion calls)
- Use environment variables for API keys (OPENAI_API_KEY)
- Handle rate limiting and API errors gracefully
- Log AI interactions for debugging (without exposing sensitive data)
- Use specific model names (e.g., "openai/gpt-4" or "gpt-4") rather than generic aliases

**Implementation Notes**:
```python
from litellm import completion

# Standard usage pattern
response = completion(
    model="openai/gpt-4",
    messages=[...],
    max_tokens=1024,
    temperature=0.7  # Moderate creativity
)
```

---

### 2. Code Extraction from AI Responses

**Decision**: Use regex-based extraction with fallback strategies

**Rationale**:
- AI responses often include markdown code blocks with triple backticks
- Format varies: may include language identifier ("```python") or not ("```")
- AI may include explanatory text before/after code blocks
- Need robust extraction that handles format variations

**Alternatives Considered**:
- **AST parsing only**: Fails when AI includes non-code text
- **String split on backticks**: Too brittle for edge cases
- **Complex markdown parser**: Overkill for this simple need

**Best Practices**:
- Primary strategy: Extract content between ``` delimiters
- Remove language identifier if present (e.g., "python", "py")
- Fallback: If no code blocks found, return entire response (assume pure code)
- Validate extracted code with Python's `ast.parse()` before returning
- Strip leading/trailing whitespace
- Handle multiple code blocks (take first one)

**Implementation Pattern**:
```python
import re
import ast

def extract_code_block(response: str) -> str:
    # Try to find code blocks
    if '```' in response:
        blocks = response.split('```')
        if len(blocks) >= 3:
            code = blocks[1].strip()
            # Remove language identifier
            if code.startswith(('python', 'py')):
                code = '\n'.join(code.split('\n')[1:])
            return code.strip()

    # Fallback: assume entire response is code
    return response.strip()
```

---

### 3. Conversation Context Management

**Decision**: Use list-based message accumulation with role-based structure

**Rationale**:
- ChatML format requires structured messages with roles
- Context must be preserved across three sequential prompts
- Each AI response should be added to history before next prompt
- Need to control what the AI "sees" in context (code only, not commentary)

**Alternatives Considered**:
- **String concatenation**: Loses structure needed for ChatML
- **Token window management**: Unnecessary for this simple 3-step process
- **Vector embeddings**: Overkill for sequential, short conversations

**Best Practices**:
- Initialize with system message establishing AI's role
- Add user message for each request
- Add assistant message after each response (use extracted code, not raw response)
- Format code in markdown blocks when adding to context
- Keep full message history (no truncation needed for 3-step process)

**Message History Pattern**:
```python
messages = [
    {"role": "system", "content": "You are a Python expert..."},
    {"role": "user", "content": "Write a function that calculates fibonacci"},
    {"role": "assistant", "content": "```python\ndef fibonacci(n):\n    ...```"},
    {"role": "user", "content": "Add comprehensive documentation..."}
]
```

---

### 4. Filename Generation Strategy

**Decision**: Sanitize description with length limits and character restrictions

**Rationale**:
- User descriptions may contain any characters
- Filenames must be valid on Windows, macOS, and Linux
- Need reasonable length limits (filesystem and usability)
- Should be human-readable and descriptive

**Alternatives Considered**:
- **Hash-based names**: Not human-readable, defeats purpose of descriptive names
- **UUID names**: Same issue, not descriptive
- **Full description**: Could exceed filesystem limits (255 chars on most systems)

**Best Practices**:
- Convert to lowercase for consistency
- Replace spaces with underscores
- Remove special characters (keep only alphanumeric and underscores)
- Limit to 30-50 characters for readability
- Add .py extension
- Handle empty descriptions (use default like "generated_function.py")
- Avoid collisions by checking if file exists (optional: append number)

**Implementation Pattern**:
```python
import re

def generate_filename(description: str, max_length: int = 30) -> str:
    # Lowercase and remove non-alphanumeric except spaces
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', description.lower())
    # Replace spaces with underscores
    cleaned = cleaned.replace(' ', '_')
    # Limit length
    cleaned = cleaned[:max_length]
    # Handle empty case
    if not cleaned:
        cleaned = "generated_function"
    return f"{cleaned}.py"
```

---

### 5. Error Handling Strategy

**Decision**: Multi-layered error handling with informative user messages

**Rationale**:
- AI service calls can fail (network, rate limits, invalid API key)
- Code extraction may fail if response format unexpected
- File writing may fail (permissions, disk space)
- Users need clear, actionable error messages

**Best Practices**:
- Catch specific exceptions at each layer (API errors, parsing errors, I/O errors)
- Provide context-specific error messages
- Log detailed errors for debugging
- Show user-friendly messages with actionable guidance
- Graceful degradation where possible

**Error Categories**:
1. **AI Service Errors**: Invalid API key, rate limits, network failures
2. **Response Parsing Errors**: Unexpected format, no code blocks found
3. **File I/O Errors**: Permission denied, disk full, invalid path
4. **Validation Errors**: Empty user input, invalid Python syntax

---

### 6. Testing Framework Selection

**Decision**: pytest for the tool itself, unittest for generated tests

**Rationale**:
- pytest offers better fixtures, parametrization, and assertion messages
- unittest is Python's standard library (no extra dependency for generated code)
- Separation: tool uses pytest, generated code uses unittest per requirements

**Best Practices**:
- Use pytest fixtures for mock AI responses
- Parametrize tests for different input scenarios
- Mock LiteLLM calls to avoid API costs in tests
- Test both success and failure paths
- Include integration tests with real (but cached) API calls

---

### 7. Project Dependencies

**Decision**: Minimal dependencies with clear separation

**Required Dependencies**:
- `litellm` - AI service integration
- `python-dotenv` - Environment variable management (optional but recommended)

**Development Dependencies**:
- `pytest` - Testing framework
- `pytest-mock` - Mocking support
- `black` - Code formatting
- `flake8` - Linting

**Rationale**:
- Keep runtime dependencies minimal
- Use standard library where possible (ast, re, os)
- Development tools enhance code quality without bloating distribution

---

## Implementation Recommendations

### Phase Sequence

1. **Core Infrastructure First**:
   - AI client wrapper (litellm integration)
   - Code extractor (regex-based)
   - Conversation manager (message history)

2. **Main Workflow**:
   - CLI entry point
   - Three-step orchestration
   - User interaction (input/output)

3. **Supporting Features**:
   - Filename generation
   - File writer
   - Error handling

### Testing Strategy

1. **Unit Tests**: Test each module independently with mocks
2. **Integration Tests**: Test full workflow with cached AI responses
3. **Manual Testing**: Real API calls for validation

### Configuration

- Use `.env` file for API keys
- Provide `.env.example` template
- Document required environment variables in README

---

## Open Questions Resolved

1. **Q: Should we support multiple AI providers?**
   A: LiteLLM already supports this. Start with OpenAI/GPT-4, document others.

2. **Q: How to handle very long AI responses?**
   A: Set max_tokens parameter (1024 should be sufficient for most functions).

3. **Q: Should we validate generated Python code?**
   A: Yes, use ast.parse() to validate syntax before saving.

4. **Q: How to handle API costs in testing?**
   A: Mock AI calls in unit tests, use cached responses for integration tests.

5. **Q: Should we support custom prompts/templates?**
   A: Not in v1. Hardcode prompts for simplicity and consistency.
