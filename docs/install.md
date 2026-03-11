# Installation

## Goal
Install `openclaw-workos` as a reusable toolkit for another OpenClaw environment, with the Work OS skill available immediately after install.

## Recommended split
### Toolkit code
Install the reusable toolkit under:
- `$HOME/.local/share/openclaw-workos`

### Runtime data
Store live data under the OpenClaw workspace:
- `~/.openclaw/workspace/ops/workos/workos.db`
- `~/.openclaw/workspace/work/projects/`
- `~/.openclaw/workspace/work/customers/`

### Skill location
Install the skill into the OpenClaw workspace skill directory:
- `~/.openclaw/workspace/skills/work-os/`

This matches OpenClaw's normal skill discovery behavior.

## User-level install
```bash
scripts/install.sh
```

The installer checks for `sqlite3` first. If it is missing, it attempts to install it automatically using a supported package manager (`apt-get`, `dnf`, `yum`, `apk`, `pacman`, or `brew`). If that fails, it stops with a clear manual-install instruction.

This installs the repo contents to:
- `$HOME/.local/share/openclaw-workos`

And symlinks:
- `$HOME/.local/bin/workctl`

It also installs the included skill to:
- `~/.openclaw/workspace/skills/work-os/`

And writes:
- `$HOME/.local/share/openclaw-workos/env.sh`

That file exports:
- `OPENCLAW_WORKSPACE`
- `OPENCLAW_WORKSPACE_SKILLS_DIR`
- `WORKCTL_DB_PATH`
- `WORKCTL_PROJECTS_ROOT`
- `WORKCTL_CUSTOMERS_ROOT`
- `PATH`

## Make `workctl` callable from everywhere
After install, run:

```bash
source "$HOME/.local/share/openclaw-workos/env.sh"
```

To make it persistent, add this to your shell profile (`.bashrc`, `.zshrc`, etc.):

```bash
source "$HOME/.local/share/openclaw-workos/env.sh"
```

## Required AGENTS.md integration
Installing the toolkit and skill is not the whole story.
To make the receiving OpenClaw actually enforce customer-linked project tracking, add the recommended Work OS policy block to that host's `AGENTS.md`.

Use:
- `docs/agents-policy-snippet.md`

This is the recommended post-install step for any serious Work OS deployment.

## Skill readiness after install
The installer copies the included `work-os` skill into the OpenClaw workspace skills directory.

That means the receiving OpenClaw instance should already have:
- the CLI/toolkit installed
- the runtime paths configured
- the skill available for discovery

The `AGENTS.md` policy block is what makes the behavior mandatory rather than optional.

## Local repo usage
For repo-local demo/testing only:

```bash
scripts/bootstrap.sh
bin/workctl doctor
tests/smoke.sh
```

## Notes
- Runtime DBs are not tracked in git.
- Demo data can be loaded with `scripts/bootstrap.sh`.
- The packaged `.skill` artifact in `dist/` is optional distribution output; normal repo install does not require it.
