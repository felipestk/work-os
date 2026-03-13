# openclaw-workos

Work OS for OpenClaw.

This repo contains:
- `workctl` CLI
- unified SQLite schema
- Work OS skill
- install/bootstrap scripts
- generic demo/test fixture data
- skill packaging helper
- install/integration/handoff docs

Current status: working prototype from PR0083 with optional task + board support.

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
- task board view
- archive/unarchive task lifecycle
- attachment management
- enriched project inspection and task-aware project filters

## Task policy
Tasks are intentionally optional.
Archived tasks are retained and hidden from normal task lists/board views by default.
There is no hard delete flow for tasks.

The default Work OS workflow is still:
- customer
- project
- project event
- offer
- activity

## Quick start
```bash
git clone https://github.com/felipestk/work-os.git openclaw-workos
cd openclaw-workos
scripts/install.sh
source ~/.local/share/openclaw-workos/env.sh
workctl doctor
tests/smoke.sh
```

## Docs
- `docs/install.md`
- `docs/openclaw-integration.md`
- `docs/handoff-message.md`
- `docs/usage.md`
- `docs/cli.md`
- `docs/testing.md`

## License
MIT
