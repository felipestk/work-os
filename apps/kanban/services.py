from __future__ import annotations

from collections import OrderedDict
from datetime import datetime, timezone
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
COLUMN_TO_STATUS = {
    'backlog': 'todo',
    'todo': 'todo',
    'doing': 'in_progress',
    'review': 'blocked',
    'done': 'done',
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def normalize_board(board: str | None) -> str:
    return (board or '').strip() or BOARD_NAME


def normalize_column(column_key: str | None) -> str:
    value = (column_key or '').strip() or 'backlog'
    return value if value in COLUMNS else 'backlog'


def project_exists(project_id: str) -> bool:
    with connect() as conn:
        init_db(conn)
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


def list_board_tasks(board: str = BOARD_NAME) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {key: [] for key in COLUMNS}
    with connect() as conn:
        init_db(conn)
        rows = conn.execute(
            '''
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
            WHERE t.status != 'archived'
              AND COALESCE(NULLIF(t.board, ''), 'main') = ?
            GROUP BY
              t.id, t.project_id, t.title, t.description, t.status, t.priority, t.assignee, t.due_at,
              t.board, t.column_key, t.wip_order, t.sort_order, p.title, c.name
            ORDER BY column_key, display_order, t.id
            ''',
            (normalize_board(board),),
        ).fetchall()
    for row in rows:
        item = dict(row)
        item['column_key'] = normalize_column(item['column_key'])
        item['description_preview'] = summarize(item.get('description'))
        grouped[item['column_key']].append(item)
    return grouped


def summarize(text: str | None, limit: int = 140) -> str:
    if not text:
        return ''
    compact = ' '.join(text.split())
    return compact if len(compact) <= limit else compact[: limit - 1].rstrip() + '…'


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
        if not project_exists(project_id):
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


def get_task(task_id: int) -> dict[str, Any] | None:
    with connect() as conn:
        init_db(conn)
        row = conn.execute(
            '''
            SELECT
              t.*,
              p.title AS project_title,
              c.name AS customer_name
            FROM tasks t
            JOIN projects p ON p.id = t.project_id
            JOIN customers c ON c.id = p.customer_id
            WHERE t.id = ?
            ''',
            (task_id,),
        ).fetchone()
        if not row:
            return None
        task = dict(row)
        task['board'] = normalize_board(task.get('board'))
        task['column_key'] = normalize_column(task.get('column_key'))
        task['comments'] = [
            dict(comment)
            for comment in conn.execute(
                'SELECT id, comment_type, body, author, created_at FROM task_comments WHERE task_id=? ORDER BY created_at ASC, id ASC',
                (task_id,),
            ).fetchall()
        ]
        task['attachments'] = [
            dict(attachment)
            for attachment in conn.execute(
                "SELECT id, file_path, mime_type, checksum, created_at FROM attachments WHERE entity_type='task' AND entity_ref=? ORDER BY created_at ASC, id ASC",
                (str(task_id),),
            ).fetchall()
        ]
        return task
