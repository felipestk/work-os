# OpenClaw integration

This repo is designed so another OpenClaw host can install the toolkit and have the skill available immediately.

## Installed result
After `scripts/install.sh`, the target host should have:
- toolkit at `~/.local/share/openclaw-workos`
- `workctl` available through `~/.local/bin/workctl`
- runtime data under `~/.openclaw/workspace`
- skill installed at `~/.openclaw/workspace/skills/work-os/`

## Required host integration
The receiving OpenClaw host should also apply:
- `docs/agents-policy-snippet.md`
- `docs/tools-snippet.md`

Why:
- install alone gives the host the toolkit + skill
- AGENTS/TOOLS integration tells the host when and how to actually use it

## Recommended AGENTS.md positioning
The host should treat Work OS as the preferred system when work has:
- customer context
- continuity over time
- PR-coded project tracking
- offer/commercial scope
- important communications or decisions
- explicit task/board needs

## Important behavioral note
Tasks are an optional extension layer.
The default behavioral model should still prioritize:
1. customer
2. project
3. project event
4. offer
5. activity

Only use tasks when explicit task tracking or kanban workflows are wanted.

## Kanban hosting expectation
When the kanban app is deployed on a host, the documented/canonical app location should be:
- `apps/workos-kanban/`

Recommended serving pattern:
- run the app process on a local-only port
- install `nginx`
- configure `nginx` as the reverse proxy in front of the kanban app

This should be treated as the default operator expectation for handoff/install docs.

## Suggested install validation on the target host
```bash
source ~/.local/share/openclaw-workos/env.sh
workctl doctor
tests/smoke.sh
```
