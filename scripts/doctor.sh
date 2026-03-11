#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ ! -x "$ROOT_DIR/bin/workctl" ]; then
  echo "ERROR: workctl not found or not executable at $ROOT_DIR/bin/workctl" >&2
  exit 1
fi

"$ROOT_DIR/bin/workctl" doctor
