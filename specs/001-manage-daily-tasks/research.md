# Research: Curso-PSWE-07 DOS-Style TUI

## 1. Full-screen library and runtime

**Decision**: Python 3.11+ and `textual==8.2.8`, no extras. Use App, Screen, ModalScreen,
built-in input/list/scroll widgets, and a small application stylesheet.

**Rationale**: Textual supports the screen stack, focus, resizing, scrolling, and async
headless testing needed by FR-017 through FR-019. One direct runtime dependency replaces
hand-built terminal, focus, and modal machinery. This is required functionality, not a
"just in case" framework. The observed PyPI metadata for 8.2.8 declares Python >=3.9,<4.0;
the project intentionally retains its 3.11 floor. Pin the selected version during
implementation, validate it, and do not install optional syntax/language extras.

**Alternatives considered**: curses needs manual dialogs, focus, scrolling, resize, and
Windows support; prompt_toolkit offers full-screen layouts but requires more composition
and bespoke testing for this screen/dialog design. Line input fails the revised spec.

**Sources** (checked 2026-10-22):
- [Version metadata](https://pypi.org/pypi/textual/8.2.8/json)
- [Screens and modals](https://textual.textualize.io/guide/screens/)
- [Input and focus](https://textual.textualize.io/guide/input/)
- [Widgets](https://textual.textualize.io/widget_gallery/)
- [Testing](https://textual.textualize.io/guide/testing/)

## 2. Dialogs, keyboard scope, and resize state

**Decision**: Separate base screens from shared task/deletion modals. Use screen-local
bindings, standard focus traversal, explicit arrow handling for action groups, and a
guard at each mutating UI handler. Maintain mounted dialogs under one resize modal.
Show the temporary notice in every topmost screen, outside its scrolling/dialog body.

**Rationale**: A modal class does not by itself prove that application-level bindings or
queued handlers cannot reach storage. Default Input/TextArea bindings may consume or
conflict with navigation; explicitly disable unwanted defaults, tab insertion, command
palette, and background printable shortcuts during editing. Test actual key routing.
Preserving mounted widgets avoids lost drafts and focus when resizing.

**Alternatives considered**: Drawing an overlay without input guards leaves mutations
reachable; reconstructing forms from stored tasks loses drafts; toasts or banners only
under a modal hide the permanent temporary warning.

**Sources**:
- [Bindings and priority](https://textual.textualize.io/guide/input/#bindings)
- [Resize event](https://textual.textualize.io/events/resize/)
- [TextArea](https://textual.textualize.io/widgets/text_area/)
- [Pilot API](https://textual.textualize.io/api/pilot/)

## 3. Lifecycle and testing

**Decision**: Retain `unittest` for unit/integration checks; use
`IsolatedAsyncioTestCase` with `App.run_test()` and Pilot for keyboard acceptance/resize.
Textual requires async-capable tests, not pytest specifically. Validate real terminal
restoration separately: POSIX PTY tests and real Windows terminal checks.

**Rationale**: Headless mode exercises the widget/event loop without a terminal, but it
cannot prove echo/cursor restoration. Use framework lifecycle cleanup, request orderly
exit for Ctrl+C, and ensure OS SIGINT exits through cleanup without saving drafts.
Verify this on the pinned release; do not assume modal or exception paths are correct
merely because the library supports them.

**Alternatives considered**: StringIO transcript tests no longer represent a TUI;
pytest/plugins and screenshot tooling add dependencies without a current need.
Manual testing alone misses focus/resize regressions.

**Sources**:
- [Textual testing guide](https://textual.textualize.io/guide/testing/)
- [Application lifecycle](https://textual.textualize.io/guide/app/)
- [Async unittest](https://docs.python.org/3.11/library/unittest.html#unittest.IsolatedAsyncioTestCase)
- [POSIX terminal controls](https://docs.python.org/3.11/library/termios.html)

## 4. Persistence and error recovery (unchanged)

**Decision**: UTF-8 JSON at `~/.curso-pswe-07/tasks.json`; create directory on first save,
write a secure sibling temporary file, flush/fsync/close, and call `os.replace` as commit.
Before commit, retain the old snapshot on failure and clean up the specific temporary
file; report both primary and cleanup errors. After replacement succeeds, new data is
authoritative; do not report a rollback for later presentation errors.

**Rationale**: Meets normal-close/reopen persistence without SQL or concurrency machinery.
Temporary mode after load failure never calls persistent save. A missing file means
first use; unreadable/invalid data yields a visible load error and separate empty temporary
session until exit. Warning and errors now appear inside the TUI, not mid-render stderr.

**Alternatives considered**: Direct overwrite risks data loss; SQLite adds no needed
capability at this scale; automatic repair, merging, backups, and power-loss durability
are outside scope.

**Sources**:
- [Atomic replacement](https://docs.python.org/3.11/library/os.html#os.replace)
- [fsync](https://docs.python.org/3.11/library/os.html#os.fsync)
- [Secure temporary files](https://docs.python.org/3.11/library/tempfile.html#tempfile.mkstemp)
- [JSON](https://docs.python.org/3.11/library/json.html)

## Resolution

No unresolved design choices remain. Implementation prerequisites: select Python 3.11+,
declare/install the pinned dependency, and prove focus, resize, latency, and terminal cleanup
with the specified tests. These are required validation steps, not claims of an existing app.
