# Work OS Architecture

Work OS is a unified operating layer for OpenClaw-based work.

## Core entities
- Customer
- Contact
- Project (`PRxxxx`)
- Offer
- Activity
- Task *(optional, for explicit task/kanban workflows only)*

## Design rules
- One repo: `openclaw-workos`
- One CLI: `workctl`
- One unified schema
- Skill included in same repo
- Keep agent default context minimal
- Keep advanced command detail in skill references

## Default operating model
The default workflow remains:
1. creating customers
2. creating projects linked to customers
3. logging project events
4. creating offers linked to customer/project
5. logging activities

Tasks are intentionally **not** part of the default workflow.
They exist as an optional operational layer for explicit task tracking and future kanban views.

## Task model
Tasks are modeled as their own entity rather than as `activity_type='task'`.

Why:
- tasks need lifecycle/status
- tasks need future kanban/board support
- tasks may have nested structure
- tasks may have their own comments and attachments
- project timelines should stay cleaner than task chatter

### Relationships
- every task belongs to one project
- customer context is inferred through the project
- tasks do **not** store a direct `customer_id` in v1
- tasks may optionally point to a parent task for simple nesting/subtasks

### Task comments
Task comments are stored separately from `activities`.

Reason:
- `activities` are the broader customer/project/offer timeline
- task comments are local discussion attached to a task
- reusing `activities` for comments would blur the model and create noisy timelines

### Attachments
Tasks reuse the shared polymorphic `attachments` model via `entity_type='task'`.

## v1 scope note
Task support is included in schema and CLI, but the skill should only use it when:
- the user explicitly asks for task tracking
- the workflow is clearly task/board based
- or a future kanban automation requires it
