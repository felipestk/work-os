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
- customers
- contacts
- projects (`PRxxxx`)
- project events
- offers
- offer versions
- offer line items
- activities

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
- installs toolkit code under `~/.local/share/openclaw-workos`
- links `workctl` into `~/.local/bin`
- stores live DB/projects/customers under `~/.openclaw/workspace`
- installs the `work-os` skill into `~/.openclaw/workspace/skills/work-os`

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
- `docs/handoff-message.md`
- `docs/architecture.md`
- `docs/cli.md`
