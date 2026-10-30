---
description: "Executable tasks for the Curso-PSWE-07 full-screen TUI"
---

# Tasks: Curso-PSWE-07 Daily Tasks TUI

**Input**: Design documents in `specs/001-manage-daily-tasks/`.
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md),
[research.md](./research.md), [data-model.md](./data-model.md),
[TUI contract](./contracts/tui.md), and [quickstart.md](./quickstart.md).
**Tests**: Mandatory under constitution Principle IV. Write tests, observe the intended
failure, implement the minimum behavior, and refactor with tests green. Do not implement
later-story behavior merely to make a future acceptance test pass.
**Organization**: Setup, foundation, five story increments in priority order, then final
cross-story validation. All paths below are repository-relative.

## Format: `[ID] [P?] [Story] Description`

- Every task is initially unchecked; checking it requires its described outcome.
- `[P]` identifies tasks that may run together after their listed prerequisites, in
  different files. It never overrides test-first ordering.
- `[US1]` through `[US5]` map to the exact numbered stories in the specification.
- Requirement IDs in each task identify the behavior it implements or verifies.

## Path Conventions

Use the root package `curso_pswe_07/` and `tests/{unit,integration,acceptance}/` from the
plan. No `src/`, web frontend, API server, old line-input CLI, or new feature directory.
Do not modify read-only attachment snapshots; the current interface contract is
[contracts/tui.md](./contracts/tui.md).

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the planned runtime, dependency, and test layout without adding
application behavior.

- [X] T001 Select an available Python 3.11+ interpreter (or obtain approval to install one if absent), verify its version, and create the repository-local `.venv/`; do not use the detected Python 3.9.6 (plan runtime prerequisite).
- [X] T002 Declare only `textual==8.2.8` without extras in `requirements.txt`, install it into `.venv/`, and verify its resolved version and imports; do not add pytest or syntax extras (plan dependency decision; FR-017–FR-019).
- [X] T003 [P] Create empty package/discovery markers in `curso_pswe_07/__init__.py`, `tests/__init__.py`, `tests/unit/__init__.py`, `tests/integration/__init__.py`, and `tests/acceptance/__init__.py` (plan project layout; constitution IV).
- [X] T004 [P] Update `.gitignore` to exclude `.venv/`, Python bytecode, and test caches, preserving existing entries; never commit local task data (plan local environment/storage).

**Checkpoint**: Python 3.11+ and the pinned dependency are usable; test discovery can
import test packages. Setup does not create production operations or dummy success stubs.

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define the shared task data and application-owned storage boundary.

- [X] T005 Write failing model/snapshot tests in `tests/unit/test_service.py` quoting these data-model constraints: id "Unique, immutable, internal identity; duplicate titles remain independent"; title "Required; `title.strip()` must not be empty; retain valid entered text"; description "Optional input; absent or whitespace-only becomes `""`"; done "New tasks start `false`; maps to Pending/Done". Also assert positive integer IDs (not booleans), filter values "All, Pending, Done" with "Starts All; retained during navigation, never persisted", no artificial text-length limit, and unchanged valid Unicode text (FR-002, FR-005, FR-016).
- [X] T006 Implement only the tested Task, TaskSnapshot, and completion-filter definitions and validation in `curso_pswe_07/models.py`; preserve the quoted constraints, with tasks/next_id in the snapshot and no UI or storage imports (T005; FR-002, FR-005; constitution III).
- [X] T007 Extend failing tests in `tests/unit/test_service.py` with a test-local fake store for load/get/list, explicit unknown-ID errors, and failed-save snapshot preservation; define expected `TaskStore.load()`/`save(snapshot)` behavior before production implementation (FR-003, FR-014, FR-015).
- [X] T008 Define the small TaskStore protocol, expected application/storage error types, initial service state, snapshot access, and candidate-save-then-publish boundary in `curso_pswe_07/service.py`; validate with the fake from T007, keep Textual/file-path logic out, and do not add unused CRUD methods (FR-003, FR-014, FR-015; constitution III).

**Checkpoint**: Foundation unit tests pass; a fake can replace persistence without the
UI or service importing the concrete adapter. No story work begins before T008.

## Phase 3: User Story 1 - Add and view daily tasks (Priority: P1) - MVP slice

**Goal**: Create validated Pending tasks and navigate List/Detail through a bordered,
keyboard-operated Add dialog.
**Independent Test**: With a fresh fake store, add tasks with/without descriptions, reject
empty titles without losing drafts, cancel Add, open the selected row, and return to List.
Use All for this increment; the Done-filter branch of scenario 2 is completed by US2.

### Tests for User Story 1

- [X] T009 [P] [US1] Add failing creation tests in `tests/unit/test_service.py` for distinct IDs with duplicate titles, Pending default, description normalization, validation before save, immutable old snapshot on failure, and incrementing next_id only after successful creation (FR-002, FR-005, FR-015).
- [X] T010 [P] [US1] Add failing Pilot acceptance tests in `tests/acceptance/test_tui.py` for US1 scenarios 1–6 under All: Curso-PSWE-07 frame, empty message/Add, create/open/back, No description, rejected title/draft retention, and Cancel creating nothing; use `IsolatedAsyncioTestCase`, fresh fake storage, and actual keyboard activation (FR-001, FR-003–FR-005, FR-008, FR-009, FR-016–FR-018).
- [X] T011 [P] [US1] Add failing Add-dialog contract tests in `tests/acceptance/test_dialogs.py` for initial title focus, Tab/Shift+Tab trapping, editable description, explicit Save, Escape/Cancel, title-required error focus, and no background shortcuts during text entry (FR-004, FR-005, FR-018).

### Implementation for User Story 1

- [X] T012 [US1] Implement validated create in `curso_pswe_07/service.py` with unique immutable IDs, next_id allocation, Pending status, and candidate commit before publication; make T009 pass without adding edit/delete prematurely (FR-002, FR-005, FR-015).
- [X] T013 [US1] Implement the shared TaskDialog structure in `curso_pswe_07/dialogs.py` for Add with Input/TextArea, Save/Cancel, validation/save-error display and retained draft, Escape cancellation, disabled tab insertion, and guarded field key routing; make T011 pass (FR-004, FR-005, FR-015, FR-018).
- [X] T014 [US1] Implement the Textual App, List/Detail screens and service injection in `curso_pswe_07/tui.py`, including selected-ID navigation, All initial filter, empty state, back control, status/No description, Add integration, and restoration of initiating focus; make T010 pass using only application-service calls (FR-001, FR-003, FR-004, FR-008, FR-009, FR-016).
- [X] T015 [US1] Style the tested frame, List/Detail content and Add dialog in `curso_pswe_07/styles.tcss` with character borders, visible focus/selection markers, fixed action/hints region and a scrollable body; assert the rendered regions in T010/T011 before adding each styling behavior (FR-017, FR-018).
- [X] T016 [US1] Run US1 unit/Pilot tests via `.venv/bin/python -m unittest tests.unit.test_service tests.acceptance.test_tui tests.acceptance.test_dialogs -v` and resolve only related failures in `curso_pswe_07/`; verify all six scenarios applicable to this increment and no UI storage imports (FR-001–FR-005, FR-008, FR-009).

**Checkpoint**: The injectable TUI is a testable in-memory demo, not yet a persistent,
launchable release. Never wire a fake store into the production entry point.

## Phase 4: User Story 2 - Track completion and filter tasks (Priority: P1)

**Goal**: Change status and navigate All/Pending/Done consistently.
**Independent Test**: Seed mixed statuses through the fake; toggle both ways in Detail,
return to each filter, and verify labels, membership, selection, and no-match state.

### Tests for User Story 2

- [X] T017 [P] [US2] Add failing status/filter service tests in `tests/unit/test_service.py` for both transitions, unchanged identity/details, exact filter membership, duplicate-title independence, and original state on save failure (FR-006, FR-007, FR-012, FR-015).
- [X] T018 [P] [US2] Add failing Pilot cases in `tests/acceptance/test_tui.py` covering all five US2 scenarios, explicit active-filter/status markers, changing status from Pending/Done and navigating back, no matching tasks, and adding a Pending task while Done stays selected (FR-006–FR-008, FR-010, FR-012, FR-016).

### Implementation for User Story 2

- [X] T019 [US2] Implement completion changes and exact All/Pending/Done filtering in `curso_pswe_07/service.py`, preserving candidate-save-then-publish and task identity; make T017 pass (FR-006, FR-012, FR-015).
- [X] T020 [US2] Add filter controls and completion actions to `curso_pswe_07/tui.py`, retaining active filter during navigation/Add and refreshing labels, visible membership and selected row without stale data; make T018 pass (FR-006–FR-008, FR-010, FR-012, FR-016).
- [X] T021 [US2] Add tested active-filter and Done/Pending textual presentation to `curso_pswe_07/styles.tcss` and `curso_pswe_07/tui.py`, distinguishing focus, selection, and filter without color/strikethrough dependence (FR-007, FR-017).
- [X] T022 [US2] Run US1/US2 regression tests in `tests/unit/test_service.py`, `tests/acceptance/test_tui.py`, and `tests/acceptance/test_dialogs.py`; verify all US2 scenarios and US1's Done-filter creation branch pass (FR-006–FR-008, FR-010, FR-012, FR-016).

## Phase 5: User Story 3 - Keep task changes between sessions (Priority: P1)

**Goal**: Commit normal-mode data safely and preserve the original file through explicit
load-error temporary sessions.
**Independent Test**: Use temporary files and prepared snapshots to check additions,
edits, statuses, and deletions through adapter round trips; recreate app/service and
verify temporary sessions never save. Full edit/delete UI paths are integrated after US4.

### Tests for User Story 3

- [X] T023 [P] [US3] Add failing adapter tests in `tests/integration/test_storage.py` for missing-file first use and exact schema constraints: "`version` must be the integer 1"; "`next_id` is a positive integer greater than every stored ID"; "Reject duplicate IDs, duplicate JSON object keys, missing/extra fields, non-boolean `done`, and wrong types"; "Booleans do not count as integers for IDs, version, or next_id despite Python's integer subtype relationship"; include Unicode, malformed JSON, unreadable file, wrong encoding, insertion order, and no UI state persisted (FR-002, FR-014, FR-015).
- [X] T024 [P] [US3] Add failing persistence/recovery acceptance tests in `tests/acceptance/test_persistence.py` using isolated homes, separate App/service instances, load failure then temporary create/view/filter/status actions, permanently visible unsaved notice, no save calls, and reopen of untouched original data; use prepared snapshots for edit/delete until US4 is available (FR-014, FR-015; US3 scenarios 1–6).
- [X] T025 [US3] Extend failing tests in `tests/integration/test_storage.py` for sibling-temp-file atomic writes, serialization/write/flush/fsync/close/replace errors, cleanup errors reported alongside the primary error, original bytes unchanged before commit, and successful replacement authoritative afterward (FR-014, FR-015).

### Implementation for User Story 3

- [X] T026 [US3] Implement strict UTF-8 JSON loading in `curso_pswe_07/storage.py` with the exact T023 constraints, empty first-use snapshot `next_id: 1`, explicit format/read errors, and no automatic file repair or broad exception fallback; make load tests pass (FR-014, FR-015).
- [X] T027 [US3] Implement saving in `curso_pswe_07/storage.py`: validate candidate, create parent on first save, stage a secure sibling file, serialize/flush/fsync/close, replace as commit, and clean up only that named file on failure with explicit cleanup diagnostics; make T025 pass (FR-014, FR-015).
- [X] T028 [US3] Implement immutable persistent/temporary session mode and load-error reporting in `curso_pswe_07/service.py`; temporary mutations publish only in memory, never call persistent save, never retry/merge mid-session, and reset on new service creation; make T024 pass for available operations (FR-014, FR-015).
- [X] T029 [US3] Add in-TUI saved/error/temporary results and permanent topmost unsaved notices in `curso_pswe_07/tui.py` and `curso_pswe_07/dialogs.py`, including Save retry with retained draft and failed status changes retaining old state; add failing Pilot assertions before each new message/banner behavior (FR-015).
- [X] T030 [US3] Write failing startup/noninteractive/exit-status tests in `tests/acceptance/test_terminal.py`, then implement the real composition root in `curso_pswe_07/__main__.py` using the home JSON adapter/service/TUI; reject noninteractive startup with stderr/status 2, expose orderly Exit/Ctrl+Q and Ctrl+C/SIGINT handling, and never save on exit (FR-014, FR-018, FR-020).
- [X] T031 [US3] Run adapter, recovery and startup tests in `tests/integration/test_storage.py`, `tests/acceptance/test_persistence.py`, and `tests/acceptance/test_terminal.py`; verify real-file create/status reopen and all failure cases implemented so far, leaving edit/delete UI persistence integration explicitly for T038 (FR-014, FR-015).

**Checkpoint**: A persistent add/view/filter/status app can launch. Adapter round trips
cover all saved shapes; complete US3 UI evidence remains gated on US4 and T038.

## Phase 6: User Story 4 - Edit and delete tasks safely (Priority: P2)

**Goal**: Reuse the task editor and require deliberate deletion with safe cancellation.
**Independent Test**: Seed tasks directly; save/cancel/validate edits, clear a description,
cancel/confirm deletion, and verify identity, status, focus, filters, and reopened state.

### Tests for User Story 4

- [X] T032 [P] [US4] Add failing edit/delete unit tests in `tests/unit/test_service.py`: immutable ID/status on edit, duplicate-title independence, no next_id decrement on deletion, unknown-ID errors and old snapshots retained on save failure (FR-005, FR-011, FR-013, FR-015).
- [X] T033 [P] [US4] Add failing Pilot contract tests in `tests/acceptance/test_dialogs.py` covering all seven US4 scenarios, shared Add/Edit dialog, prefilled fields, saved/cleared descriptions, canceled/invalid edits, initially focused Cancel on deletion, Escape/immediate Enter cancel, explicit Confirm, storage failures and focus restoration (FR-005, FR-011, FR-013, FR-015, FR-018).

### Implementation for User Story 4

- [X] T034 [US4] Implement edit/delete service operations in `curso_pswe_07/service.py` with unchanged ID/status on edit, normalized optional description, independent duplicate titles, monotonically allocated next_id, and atomic candidate publication; make T032 pass (FR-005, FR-011, FR-013, FR-015).
- [X] T035 [US4] Complete the shared Edit mode and DeleteDialog in `curso_pswe_07/dialogs.py`, including prefilled fields, explicit Save/Cancel, warning, initially focused Cancel, modal focus isolation, Escape cancellation, visible retryable errors, and temporary-mode wording/banner; make T033 pass (FR-011, FR-013, FR-015, FR-018).
- [X] T036 [US4] Wire Edit/Delete into Detail and refresh List/Detail/focus in `curso_pswe_07/tui.py`; deletion returns to prior filter with a remaining selected row or Add focus, and cancellation restores the initiating control without changing data (FR-010–FR-013, FR-016).
- [X] T037 [US4] Extend failing rendered-region assertions in `tests/acceptance/test_dialogs.py`, then update `curso_pswe_07/styles.tcss` so Edit/Delete warnings, errors, and action rows fit while the temporary banner remains visible (FR-013, FR-017, FR-019).
- [X] T038 [US4] Complete end-to-end US3 edit/delete and temporary-edit/delete persistence cases in `tests/acceptance/test_persistence.py`; drive real dialogs, recreate the app, verify all saved transitions and no temporary writes, and fix only related wiring failures in `curso_pswe_07/` (FR-014, FR-015; US3 scenarios 1–6).
- [X] T039 [US4] Run the US1–US4 regression suites in `tests/unit/`, `tests/integration/`, `tests/acceptance/test_tui.py`, `tests/acceptance/test_dialogs.py`, and `tests/acceptance/test_persistence.py`; verify all seven US4 and six US3 scenarios are covered and passing (SC-002, SC-003).

## Phase 7: User Story 5 - Use a DOS-style full-screen terminal interface (Priority: P2)

**Goal**: Complete all keyboard, scrolling, modal, resize, and real-terminal lifecycle
guarantees beyond the basic borders and navigation already required by earlier stories.
**Independent Test**: With seeded tasks and temporary storage, navigate every action at
80x24/100x30, access long content, resize with drafts/confirmation, and verify terminal
restoration after normal exit and interruption.

### Tests for User Story 5

- [X] T040 [P] [US5] Add failing Pilot tests in `tests/acceptance/test_tui.py` for full-screen windows/menus, color-independent `>` focus/selection markers, action/filter arrow navigation, Tab/Shift+Tab, Enter/Space, Home/End/PageUp/PageDown, unknown shortcuts, disabled command palette, and keyboard access to every action (FR-017, FR-018; US5 scenarios 1–2).
- [X] T041 [P] [US5] Add failing resize/scrolling tests in `tests/acceptance/test_resize.py` at 80x24/100x30 and below-minimum 79x24/80x23, using a 200-character title, 2,000-character description, long list, Unicode/control/markup-like text, repeated resizes, queued mutation callbacks, mounted draft/confirmation preservation, and unobscured temporary notices (FR-019; US5 scenarios 5–6).
- [X] T042 [P] [US5] Extend failing dialog tests in `tests/acceptance/test_dialogs.py` for complete focus traps, background shortcut isolation, literal text display, accessible scrolling/error/actions, retry/cancel, and focus restoration on all modal paths, including temporary mode (FR-017–FR-019; US5 scenarios 3–4, 7).
- [X] T043 [P] [US5] Add failing real-entry-point POSIX PTY tests in `tests/acceptance/test_terminal.py` for normal exit, Ctrl+C and delivered SIGINT, statuses 0/130, echo/canonical-mode and cursor/alternate-screen restoration, plus two-process close/reopen persistence in isolated homes; explicitly skip unsupported POSIX checks on Windows, never claim headless tests prove restoration (FR-014, FR-018; US5 scenario 8).

### Implementation for User Story 5

- [X] T044 [US5] Complete scoped bindings, action-group arrow focus, task-list paging/selection visibility, literal safe text and long Detail scrolling in `curso_pswe_07/tui.py`; suppress conflicting framework defaults and implement only the behavior required to pass T040/T041 (FR-017–FR-019).
- [X] T045 [US5] Implement one ResizeGuard over the existing mounted screen/modal stack in `curso_pswe_07/tui.py`; block each mutating handler at current size/context, including queued callbacks; restore draft, selection, filter, scroll and focus when both dimensions recover, without saves or stacked guards (T041; FR-019).
- [X] T046 [US5] Complete modal key routing/scrollable editor behavior in `curso_pswe_07/dialogs.py` and fixed header/banner/action layouts in `curso_pswe_07/styles.tcss`; make T042 and rendered-region checks pass at both supported sizes without hidden warnings/actions (FR-017–FR-019).
- [X] T047 [US5] Harden the tested lifecycle in `curso_pswe_07/__main__.py` and `curso_pswe_07/tui.py` for orderly framework cleanup on Exit/Ctrl+Q/Ctrl+C/SIGINT and unexpected errors; no broad catch, no implicit draft save, nonzero visible faults, restored terminal state; make T043 pass (FR-018).
- [X] T048 [US5] Run all eight US5 scenario groups in `tests/acceptance/test_tui.py`, `tests/acceptance/test_dialogs.py`, `tests/acceptance/test_resize.py`, and `tests/acceptance/test_terminal.py`; record platform-specific skips explicitly and fix related failures before declaring terminal guarantees complete (SC-004).

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Validate measurable outcomes and document only the finished behavior.

- [X] T049 Add and run a deterministic SC-005 measurement in `tests/acceptance/test_persistence.py` with 100 tasks and real isolated JSON commits, timing save/filter activation through completed rendered output with monotonic time; require every measured action under one second and record environment; any necessary production change must first have a failing test (SC-005).
- [X] T050 [P] Update `README.md` with actual Python/Textual setup, TUI invocation/keys, storage location, minimum size, temporary-mode warning, single-session limit, and test commands; reconcile `specs/001-manage-daily-tasks/quickstart.md` with verified behavior without removing the workshop's existing instructional content (FR-001, FR-014–FR-020).
- [ ] T051 Run real-terminal checks on macOS/Linux and Windows per `specs/001-manage-daily-tasks/quickstart.md`, recording version/platform, keyboard-only navigation, dialogs, resize, cursor/input restoration and outstanding platform gaps there; if a required environment is unavailable, leave this task incomplete and report the blocker (SC-004; FR-018, FR-019).
- [ ] T052 Conduct the specified SC-001 session with five first-time users and the three-task fixture (two Pending, one Done); record actual completion times/results in `specs/001-manage-daily-tasks/quickstart.md`, requiring at least four users to finish the full workflow within three minutes without coaching; leave incomplete if participants are unavailable (SC-001).
- [ ] T053 Run `.venv/bin/python -m unittest discover -s tests -v` on Python 3.11 and the selected newer supported interpreter, execute the verified quickstart, review `curso_pswe_07/tui.py`, `curso_pswe_07/dialogs.py`, `curso_pswe_07/service.py`, and `requirements.txt` for layer/scope compliance, and record FR-001–FR-020/SC-001–SC-005 evidence and any blockers in `specs/001-manage-daily-tasks/quickstart.md`; do not mark completion while required outcomes are unverified.

## Implementation status

T001–T050 are implemented and validated. All 44 automated tests pass on macOS with
Python 3.11.17 and 3.13.16 / Textual 8.2.8, including real POSIX PTY restoration,
isolated persistence, keyboard/resize cases and sub-second measurements with 100 tasks.
Syntax, dependency consistency and architectural import checks also pass.

T051 (manual cross-platform/Windows checks) and T052 (five first-time participants)
remain blocked by unavailable external environments/participants. T053 remains open
because it depends on those outcomes; its automated runtime and architecture portions
are verified. No manual results have been invented.
See [quickstart evidence](./quickstart.md#implementation-evidence-and-outstanding-gates).

## Dependencies & Execution Order

### Phase Dependencies

Setup -> Foundation -> US1 -> US2 -> US3 -> US4 -> US5 -> final validation.
This is the safe shared-file execution order, not a claim that every story has a logical
product dependency on every preceding story.

### Task Dependencies

All prerequisites below are mandatory; tasks in the same prerequisite row are not
implicitly parallel. Within a listed range, execute ascending IDs unless marked `[P]`
and explicitly identified as a parallel group below.

| Tasks | Prerequisites / ordering |
|-------|--------------------------|
| T001 | None |
| T002 | T001 |
| T003, T004 | T002; mutually independent |
| T005 | T003, T004 |
| T006 | T005 failing as intended |
| T007 | T006 |
| T008 | T007 failing as intended |
| T009–T011 | T008; mutually independent test files |
| T012 | T009 |
| T013 | T011 and T012's service interface |
| T014 | T010, T012, T013 |
| T015 | T014 and failing rendering assertions |
| T016 | T012–T015 |
| T017, T018 | T016; mutually independent |
| T019 | T017 |
| T020 | T018, T019 |
| T021 | T020 |
| T022 | T019–T021 |
| T023, T024 | T022; mutually independent |
| T025 | T023 (same test file) |
| T026 | T023, T025 |
| T027 | T026, T025 |
| T028 | T024, T027 |
| T029 | T028 |
| T030 | T029; failing startup tests precede its implementation |
| T031 | T030 |
| T032, T033 | T031; mutually independent |
| T034 | T032 |
| T035 | T033, T034 |
| T036 | T035 |
| T037 | T036; failing region assertions precede styling |
| T038 | T037 (closes deferred US3 UI cases) |
| T039 | T038 |
| T040–T043 | T039; mutually independent test files |
| T044 | T040, T041 |
| T045 | T044, T041 |
| T046 | T045, T042 |
| T047 | T046, T043 |
| T048 | T044–T047 |
| T049 | T048 |
| T050 | T048; can overlap T049 (different files) |
| T051 | T049, T050 |
| T052 | T051 and actual participant availability |
| T053 | T049–T052; missing manual evidence remains a blocker |

### User Story Dependencies

- **US1** depends only on foundation; its initial testable slice uses fake persistence.
- **US2** integrates with US1 navigation but tests independently using prepared task state.
- **US3** implements persistence generically and uses US1/US2 for interactive evidence.
  Full edit/delete UI evidence explicitly depends on US4/T038; do not prematurely mark
  US3 complete at T031. Snapshot round trips require no US4 production methods.
- **US4** builds on the shared US1 dialog and US3 save/error boundary; it can be tested
  with seeded tasks rather than exercising creation for every test.
- **US5** completes cross-cutting guarantees for all earlier views/dialogs and therefore
  requires their integration. Basic borders/focus are not postponed until US5.
- Every story has an isolated fixture and independent assertions; this does not imply
  that all story implementations can safely edit the same files concurrently.

### Within Each User Story

Tests precede production behavior. A failing import may establish missing structure, but
the meaningful red test must exercise the required behavior before it is implemented.
Make tests runnable as prerequisites arrive; do not use permanent skips, dummy success
stores in production, or future-story stubs to claim an increment passes.
Run focused tests after each behavior, then the story regression checkpoint.

### Parallel Opportunities

Parallel groups are limited to different-file test authoring and the explicit setup/docs
groups. Merge tests before their corresponding implementation; use one writer per shared
production file. No blanket parallel-story implementation is recommended.

## Parallel Example: User Story 1

After T008, author T009 in `tests/unit/test_service.py`, T010 in
`tests/acceptance/test_tui.py`, and T011 in `tests/acceptance/test_dialogs.py` together.
Then implement T012–T015 in dependency order.

## Parallel Example: User Story 2

After T016, author T017 service tests and T018 TUI tests in parallel. Service implementation
T019 must precede wiring T020; T021 touches that same UI, so keep it sequential.

## Parallel Example: User Story 3

After T022, author T023 storage tests and T024 recovery tests together. T025 extends the
same file as T023 and must wait. Keep adapter implementation and service/UI wiring ordered.

## Parallel Example: User Story 4

After T031, author T032 unit and T033 dialog tests together. Run the implementation tasks
sequentially because service, dialog, screen, and persistence evidence are connected.

## Parallel Example: User Story 5

After T039, author T040 keyboard, T041 resize, T042 modal, and T043 PTY tests concurrently
in their four separate files. Then complete T044–T047 in order without competing TUI edits.

## Implementation Strategy

### MVP First (User Story 1 Only)

Complete T001–T016 for the first independently testable Add/View demo using injected
fake storage. It is not a release: persistence and real entry-point wiring arrive in US3,
and resize/lifecycle guarantees finish in US5. Label this distinction honestly.

### Incremental Delivery

1. Foundation and US1: validated create/open/back dialog flow.
2. US2: status and exact filters with preserved navigation context.
3. US3: persistent launch and explicit temporary-mode behavior.
4. US4: safe edit/delete; complete all US3 saved-operation UI cases at T038.
5. US5: complete keyboard/resize/terminal guarantees, then measurable final validation.

The smallest durable workflow milestone is US1+US2+US3 for the then-supported operations.
The requested product is complete only after all five stories and final acceptance
outcomes, including human usability and real-platform evidence, are verified.

### Parallel Team Strategy

Use parallel test-authoring groups above; keep production changes single-owner when they
share files. Do not create extra abstractions, test dependencies, repositories, theme
options, or task features merely to enable parallel work.

## Notes

- 53 tasks: Setup 4; Foundation 4; US1 8; US2 6; US3 9; US4 8; US5 9; final validation 5.
- Follow the constitution's TDD mandate even where a task combines a regression test
  and its narrow fix; record meaningful red/green results during implementation.
- No code, dependencies, tests, runtime installations, or validation outcomes are created
  or claimed by this task-generation document.
- On Windows, use `.venv\Scripts\python.exe` instead of `.venv/bin/python`.
- Runtime/platform/participant blockers must remain visible; never invent successful
  measurements or check off unavailable manual validation.
