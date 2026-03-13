# Work OS Architecture

Work OS is a unified operating layer for OpenClaw-based work.

## Core entities
- Customer
- Contact
- Project (`PRxxxx`)
- Offer
- Activity

## Optional extension entities
- Task *(optional v1.1-style extension for explicit task/kanban workflows only)*
- Task comments
- Shared attachments

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

Tasks are intentionally **not** part of the default operating model.
They are available as an optional operational layer for explicit task tracking and future kanban views.

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

### Minimal kanban fields
To stay future-ready without overbuilding, tasks include minimal board fields:
- `board`
- `column_key`
- `wip_order`

These fields are optional and should only matter when a board workflow is explicitly in use.

### Task comments
Task comments are stored separately from `activities`.

Reason:
- `activities` are the broader customer/project/offer timeline
- task comments are local discussion attached to a task
- reusing `activities` for comments would blur the model and create noisy timelines

### Attachments
Tasks, projects, offers, and other entities reuse the shared polymorphic `attachments` model.

## Scope note
For product positioning, treat task support as an **optional extension layer** rather than part of the main Work OS mental model.
The schema and CLI support it, but the default skill should continue steering agents toward:
- customer
- project
- project events
- offers
- activities
