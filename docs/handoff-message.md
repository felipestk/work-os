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

## Behavioral note
Tasks are supported, but they are intentionally optional.
The default Work OS model should still center on:
- customer
- project
- project event
- offer
- activity

Use tasks only when explicit task tracking / board workflow is needed.
