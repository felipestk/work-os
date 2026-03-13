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
- attachment show/remove helpers

## Goal
This repo is meant to be sent to another OpenClaw host, installed there, and provide:
- the `workctl` toolkit
- runtime storage in the OpenClaw workspace
- the `work-os` skill available in the workspace skills directory

## Quick install for another OpenClaw host
```bash
git clone <repo-url>
cd openclaw-workos
scripts/install.sh
source ~/.local/share/openclaw-workos/env.sh
workctl doctor
```

What this does:
- checks for `sqlite3` and attempts to install it if missing
- installs toolkit code under `~/.local/share/openclaw-workos`
- links `workctl` into `~/.local/bin`
- stores live DB/projects/customers under `~/.openclaw/workspace`
- installs the `work-os` skill into `~/.openclaw/workspace/skills/work-os`

## Task policy
Tasks are intentionally optional.

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

## Demo/testing data
This repo is intended to keep only safe generic fixture data.

Fixture source:
- `examples/demo-seed.sql`

Runtime artifacts are intentionally ignored:
- `data/*.db`
- `work/`
- `dist/*.skill`

## License
MIT

## See also
- `docs/install.md`
- `docs/testing.md`
- `docs/usage.md`
- `docs/skill-packaging.md`
- `docs/openclaw-integration.md`
- `docs/agents-policy-snippet.md`
- `docs/tools-snippet.md`
- `docs/handoff-message.md`
- `docs/architecture.md`
- `docs/cli.md`
