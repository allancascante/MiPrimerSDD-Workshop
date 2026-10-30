# Implementation Plan: Curso-PSWE-07 Daily Tasks TUI

**Branch**: `main` | **Date**: 2026-10-22 | **Spec**: [spec.md](./spec.md)

**Input**: `specs/001-manage-daily-tasks/spec.md`; full-screen DOS-style TUI revision.
Setup reports feature context `001-manage-daily-tasks`; the actual Git branch is `main`.
This plan replaces the previous line-input design without changing task or storage scope.

## Summary

Build a Python full-screen terminal application using Textual: character-drawn List/Detail
windows, a shared modal add/edit dialog, confirmed deletion, visible focus, keyboard menus,
scrolling, and resize protection. Preserve All/Pending/Done filters, atomic local JSON saves,
and the explicitly temporary, never-saved session after a load failure.

Textual replaces manual line input and transcript testing. The application service and
storage adapter stay framework-independent. No GUI, network service, extra task feature,
configuration flags, or alternative line-command interface is introduced.

## Technical Context

**Language/Version**: Python 3.11+; validate on 3.11 and the selected newer supported
interpreter. The currently detected Python 3.9.6 is below the project floor.

**Primary Dependencies**: `textual==8.2.8`, without optional extras, as the only direct
runtime dependency. Its transitive dependencies include Rich; record resolution in the
implementation environment. Use standard-library dataclasses, typing, JSON, pathlib,
tempfile, os, and unittest for non-UI code. Declare Textual in `requirements.txt` during
implementation; no manifest or installation is created in this planning phase.

**Storage**: Unchanged UTF-8 JSON at `~/.curso-pswe-07/tasks.json`; sibling temporary file,
flush/fsync/close, then atomic replacement. No persistent UI preferences or schema migration.

**Testing**: `unittest`, `IsolatedAsyncioTestCase`, `unittest.mock`, Textual
`App.run_test()`/Pilot, temporary files, and POSIX pseudo-terminal process tests.
No pytest/plugin or screenshot framework dependency is needed.

**Target Platform**: Modern macOS, Linux, and Windows interactive terminals with cursor
movement and keyboard input; minimum 80 columns by 24 rows. Test 80x24 and 100x30.
Redirected input/output is rejected with an explicit startup diagnostic, not a CLI fallback.

**Project Type**: Full-screen TUI launched from the repository with
`python3 -m curso_pswe_07` after dependency installation.

**Performance Goals**: Under one second from save/filter activation through persistence
and rendered state for 100 tasks, excluding human typing. Measure full operations.

**Constraints**: One active process; offline at runtime; no concurrent-writer or power-loss
guarantee. Drafts survive resizing; mutations are blocked below minimum size. Warnings and
expected failures appear within the active TUI, never silently defaulting to successful data.

**Scale/Scope**: One user's list, five stories, twenty requirements; two base screens,
one shared task dialog, one confirmation dialog, one temporary resize guard.
The 100-task fixture is a measurement size, not a product limit.

## Constitution Check

*GATE: Evaluated before Phase 0 and again after Phase 1.*

| Principle | Pre-design gate | Post-design result |
|-----------|-----------------|--------------------|
| I. Simplicity first | Each dependency and UI mechanism must serve a requirement | PASS: one TUI framework replaces custom focus, modal, rendering, and terminal-driver machinery |
| II. Clear design | Small focused modules; no speculative framework | PASS: one reused task dialog; framework-owned layout; task and storage code independent |
| III. Structured architecture | UI calls application logic through a small persistence boundary | PASS: service owns TaskStore protocol; adapter implements it; only executable composes all layers |
| IV. TDD | Failing test precedes every production behavior | PASS: unit, integration, five-story Pilot, and real-terminal acceptance strategy defined |
| V. Spec source of truth | Superseded line-input rules must be removed | PASS: design and public contract match FR-017 through FR-019; traceability below |

These gates validate the design, not implemented behavior. No constitution exception is
requested. The ratification-date TODO remains an administrative follow-up, not a new rule.

## Project Structure

### Documentation (this feature)

```text
specs/001-manage-daily-tasks/
  spec.md
  plan.md
  research.md
  data-model.md
  contracts/tui.md
  quickstart.md
  checklists/requirements.md
```

The TUI contract replaces the old CLI contract. `tasks.md` is generated later by
`/speckit-tasks`; this phase creates neither tasks nor application code.

### Source Code (repository root)

```text
requirements.txt
curso_pswe_07/
  __init__.py
  __main__.py           # composition, startup validation, lifecycle/exit status
  tui.py                # Textual app, List/Detail screens, size guard
  dialogs.py            # shared task editor and deletion confirmation
  styles.tcss          # DOS-style borders, visible focus, constrained layout
  models.py             # Task, snapshot, completion filter
  service.py            # TaskStore protocol, operations, committed/temporary state
  storage.py            # JSON validation and atomic file replacement
tests/
  __init__.py
  unit/
    __init__.py
    test_service.py
  integration/
    __init__.py
    test_storage.py
  acceptance/
    __init__.py
    test_tui.py
    test_dialogs.py
    test_resize.py
    test_persistence.py
    test_terminal.py
```

**Structure Decision**: A small root package supports module invocation without packaging
machinery. Textual App/Screen/ModalScreen and standard widgets provide the UI; there is no
custom generic widget layer. TUI modules import only models and application service, never
the JSON adapter or path logic. The composition root supplies a service to the UI.
Package markers support recursive standard unittest discovery.

## Phase 0: Research

[research.md](./research.md) records Textual selection, compatible version, keyboard/modal
pitfalls, terminal lifecycle validation, unchanged storage decisions, and test strategy.
All design choices are resolved; terminal cleanup and platform behavior remain required
implementation acceptance checks, not assumed guarantees.

## Phase 1: Design and Contracts

- [data-model.md](./data-model.md): unchanged saved schema and commit semantics; revised
  focus, modal, scroll, and resize state.
- [contracts/tui.md](./contracts/tui.md): public layout, keyboard mapping, dialogs,
  temporary banner, resize guard, startup, and exit contract.
- [quickstart.md](./quickstart.md): prospective setup, run, tests, keyboard walkthrough,
  and real-terminal validation. Nothing is claimed runnable before implementation.

### UI design

Use List and Detail Screens, shared TaskDialog and DeleteDialog ModalScreens, and a
ResizeGuard ModalScreen. Each active screen includes its own title/status/hints frame;
temporary mode renders its warning on the topmost screen as well as the base screen.
The dialog body fits inside the frame with scrollable content and fixed action rows.

Use built-in Input, plain TextArea, ListView, buttons, and scroll containers. Disable editor
features such as syntax highlighting, line numbers, and tab insertion: Tab moves focus.
Use ASCII borders and explicit `>` focus/selection markers; a fixed restrained palette is
decorative only. No theme switcher or command palette. Render user data as literal text,
not Rich markup; escape terminal-control characters for display without changing saved text.

Do not use framework-default application shortcuts blindly. Scope actions to the active
screen and focused control; suppress background actions while editing or modal. Handle
arrow movement in action groups explicitly; widget defaults alone do not guarantee the
specified arrow-menu behavior. Show only valid context-specific hints.

On resize, preserve the mounted underlying screen/dialog and push one size guard when
width <80 or height <24; do not rebuild editor widgets. Pop only that guard when both
dimensions recover. Retain focus, selection, draft, scroll positions, and filter.
Every mutating UI handler checks dimensions and active modal context, including queued
events, immediately before invoking the service. Storage stays synchronous and serialized
for this small dataset; measure SC-005 before considering any worker complexity.

### Requirement traceability and validation

| Work area | Requirements | Required evidence |
|-----------|--------------|-------------------|
| Validation, identity, operations | FR-002, FR-005, FR-010 through FR-013 | Service tests using fake store; duplicate-title independence |
| List/Detail and task dialogs | FR-001, FR-003, FR-004, FR-008 through FR-011, FR-016 | Stories 1/4 Pilot tests through actual focus and keyboard flow |
| Completion and filters | FR-006, FR-007, FR-012, FR-016 | Story 2 Pilot tests and unit filter membership |
| Storage and temporary mode | FR-014, FR-015 | Fault-injected adapter tests, Story 3 Pilot tests, app recreation and process reopen checks |
| Focus, borders, modals, scrolling | FR-017, FR-018 | Story 5 Pilot checks for regions, marker state, input isolation, and reachable long text |
| Resize and banner | FR-019 | Pilot resize tests at 80x24, 100x30, 79x24, 80x23; guard stops all mutations |
| Lifecycle and scope | FR-018, FR-020 | Real-terminal normal/interrupt cleanup; no unrequested commands or dependencies |

Follow Red-Green-Refactor for every behavior. One or more acceptance tests per story must
mirror all of its scenarios. Use `IsolatedAsyncioTestCase` for Pilot async contexts and
fresh App/service instances with temporary storage for each test. Headless tests never
write to a developer's home. Assert widget state, focus, visible regions, and storage
results; snapshots alone are not acceptance evidence.

Headless tests cannot prove actual terminal restoration: use POSIX PTYs for terminal
attributes before/after exit and SIGINT, plus real-terminal Windows checks. Unsupported
platform-specific automated checks must report skips explicitly; manual evidence is still
required on a supported platform. A terminal-size/display warning is not an implementation
success fallback.

Measure SC-005 through the completed render after real temporary-file commits. SC-001
requires five real first-time participants; Pilot does not replace the usability study.

## Complexity Tracking

No rule violations. Textual and its transitive dependencies are justified by the requested
full-screen borders, modal focus isolation, keyboard navigation, scrolling, resizing, and
headless tests (FR-017 through FR-019). Standard-library curses would require substantially
more custom code plus a Windows dependency; line input no longer meets the spec.
The persistence protocol, atomic replacement, and temporary mode remain required by the
constitution and FR-014/FR-015. No database, worker system, plugin mechanism, or theme
configuration is added.
