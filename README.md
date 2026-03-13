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

Current status: working internal v1 from PR0083 with optional task + board support.

Kanban app lives under `apps/kanban/` and currently includes:
- global `/board` view across all non-archived tasks
- fixed backlog / to do / doing / review / done columns
- backlog quick add
- drawer-based task detail/edit flow
- comment creation from drawer
- attachment upload / download / remove from drawer
- project + customer picker flows
- archive and left/right move interactions
- regression coverage via `tests/kanban_regression.py`

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

## Kanban app
### Local run
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-kanban.txt
uvicorn apps.kanban.main:app --host 0.0.0.0 --port 8010 --reload
```

Then open `http://127.0.0.1:8010/board`.

### Runtime notes
- app entrypoint: `apps.kanban.main:app`
- default runtime DB: `~/.openclaw/workspace/ops/workos/workos.db`
- uploaded task files are stored under the owning project folder:
  - `work/projects/<project-folder>/tasks/<task_id>/attachments/`
- if upgrading from an older DB, app startup now migrates the `attachments` table to allow task attachments

## Docs
- `docs/install.md`
- `docs/openclaw-integration.md`
- `docs/handoff-message.md`
- `docs/usage.md`
- `docs/cli.md`
- `docs/testing.md`
- `docs/kanban.md`

## License
MIT
