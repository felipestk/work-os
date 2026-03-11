# OpenClaw integration

This repo is designed so another OpenClaw host can install the toolkit and have the skill available immediately.

## Installed result
After `scripts/install.sh`, the target host should have:
- toolkit at `~/.local/share/openclaw-workos`
- `workctl` available through `~/.local/bin/workctl`
- runtime data under `~/.openclaw/workspace`
- skill installed at `~/.openclaw/workspace/skills/work-os/`

## Required AGENTS.md integration
The receiving OpenClaw host should also add the Work OS policy block to its `AGENTS.md`.

Use the exact block from:
- `docs/agents-policy-snippet.md`

This matters because installation alone gives the host:
- the toolkit
- the skill
- the runtime paths

But the `AGENTS.md` rule is what makes customer-linked project tracking a mandatory behavior.

## Recommended TOOLS.md integration
The receiving OpenClaw host should also add the Work OS tooling reference block to its `TOOLS.md`.

Use the exact block from:
- `docs/tools-snippet.md`

This gives the host a local command reference that matches the installed `workctl` workflow.

## Recommended short AGENTS.md skill entry
If the receiving host keeps a short installed-skills list, add a line like:

```md
## Installed Skills
- **work-os**: Unified customer, project, offer, and activity workflow for tracked work via `workctl`. Use when work should be linked to customers, PR-coded projects, offers, or activity timelines instead of being handled as untracked ad-hoc work.
```

## Optional stronger behavioral nudge
If desired, also add:

```md
When work has continuity, client context, pricing, project tracking, or operational follow-up needs, prefer the `work-os` skill and `workctl` workflow over ad-hoc notes or untracked files.
```

## Why this matters
OpenClaw uses skills more reliably when both are true:
1. the skill exists in a discoverable path
2. the host instructions clearly reinforce when it should be used

The goal is to make `work-os` both installed and behaviorally adopted.
