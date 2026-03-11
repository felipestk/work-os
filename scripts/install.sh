#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_ROOT="${OPENCLAW_WORKOS_HOME:-$HOME/.local/share/openclaw-workos}"
BIN_DIR="${OPENCLAW_WORKOS_BIN_DIR:-$HOME/.local/bin}"
WORKSPACE_DIR="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
WORKSPACE_SKILLS_DIR="${OPENCLAW_WORKSPACE_SKILLS_DIR:-$WORKSPACE_DIR/skills}"
ENV_FILE="$INSTALL_ROOT/env.sh"

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
