# Entity model

## Customer
Company or private/internal account.

## Contact
Person linked to a customer.

## Project
Main work container. Keeps `PRxxxx` code.

## Offer
Commercial proposal tied to customer and optionally project.

## Activity
Broader timeline record for notes, calls, emails, meetings, decisions, and summaries.

## Task
Optional project-linked work item for explicit task tracking or kanban workflows.
Treat this as an optional extension layer rather than a default operating primitive.

Rules:
- every task belongs to a project
- customer context is inferred through the project
- tasks are not part of the default workflow
- tasks have their own comments thread
- task attachments use the shared `attachments` model with `entity_type='task'`
- minimal kanban support is available via `board`, `column_key`, and `wip_order`
