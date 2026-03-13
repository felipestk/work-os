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


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_PATH.read_text(encoding='utf-8'))
    conn.commit()
