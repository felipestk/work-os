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

## User-level install
```bash
git clone https://github.com/felipestk/work-os.git openclaw-workos
cd openclaw-workos
scripts/install.sh
source "$HOME/.local/share/openclaw-workos/env.sh"
workctl doctor
```

The installer:
- checks for `sqlite3`
- attempts package-manager install when possible
- installs toolkit files under `$HOME/.local/share/openclaw-workos`
- symlinks `workctl` into `$HOME/.local/bin`
- installs the `work-os` skill into `~/.openclaw/workspace/skills/work-os/`
- writes `$HOME/.local/share/openclaw-workos/env.sh`

## Recommended post-install validation
```bash
workctl doctor
tests/smoke.sh
```

Expected outcome:
- `workctl` runs from shell
- DB path resolves into the workspace
- skill exists under workspace skills
- smoke test passes on the target host

## Required OpenClaw integration
To make the receiving OpenClaw actually follow Work OS conventions, also apply:
- `docs/agents-policy-snippet.md`
- `docs/tools-snippet.md`
- `docs/openclaw-integration.md`

The installer makes the toolkit available.
The policy/docs integration makes the behavior reliable.

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
- Tasks are an optional extension layer; the default workflow is still customer → project → offer/activity.
