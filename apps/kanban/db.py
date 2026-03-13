import os
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WORKSPACE = Path(os.environ.get('OPENCLAW_WORKSPACE', str(Path.home() / '.openclaw' / 'workspace'))).expanduser()
DB_PATH = Path(os.environ.get('WORKCTL_DB_PATH', str(DEFAULT_WORKSPACE / 'ops' / 'workos' / 'workos.db'))).expanduser()
SCHEMA_PATH = Path(os.environ.get('WORKCTL_SCHEMA_PATH', str(ROOT / 'schema' / 'workos.sql'))).expanduser()


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    return conn


def migrate_attachments_table(conn: sqlite3.Connection) -> None:
    row = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='attachments'").fetchone()
    if not row or not row['sql']:
        return
    sql = row['sql']
    if "'task'" in sql:
        return
    conn.executescript(
        '''
        ALTER TABLE attachments RENAME TO attachments_legacy;
        CREATE TABLE attachments (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          entity_type TEXT NOT NULL CHECK (entity_type IN ('activity','offer','customer','contact','project','task')),
          entity_ref TEXT NOT NULL,
          file_path TEXT NOT NULL,
          mime_type TEXT,
          checksum TEXT,
          created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
        );
        INSERT INTO attachments(id, entity_type, entity_ref, file_path, mime_type, checksum, created_at)
        SELECT id, entity_type, entity_ref, file_path, mime_type, checksum, created_at
        FROM attachments_legacy;
        DROP TABLE attachments_legacy;
        CREATE INDEX IF NOT EXISTS idx_attachments_entity ON attachments(entity_type, entity_ref, created_at DESC);
        '''
    )


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_PATH.read_text(encoding='utf-8'))
    migrate_attachments_table(conn)
    conn.commit()
