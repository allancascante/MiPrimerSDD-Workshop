<!--
Sync Impact Report
Version change: unversioned → 1.0.0 (initial constitution)
Modified principles: template placeholders → five project principles below
Added sections: Additional Constraints; Development Workflow
Removed sections: none
Follow-up TODO: confirm the original ratification date.
-->
# Curso-PSWE-07 Constitution

## Core Principles

### I. SIMPLICITY FIRST (YAGNI)
The implementation MUST include only what the specification requires and MUST choose the
simplest solution that works; added complexity MUST be justified in writing in the plan.
Rationale: Unneeded features and complexity increase cost without serving an agreed need.

### II. SIMPLE, CLEAR DESIGN
Code MUST use small, single-responsibility functions and modules and clear names; it MUST avoid
duplication only when it is real, MUST NOT build abstractions for a single use, and MUST NOT
optimize prematurely.
Rationale: Clear, focused code is easier to understand and change.

### III. STRUCTURED ARCHITECTURE
The application MUST separate UI, application logic, and persistence, with dependencies flowing
UI → logic → persistence; UI MUST NOT access storage directly, and persistence MUST be hidden
behind a small interface that can be replaced or faked in tests.
Rationale: Clear boundaries make behavior testable and storage replaceable.

### IV. TEST-DRIVEN DEVELOPMENT (NON-NEGOTIABLE)
Production code MUST be preceded by a failing test and follow Red-Green-Refactor; business logic
MUST have unit tests, each user story MUST have at least one acceptance test mirroring its
acceptance scenarios, and tests MUST be fast and independent.
Rationale: Tests verify behavior while guiding the smallest implementation that meets it.

### V. SPEC IS THE SOURCE OF TRUTH
Every implementation task MUST trace to a specification requirement; anything not specified
MUST remain out of scope, and ambiguity MUST be clarified before implementation.
Rationale: Traceability prevents unapproved assumptions from becoming product behavior.

## Additional Constraints

The approved specification defines product scope. No unrequested feature, dependency, or
configuration option may be introduced.

## Development Workflow

Plans MUST identify the specification requirements addressed by their tasks and justify any
complexity beyond the simplest solution. Reviews MUST verify traceability, architectural
boundaries, and required test coverage.

## Governance

Amendments MUST be documented in this file and reviewed before adoption. Version numbers use
MAJOR.MINOR.PATCH: MAJOR for incompatible rule changes, MINOR for new or materially expanded
rules, and PATCH for clarifications or non-semantic edits. Plans and reviews MUST assess
compliance with these principles; deviations MUST be justified in writing and approved before
implementation.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): confirm original adoption date | **Last Amended**: 2026-10-22
