# Quickstart and Validation: Full-Screen TUI

## Status and prerequisites

The application and automated tests are implemented. All 44 tests pass on macOS with
Python 3.11.17 and 3.13.16, using Textual 8.2.8. Release validation is not complete:
Windows/manual cross-platform checks and the five-person usability study remain unverified.

- Python 3.11+; check `python3 --version` before creating the environment. The system
  Python 3.9.6 is insufficient; this implementation used Python 3.13.16 and an isolated
  Python 3.11.17 validation environment.
- A modern interactive macOS/Linux/Windows terminal, at least 80 columns by 24 rows.
- Run from repository root; only one active app instance.
- Install the declared Textual dependency once; application use thereafter is offline.
- Saved data lives at `~/.curso-pswe-07/tasks.json`. Never delete an existing list to test.

## Setup and launch

Use a Python 3.11+ executable for these commands:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m curso_pswe_07
```

On Windows use `py -3.11 -m venv .venv` and `.venv\Scripts\Activate.ps1` in PowerShell
instead of the first two commands. The manifest declares `textual==8.2.8`
without extras. No separate test dependencies.

Expect a full-screen `Curso-PSWE-07` frame with character-drawn borders, task list,
All/Pending/Done filters, visible focus, action menu, and key hints, not line prompts.
See [TUI contract](./contracts/tui.md) and [data model](./data-model.md).

## Automated checks

```sh
python -m unittest discover -s tests/unit -v
python -m unittest discover -s tests/integration -v
python -m unittest discover -s tests/acceptance -v
```

Use targeted suites during Red-Green-Refactor; run all tests before delivery:

```sh
python -m unittest discover -s tests -v
```

Acceptance tests use `IsolatedAsyncioTestCase` with Textual `run_test(size=(80, 24))`
and Pilot key events, then repeat layout cases at `(100, 30)`. Use Pilot terminal resizing
for below-minimum checks. Assert focus targets, visible marker state and regions, and
actual service/file results; do not substitute transcript or screenshot-only checks.
Create a new App per test; inject service/store for tests, not public configuration flags.
All test paths/homes must be temporary and isolated from developer saved data.

## Keyboard walkthrough

1. Tab to Add task, Enter. Type a title; Tab to description and enter optional text.
   Tab to Save, Enter. Verify a Pending row under All/Pending.
2. Focus list; use arrows to select the row and Enter to open Detail.
   Verify full title/description, status, menu, and hints.
3. Tab to Mark as done, Enter. Verify Done and Mark as not done. Escape to List.
   Reach the filter group, select Done with arrows and Enter; verify membership.
4. Open Detail and Edit. Change fields, Escape; verify no saved change.
   Repeat and activate Save; verify updated values with unchanged status.
5. Create a duplicate-title task; changing one must not alter the other.
6. Choose Delete. Verify initial Cancel focus; Enter cancels. Reopen, move to Confirm,
   Enter; verify only the intended task disappears and focus returns sensibly.
7. Save a blank or whitespace-only title; verify error and retained draft. Clear an
   existing description and save; verify `No description`. Type shortcut-like text in
   fields; it must not launch background actions.
8. Exit through menu or Ctrl+Q; reopen and verify the saved state. Ctrl+C with a draft
   must discard it and restore the terminal. No task writes occur on exit.

Description editing follows Textual's editor bindings: Enter inserts a newline,
F7 selects all text, and Backspace deletes the selection. Title Enter does not Save.

## Persistence and recovery cases

Automate with temporary directories and injected expected errors, not real data damage:

| Case | Expected result |
|------|-----------------|
| Missing file | Empty persistent session; first save creates file |
| Save changes then recreate app/service | Final titles/descriptions/status/deletions remain |
| Write/fsync/close/replace fails before commit | In-TUI error, old snapshot/file, retained draft |
| Successful replace | New state authoritative; no false rollback after commit |
| Malformed JSON/schema, unreadable file | Load error and permanent temporary notice |
| Temporary create/edit/filter/status/delete | All usable, persistent save never called |
| Temporary session exit then successful original reload | Temporary tasks gone; original saved list intact |
| Named temporary-file cleanup fails | Both primary failure and cleanup error surfaced |

Include a two-process close/reopen smoke test of the real entry point with isolated home
and a real terminal/PTY, not redirected line input. Headless app recreation tests cover
every persistence scenario; the process test verifies composition and lifecycle.

## Layout, modal, and resize checks

- At 80x24 and 100x30, cover both views, Add/Edit, confirmation, errors, and temporary mode.
  Check borders, focus markers, active filter, fixed action area, and unobscured notice.
- Exercise 200-character titles, 2,000-character descriptions, unbroken words, Unicode,
  and control-code/markup-like input. Full text remains accessible and never executes
  terminal controls or markup.
- With a long list, arrows/Home/End/PageUp/PageDown keep the selected row visible.
  Detail and text fields scroll to all content without losing access to actions.
- Open a draft, resize to 79x24 then 80x23; all mutation actions must be blocked.
  Repeated small resizes must not stack guards. Restore 80x24; verify draft, filter,
  selection, scroll, and focus. Repeat while confirmation is open and in temporary mode.
- Tab/Shift+Tab cannot escape a dialog. Escape never confirms deletion. Unknown keys and
  background shortcuts must not change stored data. Verify color-independent markers.

## Real-terminal lifecycle and outcomes

- On POSIX use a temporary-home subprocess attached to a PTY. Capture initial termios
  flags, exit normally and with SIGINT, and assert echo/canonical state is restored.
  Inspect emitted cursor/alternate-screen restoration sequences and confirm visually
  that cursor visibility and ordinary shell input work after both exits.
- Check the same normal/Ctrl+C behavior in a Windows terminal; POSIX tests may explicitly
  skip there but manual evidence is still required. Headless tests cannot prove cleanup.
- Noninteractive invocation must fail clearly with status 2, without touching saved data.
  Normal exit is 0; interruption is 130. Unexpected faults are nonzero, never silent success.
- For SC-005 prepare 100 tasks, measure from save/filter activation through file commit
  and rendered result using monotonic time, under one second in every measured run.
  Record OS, terminal size, interpreter, and dependency version; exclude typing time.
- For SC-001 recruit five first-time users with the specified three-task fixture; at least
  four must complete the defined workflow within three minutes without coaching.
  Automated tests do not replace this study.
- Map evidence to SC-001 through SC-005 and FR-001 through FR-020. Failing requirements
  block completion; do not hide them behind a fallback line interface.

## Implementation evidence and outstanding gates

Environment: macOS (Darwin), Python 3.11.17 and 3.13.16, Textual 8.2.8, POSIX PTY at 80x24;
headless keyboard/layout checks at 80x24 and 100x30. Tests use isolated homes/files.
No developer task data was used. Production code depends only on the standard library
and the single declared Textual dependency.

Full unittest results: **44 passed** on Python 3.13.16 (107.636 s) and **44 passed**
on Python 3.11.17 (93.619 s), with no skips on this POSIX host. Following the
minimum-runtime JSON recovery fix, the 17 storage/domain tests also passed again on
Python 3.13. Syntax compilation, installed dependency consistency, and AST import-boundary
checks passed. No separate static type checker/build tool is configured or claimed.

The test-first increments covered models/service, Add/View, status/filter, atomic JSON
storage and temporary sessions, Edit/Delete, keyboard/resize, and terminal lifecycle.
The original 100-task filter measurement exceeded one second (1.05 s); retaining
unchanged mounted rows instead of rebuilding the entire list brought the measured
actions below the requirement. No new cache, configuration, or dependency was added.
Minimum-runtime validation also exposed a deeply nested corrupt-JSON parser
`RecursionError`; it is now explicitly reported as a load failure, entering the same
non-writing temporary mode rather than terminating startup.

### Functional requirement traceability

Test paths below are relative to the repository root.

| Requirement | Implementation / automated evidence |
|-------------|--------------------------------------|
| FR-001 | `tui.py`: named full-screen List/Detail; `tests/acceptance/test_tui.py` |
| FR-002 | `models.py`: task fields/invariants; `tests/unit/test_service.py` |
| FR-003 | `service.py` lookup and `tui.py` selected-ID navigation; `test_tui.py` |
| FR-004 | Shared Add dialog and form entry; `test_dialogs.py`, `test_tui.py` |
| FR-005 | Required title, optional description, normalization; unit/dialog tests |
| FR-006 | Both status transitions; unit tests and `test_tui.py` |
| FR-007 | All/Pending/Done membership and active marker; unit/TUI tests |
| FR-008 | Empty-list/no-match states retain Add; `test_tui.py` |
| FR-009 | Full details, status, No description; `test_tui.py`, `test_resize.py` |
| FR-010 | Detail Edit/Delete/status actions; `test_tui.py`, `test_dialogs.py` |
| FR-011 | Shared prefilled editor, Save/Cancel, unchanged status; `test_dialogs.py` |
| FR-012 | Status labels, list membership, completed row styling; `test_tui.py` |
| FR-013 | Cancel-first warning/confirmation and explicit deletion; `test_dialogs.py` |
| FR-014 | Real JSON round trips, all mutation reopen paths, two-process PTY; `test_storage.py`, `test_persistence.py`, `test_terminal.py` |
| FR-015 | Strict load validation, write/flush/close/fsync/replace/cleanup errors, retained drafts, no temporary writes; storage/persistence/dialog tests |
| FR-016 | Filter and selected identity survive navigation; `test_tui.py`, `test_resize.py` |
| FR-017 | ASCII frames, textual selection/focus/filter/status, modal regions; TUI/dialog/resize tests |
| FR-018 | Keyboard groups, modal focus, scoped keys, normal/interrupt/fault cleanup; TUI/dialog/POSIX PTY tests; Windows check pending |
| FR-019 | Long values, scrolling, supported sizes, single resize guard, suspended queued handlers and retained state; `test_resize.py`; manual Windows check pending |
| FR-020 | UI -> service -> persistence protocol, concrete adapter only at composition root; source/import inspection; no excluded task features or extra direct dependencies |

Application modules are in `curso_pswe_07/`. The short filenames in the table refer
to that package; the test modules are under `tests/unit/`, `tests/integration/`, or
`tests/acceptance/` as appropriate.

### Measurable outcomes

| Outcome | Evidence / status |
|---------|-------------------|
| SC-001 | **BLOCKED**: five first-time participants are unavailable. No user times or completion rates have been fabricated. Use the specified two-Pending/one-Done fixture when conducting the study. |
| SC-002 | Automated create/edit/status/delete round trips and app recreation pass; real-entry-point two-process create/reopen also passes. |
| SC-003 | Automated scenario, validation, cancellation, failure, and temporary-session cases are implemented; see the complete unittest run. |
| SC-004 | Headless 80x24/100x30 and below-minimum checks plus real macOS PTY restoration pass. Windows and human visual/keyboard terminal checks remain pending. |
| SC-005 | With 100 prepared tasks, all seven measured save/filter actions passed <1 s: Python 3.13 range 0.1027–0.6699 s; Python 3.11 range 0.1344–0.7030 s. Measurements include real isolated JSON commits and completed rendering, excluding typing. See detailed timings below. |

| Action | Python 3.13.16 | Python 3.11.17 |
|--------|----------------|----------------|
| Pending filter | 0.4909 s | 0.4582 s |
| Done filter | 0.6627 s | 0.6828 s |
| All filter | 0.6699 s | 0.7030 s |
| Completion change | 0.1027 s | 0.1344 s |
| Edit Save | 0.1665 s | 0.1683 s |
| Add Save | 0.4515 s | 0.4422 s |
| Confirm deletion | 0.4646 s | 0.3087 s |

POSIX PTY evidence includes Exit/Ctrl+Q, Ctrl+C, delivered SIGINT, and an injected
unexpected runtime fault: expected statuses 0/130/1, restored termios flags,
cursor-show and alternate-screen exit sequences. Noninteractive startup reports a
clear error with status 2 without creating user data; known cursorless `TERM=dumb`
terminals are also rejected before starting the app. This is real terminal-protocol
evidence, not a claim of manual visual inspection or Windows verification.

### Tasks intentionally left open

- **T051**: No Windows terminal or separate manual cross-platform session is available.
  Perform the walkthrough, resize, normal exit, and interruption checks there; record
  terminal/OS versions and results. macOS PTY evidence is recorded above.
- **T052**: Recruit five first-time users and record their actual completion times;
  at least four must finish the specified workflow in three minutes without coaching.
- **T053**: Both runtime suites, quickstart launch via the real entry point, and
  architecture/scope checks are done. This final gate depends on T051 and T052;
  leave it open until the required manual platform/usability outcomes are verified.
