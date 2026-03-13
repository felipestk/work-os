# openclaw-workos

Work OS for OpenClaw.

This repo contains:
- `workctl` CLI
- unified SQLite schema
- Work OS skill
- install/bootstrap scripts
- generic demo/test fixture data
- skill packaging helper

Current status: working early prototype based on PR0083 planning.

## What Work OS manages
### Default model
- customers
- contacts
- projects (`PRxxxx`)
- project events
- offers
- offer versions
- offer line items
- activities

### Optional extension layer
- tasks
- task comments
- shared attachments
- minimal kanban fields on tasks (`board`, `column_key`, `wip_order`)
- task update/move helpers
- archive/unarchive task lifecycle
- attachment show/remove helpers
- enriched project inspection with optional linked tasks/attachments

## Task policy
Tasks are intentionally optional.
Archived tasks are retained and hidden from task lists by default.
There is no hard delete flow for tasks.

The default Work OS workflow is still:
- customer
- project
- project event
- offer
- activity

Use tasks only when explicit task tracking or board/kanban workflows are needed.

## Attachment policy
Use the shared attachment model to connect files to tasks, projects, offers, and other supported entities.
Attachment management includes add/list/show/remove flows.

## Repo-local demo/testing
```bash
scripts/bootstrap.sh
bin/workctl doctor
tests/smoke.sh
```

## License
MIT
