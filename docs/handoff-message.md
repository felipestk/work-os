# Handoff message

Use this when sending the repo to another OpenClaw host/operator.

---

I put together a reusable **Work OS** toolkit/skill for OpenClaw.

**Repo:** `https://github.com/felipestk/work-os/`

It gives an OpenClaw host a structured workflow for:
- customers
- PR-coded projects
- offers
- activities
- optional tasks / kanban tracking
- attachments

## What to install
```bash
git clone https://github.com/felipestk/work-os.git openclaw-workos
cd openclaw-workos
scripts/install.sh
source ~/.local/share/openclaw-workos/env.sh
workctl doctor
tests/smoke.sh
```

## Expected result
- `sqlite3` available
- toolkit installed under `~/.local/share/openclaw-workos`
- `workctl` available in `~/.local/bin`
- runtime DB under `~/.openclaw/workspace/ops/workos/workos.db`
- projects under `~/.openclaw/workspace/work/projects`
- customers under `~/.openclaw/workspace/work/customers`
- skill installed under `~/.openclaw/workspace/skills/work-os`

## Important follow-up on the target host
Please also apply the repo snippets/docs to the target OpenClaw host:
- `docs/agents-policy-snippet.md`
- `docs/tools-snippet.md`
- `docs/openclaw-integration.md`

That part matters because:
- install makes the toolkit and skill available
- AGENTS/TOOLS integration makes the host actually prefer and enforce the workflow

## Kanban deployment expectation
If the kanban app is being deployed on the target host, please standardize on:
- app location: `apps/workos-kanban/`
- serving model: `nginx` as a reverse proxy in front of the app

Recommended shape:
- run the app on a local/internal port (for example `127.0.0.1:8010`)
- terminate/expose through `nginx`
- keep direct public exposure off the Uvicorn process

This gives us one predictable place for routing, TLS, auth, and operational hardening.

## Behavioral note
Tasks are supported, but they are intentionally optional.
The default Work OS model should still center on:
- customer
- project
- project event
- offer
- activity

Use tasks only when explicit task tracking / board workflow is needed.
