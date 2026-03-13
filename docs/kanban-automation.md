# Kanban Automation with OpenClaw

This document proposes the next expansion of the Work OS kanban app so tasks can be executed by OpenClaw agents in a controlled, reviewable workflow.

## Goal
Use the kanban board as a human + agent execution loop.

The key idea is:
- task creation does **not** trigger automation
- moving a task into `doing` is the explicit signal that the task is ready for execution
- an OpenClaw agent can then claim the task and work it
- the task is protected from conflicting edits while the agent is actively working
- the result is sent to `review` for human feedback and approval
- the human can move the task back to `doing` for another pass or to `done` when accepted

This is a better operational model than triggering an agent run on task creation.

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
  - agent has completed a pass
  - human reviews output and adds feedback if needed
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

## Recommended completion behavior

### Preferred model
When the agent finishes successfully, the task should move to `review`, not directly to `done`.

That keeps human approval explicit.

Recommended loop:
1. human moves task to `doing`
2. queue records an automation job
3. agent runs
4. agent posts summary / outputs
5. task moves to `review`
6. human either:
   - moves back to `doing` with feedback/comments, or
   - moves to `done`

### Optional future mode
A future setting can allow some projects or tasks to auto-complete directly to `done`, but this should not be the default.

---

## OpenClaw-first design principle
The kanban app should **not** become its own mini agent platform.

Instead:
- Work OS manages task state, locking, queueing, and visibility
- OpenClaw performs the actual execution work

This separation is important.

### Work OS / kanban responsibilities
- task lifecycle and board state
- automation settings
- run queue management
- locking / claim semantics
- status display
- writeback storage
- operator controls (cancel, retry, unlock)

### OpenClaw responsibilities
- read the task and project context
- perform the requested work
- create or edit artifacts
- report blockers
- summarize results
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
- `review_required`
- `retry_count`

These fields let Work OS distinguish:
- a task that is visually in `doing`
- a task that is actually claimed and locked by a running agent

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
- view task details
- cancel run
- force unlock / reclaim

Blocked or restricted:
- editing title
- editing main description
- changing project assignment
- moving to another column without override
- deleting or altering critical run-related attachments

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
- `summary`
- `started_at`
- `finished_at`

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

### Future task-level flags
Possible future additions:
- `auto_run_enabled`
- `auto_complete_allowed`
- `requires_human_review`
- `execution_profile`

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
- task comments or review notes as needed
- linked attachments or relevant file paths
- expected completion behavior

Example behavior contract:
- work under the task's project folder
- produce files/artifacts there
- write back a task summary
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

### 4) Writeback
On completion, the run should write back:
- summary of what was done
- artifact or file references
- any warnings/blockers/follow-ups
- execution result status

### 5) Completion transition
Recommended default:
- success → move task to `review`
- blocked/failed → keep task in `doing` and add failure/blocker comment
- human accepted → move task to `done`
- human wants changes → add comments and move back to `doing`

---

## Suggested operator controls in the UI
To make this workable day to day, the board should expose operator controls for active or recent runs.

Recommended controls:
- show locked/running badge on tasks
- show queued/running/failed/review-needed state
- cancel run
- force unlock
- requeue
- move back to `todo`
- move back to `doing` after review comments

This matters because automation without clear operator controls quickly becomes frustrating.

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

Without this, the automation becomes a black box.

---

## Phased implementation plan

### Phase 1 — workflow and design
Define and document:
- board workflow semantics
- locking rules
- queue schema
- run status model
- writeback behavior
- settings hierarchy

Deliverable:
- this design doc

### Phase 2 — schema + backend plumbing
Implement:
- `automation_queue`
- `automation_runs`
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
- writeback comments
- transition to `review` on success

Deliverable:
- end-to-end asynchronous execution flow

### Phase 5 — UI and operator controls
Implement:
- run state indicators
- task lock indicators
- cancel / retry / force unlock controls
- review guidance

Deliverable:
- usable human + agent interaction model

### Phase 6 — policy and safety
Implement:
- per-project settings
- allowed runtime/agent restrictions
- retry limits
- concurrency limits
- audit visibility

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
- add minimal task execution lock metadata
- trigger queue record when task enters `doing`
- build one worker process
- worker launches one bounded OpenClaw run per task
- on success:
  - add summary comment
  - move task to `review`
  - unlock task
- on failure:
  - add failure comment
  - keep task in `doing`
  - unlock task or mark failed

This is enough to validate the workflow before adding more advanced policy layers.

---

## Final recommendation
For Work OS, the best expansion path is:
- use `doing` as the explicit automation trigger
- keep execution asynchronous via `automation_queue`
- lock tasks while an OpenClaw agent is actively working them
- move successful runs to `review` by default
- let humans control acceptance, feedback, re-runs, and final completion

This provides a strong collaboration model between human operators and OpenClaw without turning the board into a fragile black box.
