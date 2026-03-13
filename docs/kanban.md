# Kanban App

This document describes the current internal kanban app that ships inside `openclaw-workos`.

## Purpose
The kanban app is a lightweight operational board over the optional task layer in Work OS.

It is intentionally:
- server-rendered
- internal-first
- simple to run
- built for fast iteration without a SPA build pipeline

## Stack
- FastAPI
- Jinja2 templates
- HTMX
- small vanilla JS
- SQLite through the shared Work OS schema

## App location
The canonical repo location for the kanban app should be:
- app code: `apps/workos-kanban/`
- Python package / entrypoint: `apps.kanban.main:app`

Implementation note:
- the import path can remain `apps.kanban.main:app` even if the product-facing repo folder is referred to as `apps/workos-kanban/`, but the deployment/docs convention should consistently point operators to `apps/workos-kanban/` as the app location.

## Current feature set
### Board
- global `/board` view across all non-archived tasks
- fixed columns:
  - backlog
  - todo
  - doing
  - review
  - done
- tasks grouped by column
- project and customer context shown on cards
- project and customer filters

### Task creation and movement
- quick add in backlog
- project picker for task creation
- explicit left/right move controls
- archive from card or drawer

### Drawer
- open task details in right-side drawer
- edit title, project, priority, due date, assignee, description
- add comments from drawer
- add attachments from drawer
- remove attachments from drawer
- download uploaded attachments
- inline error feedback for bad submissions

### Attachments
- upload-only UI in the drawer
- uploaded files are stored in the task folder inside the owning project
- attachment rows show file-type-aware icons
- clicking an attachment downloads it

### Project/customer creation flow
- searchable project picker
- create-project modal from picker flow
- searchable customer lookup inside project creation

## Run instructions
### 1) Create venv and install dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-kanban.txt
```

### 2) Start the app
```bash
uvicorn apps.kanban.main:app --host 0.0.0.0 --port 8010 --reload
```

### 3) Open the board
```text
http://127.0.0.1:8010/board
```

## Runtime behavior
### DB location
By default the app uses the shared Work OS DB:
- `~/.openclaw/workspace/ops/workos/workos.db`

### Environment overrides
The app respects the same environment overrides as the rest of Work OS:
- `OPENCLAW_WORKSPACE`
- `WORKCTL_DB_PATH`
- `WORKCTL_PROJECTS_ROOT`
- `WORKCTL_CUSTOMERS_ROOT`
- `WORKCTL_SCHEMA_PATH`

### Attachment storage
Uploaded task files are stored under the owning project folder:
- `work/projects/<project-folder>/tasks/<task_id>/attachments/`

Example shape:
- `work/projects/PR0002-example-project/tasks/14/attachments/brief-abc12345.pdf`

### Schema migration note
If the DB was created before task attachments were allowed in the shared `attachments` table, the app now migrates that table automatically during startup.

## Main routes
### Page routes
- `GET /board`
- `GET /tasks/{task_id}`

### Picker/search routes
- `GET /board/projects/search?q=...`
- `GET /board/projects/filter-search?q=...`
- `GET /board/customers/search?q=...`
- `GET /board/customers/filter-search?q=...`
- `GET /board/project-create`
- `POST /board/project-create`

### Task mutation routes
- `POST /board/tasks`
- `POST /board/tasks/{task_id}/move`
- `POST /board/tasks/{task_id}/update`
- `POST /board/tasks/{task_id}/archive`
- `POST /board/tasks/{task_id}/comments`
- `POST /board/tasks/{task_id}/attachments`
- `POST /board/tasks/{task_id}/attachments/{attachment_id}/remove`
- `GET /board/tasks/{task_id}/attachments/{attachment_id}/download`

## Testing
### Existing general smoke test
```bash
tests/smoke.sh
```

### Kanban-specific regression check
```bash
source .venv/bin/activate
python tests/kanban_regression.py
```

This regression script currently checks:
- board load
- task drawer load
- project/customer search endpoints
- project-create flow
- comment creation and comment validation
- attachment upload
- attachment download
- attachment remove
- move
- update
- archive

## Operational recommendation
For local or server usage, keep one canonical port and one running instance.

Recommended canonical command:
```bash
uvicorn apps.kanban.main:app --host 0.0.0.0 --port 8010
```

## Current maturity
Treat the app as:
- usable internal v1
- stable enough for day-to-day iteration
- still worth continued polish, especially around UX refinement and broader regression coverage
