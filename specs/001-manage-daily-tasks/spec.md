# Feature Specification: Curso-PSWE-07 Daily Tasks TUI

**Feature Context**: `001-manage-daily-tasks` (directory identifier; current Git branch is `main`).

**Created**: 2026-10-22

**Status**: Draft

**Input**: User description: "Build a simple to-do list application named Curso-PSWE-07
with list and detail screens, task creation and editing, completion filters, confirmed
deletion, persistence between sessions, and a minimal responsive design. No accounts,
categories, due dates, priorities, search, or sync." Subsequently revised by the user to an
interactive command-line application, and now to a full-screen, DOS-style text-based user
interface (TUI) with character-drawn windows, borders, menus, dialogs, and keyboard navigation.
This revision updates the existing feature; task scope, persistence, and temporary-session
behavior are unchanged.

## Clarifications

### Session 2026-10-22

- Q: What should the app guarantee if the same task list is open in more than one window
  or tab? → A: Only one active window/tab is supported; simultaneous use is outside
  acceptance scope.
- Q: What should users be able to do when their saved tasks cannot be loaded?
  → A: Use a temporary list that is never saved and is discarded on close.
- Q: How should the graphical requirements change for the command-line application?
  → A: Originally interactive terminal List/Detail views with shared prompts; superseded
  by the requested full-screen DOS-style TUI with bordered views and shared add/edit dialogs.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add and view daily tasks (Priority: P1)

As a user, I want to add tasks and open their details so I can organize my daily work.

**Why this priority**: Creating and viewing tasks provides the application's core value.

**Independent Test**: Start with an empty list, add tasks with and without descriptions,
and open their details to verify the saved information.

**Acceptance Scenarios**:

1. **Given** no tasks exist, **When** the list opens, **Then** its header and the
   terminal view heading show "Curso-PSWE-07", a friendly empty-state message appears,
   and "Add task" remains available.
2. **Given** the list is open, **When** the user selects "Add task", enters a title and
   description, and selects Save, **Then** the form closes, the list reflects the new Pending
   task under All/Pending, and opening its selected row shows the saved title, description,
   and Pending label; if Done is active, the new task remains excluded.
3. **Given** the add form is open, **When** a task is saved without a description and opened,
   **Then** its details show the title and "No description" text.
4. **Given** the add form is open, **When** the user saves an empty or whitespace-only title,
   **Then** a title-required validation message appears, the form stays open with its
   entered values, and no task is created.
5. **Given** the add form contains unsaved input, **When** the user selects Cancel,
   **Then** the list returns without creating a task.
6. **Given** a task's details are open, **When** the user uses the back control,
   **Then** the list returns with its previously selected filter.

---

### User Story 2 - Track completion and filter tasks (Priority: P1)

As a user, I want to change completion status and filter the list so I can focus on
pending or completed work.

**Why this priority**: Completion tracking distinguishes the application from a static list.

**Independent Test**: Use prepared Pending and Done tasks, change each status in its
details, and verify membership in All, Pending, and Done filters.

**Acceptance Scenarios**:

1. **Given** tasks of both statuses exist, **When** the user selects All, Pending, or Done,
   **Then** exactly the corresponding tasks appear and the selected filter is highlighted.
2. **Given** a Pending task is open, **When** the user selects "Mark as done",
   **Then** its status label becomes Done and the action becomes "Mark as not done";
   on returning to the list, its status indicator and filter membership reflect Done.
3. **Given** a Done task is open, **When** the user selects "Mark as not done",
   **Then** its label becomes Pending and the action becomes "Mark as done";
   on returning to the list, its status indicator and filter membership reflect Pending.
4. **Given** Done tasks are visible, **When** the list is viewed, **Then** their titles
   use a clear textual Done indicator, distinct from Pending, without relying on color
   or strikethrough.
5. **Given** no tasks match a selected filter, **When** the list is viewed,
   **Then** a friendly no-matching-tasks message appears and "Add task" remains available.

---

### User Story 3 - Keep task changes between sessions (Priority: P1)

As a user, I want saved tasks and changes to survive closing the application so I can
rely on my list over time.

**Why this priority**: Losing saved work undermines every task-management operation.

**Independent Test**: Prepare tasks, save additions, edits, status changes, and a deletion,
then close and reopen the application and compare the result with the last saved state.

**Acceptance Scenarios**:

1. **Given** tasks have been successfully added, edited, and marked Done or Pending,
   **When** the application is closed and reopened in the same environment,
   **Then** all saved titles, descriptions, and statuses remain unchanged.
2. **Given** a task was successfully deleted, **When** the application is closed and
   reopened, **Then** it remains absent.
3. **Given** a task operation cannot be saved, **When** the user attempts the operation,
   **Then** a visible message explains that it was not saved, no success is presented,
   and the previously saved state remains authoritative.
4. **Given** saved tasks cannot be loaded, **When** the application opens,
   **Then** an explicit loading-error message appears instead of claiming the list is empty,
   a clearly labeled temporary list is available, and existing saved data is not overwritten.
5. **Given** the temporary list is in use after a loading failure, **When** the user adds,
   edits, completes, or deletes temporary tasks, **Then** only that temporary list changes,
   a persistent notice states that changes are not saved and will be lost on close,
   and no operation is reported as saved.
6. **Given** temporary tasks were changed, **When** the application is closed and reopened,
   **Then** those temporary tasks are discarded and loading the original saved list is
   attempted again; if loading succeeds, only the original saved tasks appear.

---

### User Story 4 - Edit and delete tasks safely (Priority: P2)

As a user, I want to update task details or deliberately remove a task so my list stays
accurate without accidental loss.

**Why this priority**: Maintenance is important once tasks exist, but creation and tracking
provide the initial value.

**Independent Test**: Use a prepared task to save and cancel edits, reject invalid input,
and cancel and confirm deletion.

**Acceptance Scenarios**:

1. **Given** task details are open, **When** the user selects Edit, **Then** the same form
   used for adding tasks opens with the current title and description and Save/Cancel actions.
2. **Given** the edit form is open, **When** a valid title or description change is saved,
   **Then** details show the saved values and the completion status is unchanged.
3. **Given** the edit form contains changes, **When** Cancel is selected,
   **Then** details return with the previously saved values.
4. **Given** the edit form is open, **When** the user saves an empty or whitespace-only title,
   **Then** a validation message appears and the saved task is unchanged.
5. **Given** task details are open, **When** Delete is selected, **Then** confirmation is
   requested before removal; canceling leaves the task and details unchanged.
6. **Given** deletion confirmation is open, **When** deletion is confirmed and succeeds,
   **Then** the list returns with its previous filter and the task is absent from every filter.
7. **Given** a description is removed in Edit, **When** Save succeeds,
   **Then** details show "No description" text.

---

### User Story 5 - Use a DOS-style full-screen terminal interface (Priority: P2)

As a user, I want character-drawn windows, menus, and dialogs with visible keyboard focus
so I can manage tasks in a DOS-style console interface without typing line-by-line commands.

**Why this priority**: The requested presentation makes the primary workflows usable.

**Independent Test**: Navigate both full-screen views and their dialogs using only the
keyboard at 80 columns by 24 rows and 100 columns by 30 rows, including long content,
completed tasks, validation, empty states, and deletion confirmation.

**Acceptance Scenarios**:

1. **Given** the application is open in a supported terminal size, **When** List or Detail
   is displayed, **Then** it occupies the available terminal area with character-drawn
   borders, a titled content window, a visible action menu, and keyboard hints rather
   than an accumulating transcript of prompts.
2. **Given** List is active, **When** the user uses arrow keys to select tasks, Tab and
   Shift+Tab to move between controls, and Enter to activate the focused control,
   **Then** they can open a task, select filters, and reach every displayed action;
   the focused control and selected task remain visibly identifiable without color.
3. **Given** Add or Edit is selected, **When** its bordered dialog opens, **Then** focus
   stays within the dialog, fields can be edited with the keyboard, and Save or Cancel
   returns to the originating view; Escape is equivalent to Cancel.
4. **Given** Delete is selected, **When** confirmation opens, **Then** a bordered modal
   dialog shows the warning and Confirm/Cancel actions, initially focuses Cancel, and
   blocks background actions until dismissed; Escape cancels without deleting.
5. **Given** long task content or more tasks than fit in the window, **When** the user
   navigates or scrolls with the keyboard, **Then** all task content is reachable,
   selection stays visible, and menus and active-dialog actions remain accessible.
6. **Given** a supported terminal is resized below 80 columns or 24 rows,
   **When** the interface redraws, **Then** a resize message appears, task-changing
   actions pause, and restoring a supported size restores the same view and draft.
7. **Given** validation or storage fails while a dialog is open, **When** the error appears,
   **Then** it is visible within the TUI, the draft is retained, and keyboard correction,
   retry, or cancellation remains available.
8. **Given** the user exits normally or interrupts the app, **When** control returns
   to the terminal, **Then** normal input echo and cursor visibility are restored and
   no unsaved draft or temporary-list data is written.

### Edge Cases

- Empty and whitespace-only titles are rejected in both add and edit forms; an optional
  description containing only whitespace displays as "No description".
- Identical titles are allowed; editing, completing, or deleting one task does not alter
  another task with the same title.
- Changing status while viewing a task reached from a filter immediately changes its
  membership when returning to that filtered list; no stale row remains.
- Adding a Pending task while Done is selected preserves the filter; the task is visible
  under All and Pending, not Done.
- Canceling edits or deletion never changes the saved task; deleting the final task
  displays the appropriate empty state.
- Save failures keep entered form values for correction or retry; failed status changes
  or deletions leave the task at its last saved state.
- After an initial loading failure, temporary task operations never attempt to write saved
  data. The temporary list starts empty but is labeled as temporary, not as an empty saved
  list; reopening discards it and retries loading the original saved data.
- Very long titles and descriptions wrap without obscuring navigation or task actions.
- A list row may show a shortened title if the full value remains reachable in Detail.
  Long Detail/form content is scrollable without changing stored values.
- Resizing with an open dialog preserves draft values and the active filter; below the
  minimum size no task mutation is allowed until the terminal is enlarged.
- Unknown or unavailable shortcuts do not change data; context-specific key hints remain
  visible. Escape cancels a dialog or returns from Detail, never confirms deletion.
- After a modal dialog closes, focus returns to the initiating control when it still exists;
  after deletion, List receives focus on a remaining row or Add task when the list is empty.
- The temporary-session notice remains visible in both views and while dialogs are open;
  modal content must not obscure the warning that changes will be lost.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The application MUST provide full-screen To-Do List and To-Do Detail terminal
  views, with "Curso-PSWE-07" in the application frame. It MUST NOT require changing
  terminal-window settings or title.
- **FR-002**: Each task MUST have a required title, optional description, and a completion
  status of Pending (not done) or Done; a new task MUST start Pending.
- **FR-003**: The list MUST show each task's title and status indicator; activating a row
  by keyboard MUST open that task's details.
- **FR-004**: A clearly visible "Add task" action MUST open a bordered title/description dialog
  with Save and Cancel; successful saving MUST return to the list.
- **FR-005**: Adding or editing MUST reject empty and whitespace-only titles with a visible
  title-required message and MUST NOT change saved data on validation failure.
- **FR-006**: The list MUST provide All, Pending, and Done filters, highlight the active
  filter, and show exactly the tasks matching it.
- **FR-007**: Done and Pending tasks MUST have distinct textual status indicators; color
  and strikethrough MUST NOT be required to distinguish them.
- **FR-008**: The list MUST show distinct friendly messages for no tasks and no matching
  tasks, while keeping "Add task" available.
- **FR-009**: Details MUST provide a back control, a prominent title, a description below
  it or "No description" when absent, and a visible Done/Pending label.
- **FR-010**: Details MUST offer Edit, Delete, and a completion action labeled "Mark as done"
  for Pending tasks or "Mark as not done" for Done tasks.
- **FR-011**: Edit MUST reuse the add form, prefill saved values, and provide Save and Cancel.
  Saving MUST return to updated details without changing status; Cancel MUST return without
  saving. Canceling Add MUST create nothing.
- **FR-012**: Successful completion changes MUST update the status label, action label,
  list status indicator, completed styling, and filter membership.
- **FR-013**: Delete MUST display a textual deletion warning in a bordered modal dialog
  with Confirm and Cancel; Cancel MUST be initially focused and Escape MUST cancel.
  Canceling MUST preserve the task; successful confirmed deletion MUST return to the list
  and remove only the selected task.
- **FR-014**: Additions, edits, status changes, and deletions reported as saved MUST survive
  normal application closure and reopening in the same environment.
- **FR-015**: Save and load failures MUST be visibly reported, MUST NOT be presented as
  success or an empty saved list, and MUST NOT overwrite previously saved data.
  Failed form saves MUST preserve entered values.
  After an initial load failure, the application MUST allow adding, viewing, editing,
  filtering, completing, and deleting tasks in a separate, initially empty temporary list.
  A persistent notice MUST state that this list is temporary and all changes will be lost
  on close. Save in a temporary form MUST update only the temporary list and MUST NOT be
  reported as saved; no temporary operation may write to saved data.
  Reopening MUST discard the temporary list and attempt to load the original saved data.
- **FR-016**: Returning to the list MUST preserve its selected filter and show current
  task membership. A new session MUST initially select All.
- **FR-017**: The application MUST use a DOS-style full-screen layout with character-drawn
  window borders, titles, action menus, and bordered add/edit and confirmation dialogs.
  Focus, selected task, status, and active filter MUST be identifiable by textual markers
  or borders without relying solely on color. A line-by-line prompt transcript MUST NOT
  serve as the primary interface.
- **FR-018**: Every action MUST be usable by keyboard: arrows navigate task rows and menu
  choices, Tab/Shift+Tab move focus, and Enter activates the focused control. Context-specific
  key hints MUST be visible. Dialogs MUST confine focus and block background actions;
  Escape MUST cancel dialogs or return from Detail. Form text entry MUST NOT trigger
  background shortcuts. Unknown/unavailable shortcuts MUST NOT mutate task data.
  Exiting or interruption MUST restore normal terminal input echo and cursor visibility.
- **FR-019**: Views and dialogs MUST remain usable at terminal sizes of at least 80 columns
  by 24 rows, including 100 columns by 30 rows. Long content MUST wrap or scroll so complete
  values are reachable without obscuring menus/actions. Resizing MUST preserve the current
  view, draft, and filter; below the minimum size the application MUST show a resize notice
  and suspend task mutations until the terminal is enlarged. The temporary-session notice
  MUST remain visible alongside dialogs at supported sizes.
- **FR-020**: The application MUST NOT include accounts, categories, due dates, priorities,
  search, sync, or other unrequested features.
  Support is limited to one active application session; simultaneous-session consistency and
  conflict resolution are outside this version's acceptance scope.

### Key Entities *(include if feature involves data)*

- **Task**: A distinct item of daily work with a required title, optional description, and
  Done/Pending status. Tasks with identical titles remain separate items.
- **Completion filter**: A current list view of All, Pending, or Done; it does not change
  saved tasks.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a moderated session with five first-time users and three prepared tasks
  (two Pending, one Done), at least four users independently add a task, open it, mark it
  Done, find it with the Done filter, edit it, and confirm its deletion within three minutes,
  without instruction beyond that task list.
- **SC-002**: In acceptance testing, 100% of successful additions, edits, completion changes,
  and deletions match their last saved state after a normal close and reopen.
- **SC-003**: All acceptance scenarios pass, including invalid titles, both cancellation
  paths, duplicate titles, empty/filter states, save/load failures, and temporary-list
  operations followed by reopening; no tested failure silently loses saved data or reports
  an unsaved change as saved.
- **SC-004**: At 80 columns by 24 rows and 100 columns by 30 rows, both views, the shared
  add/edit dialog, and confirmation
  meet FR-017 through FR-019, including completed and empty states and task text of
  200-character titles and 2,000-character descriptions. These are test fixtures, not limits.
  Keyboard-only checks MUST reach every action and all long content; resize checks MUST
  preserve drafts and block mutations below the minimum size. Exit/interrupt checks MUST
  restore normal terminal input and cursor behavior.
- **SC-005**: After a successful save or filter selection with 100 prepared tasks,
  the visible list/details reflect the operation within one second in every acceptance run.

## Assumptions

- One person uses a single task list in the same device/application environment.
  Only one application session is active at a time; simultaneous use is not supported.
  Reopening does not include clearing application data, uninstalling, or moving devices.
  No external account, service, or synchronization dependency is required.
- All is the initial session filter; navigation within a session preserves the selected
  filter. Task ordering and filter persistence across sessions are not acceptance constraints.
- Saving is explicit through Save for forms, through the completion action for status,
  and through confirmation for deletion; no autosave or undo feature is implied.
  The temporary list after a loading failure is an explicit exception: its operations only
  change the current session and never save, merge, or recover temporary data on reopening.
- Whitespace-only titles are invalid; whitespace-only descriptions count as absent.
  No title uniqueness rule or additional text-length limit is introduced.
- English labels quoted in the request are retained. Confirmation offers explicit confirm
  and cancel choices. Adding/editing returns to the list/details respectively.
- Screens, rows, and forms now mean full-screen character-drawn terminal windows,
  selectable task rows, and shared modal add/edit dialogs. This supersedes the previous
  line-by-line CLI. DOS-style describes the visual interaction, not a requirement to run
  on historical DOS systems.
- An interactive terminal supporting cursor movement and keyboard navigation is required;
  redirected input/output and a separate line-command interface are outside acceptance scope.
  Character borders may use ASCII or box-drawing characters; no exact palette, font,
  pixel-sized targets, mouse support, mobile layout, or terminal-window title control is required.
- The minimum 80-by-24 size and the 100-by-30 validation size are proposed defaults for
  character-window usability, replacing the earlier 40/80-column line-interface checks.
  Usability sampling and the one-second response target remain unchanged.
  Language, libraries, and storage implementation choices belong in the implementation plan.
