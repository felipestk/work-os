#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_DIR="$ROOT_DIR/skills/work-os"
DIST_DIR="$ROOT_DIR/dist"
PACKAGER="/usr/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py"

if [ ! -f "$PACKAGER" ]; then
  echo "ERROR: package_skill.py not found at $PACKAGER" >&2
  exit 1
fi

mkdir -p "$DIST_DIR"
python3 "$PACKAGER" "$SKILL_DIR" "$DIST_DIR"

echo "Packaged skill into: $DIST_DIR"
