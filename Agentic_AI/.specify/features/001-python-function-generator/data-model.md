# Data Model: Python Function Generator Tool

**Feature**: 001-python-function-generator
**Date**: 2025-11-16

## Overview

This document describes the core data structures used in the Python Function Generator tool. The tool operates on three main entities: Messages (for AI conversation), Code Artifacts (for different stages of generation), and Generation Configuration.

---

## Core Entities

### 1. Message

Represents a single message in the conversation with the AI service.

**Purpose**: Structure conversations using ChatML format required by LLM APIs.

**Attributes**:
- `role`: string - One of "system", "user", or "assistant"
- `content`: string - The actual message text or code

**Validation Rules**:
- `role` must be one of the three allowed values
- `content` must not be empty
- `content` should be stripped of leading/trailing whitespace

**Relationships**:
- Messages are organized in a `Conversation` (see below)
- Messages are immutable once created

**State**: Immutable value object

**Example**:
```python
{
    "role": "user",
    "content": "Write a function that calculates fibonacci numbers"
}
```

---

### 2. Conversation

Manages the ordered sequence of messages for context preservation.

**Purpose**: Maintain conversation history across the three-phase generation process.

**Attributes**:
- `messages`: List[Message] - Ordered list of all messages in the conversation
- `system_prompt`: string - Initial system message establishing AI role

**Validation Rules**:
- First message must have role="system"
- Messages must alternate between user and assistant (after system message)
- Cannot remove messages (append-only)

**Relationships**:
- Contains multiple `Message` objects
- Used by `AIClient` to make requests

**State Transitions**:
1. **Initialized**: Contains only system message
2. **First Request**: User message added
3. **First Response**: Assistant message added
4. **Second Request**: User message added
5. **Second Response**: Assistant message added
6. **Third Request**: User message added
7. **Complete**: All three phases finished

**Methods**:
- `add_user_message(content: str)` - Add a user request
- `add_assistant_message(content: str)` - Add AI response
- `get_messages()` - Return all messages for API call
- `get_message_count()` - Return total number of messages

---

### 3. CodeArtifact

Represents generated code at different stages of completion.

**Purpose**: Track the evolution of code through basic → documented → tested phases.

**Attributes**:
- `code`: string - The actual Python code
- `stage`: string - One of "basic", "documented", "tested"
- `is_valid`: boolean - Whether code passes syntax validation
- `created_at`: datetime - When this artifact was created

**Validation Rules**:
- `code` must not be empty
- `code` must be valid Python (checked with ast.parse)
- `stage` must be one of three allowed values

**Relationships**:
- Created by `CodeExtractor` from AI responses
- Consumed by `FileWriter` for output

**State Transitions**:
```
basic → documented → tested
```

Each transition creates a new artifact; previous artifacts are preserved for display.

**Methods**:
- `validate_syntax()` - Check if code is syntactically valid Python
- `get_function_name()` - Extract the main function name (if possible)
- `to_markdown()` - Format code for display with code blocks

---

### 4. GenerationRequest

Represents the user's initial request to generate a function.

**Purpose**: Encapsulate all user input and generation parameters.

**Attributes**:
- `description`: string - Natural language description of desired function
- `output_filename`: string - Generated filename for output (derived from description)
- `max_tokens`: int - Maximum tokens for AI responses (default: 1024)
- `temperature`: float - AI creativity parameter (default: 0.7)

**Validation Rules**:
- `description` must not be empty or whitespace-only
- `description` length should be reasonable (< 500 characters)
- `output_filename` must be valid for target OS
- `max_tokens` must be positive (100-4096 range)
- `temperature` must be between 0.0 and 2.0

**Relationships**:
- Created from user input in `main.py`
- Used to initialize `Conversation` and generate prompts

**Methods**:
- `validate()` - Check all validation rules
- `generate_filename()` - Create safe filename from description
- `to_dict()` - Serialize for logging

---

### 5. GenerationResult

Represents the complete output of the generation process.

**Purpose**: Package all artifacts and metadata for final output.

**Attributes**:
- `basic_code`: CodeArtifact - Code from phase 1
- `documented_code`: CodeArtifact - Code from phase 2
- `tested_code`: CodeArtifact - Code from phase 3 (final)
- `filename`: string - Where the final code was saved
- `success`: boolean - Whether all phases completed successfully
- `error_message`: string - Error details if success=false
- `execution_time`: float - Total time in seconds

**Validation Rules**:
- If `success=true`, all three artifacts must be present
- If `success=false`, `error_message` must be set
- `filename` must be set if success=true

**Relationships**:
- Contains three `CodeArtifact` objects
- Created by main orchestration logic
- Used for display and reporting

**Methods**:
- `get_final_code()` - Return the tested_code artifact
- `display_progression()` - Show all three stages to user
- `to_summary()` - Create summary string for display

---

## Supporting Entities

### 6. AIResponse

Represents the raw response from the AI service.

**Purpose**: Wrap AI service responses for processing.

**Attributes**:
- `raw_content`: string - Original response from AI
- `model`: string - Model that generated the response
- `tokens_used`: int - Token count for this response
- `finish_reason`: string - Why generation stopped (e.g., "stop", "length")

**Validation Rules**:
- `raw_content` must not be None
- `tokens_used` should be positive

**Relationships**:
- Returned by `AIClient`
- Processed by `CodeExtractor`

---

### 7. ExtractionResult

Represents the result of extracting code from an AI response.

**Purpose**: Capture both extracted code and extraction metadata.

**Attributes**:
- `extracted_code`: string - The extracted Python code
- `had_code_blocks`: boolean - Whether response used ``` delimiters
- `had_language_identifier`: boolean - Whether language was specified
- `extraction_method`: string - Which strategy succeeded ("code_block", "fallback", etc.)

**Validation Rules**:
- `extracted_code` must not be empty
- `extraction_method` must match one of the defined strategies

**Relationships**:
- Created by `CodeExtractor`
- Converted to `CodeArtifact` after validation

---

## Data Flow

```
User Input (description)
    ↓
GenerationRequest (validated)
    ↓
Conversation (initialized with system prompt)
    ↓
Phase 1: Basic Code
    - User message added to Conversation
    - AIClient makes request → AIResponse
    - CodeExtractor processes → ExtractionResult
    - Validation → CodeArtifact (stage="basic")
    - Assistant message added to Conversation
    ↓
Phase 2: Documentation
    - User message (with basic code) added
    - AIClient makes request → AIResponse
    - CodeExtractor processes → ExtractionResult
    - Validation → CodeArtifact (stage="documented")
    - Assistant message added to Conversation
    ↓
Phase 3: Testing
    - User message (with documented code) added
    - AIClient makes request → AIResponse
    - CodeExtractor processes → ExtractionResult
    - Validation → CodeArtifact (stage="tested")
    ↓
FileWriter saves to disk
    ↓
GenerationResult (complete)
```

---

## Error States

Each entity can be in an error state:

### Message
- **Invalid Role**: Role not in allowed set → ValueError
- **Empty Content**: Content is empty or whitespace → ValueError

### Conversation
- **Malformed History**: Messages don't follow system→user→assistant pattern → StateError
- **Missing System Message**: First message is not system → StateError

### CodeArtifact
- **Invalid Syntax**: Code doesn't parse with ast.parse() → SyntaxError
- **Empty Code**: No code extracted → ValueError

### GenerationRequest
- **Empty Description**: User provided no input → ValueError
- **Invalid Filename**: Generated filename has invalid characters → ValueError

### ExtractionResult
- **No Code Found**: No code extracted from response → ExtractionError

---

## Persistence

**File System**:
- Output Python files (.py) written to current directory
- Format: documented function + test cases in single file
- Filename derived from user description

**In-Memory Only**:
- All entities except final output file
- Conversation history (not persisted)
- Intermediate artifacts (not saved separately)

**No Database**: This tool has no persistent storage requirements beyond output files.

---

## Serialization

### For Logging
- `GenerationRequest` → JSON for debug logs
- `Conversation` → JSON (list of messages) for debugging
- `GenerationResult` → Summary string for user display

### For API Calls
- `Conversation` → List[Dict] (ChatML format) for LiteLLM

### For File Output
- `CodeArtifact` → Plain text (Python source code)
