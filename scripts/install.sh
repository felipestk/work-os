#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_ROOT="${OPENCLAW_WORKOS_HOME:-$HOME/.local/share/openclaw-workos}"
BIN_DIR="${OPENCLAW_WORKOS_BIN_DIR:-$HOME/.local/bin}"
WORKSPACE_DIR="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
WORKSPACE_SKILLS_DIR="${OPENCLAW_WORKSPACE_SKILLS_DIR:-$WORKSPACE_DIR/skills}"
ENV_FILE="$INSTALL_ROOT/env.sh"

run_as_root() {
  if [ "$(id -u)" -eq 0 ]; then
    "$@"
  elif command -v sudo >/dev/null 2>&1; then
    sudo "$@"
  else
    return 1
  fi
}

ensure_sqlite3() {
  if command -v sqlite3 >/dev/null 2>&1; then
    return 0
  fi

  echo "sqlite3 not found. Attempting to install it..."

  if command -v apt-get >/dev/null 2>&1; then
    run_as_root apt-get update && run_as_root apt-get install -y sqlite3
  elif command -v dnf >/dev/null 2>&1; then
    run_as_root dnf install -y sqlite
  elif command -v yum >/dev/null 2>&1; then
    run_as_root yum install -y sqlite
  elif command -v apk >/dev/null 2>&1; then
    run_as_root apk add --no-cache sqlite
  elif command -v pacman >/dev/null 2>&1; then
    run_as_root pacman -Sy --noconfirm sqlite
  elif command -v brew >/dev/null 2>&1; then
    brew install sqlite
  else
    echo "ERROR: sqlite3 is required but no supported package manager was detected." >&2
    echo "Please install sqlite3 manually, then rerun scripts/install.sh" >&2
    exit 1
  fi

  if ! command -v sqlite3 >/dev/null 2>&1; then
    echo "ERROR: sqlite3 installation did not succeed. Please install it manually and rerun scripts/install.sh" >&2
    exit 1
  fi
}

ensure_sqlite3

mkdir -p "$INSTALL_ROOT" "$BIN_DIR" "$WORKSPACE_DIR/ops/workos" "$WORKSPACE_DIR/work/projects" "$WORKSPACE_DIR/work/customers" "$WORKSPACE_SKILLS_DIR"

rm -rf "$INSTALL_ROOT/bin" "$INSTALL_ROOT/schema" "$INSTALL_ROOT/skills" "$INSTALL_ROOT/docs" "$INSTALL_ROOT/examples" "$INSTALL_ROOT/tests" "$INSTALL_ROOT/scripts"
cp -R "$ROOT_DIR/bin" "$INSTALL_ROOT/"
cp -R "$ROOT_DIR/schema" "$INSTALL_ROOT/"
cp -R "$ROOT_DIR/skills" "$INSTALL_ROOT/"
cp -R "$ROOT_DIR/docs" "$INSTALL_ROOT/"
cp -R "$ROOT_DIR/examples" "$INSTALL_ROOT/"
cp -R "$ROOT_DIR/tests" "$INSTALL_ROOT/"
cp -R "$ROOT_DIR/scripts" "$INSTALL_ROOT/"
cp "$ROOT_DIR/README.md" "$INSTALL_ROOT/"
cp "$ROOT_DIR/.gitignore" "$INSTALL_ROOT/" 2>/dev/null || true

chmod +x "$INSTALL_ROOT/bin/workctl" "$INSTALL_ROOT/scripts/"*.sh
ln -sf "$INSTALL_ROOT/bin/workctl" "$BIN_DIR/workctl"

# Install the skill into the workspace skills directory so OpenClaw can discover it.
rm -rf "$WORKSPACE_SKILLS_DIR/work-os"
cp -R "$INSTALL_ROOT/skills/work-os" "$WORKSPACE_SKILLS_DIR/work-os"

cat > "$ENV_FILE" <<EOF
export OPENCLAW_WORKSPACE="$WORKSPACE_DIR"
export OPENCLAW_WORKSPACE_SKILLS_DIR="$WORKSPACE_SKILLS_DIR"
export WORKCTL_DB_PATH="$WORKSPACE_DIR/ops/workos/workos.db"
export WORKCTL_PROJECTS_ROOT="$WORKSPACE_DIR/work/projects"
export WORKCTL_CUSTOMERS_ROOT="$WORKSPACE_DIR/work/customers"
export PATH="$BIN_DIR:\$PATH"
EOF

cat <<EOF
Installed openclaw-workos to: $INSTALL_ROOT
Linked CLI to: $BIN_DIR/workctl
Runtime workspace: $WORKSPACE_DIR
Installed skill to: $WORKSPACE_SKILLS_DIR/work-os
Environment helper: $ENV_FILE

To activate in your shell:
  source "$ENV_FILE"

Or add this line to your shell profile:
  source "$ENV_FILE"
EOF
