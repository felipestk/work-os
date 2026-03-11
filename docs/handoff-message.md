# Handoff message

Use this message when sending the repo to another OpenClaw host/operator for installation.

---

I put together a repo for a reusable **Work OS** toolkit/skill for OpenClaw:

**Repo:** `https://github.com/felipestk/work-os/`

The goal is to give an OpenClaw host a unified workflow for:
- customers
- PR-coded projects
- offers
- activities / continuity logging

It includes:
- `workctl` CLI
- SQLite schema
- OpenClaw skill: `work-os`
- install/bootstrap scripts
- docs and demo fixtures

## What I’d like you to do
Please install it on the target OpenClaw host and make sure both the toolkit **and** the skill are available.

### Install steps
```bash
git clone https://github.com/felipestk/work-os/
cd openclaw-workos
scripts/install.sh
source ~/.local/share/openclaw-workos/env.sh
workctl doctor
```

### Expected install result
- toolkit under `~/.local/share/openclaw-workos`
- `workctl` available via `~/.local/bin/workctl`
- runtime DB under `~/.openclaw/workspace/ops/workos/workos.db`
- projects under `~/.openclaw/workspace/work/projects`
- customers under `~/.openclaw/workspace/work/customers`
- skill installed under `~/.openclaw/workspace/skills/work-os`

## Important: AGENTS.md integration
Please also add the recommended Work OS policy block to that host’s `AGENTS.md`.

Use this file from the repo:
- `docs/agents-policy-snippet.md`

That part is important because the installer makes the toolkit/skill available, but the `AGENTS.md` block makes customer-linked project tracking a mandatory behavior.

## Helpful docs
- `docs/install.md`
- `docs/openclaw-integration.md`
- `docs/agents-policy-snippet.md`
- `docs/usage.md`

## Optional validation
You can also run:
```bash
tests/smoke.sh
```
