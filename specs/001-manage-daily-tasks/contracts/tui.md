# Public TUI Contract

## Invocation

After installing dependencies with Python 3.11+, run `python3 -m curso_pswe_07` from
the repository. Requires interactive terminal input/output and cursor support.
No line-command fallback, subcommands, or user-selectable storage path.
Reject unsupported/noninteractive startup explicitly on stderr with status 2, without
mutating saved data. A small terminal is recoverable through the resize guard.

Persistent data: `~/.curso-pswe-07/tasks.json`. One active instance is supported.
The application manages its full-screen terminal session but does not change the user's
terminal-window title or persistent terminal theme/settings.

## Frame and layout

Each topmost screen shows `Curso-PSWE-07`, a titled ASCII-bordered content window,
context-specific action menu/key hints, and a status/error region.
Use a restrained DOS-style palette, but textual labels, `>` selection/focus markers,
and borders carry meaning independently of color. No theme configuration or command palette.

At 80x24, reserve the header, temporary notice when applicable, and footer/action area;
only the body scrolls. Dialogs draw within those bounds. At 100x30 expand the body.
Long rows may shorten titles; complete content is available in Detail.
Detail wraps and scrolls long content. Do not interpret user strings as Rich markup or
terminal escape instructions; visibly escape control codes while retaining underlying data.

## Keyboard conventions

| Context | Keys | Result |
|---------|------|--------|
| All supported views | Tab / Shift+Tab | Next/previous enabled control in current focus scope |
| Task list | Up / Down, Home / End, PageUp / PageDown | Move task selection and keep it visible |
| Task list | Enter | Open selected task's Detail |
| Action/filter group | Left / Right or Up / Down | Move focus between group choices |
| Focused button/filter | Enter or Space | Activate the focused control |
| Detail content | Up / Down, PageUp / PageDown | Scroll long content |
| Detail | Escape | Back to List, same filter |
| Task/deletion dialog | Escape | Cancel, never save or confirm deletion |
| Active terminal session | Ctrl+Q | Orderly exit, discard draft/temporary data |
| Active terminal session | Ctrl+C | Orderly interruption, discard draft/temporary data |

Keyboard hints must reflect the current control context. Printable characters typed in
fields are input, never background action commands. Unknown/unavailable shortcuts do
not mutate task data. Explicit Exit is also present in the base action menus.
Shortcuts are screen-scoped; only exit/interruption remain global. Override default
framework/editor commands that conflict with these rules.

## List

Show All/Pending/Done as a keyboard-selectable filter group with a textual active marker.
Each row has title and Pending/Done status; row selection is distinct from active filter.
Menu: Add task, Open, Exit. Open is disabled when no visible task is selected.
Show distinct friendly empty-list and no-matching-filter messages, retaining Add task.
New sessions start All; navigation and Add preserve the active filter.

## Detail

Show task title, description or `No description`, and `Status: Pending`/`Status: Done`.
Menu: Back, Edit, Mark as done / Mark as not done, Delete, Exit.
Status updates stay in Detail and update action/status labels; Back returns to current
filter membership. Disambiguate tasks by internal identity, never by title.

## Shared Add/Edit dialog

A bordered modal has labeled title Input, description TextArea, Save, Cancel, and error
region. Add starts empty; Edit preloads existing values. Initial focus is title.
Tab/Shift+Tab move between fields and buttons, never insert tabs in the TextArea.
Enter activates buttons; in description it inserts a newline. Title Enter does not save
implicitly: saving requires activating Save. Text controls support standard editing and
scrolling; field contents may be cleared completely using keyboard selection/deletion.

Focus cycles within the dialog; background shortcuts/widgets are inactive. Save validates
title and invokes exactly one service operation. Empty/whitespace titles show `Title is
required`, preserve the draft, and focus title. Save errors leave the dialog/draft open
with a visible actionable error; retry through Save or Cancel is available.
Cancel/Escape discards only the draft. Successful Add returns to List; successful Edit
returns to updated Detail without changing task status. Restore initiating focus.

## Delete dialog

A bordered modal shows selected title, `Delete this task? This cannot be undone.`,
Confirm and Cancel. Initial focus is Cancel, so immediate Enter cancels.
Tab/arrows can reach Confirm; only activating it deletes. Escape cancels.
Background controls cannot receive input. Failure leaves the task and dialog intact with
an error and Cancel available. Success returns to List with its previous filter,
selecting a remaining row or focusing Add task if no visible rows remain.

## Persistence, temporary mode, and messages

Persistent mutations publish new UI state and a saved result only after storage commits.
Expected validation/storage errors appear in the active view/dialog, not stderr during
full-screen rendering. Startup diagnostics before the TUI or fatal errors after cleanup
may use stderr. Never catch arbitrary programming errors as empty-list success.

A missing file is first use. Unreadable/invalid data reports the load error and starts
an empty temporary list; the original file stays untouched. Every active screen/dialog
reserves a non-scrolling visible notice:

```text
TEMPORARY LIST: Changes are not saved and will be lost on close.
```

No modal may obscure it. Temporary operations report `Updated temporary list; not saved`,
never `Saved` or a misleading persistent deletion result. They never call persistent save.
No mid-session merge/recovery; reopening discards temporary data and retries the original.

## Resize

If width <80 or height <24, overlay a resize guard while leaving underlying mounted
screens/dialogs intact. Display the required minimum and compact temporary warning if
applicable. Suspend all task mutations, including queued mouse/button/keyboard callbacks;
exit/interruption remain available. Do not add duplicate guards on repeated small resizes.
When both dimensions recover, dismiss only the guard and restore view, filter, draft,
selection, scroll, and focus. No save or deletion occurs as a consequence of resize.

## Exit and terminal restoration

Exit menu/Ctrl+Q returns status 0. Ctrl+C or delivered SIGINT returns 130 after orderly
cleanup; do not rely on Textual's default Ctrl+C behavior. No implicit save on exit.
Restore terminal echo, cursor visibility, and normal screen/input handling on exit and
interruption. Unexpected faults exit nonzero after framework cleanup and remain visible
as errors; do not present them as successful task operations.
Verify restoration in a real terminal, not just headless tests.
