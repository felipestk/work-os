from __future__ import annotations

import hashlib
import mimetypes
import os
import re
import shutil
import sqlite3
import uuid
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .db import connect, init_db

BOARD_NAME = 'main'
COLUMNS = OrderedDict([
    ('backlog', 'backlog'),
    ('todo', 'to do'),
    ('doing', 'doing'),
    ('review', 'review'),
    ('done', 'done'),
])
COLUMN_KEYS = list(COLUMNS.keys())
COLUMN_TO_STATUS = {
    'backlog': 'todo',
    'todo': 'todo',
    'doing': 'in_progress',
    'review': 'blocked',
    'done': 'done',
}
PRIORITY_OPTIONS = ['low', 'medium', 'high', 'urgent']
DEFAULT_WORKSPACE = Path(os.environ.get('OPENCLAW_WORKSPACE', str(Path.home() / '.openclaw' / 'workspace'))).expanduser()
PROJECTS_ROOT = Path(os.environ.get('WORKCTL_PROJECTS_ROOT', str(DEFAULT_WORKSPACE / 'work' / 'projects'))).expanduser()
CUSTOMERS_ROOT = Path(os.environ.get('WORKCTL_CUSTOMERS_ROOT', str(DEFAULT_WORKSPACE / 'work' / 'customers'))).expanduser()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text or 'item'


def next_customer_code(conn: sqlite3.Connection) -> str:
    row = conn.execute("SELECT customer_code FROM customers ORDER BY id DESC LIMIT 1").fetchone()
    if not row:
        return 'CUST0001'
    return f"CUST{int(row['customer_code'][4:]) + 1:04d}"


def next_project_id(conn: sqlite3.Connection) -> str:
    row = conn.execute("SELECT id FROM projects ORDER BY id DESC LIMIT 1").fetchone()
    if not row:
        return 'PR0001'
    return f"PR{int(row['id'][2:]) + 1:04d}"


def normalize_board(board: str | None) -> str:
    return (board or '').strip() or BOARD_NAME


def normalize_column(column_key: str | None) -> str:
    value = (column_key or '').strip() or 'backlog'
    return value if value in COLUMNS else 'backlog'


def normalize_priority(priority: str | None) -> str | None:
    value = (priority or '').strip().lower()
    return value if value in PRIORITY_OPTIONS else None


def normalize_due_at(due_at: str | None) -> str | None:
    value = (due_at or '').strip()
    if not value:
        return None
    if len(value) == 10:
        return f'{value}T00:00:00Z'
    return value


def today_iso() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def previous_column(column_key: str) -> str | None:
    column_key = normalize_column(column_key)
    idx = COLUMN_KEYS.index(column_key)
    return COLUMN_KEYS[idx - 1] if idx > 0 else None


def next_column(column_key: str) -> str | None:
    column_key = normalize_column(column_key)
    idx = COLUMN_KEYS.index(column_key)
    return COLUMN_KEYS[idx + 1] if idx < len(COLUMN_KEYS) - 1 else None


def project_exists(conn, project_id: str) -> bool:
    row = conn.execute('SELECT 1 FROM projects WHERE id = ?', (project_id,)).fetchone()
    return row is not None


def list_projects() -> list[dict[str, Any]]:
    with connect() as conn:
        init_db(conn)
        rows = conn.execute(
            '''
            SELECT p.id, p.title, c.name AS customer_name
            FROM projects p
            JOIN customers c ON c.id = p.customer_id
            ORDER BY p.id DESC
            '''
        ).fetchall()
    return [dict(row) for row in rows]


def search_projects(query: str = '', limit: int = 10) -> list[dict[str, Any]]:
    query = (query or '').strip()
    project_id_match = re.match(r'^(PR\d{4})\b', query, re.IGNORECASE)
    normalized_project_id = project_id_match.group(1).upper() if project_id_match else None
    like = f'%{query}%'
    with connect() as conn:
        init_db(conn)
        if normalized_project_id:
            rows = conn.execute(
                '''
                SELECT p.id, p.title, c.name AS customer_name
                FROM projects p
                JOIN customers c ON c.id = p.customer_id
                WHERE p.id = ? OR p.id LIKE ? OR p.title LIKE ? OR c.name LIKE ?
                ORDER BY CASE WHEN p.id = ? THEN 0 ELSE 1 END, p.id DESC
                LIMIT ?
                ''',
                (normalized_project_id, f'%{normalized_project_id}%', like, like, normalized_project_id, limit),
            ).fetchall()
        elif query:
            rows = conn.execute(
                '''
                SELECT p.id, p.title, c.name AS customer_name
                FROM projects p
                JOIN customers c ON c.id = p.customer_id
                WHERE p.id LIKE ? OR p.title LIKE ? OR c.name LIKE ?
                ORDER BY p.id DESC
                LIMIT ?
                ''',
                (like, like, like, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                '''
                SELECT p.id, p.title, c.name AS customer_name
                FROM projects p
                JOIN customers c ON c.id = p.customer_id
                ORDER BY p.id DESC
                LIMIT ?
                ''',
                (limit,),
            ).fetchall()
    return [dict(r) for r in rows]


def search_customers(query: str = '', limit: int = 10) -> list[dict[str, Any]]:
    query = (query or '').strip()
    like = f'%{query}%'
    with connect() as conn:
        init_db(conn)
        if query:
            rows = conn.execute(
                '''
                SELECT id, customer_code, name
                FROM customers
                WHERE name LIKE ? OR customer_code LIKE ?
                ORDER BY name ASC
                LIMIT ?
                ''',
                (like, like, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                '''
                SELECT id, customer_code, name
                FROM customers
                ORDER BY name ASC
                LIMIT ?
                ''',
                (limit,),
            ).fetchall()
    return [dict(r) for r in rows]


def list_filter_options() -> dict[str, list[str]]:
    with connect() as conn:
        init_db(conn)
        assignees = [r['assignee'] for r in conn.execute("SELECT DISTINCT assignee FROM tasks WHERE assignee IS NOT NULL AND TRIM(assignee) != '' AND status != 'archived' ORDER BY assignee")]
        customers = [r['customer_name'] for r in conn.execute(
            '''
            SELECT DISTINCT c.name AS customer_name
            FROM tasks t
            JOIN projects p ON p.id = t.project_id
            JOIN customers c ON c.id = p.customer_id
            WHERE t.status != 'archived'
            ORDER BY c.name
            '''
        )]
    return {'assignees': assignees, 'customers': customers}


def build_filters(project_id: str = '', customer_name: str = '') -> dict[str, str]:
    return {
        'project_id': (project_id or '').strip(),
        'customer_name': (customer_name or '').strip(),
    }


def create_customer_and_project(*, customer_name: str, project_title: str, owner: str | None = None) -> dict[str, str]:
    customer_name = customer_name.strip()
    project_title = project_title.strip()
    if not customer_name or not project_title:
        raise ValueError('customer and project title are required')
    with connect() as conn:
        init_db(conn)
        row = conn.execute('SELECT id, customer_code, name FROM customers WHERE name = ?', (customer_name,)).fetchone()
        if row:
            customer_id = row['id']
            customer_code = row['customer_code']
        else:
            customer_code = next_customer_code(conn)
            cur = conn.execute(
                "INSERT INTO customers(customer_code, customer_type, name) VALUES (?, 'company', ?)",
                (customer_code, customer_name),
            )
            customer_id = cur.lastrowid
            (CUSTOMERS_ROOT / customer_code).mkdir(parents=True, exist_ok=True)
        project_id = next_project_id(conn)
        slug = slugify(project_title)
        folder = PROJECTS_ROOT / f'{project_id}-{slug}'
        folder.mkdir(parents=True, exist_ok=True)
        conn.execute(
            '''
            INSERT INTO projects(id, slug, customer_id, title, status, objective, summary, folder_path, owner)
            VALUES (?, ?, ?, ?, 'active', ?, ?, ?, ?)
            ''',
            (project_id, slug, customer_id, project_title, f'Created from kanban picker for {customer_name}', None, str(folder), owner),
        )
        conn.execute(
            "INSERT INTO project_events(project_id, event_type, note, metadata_json) VALUES (?, 'created', ?, ?)",
            (project_id, 'Project created from kanban picker', '{"actor":"kanban","timestamp":"' + now_iso() + '"}'),
        )
        conn.commit()
    return {'id': project_id, 'title': project_title, 'customer_name': customer_name}


def list_board_tasks(board: str = BOARD_NAME, *, filters: dict[str, str] | None = None) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {key: [] for key in COLUMNS}
    filters = build_filters(**(filters or {}))
    where = ["t.status != 'archived'", "COALESCE(NULLIF(t.board, ''), 'main') = ?"]
    params: list[Any] = [normalize_board(board)]
    if filters['project_id']:
        where.append('t.project_id = ?')
        params.append(filters['project_id'])
    if filters['customer_name']:
        where.append('c.name = ?')
        params.append(filters['customer_name'])
    with connect() as conn:
        init_db(conn)
        rows = conn.execute(
            f'''
            SELECT
              t.id,
              t.project_id,
              t.title,
              t.description,
              t.status,
              t.priority,
              t.assignee,
              t.due_at,
              COALESCE(NULLIF(t.board, ''), 'main') AS board,
              COALESCE(NULLIF(t.column_key, ''), 'backlog') AS column_key,
              COALESCE(t.wip_order, t.sort_order, t.id) AS display_order,
              p.title AS project_title,
              c.name AS customer_name,
              COUNT(DISTINCT tc.id) AS comment_count,
              COUNT(DISTINCT a.id) AS attachment_count
            FROM tasks t
            JOIN projects p ON p.id = t.project_id
            JOIN customers c ON c.id = p.customer_id
            LEFT JOIN task_comments tc ON tc.task_id = t.id
            LEFT JOIN attachments a ON a.entity_type = 'task' AND a.entity_ref = CAST(t.id AS TEXT)
            WHERE {' AND '.join(where)}
            GROUP BY
              t.id, t.project_id, t.title, t.description, t.status, t.priority, t.assignee, t.due_at,
              t.board, t.column_key, t.wip_order, t.sort_order, p.title, c.name
            ORDER BY column_key, display_order, t.id
            ''',
            params,
        ).fetchall()
    for row in rows:
        item = decorate_task(dict(row))
        grouped[item['column_key']].append(item)
    return grouped


def summarize(text: str | None, limit: int = 140) -> str:
    if not text:
        return ''
    compact = ' '.join(text.split())
    return compact if len(compact) <= limit else compact[: limit - 1].rstrip() + '…'


def decorate_task(task: dict[str, Any]) -> dict[str, Any]:
    task['board'] = normalize_board(task.get('board'))
    task['column_key'] = normalize_column(task.get('column_key'))
    task['priority'] = normalize_priority(task.get('priority'))
    task['description_preview'] = summarize(task.get('description'))
    task['previous_column'] = previous_column(task['column_key'])
    task['next_column'] = next_column(task['column_key'])
    task['column_label'] = COLUMNS[task['column_key']]
    task['due_date'] = (task.get('due_at') or '')[:10] if task.get('due_at') else None
    task['is_overdue'] = bool(task['due_date'] and task['due_date'] < today_iso() and task['column_key'] != 'done')
    task['is_due_today'] = bool(task['due_date'] and task['due_date'] == today_iso() and task['column_key'] != 'done')
    return task


def column_counts(grouped: dict[str, list[dict[str, Any]]]) -> dict[str, int]:
    return {column: len(grouped.get(column, [])) for column in COLUMNS}


def next_wip_order(conn, column_key: str, board: str = BOARD_NAME) -> float:
    row = conn.execute(
        '''
        SELECT COALESCE(MAX(COALESCE(wip_order, sort_order, id)), 0) AS max_order
        FROM tasks
        WHERE status != 'archived'
          AND COALESCE(NULLIF(board, ''), 'main') = ?
          AND COALESCE(NULLIF(column_key, ''), 'backlog') = ?
        ''',
        (normalize_board(board), normalize_column(column_key)),
    ).fetchone()
    return float(row['max_order'] or 0) + 10.0


def create_task(*, title: str, project_id: str, column_key: str, description: str | None = None) -> int:
    with connect() as conn:
        init_db(conn)
        if not project_exists(conn, project_id):
            raise ValueError(f'Unknown project: {project_id}')
        normalized_column = normalize_column(column_key)
        wip_order = next_wip_order(conn, normalized_column)
        cur = conn.execute(
            '''
            INSERT INTO tasks(project_id, title, description, status, board, column_key, wip_order, sort_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                project_id,
                title.strip(),
                (description or '').strip() or None,
                COLUMN_TO_STATUS[normalized_column],
                BOARD_NAME,
                normalized_column,
                wip_order,
                int(wip_order),
            ),
        )
        conn.execute(
            "INSERT INTO task_comments(task_id, comment_type, body, author) VALUES (?, 'system', ?, 'kanban')",
            (cur.lastrowid, f'Task created on the {normalized_column} column'),
        )
        conn.commit()
        return int(cur.lastrowid)


def move_task(task_id: int, destination_column: str) -> None:
    normalized_column = normalize_column(destination_column)
    with connect() as conn:
        init_db(conn)
        task = conn.execute('SELECT id, column_key, status FROM tasks WHERE id = ?', (task_id,)).fetchone()
        if not task:
            raise ValueError(f'Unknown task: {task_id}')
        if task['status'] == 'archived':
            raise ValueError('Archived tasks cannot be moved from the board')
        wip_order = next_wip_order(conn, normalized_column)
        conn.execute(
            'UPDATE tasks SET board=?, column_key=?, wip_order=?, sort_order=?, status=? WHERE id=?',
            (BOARD_NAME, normalized_column, wip_order, int(wip_order), COLUMN_TO_STATUS[normalized_column], task_id),
        )
        conn.execute(
            "INSERT INTO task_comments(task_id, comment_type, body, author) VALUES (?, 'system', ?, 'kanban')",
            (task_id, f'Task moved to {normalized_column}'),
        )
        conn.commit()


def archive_task(task_id: int) -> None:
    with connect() as conn:
        init_db(conn)
        task = conn.execute('SELECT id FROM tasks WHERE id = ?', (task_id,)).fetchone()
        if not task:
            raise ValueError(f'Unknown task: {task_id}')
        conn.execute("UPDATE tasks SET status='archived' WHERE id=?", (task_id,))
        conn.execute("INSERT INTO task_comments(task_id, comment_type, body, author) VALUES (?, 'system', 'Task archived from board', 'kanban')", (task_id,))
        conn.commit()


def update_task(task_id: int, *, title: str, description: str | None, project_id: str, priority: str | None, assignee: str | None, due_at: str | None) -> None:
    with connect() as conn:
        init_db(conn)
        task = conn.execute('SELECT id FROM tasks WHERE id = ?', (task_id,)).fetchone()
        if not task:
            raise ValueError(f'Unknown task: {task_id}')
        if not project_exists(conn, project_id):
            raise ValueError(f'Unknown project: {project_id}')
        conn.execute(
            'UPDATE tasks SET title=?, description=?, project_id=?, priority=?, assignee=?, due_at=? WHERE id=?',
            (
                title.strip(),
                (description or '').strip() or None,
                project_id,
                normalize_priority(priority),
                (assignee or '').strip() or None,
                normalize_due_at(due_at),
                task_id,
            ),
        )
        conn.execute("INSERT INTO task_comments(task_id, comment_type, body, author) VALUES (?, 'system', 'Task updated from board drawer', 'kanban')", (task_id,))
        conn.commit()


def add_task_comment(task_id: int, *, body: str, author: str | None = None, comment_type: str = 'comment') -> int:
    cleaned_body = (body or '').strip()
    cleaned_author = (author or '').strip() or 'kanban'
    cleaned_type = (comment_type or '').strip().lower() or 'comment'
    if not cleaned_body:
        raise ValueError('comment body is required')
    if cleaned_type not in {'comment', 'note', 'system'}:
        cleaned_type = 'comment'
    with connect() as conn:
        init_db(conn)
        task = conn.execute('SELECT id FROM tasks WHERE id = ?', (task_id,)).fetchone()
        if not task:
            raise ValueError(f'Unknown task: {task_id}')
        cur = conn.execute(
            'INSERT INTO task_comments(task_id, comment_type, body, author) VALUES (?, ?, ?, ?)',
            (task_id, cleaned_type, cleaned_body, cleaned_author),
        )
        conn.commit()
        return int(cur.lastrowid)


def file_checksum(file_path: Path) -> str:
    digest = hashlib.sha256()
    with file_path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(65536), b''):
            digest.update(chunk)
    return digest.hexdigest()


def safe_filename(name: str) -> str:
    cleaned = Path(name or '').name.strip()
    cleaned = re.sub(r'[^A-Za-z0-9._-]+', '-', cleaned)
    cleaned = re.sub(r'-+', '-', cleaned).strip('-')
    return cleaned or 'attachment.bin'


def task_attachment_dir(conn: sqlite3.Connection, task_id: int) -> Path:
    row = conn.execute(
        '''
        SELECT t.id, p.folder_path
        FROM tasks t
        JOIN projects p ON p.id = t.project_id
        WHERE t.id = ?
        ''',
        (task_id,),
    ).fetchone()
    if not row:
        raise ValueError(f'Unknown task: {task_id}')
    project_folder = Path(row['folder_path']) if row['folder_path'] else PROJECTS_ROOT / f'unknown-project-{task_id}'
    target = project_folder / 'tasks' / str(task_id) / 'attachments'
    target.mkdir(parents=True, exist_ok=True)
    return target


def save_uploaded_task_attachment(task_id: int, *, filename: str, source) -> dict[str, str | None]:
    cleaned_name = safe_filename(filename)
    with connect() as conn:
        init_db(conn)
        target_dir = task_attachment_dir(conn, task_id)
    stem = Path(cleaned_name).stem or 'attachment'
    suffix = Path(cleaned_name).suffix
    stored_name = f"{stem}-{uuid.uuid4().hex[:8]}{suffix}"
    destination = target_dir / stored_name
    with destination.open('wb') as handle:
        shutil.copyfileobj(source, handle)
    guessed_mime = mimetypes.guess_type(destination.name)[0]
    checksum = file_checksum(destination)
    return {'file_path': str(destination), 'mime_type': guessed_mime, 'checksum': checksum}


def add_task_attachment(task_id: int, *, file_path: str, mime_type: str | None = None) -> int:
    raw_path = (file_path or '').strip()
    cleaned_mime_type = (mime_type or '').strip() or None
    if not raw_path:
        raise ValueError('attachment path or URL is required')

    resolved_path = raw_path
    checksum = None
    if re.match(r'^https?://', raw_path, re.IGNORECASE):
        resolved_path = raw_path
    else:
        local_path = Path(raw_path).expanduser()
        if not local_path.is_absolute():
            local_path = (DEFAULT_WORKSPACE / local_path).resolve()
        else:
            local_path = local_path.resolve()
        if not local_path.exists() or not local_path.is_file():
            raise ValueError(f'File not found: {local_path}')
        resolved_path = str(local_path)
        checksum = file_checksum(local_path)

    with connect() as conn:
        init_db(conn)
        task = conn.execute('SELECT id FROM tasks WHERE id = ?', (task_id,)).fetchone()
        if not task:
            raise ValueError(f'Unknown task: {task_id}')
        cur = conn.execute(
            'INSERT INTO attachments(entity_type, entity_ref, file_path, mime_type, checksum) VALUES (?, ?, ?, ?, ?)',
            ('task', str(task_id), resolved_path, cleaned_mime_type, checksum),
        )
        conn.execute(
            "INSERT INTO task_comments(task_id, comment_type, body, author) VALUES (?, 'system', ?, 'kanban')",
            (task_id, f'Attachment added: {resolved_path}'),
        )
        conn.commit()
        return int(cur.lastrowid)


def create_uploaded_task_attachment(task_id: int, *, filename: str, source, mime_type: str | None = None) -> int:
    with connect() as conn:
        init_db(conn)
        task = conn.execute('SELECT id FROM tasks WHERE id = ?', (task_id,)).fetchone()
        if not task:
            raise ValueError(f'Unknown task: {task_id}')
    saved = save_uploaded_task_attachment(task_id, filename=filename, source=source)
    final_mime_type = (mime_type or '').strip() or saved['mime_type']
    with connect() as conn:
        init_db(conn)
        cur = conn.execute(
            'INSERT INTO attachments(entity_type, entity_ref, file_path, mime_type, checksum) VALUES (?, ?, ?, ?, ?)',
            ('task', str(task_id), saved['file_path'], final_mime_type, saved['checksum']),
        )
        conn.execute(
            "INSERT INTO task_comments(task_id, comment_type, body, author) VALUES (?, 'system', ?, 'kanban')",
            (task_id, f"Attachment uploaded: {saved['file_path']}"),
        )
        conn.commit()
        return int(cur.lastrowid)


def remove_task_attachment(task_id: int, attachment_id: int) -> None:
    with connect() as conn:
        init_db(conn)
        task = conn.execute('SELECT id FROM tasks WHERE id = ?', (task_id,)).fetchone()
        if not task:
            raise ValueError(f'Unknown task: {task_id}')
        attachment = conn.execute(
            "SELECT id, file_path FROM attachments WHERE id = ? AND entity_type='task' AND entity_ref = ?",
            (attachment_id, str(task_id)),
        ).fetchone()
        if not attachment:
            raise ValueError(f'Unknown task attachment: {attachment_id}')
        conn.execute('DELETE FROM attachments WHERE id = ?', (attachment_id,))
        conn.execute(
            "INSERT INTO task_comments(task_id, comment_type, body, author) VALUES (?, 'system', ?, 'kanban')",
            (task_id, f"Attachment removed: {attachment['file_path']}"),
        )
        conn.commit()
    try:
        attachment_path = Path(attachment['file_path'])
        if attachment_path.exists() and attachment_path.is_file():
            attachment_path.unlink()
    except OSError:
        pass


def get_task_attachment(task_id: int, attachment_id: int) -> dict[str, Any] | None:
    with connect() as conn:
        init_db(conn)
        row = conn.execute(
            "SELECT id, entity_type, entity_ref, file_path, mime_type, checksum, created_at FROM attachments WHERE id = ? AND entity_type='task' AND entity_ref = ?",
            (attachment_id, str(task_id)),
        ).fetchone()
    if not row:
        return None
    attachment = dict(row)
    attachment_path = Path(attachment['file_path'])
    attachment['file_name'] = attachment_path.name or attachment['file_path']
    attachment['download_name'] = re.sub(r'-[0-9a-f]{8}(\.[^.]+)$', r'\1', attachment['file_name'])
    return attachment


def get_task(task_id: int) -> dict[str, Any] | None:
    with connect() as conn:
        init_db(conn)
        row = conn.execute(
            '''
            SELECT t.*, p.title AS project_title, c.name AS customer_name,
                   COUNT(DISTINCT tc.id) AS comment_count,
                   COUNT(DISTINCT a.id) AS attachment_count
            FROM tasks t
            JOIN projects p ON p.id = t.project_id
            JOIN customers c ON c.id = p.customer_id
            LEFT JOIN task_comments tc ON tc.task_id = t.id
            LEFT JOIN attachments a ON a.entity_type = 'task' AND a.entity_ref = CAST(t.id AS TEXT)
            WHERE t.id = ?
            GROUP BY t.id, p.title, c.name
            ''',
            (task_id,),
        ).fetchone()
        if not row:
            return None
        task = decorate_task(dict(row))
        task['comments'] = [dict(comment) for comment in conn.execute('SELECT id, comment_type, body, author, created_at FROM task_comments WHERE task_id=? ORDER BY created_at ASC, id ASC', (task_id,)).fetchall()]
        task['attachments'] = [dict(attachment) for attachment in conn.execute("SELECT id, file_path, mime_type, checksum, created_at FROM attachments WHERE entity_type='task' AND entity_ref=? ORDER BY created_at ASC, id ASC", (str(task_id),)).fetchall()]
        for attachment in task['attachments']:
            attachment_path = Path(attachment['file_path'])
            attachment['file_name'] = attachment_path.name or attachment['file_path']
            attachment['download_name'] = re.sub(r'-[0-9a-f]{8}(\.[^.]+)$', r'\1', attachment['file_name'])
        return task
