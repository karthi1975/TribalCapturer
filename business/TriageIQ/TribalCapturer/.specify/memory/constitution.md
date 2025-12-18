<!--
  SYNC IMPACT REPORT
  Version Change: Initial → 1.0.0
  Modified Principles: N/A (initial creation)
  Added Sections:
    - Core Principles (5 principles: Healthcare-First, Multi-Channel Capture, Test-First, Data Privacy & Security, Simplicity)
    - Technical Standards
    - Development Workflow
    - Governance
  Removed Sections: N/A
  Templates Requiring Updates:
    ✅ plan-template.md - Constitution Check section verified compatible
    ✅ spec-template.md - Requirements alignment verified
    ✅ tasks-template.md - Task categorization supports principles
  Follow-up TODOs: None
-->

# TribalCapturer Constitution

## Core Principles

### I. Healthcare-First Design

The TribalCapturer system exists to improve patient care by capturing and operationalizing tribal knowledge in healthcare scheduling. Every feature MUST:

- Prioritize patient safety and continuity of care
- Preserve the nuance and context of tribal knowledge
- Support real-world clinical workflows without adding friction
- Enable schedulers to make better, faster decisions

**Rationale**: Healthcare scheduling directly impacts patient outcomes. System design must respect the complexity of clinical care and empower, not replace, human expertise.

### II. Multi-Channel Knowledge Capture

Knowledge capture MUST support multiple input channels to accommodate different types of tribal knowledge:

- **Direct Entry**: Free-text portal for explicit knowledge with minimal structure
- **Prompted Mining**: Scenario-based questionnaires to extract implicit knowledge
- **Friction Capture**: Real-time logging of scheduling problems and their solutions
- **Pattern Analysis**: Automated detection of knowledge from historical data
- **Feedback Loop**: Learning from AI recommendation acceptance/override

**Rationale**: Tribal knowledge exists in multiple forms (explicit, implicit, contextual, relational, temporal). A single capture method will miss critical insights that only emerge in context.

### III. Test-First Development (NON-NEGOTIABLE)

Test-Driven Development (TDD) is MANDATORY for all feature work:

1. Write automated tests FIRST based on acceptance criteria
2. Verify tests FAIL before implementation begins
3. Implement feature until tests pass
4. Refactor while keeping tests green
5. All tests MUST pass before committing code

**Contract & Integration Tests** are required for:
- New API endpoints and data models
- Changes to existing contracts or schemas
- Inter-service communication points
- Knowledge extraction and rule generation pipelines

**Rationale**: Healthcare systems require high reliability. TDD ensures correctness, enables confident refactoring, and serves as living documentation. This is non-negotiable because patient care depends on system accuracy.

### IV. Data Privacy & Security

Patient data and tribal knowledge MUST be protected:

- HIPAA compliance is MANDATORY for all patient-related data
- Knowledge entries MUST support role-based access control (RBAC)
- Audit logging REQUIRED for all knowledge creation, modification, and rule application
- Personal identifiers in knowledge entries MUST be flagged for review
- Data retention policies MUST align with healthcare regulatory requirements

**Rationale**: Healthcare data is highly sensitive. Tribal knowledge often contains implicit patient information. Security and privacy must be built-in, not bolted-on.

### V. Simplicity & Pragmatism

Start with the simplest solution that solves the problem:

- Avoid premature optimization and over-engineering
- Use proven technologies and patterns appropriate to healthcare systems
- Prefer boring, reliable solutions over cutting-edge complexity
- Only add abstraction when multiple real examples demand it (Rule of Three)
- Keep knowledge extraction NLP pipeline transparent and debuggable

**Rationale**: Healthcare systems must be maintainable and reliable. Complexity is the enemy of both. YAGNI (You Aren't Gonna Need It) prevents technical debt.

## Technical Standards

### Technology Stack

- **Backend**: Python 3.11+ with FastAPI or Django for healthcare system integration
- **Database**: PostgreSQL for relational data with JSONB for flexible knowledge schemas
- **NLP/AI**: OpenAI GPT-based extraction with transparent prompt engineering
- **Testing**: pytest with contract testing (Pact or similar)
- **Authentication**: OIDC/SAML for enterprise SSO integration

### Code Quality

- Type hints REQUIRED for all Python functions
- Linting with `ruff` or `pylint` (enforced in CI)
- Code formatting with `black` (enforced in CI)
- Maximum function complexity: 10 (cyclomatic)
- Test coverage minimum: 80% for core business logic

### API Design

- RESTful conventions for all endpoints
- OpenAPI 3.0 specification REQUIRED for all APIs
- Versioning: `/api/v1/` prefix for all endpoints
- Error responses MUST use standard HTTP status codes with detailed error messages
- All endpoints MUST support JSON input/output

### Observability

- Structured logging (JSON format) for all services
- Log levels: DEBUG for development, INFO for production
- Correlation IDs for request tracing across services
- Performance metrics for knowledge extraction pipeline
- Alert thresholds for rule application failures

## Development Workflow

### Branch Strategy

- `main` branch is always deployable
- Feature branches: `###-feature-name` format (e.g., `001-knowledge-portal`)
- Branch protection: MUST pass all tests + code review before merge

### Code Review Requirements

- All code MUST be reviewed by at least one other developer
- Reviewers MUST verify:
  - Tests exist and pass
  - Constitution principles followed
  - HIPAA compliance considered
  - Documentation updated
- No self-merging allowed

### Commit Standards

- Commits MUST follow Conventional Commits format
- Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`
- Include task ID in commit message: `feat(T042): add friction capture endpoint`

### Testing Gates

Before merging to `main`:
1. All unit tests pass
2. All integration tests pass
3. Contract tests pass (if contracts changed)
4. Code coverage meets 80% threshold
5. Linting passes with no errors

## Governance

### Constitution Authority

This constitution supersedes all other development practices and guidelines. When conflicts arise, the constitution takes precedence.

### Amendment Process

1. Proposed amendments MUST be documented with:
   - Rationale for change
   - Impact analysis on existing principles
   - Migration plan for affected code
2. Amendments REQUIRE approval from project lead and technical architect
3. Version increments:
   - **MAJOR**: Backward-incompatible changes, principle removals, or redefinitions
   - **MINOR**: New principles, sections, or material expansions
   - **PATCH**: Clarifications, wording fixes, non-semantic refinements
4. All templates in `.specify/templates/` MUST be updated to reflect constitutional changes

### Compliance Review

- Code reviews MUST verify constitutional compliance
- Complexity introduced MUST be justified against Principle V (Simplicity)
- Privacy/security violations are automatic PR rejections
- Test-first violations require explanation and remediation plan

### Violation Remediation

When constitutional violations are discovered:
1. Document the violation and impact
2. Create remediation task with priority based on principle violated
3. Non-negotiable principles (Test-First, Privacy & Security) require immediate remediation
4. Preferential principles (Simplicity) require remediation within current sprint

**Version**: 1.0.0 | **Ratified**: 2025-12-17 | **Last Amended**: 2025-12-17
