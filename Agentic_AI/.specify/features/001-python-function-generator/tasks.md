# Tasks: Python Function Generator Tool

**Input**: Design documents from `.specify/features/001-python-function-generator/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/module-interfaces.md

**Tests**: Tests are NOT included as the tool itself generates tests as output. No test files will be created for the tool.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- All paths relative to `/Users/karthi/Agentic_AI`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directory structure: src/function_generator/, tests/unit/, tests/integration/, tests/fixtures/
- [ ] T002 Create requirements.txt with litellm and python-dotenv dependencies
- [ ] T003 [P] Create .env.example template with OPENAI_API_KEY placeholder
- [ ] T004 [P] Create setup.py or pyproject.toml for package configuration
- [ ] T005 [P] Create src/function_generator/__init__.py with package metadata
- [ ] T006 [P] Create README.md with project overview and setup instructions
- [ ] T007 [P] Create .gitignore to exclude .env, __pycache__, *.pyc, venv/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Create src/function_generator/conversation.py with Conversation class (message management)
- [ ] T009 Create src/function_generator/code_extractor.py with CodeExtractor class (regex-based extraction)
- [ ] T010 [P] Create src/function_generator/file_writer.py with FileWriter class (filename generation and file I/O)
- [ ] T011 [P] Create src/function_generator/ai_client.py with AIClient class (LiteLLM wrapper)
- [ ] T012 Create tests/fixtures/sample_responses.json with mock AI responses for different scenarios

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Generate Basic Code Function (Priority: P1) 🎯 MVP

**Goal**: Enable users to generate working Python code from natural language descriptions

**Independent Test**: Provide a function description (e.g., "calculate factorial") and verify that valid, syntactically correct Python code is generated and displayed

### Implementation for User Story 1

- [ ] T013 [US1] Implement Conversation.__init__() with system_prompt parameter in src/function_generator/conversation.py
- [ ] T014 [US1] Implement Conversation.add_user_message() method in src/function_generator/conversation.py
- [ ] T015 [US1] Implement Conversation.add_assistant_message() method in src/function_generator/conversation.py
- [ ] T016 [US1] Implement Conversation.get_messages() to return ChatML format in src/function_generator/conversation.py
- [ ] T017 [P] [US1] Implement CodeExtractor.extract_code_block() with regex pattern matching in src/function_generator/code_extractor.py
- [ ] T018 [P] [US1] Implement CodeExtractor.validate_python_syntax() using ast.parse() in src/function_generator/code_extractor.py
- [ ] T019 [P] [US1] Implement AIClient.__init__() with model, max_tokens, temperature parameters in src/function_generator/ai_client.py
- [ ] T020 [US1] Implement AIClient.generate_response() using litellm.completion() in src/function_generator/ai_client.py
- [ ] T021 [US1] Create main.py with get_user_input() function to prompt for function description in src/function_generator/main.py
- [ ] T022 [US1] Implement phase_1_generate_basic_code() in main.py to orchestrate basic code generation in src/function_generator/main.py
- [ ] T023 [US1] Add display_code_output() function to print code with visual separation in src/function_generator/main.py
- [ ] T024 [US1] Add error handling for empty/vague descriptions in src/function_generator/main.py
- [ ] T025 [US1] Add error handling for AI service failures in src/function_generator/ai_client.py

**Checkpoint**: At this point, User Story 1 should be fully functional - users can generate basic Python functions from descriptions

---

## Phase 4: User Story 2 - Add Comprehensive Documentation (Priority: P2)

**Goal**: Automatically add professional documentation (docstrings) to generated functions

**Independent Test**: Take output from User Story 1 and verify that comprehensive documentation with description, parameters, returns, examples, and edge cases is added

### Implementation for User Story 2

- [ ] T026 [US2] Implement phase_2_add_documentation() in main.py to request documentation from AI in src/function_generator/main.py
- [ ] T027 [US2] Create documentation prompt template in main.py specifying docstring requirements in src/function_generator/main.py
- [ ] T028 [US2] Update display logic to show "=== Documented Function ===" section in src/function_generator/main.py
- [ ] T029 [US2] Add validation to ensure documentation follows PEP 257 conventions in src/function_generator/code_extractor.py
- [ ] T030 [US2] Add error handling for missing documentation elements in src/function_generator/main.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can generate documented functions

---

## Phase 5: User Story 3 - Generate Unit Tests (Priority: P3)

**Goal**: Automatically generate comprehensive unittest test cases for generated functions

**Independent Test**: Take documented code and verify that comprehensive unit test cases covering basic functionality, edge cases, and error scenarios are generated

### Implementation for User Story 3

- [ ] T031 [US3] Implement phase_3_add_tests() in main.py to request test cases from AI in src/function_generator/main.py
- [ ] T032 [US3] Create test generation prompt template specifying unittest framework requirements in src/function_generator/main.py
- [ ] T033 [US3] Update display logic to show "=== Test Cases ===" section in src/function_generator/main.py
- [ ] T034 [US3] Add validation to ensure tests use unittest framework in src/function_generator/code_extractor.py
- [ ] T035 [US3] Handle cases where AI returns tests without original function in src/function_generator/code_extractor.py
- [ ] T036 [US3] Add error handling for incomplete test coverage in src/function_generator/main.py

**Checkpoint**: At this point, all three generation phases work - users see progression from basic → documented → tested code

---

## Phase 6: User Story 4 - Save Complete Function to File (Priority: P1)

**Goal**: Save final generated code (documented function + tests) to a properly named Python file

**Independent Test**: Complete the generation process and verify a .py file is created with appropriate name derived from description

### Implementation for User Story 4

- [ ] T037 [P] [US4] Implement FileWriter.generate_filename() with sanitization logic in src/function_generator/file_writer.py
- [ ] T038 [P] [US4] Implement FileWriter.write_code_file() for writing to current directory in src/function_generator/file_writer.py
- [ ] T039 [P] [US4] Implement FileWriter.check_file_exists() for overwrite warning in src/function_generator/file_writer.py
- [ ] T040 [US4] Integrate FileWriter into main workflow after phase 3 in src/function_generator/main.py
- [ ] T041 [US4] Add filename display in final output confirmation in src/function_generator/main.py
- [ ] T042 [US4] Add error handling for file write permissions in src/function_generator/file_writer.py
- [ ] T043 [US4] Add error handling for invalid filenames (special characters, length) in src/function_generator/file_writer.py

**Checkpoint**: Complete workflow - users can generate, view, and save functions to files

---

## Phase 7: Integration & Main Entry Point

**Purpose**: Wire all components together into a cohesive CLI application

- [ ] T044 Create main() function as CLI entry point in src/function_generator/main.py
- [ ] T045 Implement develop_custom_function() to orchestrate all three phases in src/function_generator/main.py
- [ ] T046 Add command-line argument parsing (if needed) in src/function_generator/main.py
- [ ] T047 Add informative print statements for each phase in src/function_generator/main.py
- [ ] T048 Implement graceful error handling and user-friendly error messages in src/function_generator/main.py
- [ ] T049 Add environment variable validation (check OPENAI_API_KEY exists) in src/function_generator/ai_client.py
- [ ] T050 Create __main__.py to enable python -m execution in src/function_generator/__main__.py

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final touches

- [ ] T051 [P] Add docstrings to all public methods following PEP 257 in src/function_generator/*.py
- [ ] T052 [P] Add inline comments for complex logic (especially regex patterns) in src/function_generator/code_extractor.py
- [ ] T053 [P] Update README.md with complete usage examples and troubleshooting in README.md
- [ ] T054 [P] Create comprehensive quickstart guide based on quickstart.md in docs/QUICKSTART.md
- [ ] T055 Handle edge case: very long function descriptions (truncate or warn) in src/function_generator/main.py
- [ ] T056 Handle edge case: API key missing or invalid (clear error message) in src/function_generator/ai_client.py
- [ ] T057 Handle edge case: malformed AI responses (retry or fallback) in src/function_generator/ai_client.py
- [ ] T058 Add logging for debugging (optional, use Python logging module) in src/function_generator/*.py
- [ ] T059 Validate all file paths are cross-platform compatible (Windows, macOS, Linux) in src/function_generator/file_writer.py
- [ ] T060 Run manual end-to-end test with sample function descriptions from quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 (Phase 3): Can start after Foundational - No dependencies on other stories
  - US2 (Phase 4): Depends on US1 completion (needs basic code generation working)
  - US3 (Phase 5): Depends on US2 completion (needs documented code to add tests)
  - US4 (Phase 6): Can start after Foundational - Independent but integrates with all phases
- **Integration (Phase 7)**: Depends on all user stories (US1-4) being complete
- **Polish (Phase 8)**: Depends on Integration completion

### User Story Dependencies

```
US1 (Generate Basic Code) → US2 (Add Documentation) → US3 (Add Tests)
                                                           ↓
US4 (Save to File) ←──────────────────────────────────────┘
```

- **User Story 1 (P1)**: Foundation for all other stories - must complete first
- **User Story 2 (P2)**: Depends on US1 (needs basic code to document)
- **User Story 3 (P3)**: Depends on US2 (needs documented code to test)
- **User Story 4 (P1)**: Independent implementation, but integrates with final output from US3

### Within Each User Story

- US1: Conversation → CodeExtractor & AIClient (parallel) → main.py orchestration
- US2: Prompt template → AI call → validation → display
- US3: Prompt template → AI call → validation → display
- US4: FileWriter methods (parallel) → integration with main workflow

### Parallel Opportunities

**Phase 1 (Setup)**: T003, T004, T005, T006, T007 can all run in parallel

**Phase 2 (Foundational)**:
- T010 & T011 can run in parallel (FileWriter & AIClient are independent)
- T008 & T009 can run in parallel after reviewing data model

**Phase 3 (US1)**:
- T017 & T018 (CodeExtractor methods) can run in parallel
- T019 & T020 (AIClient methods) must be sequential

**Phase 6 (US4)**:
- T037, T038, T039 (all FileWriter methods) can run in parallel

**Phase 8 (Polish)**:
- T051, T052, T053, T054 (documentation tasks) can all run in parallel

---

## Parallel Example: User Story 1

```bash
# After T016 completes, launch these in parallel:
Task T017: "Implement CodeExtractor.extract_code_block() in src/function_generator/code_extractor.py"
Task T018: "Implement CodeExtractor.validate_python_syntax() in src/function_generator/code_extractor.py"

# After T018 completes, continue with:
Task T019: "Implement AIClient.__init__() in src/function_generator/ai_client.py"
```

---

## Parallel Example: User Story 4

```bash
# All FileWriter methods can be implemented in parallel:
Task T037: "Implement FileWriter.generate_filename() in src/function_generator/file_writer.py"
Task T038: "Implement FileWriter.write_code_file() in src/function_generator/file_writer.py"
Task T039: "Implement FileWriter.check_file_exists() in src/function_generator/file_writer.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 4 Only)

**Minimal Viable Product** - Get a working version quickly:

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T012) - CRITICAL
3. Complete Phase 3: User Story 1 (T013-T025) - Basic code generation
4. Complete Phase 6: User Story 4 (T037-T043) - File saving
5. Complete Phase 7: Integration (T044-T050)
6. **STOP and VALIDATE**: Test end-to-end workflow
7. **MVP ACHIEVED**: Users can generate basic Python functions and save them

**Why this works**:
- User Story 1 (generate code) + User Story 4 (save file) = minimal useful tool
- User Stories 2 & 3 (documentation and tests) are valuable but not essential for MVP
- Can deploy and get user feedback quickly

### Incremental Delivery

**Full Feature Set** - Add value incrementally:

1. Complete Setup + Foundational → Foundation ready (T001-T012)
2. Add User Story 1 → Test independently → **Demo basic generation** (T013-T025)
3. Add User Story 2 → Test independently → **Demo with documentation** (T026-T030)
4. Add User Story 3 → Test independently → **Demo with tests** (T031-T036)
5. Add User Story 4 → Test independently → **Demo complete workflow** (T037-T043)
6. Integration → Complete tool (T044-T050)
7. Polish → Production ready (T051-T060)

Each increment adds demonstrable value!

### Sequential Development (Single Developer)

**Recommended order**:

1. **Phase 1**: Setup (1 hour)
2. **Phase 2**: Foundational (3-4 hours)
3. **Phase 3**: US1 - Basic generation (4-5 hours)
4. **Phase 4**: US2 - Documentation (2 hours)
5. **Phase 5**: US3 - Tests (2 hours)
6. **Phase 6**: US4 - File saving (2 hours)
7. **Phase 7**: Integration (2 hours)
8. **Phase 8**: Polish (2-3 hours)

**Total estimated time**: 18-22 hours for complete implementation

### Parallel Team Strategy

With 2-3 developers after Foundational phase:

1. **Team completes Setup + Foundational together** (Phases 1-2)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (Phase 3) - Core generation logic
   - **Developer B**: User Story 4 (Phase 6) - File I/O operations
   - **Developer C**: User Story 2 (Phase 4) - Documentation enhancement
3. After US1 + US4 complete:
   - Developer A integrates (Phase 7)
   - Developer B works on US3 (Phase 5) - Test generation
   - Developer C starts polish (Phase 8)
4. Final integration and testing together

**Time savings**: Can complete in 8-10 hours with 3 developers vs 18-22 hours solo

---

## Notes

- **[P] tasks**: Different files, no dependencies - safe for parallel execution
- **[Story] label**: Maps task to specific user story for traceability and independent testing
- **No tests included**: Per requirements, the tool generates tests as output but doesn't have its own test suite in this implementation
- **Critical path**: Setup → Foundational → US1 → US2 → US3 → Integration → Polish
- **MVP path**: Setup → Foundational → US1 → US4 → Integration (skip US2, US3 initially)
- **Validation**: After each user story phase, test that story independently before proceeding
- **Error handling**: Incorporated throughout all phases, especially for AI communication
- **Cross-platform**: File operations validated for Windows, macOS, Linux compatibility

---

## Task Summary

**Total Tasks**: 60
**By Phase**:
- Phase 1 (Setup): 7 tasks
- Phase 2 (Foundational): 5 tasks
- Phase 3 (US1): 13 tasks
- Phase 4 (US2): 5 tasks
- Phase 5 (US3): 6 tasks
- Phase 6 (US4): 7 tasks
- Phase 7 (Integration): 7 tasks
- Phase 8 (Polish): 10 tasks

**By User Story**:
- US1 (Generate Basic Code): 13 tasks
- US2 (Add Documentation): 5 tasks
- US3 (Generate Tests): 6 tasks
- US4 (Save to File): 7 tasks
- Infrastructure/Integration: 29 tasks

**Parallel Opportunities**: 15 tasks marked [P] can run in parallel within their phases

**MVP Scope**:
- Minimum: Phases 1, 2, 3 (US1), 6 (US4), 7 = 32 tasks
- Full: All 60 tasks

**Independent Test Criteria Met**: Each user story can be tested independently and delivers standalone value
