# Data Model: Daily Tasks TUI

## Task

| Field | Type | Rules |
|-------|------|-------|
| id | positive integer | Unique, immutable, internal identity; duplicate titles remain independent |
| title | string | Required; `title.strip()` must not be empty; retain valid entered text |
| description | string | Optional input; absent or whitespace-only becomes `""` |
| done | boolean | New tasks start `false`; maps to Pending/Done |

No dates, categories, priority, user account, or artificial text-length limit.
Identity is not a row index: selection after filtering still refers to the same internal ID.

## Persistent document

One UTF-8 JSON object:

```json
{
  "version": 1,
  "next_id": 2,
  "tasks": [
    {"id": 1, "title": "Prepare workshop", "description": "", "done": false}
  ]
}
```

- `version` must be the integer 1; unsupported versions fail loading explicitly.
- `next_id` is a positive integer greater than every stored ID; allocate it on creation
  and increment only when that creation is committed. Deletions do not decrement it.
- `tasks` is an array of validated tasks. Reject duplicate IDs, duplicate JSON object keys,
  missing/extra fields, non-boolean `done`, and wrong types. Booleans do not count as integers
  for IDs, version, or next_id despite Python's integer subtype relationship.
- An empty saved list has `tasks: []`; it is different from an unreadable document.
- Retain insertion order for deterministic presentation; edits/status changes keep position.
  This is a design choice, not a new user-facing sorting feature.

## Session state

| State | Values | Lifetime |
|-------|--------|----------|
| filter | All, Pending, Done | Starts All; retained during navigation, never persisted |
| view | List or Detail | Mounted base screen; retained under modals |
| modal stack | TaskDialog, DeleteDialog, optional ResizeGuard | Topmost receives interaction; background actions blocked |
| selected task | internal ID or absent | Detail/edit/confirmation refer to the same task |
| mode | persistent or temporary | Selected at initial load; immutable until exit |
| task snapshot | tasks and next_id | Loaded committed state or temporary in-memory state |
| form draft | title, description | Never committed until Save; kept on validation/save errors |
| focus | widget/control reference | Trapped in modal; restored to initiating control on close |
| selection and scroll | selected ID and per-view offsets | Keep selected row visible; no persistent UI data |
| terminal size | columns and rows | Below 80x24 suspends task mutations |
| resize resume state | existing mounted view/modal stack | Guard overlays without recreating the form or losing draft |

A missing task file initializes a persistent empty snapshot with `next_id: 1`. Any other
load/schema failure initializes a separate temporary snapshot and displays the error and
a notice on every view/form/confirmation. Temporary data has no relationship or merge
operation with the unreadable saved document.

## Application and storage boundary

The application service owns the small `TaskStore` protocol:

- `load() -> TaskSnapshot`: return a validated snapshot; missing file yields a new empty
  snapshot; an expected read/format failure raises an explicit storage error.
- `save(snapshot: TaskSnapshot) -> None`: return only after successful file replacement;
  on a pre-commit failure raise an explicit storage error without modifying the saved file.

`TaskSnapshot` contains tasks and next_id. The JSON adapter implements the protocol;
TUI code never calls it or knows its file path. The executable module wires adapter and
service. Tests supply a small in-memory fake. There is no runtime-pluggable storage setting.

Application operations: list matching tasks, get a selected task, create, edit details,
set completion status, and delete. Every mutation constructs a candidate snapshot,
validates it, persists it if in persistent mode, and only then publishes it as current.
Temporary mode publishes only in memory and explicitly reports "temporary; not saved."
On a persistent save error, keep the old snapshot; the UI retains any form draft.

## State transitions

| Operation | Before | After success | On cancellation/failure |
|-----------|--------|---------------|------------------------|
| Create | Valid form draft | New Pending task with next ID; List returns | No task; draft stays on failure |
| Edit | Existing task + draft | Same ID/status, new details; Detail returns | Original task; draft stays on failure |
| Complete/reopen | Pending/Done task | Done/Pending respectively; Detail stays | Original status |
| Delete | Existing task + confirmation | Task absent; List returns | Task unchanged; Detail stays |
| Filter | Any filter | Matching entries; task data unchanged | Invalid input changes nothing |
| Open dialog | List/Detail | Modal receives focus; background inert | No task mutation |
| Resize below minimum | Existing view/dialog | Single resize guard; mutation handlers disabled | Draft, filter, selection, focus retained |
| Resize to supported size | Resize guard | Guard removed; underlying state/focus restored | No implicit save |
| Exit | Any session | Draft/temporary state discarded | Persistent committed snapshot unchanged |

## File commit and error semantics

Use a temporary file in the destination directory, serialize the entire candidate,
flush/fsync, close, then replace. Successful replacement is the commit point. No save on
exit is necessary. Clean up only the specific temporary file created for that attempt;
report cleanup errors. No backups, lock files, migrations, or automatic corruption repair.

Normal-close/reopen behavior is guaranteed; simultaneous instances and sudden power-loss
recovery are outside scope. Validation failures must not write. Unknown task selections
are explicit errors, not implicit creation or success.

## UI projection and boundaries

Textual state is only a projection of the service snapshot. Focus, dialogs, key hints,
scroll, and terminal size never enter the saved schema or application service.
Mutations from queued UI events must recheck current size/modal context before calling
the service. Serialization/save is synchronous and serialized; no background save races.

On dialog cancellation, restore focus to its originating control if it still exists.
After deletion, select a remaining visible row or focus Add task when none remains.
Temporary mode exposes the same operations but includes its permanent notice on every
topmost screen, including task/deletion dialogs and resize guard when space permits.
The resize notice includes a compact unsaved warning in temporary mode.

Task text remains literal data. Display shortening/escaping and Rich markup suppression
must not alter saved title/description. Full values remain accessible in scrollable
Detail and editable form widgets.
