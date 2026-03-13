# Kanban Automation with OpenClaw

This document proposes the next expansion of the Work OS kanban app so tasks can be executed by OpenClaw agents in a controlled, reviewable workflow.

It also refines the original plan to address the main blind spots:
- whether the human review loop is actually the best possible shape
- how output should be structured
- whether revisions should be comments only
- how to avoid ambiguity between task state, run state, and deliverable state

## Goal
Use the kanban board as a human + agent execution loop.

The key idea is:
- task creation does **not** trigger automation
- moving a task into `doing` is the explicit signal that the task is ready for execution
- an OpenClaw agent can then claim the task and work it
- the task is protected from conflicting edits while the agent is actively working
- the result is sent into a structured review flow
- the human can approve, request changes, or re-run with additional guidance

This is a better operational model than triggering an agent run on task creation.

---

## Executive recommendation

After pressure-testing the workflow, the recommended model is:
- use `doing` as the execution trigger
- use a queue-backed async execution worker
- lock tasks while a run is active
- treat each agent attempt as a separate **run** with its own status and output record
- keep **task comments** for discussion and lightweight notes only
- keep **structured outputs** in a dedicated output area tied to each run
- make **review** a first-class decision point with explicit actions:
  - approve
  - request changes
  - re-run
  - reject / send back to planning

The most important refinement is this:

> The human should not need to use column movement alone to communicate review intent.

Moving a task from `review` back to `doing` can still exist, but it should be the result of an explicit review action such as **Request changes**, not the only mechanism for feedback.

---

## Recommended workflow

### Board semantics
- `backlog`
  - ideas, capture, rough planning
  - no automation
- `todo`
  - ready for prioritization / assignment
  - no automation
- `doing`
  - explicit execution state
  - moving a task here queues agent work
  - task becomes execution-locked while actively claimed by an agent
- `review`
  - execution pass completed
  - output is waiting for human decision
- `done`
  - human-accepted completion

## Why trigger on `doing`
Triggering on task creation is too early.

At creation time, tasks are often:
- incomplete
- exploratory
- missing files/context
- not yet approved for execution

Moving to `doing` is a much better trigger because it means the human is saying:
- this task is real
- it is ready to be worked
- the current description/attachments are good enough for an execution pass

---

## Human review loop — refined recommendation

### Original model
The initial idea was:
- task goes to `review`
- human adds comments
- human moves it back to `doing` if more work is needed

That works, but it is not the cleanest possible model.

### Problem with using movement alone as feedback
If the only way to request another pass is moving `review -> doing`, several things become muddy:
- *why* it was moved back is not explicit
- the difference between “re-run unchanged” and “re-run with feedback” is unclear
- it is harder to preserve a clean revision history
- the board column starts carrying too much semantic meaning

### Better model
Keep the columns, but add explicit review actions.

When a task is in `review`, the human should be able to choose one of these actions:
- **Approve**
  - move task to `done`
- **Request changes**
  - create a structured revision request
  - reopen the task for another execution pass
  - move task to `doing`
- **Re-run**
  - no major revision note required
  - useful for transient failures or “try again with same brief”
  - move task to `doing`
- **Send back to planning**
  - move task to `todo` or `backlog`
  - indicates task was not actually ready / needs redefinition

This gives the human a cleaner operating model.

### Recommended semantic rule
Column movement should represent **state**.
Review buttons/actions should represent **intent**.

That is a much better long-term design.

---

## Output model — most important design decision

This is where the system can either become very usable or very messy.

### Recommendation
Do **not** treat comments as the only output channel.

Comments are good for:
- short human notes
- revision requests
- quick observations
- run status messages

Comments are **not** a great primary container for agent output because output may be:
- a summary text
- a website URL
- multiple artifact files
- edited project files
- structured results
- follow-up actions
- blocker explanations

### Best model
Each execution pass should create a structured **run output** record.

That means output should live in one dedicated place per run, with comments sitting alongside it as discussion.

This separates:
- conversational feedback
- machine execution record
- actual deliverables

That separation will save a lot of pain later.

---

## Recommended information architecture

### 1) Task
The task is the long-lived work item.

It should store:
- task title
- task description
- project link
- current board state
- execution settings/flags
- overall latest status

### 2) Run
A run is one execution attempt by an agent.

It should store:
- run status
- who/what ran it
- timestamps
- run summary
- outcome class (`success`, `blocked`, `failed`, `cancelled`)
- links to outputs/artifacts

### 3) Output
An output is the structured result of a run.

It should store or reference:
- summary text
- main result body (if textual)
- website/app URL if relevant
- files/attachments if relevant
- changed file paths if relevant
- follow-up notes
- warnings/blockers

### 4) Comments / review notes
Comments should stay comments.

Use them for:
- human feedback
- review notes
- clarifying questions
- small discussion points
- system status notes

This gives four clean layers instead of stuffing everything into a single task timeline.

---

## Recommended output structure

### Per-run output section
Each task should expose an **Outputs** section.

This section should list execution runs in reverse chronological order.

For each run, show:
- run id
- status
- agent/runtime
- started/finished timestamps
- concise summary
- output type(s)
- primary links/files
- blockers/warnings
- review status

### Output types to support explicitly
At minimum, the output model should handle these types:
- `text`
- `url`
- `attachment`
- `file_reference`
- `structured_json`

Examples:
- text summary of research
- deployed preview URL
- generated proposal PDF attachment
- edited files under a project folder
- JSON-like structured extraction or analysis result

### Primary output + supporting outputs
Each run should be able to identify:
- one **primary output**
- zero or more supporting outputs

Examples:
- primary output = preview URL
- supporting outputs = changed files, screenshots, summary note

or:
- primary output = markdown summary
- supporting outputs = attachment bundle, logs

This makes the UI much easier to read.

### Recommended output schema concept
Possible fields for a run output record:
- `id`
- `run_id`
- `output_kind`
- `title`
- `summary`
- `body_text`
- `url`
- `attachment_id`
- `file_path`
- `mime_type`
- `is_primary`
- `sort_order`
- `metadata_json`
- `created_at`

---

## Should all output be in one place?

### Yes, but with structure
The answer is **yes**, but not as one giant blob.

It does make sense for each task to have one place where the human can inspect results.
But inside that place, the output needs structure.

So the right model is:
- task has an **Outputs** section
- Outputs section contains one or more **run outputs**
- each run output contains structured items
- comments/review sit nearby, but are not the output itself

### Why this is better
Without a dedicated output section, the user has to reconstruct work from:
- status comments
- scattered links
- attached files
- maybe edited files in the project tree

That becomes painful fast.

A dedicated output section gives the task a reliable “result surface.”

---

## Revision model — comments alone are not enough

### Recommendation
Revision should not be modeled as freeform comments only.

Comments are useful, but a revision request needs a stronger structure.

### Better model
Add a **review decision** or **revision request** record tied to a task and optionally to a specific run.

Possible fields:
- `id`
- `task_id`
- `run_id`
- `decision_type` (`approve`, `request_changes`, `rerun`, `reject`)
- `body`
- `author`
- `created_at`

### Why this matters
This makes it possible to tell the difference between:
- “looks good” comment
- actual approval
- request for a new pass
- request to redo from scratch
- incidental discussion

That distinction is extremely useful for automation and audit history.

### Human UX recommendation
In the UI, the human can still type a note in the same drawer.
But under the hood, if they click **Request changes**, that note should be stored as a structured review decision, not just a plain comment.

---

## Recommended completion behavior

### Preferred model
When the agent finishes successfully, the task should move to `review`, not directly to `done`.

That keeps human approval explicit.

Recommended loop:
1. human moves task to `doing`
2. queue records an automation job
3. agent runs
4. agent writes structured output and summary
5. task moves to `review`
6. human chooses one of:
   - approve → `done`
   - request changes → create revision record and move to `doing`
   - re-run → create new run and move to `doing`
   - send back to planning → `todo` or `backlog`

### Optional future mode
A future setting can allow some projects or tasks to auto-complete directly to `done`, but this should not be the default.

---

## OpenClaw-first design principle
The kanban app should **not** become its own mini agent platform.

Instead:
- Work OS manages task state, locking, queueing, visibility, outputs, and review records
- OpenClaw performs the actual execution work

This separation is important.

### Work OS / kanban responsibilities
- task lifecycle and board state
- automation settings
- run queue management
- locking / claim semantics
- output storage/indexing
- review decision storage
- status display
- operator controls (cancel, retry, unlock)

### OpenClaw responsibilities
- read the task and project context
- perform the requested work
- create or edit artifacts
- report blockers
- write a structured result back
- signal completion state back to Work OS

This keeps the kanban app operationally simple while letting OpenClaw do what it is good at.

---

## Proposed state and lock model

The visible board columns remain:
- `backlog`
- `todo`
- `doing`
- `review`
- `done`

Behind that, tasks need execution metadata.

## Proposed task execution fields
Possible additions to the task model:
- `execution_mode` — `manual` or `agent`
- `execution_lock` — `none`, `queued`, `running`
- `claimed_by_run_id`
- `claimed_by_agent`
- `claimed_at`
- `last_run_status`
- `last_run_at`
- `current_review_state`
- `review_required`
- `retry_count`

These fields let Work OS distinguish:
- a task that is visually in `doing`
- a task that is actually claimed and locked by a running agent
- a task that is in `review` but awaiting a formal decision

---

## Locking rules
When a task is moved to `doing` and an automation job is queued:
- the task should become agent-owned for that execution pass
- humans should still be able to comment
- humans should be able to cancel the run or force unlock
- humans should not silently edit the core task body while an active run is in progress

### Recommended lock policy while agent is active
Allowed:
- add comments
- add review guidance before the run starts if it is still only queued
- view task details
- cancel run
- force unlock / reclaim

Blocked or restricted:
- editing title
- editing main description
- changing project assignment
- moving to another column without override
- deleting or altering critical run-related attachments

### Important nuance
If the task is only **queued** and has not yet been claimed by a worker, a human override may still be reasonable.

Once the run is actually **running**, the lock should be stricter.

This avoids race conditions between human edits and agent execution.

---

## Queue-based execution model

### Why use an automation queue
A queue is the right model because task movement should stay fast and reliable.

When a task enters `doing`, the app should:
1. update the task state immediately
2. insert a record into `automation_queue`
3. return control to the UI
4. let a worker process launch and monitor the OpenClaw execution asynchronously

Benefits:
- board interaction stays responsive
- failures are isolated from the request cycle
- retries become possible
- queue state can be inspected
- execution is easier to audit

### Do not run automation inline in the HTTP request
The web request that moves a task should not wait for the agent run to finish.

---

## Proposed data model

### `automation_queue`
Purpose: pending/running automation jobs.

Suggested fields:
- `id`
- `task_id`
- `trigger_type` (example: `task_moved_to_doing`)
- `status` (`queued`, `running`, `completed`, `failed`, `cancelled`)
- `priority`
- `created_at`
- `started_at`
- `finished_at`
- `attempt_count`
- `runner_type`
- `config_snapshot_json`
- `payload_json`
- `error_text`

### `automation_runs`
Purpose: execution history and external/OpenClaw linkage.

Suggested fields:
- `id`
- `queue_id`
- `task_id`
- `openclaw_session_key` or runtime run id
- `agent_id`
- `model`
- `status`
- `outcome_class` (`success`, `blocked`, `failed`, `cancelled`)
- `summary`
- `started_at`
- `finished_at`

### `automation_outputs`
Purpose: structured result items tied to a run.

Suggested fields:
- `id`
- `run_id`
- `task_id`
- `output_kind`
- `title`
- `summary`
- `body_text`
- `url`
- `attachment_id`
- `file_path`
- `mime_type`
- `is_primary`
- `sort_order`
- `metadata_json`
- `created_at`

### `review_decisions`
Purpose: formal human review actions.

Suggested fields:
- `id`
- `task_id`
- `run_id`
- `decision_type` (`approve`, `request_changes`, `rerun`, `reject`)
- `body`
- `author`
- `created_at`

### `automation_settings`
Purpose: global and project-level automation configuration.

Possible shape:
- setting scope (`global`, `project`)
- scope key (for example project id)
- enabled flag
- target agent/runtime
- default model
- completion target (`review` or `done`)
- retry policy
- concurrency policy
- prompt template or template key

---

## Settings model

### Global settings
Minimum recommended settings:
- automation enabled
- trigger on move to `doing`
- default agent id
- default model
- completion target (`review` recommended)
- allow comments while locked
- allow admin override
- require structured output on completion
- allow direct-auto-done (default: false)

### Per-project settings
Per-project overrides are strongly recommended because different projects may need different execution behavior.

Recommended project-level settings:
- automation enabled
- agent profile / target runtime
- prompt template override
- completion target (`review` vs `done`)
- retry policy
- max concurrency
- whether direct human overrides are allowed
- default output expectations
- review strictness level

### Future task-level flags
Possible future additions:
- `auto_run_enabled`
- `auto_complete_allowed`
- `requires_human_review`
- `execution_profile`
- `expected_output_kind`

---

## Best OpenClaw integration approach

### Principle
Use OpenClaw as the execution engine, but keep each run bounded and explicit.

### Strong recommendation
Treat each task execution as its own run.

Do not rely on one giant long-lived agent context for the whole board.

Per-task runs are better because they provide:
- clearer auditability
- less context drift
- easier retries
- better isolation
- safer behavior

### What each OpenClaw run should receive
Each run should get a structured execution brief including:
- project id
- project folder path
- task id
- task title
- task description
- current review/revision context
- prior run outputs when relevant
- linked attachments or relevant file paths
- expected completion behavior
- expected output structure

Example behavior contract:
- work under the task's project folder
- produce files/artifacts there
- write back a structured task result
- set one primary output
- move the task to `review` when complete
- if blocked, keep the task in `doing` and report the blocker

This is a much better fit for OpenClaw than a vague instruction like “go do the ticket.”

---

## Recommended execution lifecycle

### 1) Human moves task to `doing`
System behavior:
- validate task is eligible
- check that no active run already exists
- lock task for execution
- insert queue job
- add a system comment such as `Execution queued`

### 2) Worker claims queued job
System behavior:
- mark job as `running`
- create a corresponding `automation_runs` record
- launch the OpenClaw run
- record session/run identifiers
- add a system comment such as `Execution started by agent ...`

### 3) OpenClaw executes task
OpenClaw behavior:
- reads task + project context
- performs the requested work
- creates/edits artifacts as needed
- reports blockers if it cannot continue

### 4) Structured writeback
On completion, the run should write back:
- run summary
- one primary output
- zero or more supporting outputs
- warnings/blockers/follow-ups
- execution result status

### 5) Completion transition
Recommended default:
- success → move task to `review`
- blocked/failed → keep task in `doing` and add failure/blocker note
- cancelled → unlock task and keep in `doing` or return to `todo`

### 6) Human review decision
In `review`, the human should choose one of:
- approve → `done`
- request changes → store review decision and move to `doing`
- re-run → create new run and move to `doing`
- reject/send back to planning → move to `todo` or `backlog`

---

## Suggested operator controls in the UI
To make this workable day to day, the board should expose operator controls for active or recent runs.

Recommended controls:
- show locked/running badge on tasks
- show queued/running/failed/review-needed state
- show latest primary output summary on the task detail view
- dedicated Outputs section per task
- dedicated Review panel per task
- cancel run
- force unlock
- requeue
- approve
- request changes
- send back to planning

This matters because automation without clear operator controls quickly becomes frustrating.

---

## Task detail UX recommendation
The task drawer/page should eventually have distinct sections:

### 1) Task brief
- title
- description
- project
- metadata

### 2) Execution status
- queued/running/review/done/failed
- last run info
- lock state

### 3) Outputs
- list of runs
- primary output highlighted
- attachments, URLs, summaries

### 4) Review
- formal review decisions
- revision requests
- approval status

### 5) Comments
- general human discussion
- small notes
- system notes if desired

This is much cleaner than a single mixed activity stream.

---

## Key failure and safety cases

### Duplicate runs
Need a uniqueness guard so one task cannot have multiple active execution runs accidentally.

Suggested rule:
- at most one active queued/running automation job per task

### Human-agent races
Need explicit lock semantics and override controls so humans and agents do not edit the same task blindly at the same time.

### Ambiguous completion
Need a clear state rule:
- success → `review`
- failure/blocker → remain `doing`
- accepted by human → `done`

### Output ambiguity
Need a structured output model so the operator does not have to reconstruct results from comments.

### Review ambiguity
Need structured review decisions so approval, rejection, and revision are not hidden inside ordinary comments.

### Retry behavior
A failed run should not loop forever.

Need:
- retry limits
- manual requeue control
- visible failure reason

### Observability
Operators need a way to inspect:
- queued jobs
- running jobs
- failed jobs
- last run status per task
- latest primary output per task
- latest formal review decision per task

Without this, the automation becomes a black box.

---

## Phased implementation plan

### Phase 1 — workflow and design
Define and document:
- board workflow semantics
- locking rules
- queue schema
- run status model
- structured output model
- review decision model
- settings hierarchy

Deliverable:
- this design doc

### Phase 2 — schema + backend plumbing
Implement:
- `automation_queue`
- `automation_runs`
- `automation_outputs`
- `review_decisions`
- settings storage
- task execution metadata fields
- lock/unlock service functions

Deliverables:
- schema migration
- service-layer support

### Phase 3 — trigger on move to `doing`
Implement:
- queue creation when task moves into `doing`
- eligibility checks
- dedupe guard for active runs
- system comments for queueing

Deliverable:
- moving to `doing` creates a queued automation job

### Phase 4 — worker process
Implement:
- worker loop / queue poller
- run claiming
- OpenClaw execution bridge
- status updates
- structured writeback
- transition to `review` on success

Deliverable:
- end-to-end asynchronous execution flow

### Phase 5 — review and output UX
Implement:
- Outputs section
- Review section
- primary output presentation
- approve / request changes / rerun actions
- lock and run state indicators

Deliverable:
- usable human + agent interaction model

### Phase 6 — policy and safety
Implement:
- per-project settings
- allowed runtime/agent restrictions
- retry limits
- concurrency limits
- audit visibility
- output requirements / validation

Deliverable:
- safer operational model

### Phase 7 — deployment and handoff docs
Document:
- worker deployment model
- service management expectations
- OpenClaw integration expectations
- nginx/reverse proxy placement for the kanban app
- operator runbooks

Deliverable:
- complete operator handoff documentation

---

## Recommended first implementation slice
If the goal is to prove the model quickly without overbuilding it, start here:

### v1 implementation slice
- add `automation_queue`
- add `automation_runs`
- add minimal `automation_outputs`
- add minimal `review_decisions`
- add minimal task execution lock metadata
- trigger queue record when task enters `doing`
- build one worker process
- worker launches one bounded OpenClaw run per task
- on success:
  - add structured summary output
  - move task to `review`
  - unlock task
- on failure:
  - add structured failure output or note
  - keep task in `doing`
  - unlock task or mark failed
- add review actions:
  - approve
  - request changes
  - rerun

This is enough to validate the workflow before adding more advanced policy layers.

---

## Final recommendation
For Work OS, the best expansion path is:
- use `doing` as the explicit automation trigger
- keep execution asynchronous via `automation_queue`
- lock tasks while an OpenClaw agent is actively working them
- treat each attempt as a separate run
- store output in a dedicated structured Outputs area
- keep comments for discussion, not as the only deliverable container
- use explicit review decisions rather than relying on column movement alone
- move successful runs to `review` by default
- let humans control approval, revision, re-runs, and final completion

This provides a much stronger collaboration model between human operators and OpenClaw and closes several likely blind spots before implementation starts.
