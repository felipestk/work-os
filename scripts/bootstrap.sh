#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DB_PATH="${WORKCTL_DB_PATH:-$ROOT_DIR/data/workos.db}"
WORKSPACE_DIR="${OPENCLAW_WORKSPACE:-$ROOT_DIR}"
PROJECTS_ROOT="${WORKCTL_PROJECTS_ROOT:-$WORKSPACE_DIR/work/projects}"
CUSTOMERS_ROOT="${WORKCTL_CUSTOMERS_ROOT:-$WORKSPACE_DIR/work/customers}"

mkdir -p "$(dirname "$DB_PATH")" "$PROJECTS_ROOT" "$CUSTOMERS_ROOT"
rm -f "$DB_PATH"
OPENCLAW_WORKSPACE="$WORKSPACE_DIR" \
WORKCTL_DB_PATH="$DB_PATH" \
WORKCTL_PROJECTS_ROOT="$PROJECTS_ROOT" \
WORKCTL_CUSTOMERS_ROOT="$CUSTOMERS_ROOT" \
"$ROOT_DIR/bin/workctl" init >/dev/null
sqlite3 "$DB_PATH" < "$ROOT_DIR/examples/demo-seed.sql"

echo "Bootstrapped demo database at: $DB_PATH"
echo "Projects root: $PROJECTS_ROOT"
echo "Customers root: $CUSTOMERS_ROOT"
