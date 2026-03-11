# Skill packaging

The Work OS skill lives inside this repo at:
- `skills/work-os/`

This is intentional.
The repo is the source of truth for:
- the `workctl` CLI
- the schema
- the skill instructions
- the skill references

## Default installation behavior
Normal repo installation already copies the skill into the OpenClaw workspace skills directory:
- `~/.openclaw/workspace/skills/work-os/`

So for most users, sending the repo link and running `scripts/install.sh` should be enough.

## Why package the skill separately?
Separate packaging is still useful when you want to:
- distribute only the skill
- test skill packaging validation
- publish the skill artifact independently of the full toolkit

## How to package the skill
Use the helper script from the repo root:

```bash
scripts/package-skill.sh
```

This packages:
- `skills/work-os/`

And writes the output to:
- `dist/`

## What the helper uses
The helper wraps OpenClaw's official packaging script:
- `/usr/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py`

## Expected output
After packaging, expect a file like:
- `dist/work-os.skill`

## Notes
- The skill package includes only the skill folder contents.
- Runtime DBs and local generated work folders are not part of the skill package.
- The toolkit repo can be installed on a machine even if the skill is distributed separately.
