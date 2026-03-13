import io
import os
import sqlite3
import sys
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
TMPDIR = Path(tempfile.mkdtemp(prefix='kanban-regression-'))
os.environ['OPENCLAW_WORKSPACE'] = str(TMPDIR / 'ws')
os.environ['WORKCTL_DB_PATH'] = str(TMPDIR / 'workos.db')
os.environ['WORKCTL_PROJECTS_ROOT'] = str(TMPDIR / 'ws' / 'work' / 'projects')
os.environ['WORKCTL_CUSTOMERS_ROOT'] = str(TMPDIR / 'ws' / 'work' / 'customers')
(TMPDIR / 'ws').mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(os.environ['WORKCTL_DB_PATH'])
conn.executescript((ROOT / 'schema' / 'workos.sql').read_text())
conn.executescript((ROOT / 'examples' / 'demo-seed.sql').read_text())
conn.execute("INSERT INTO tasks(project_id, title, status, board, column_key, wip_order, sort_order) VALUES ('PR0002', 'Regression target', 'todo', 'main', 'backlog', 10, 10)")
conn.commit()
conn.close()

from apps.kanban.main import app  # noqa: E402
from apps.kanban.services import get_task  # noqa: E402

client = TestClient(app)

assert client.get('/board').status_code == 200
assert client.get('/tasks/1').status_code == 200
assert client.get('/board', params={'project_id': 'PR0002'}).status_code == 200
assert client.get('/board/projects/search', params={'q': 'PR0002'}).status_code == 200
assert client.get('/board/customers/search', params={'q': 'Northwind'}).status_code == 200
assert client.get('/board/project-create', params={'origin': 'quick-add', 'target': 'project_id'}).status_code == 200
assert client.post('/board/project-create', data={'customer_name': 'Regression Customer', 'project_title': 'Regression Project', 'origin': 'quick-add', 'target': 'project_id'}).status_code == 200

assert client.post('/board/tasks/1/comments', data={'body': 'hello', 'author': 'me'}).status_code == 200
bad_comment = client.post('/board/tasks/1/comments', data={'body': '', 'author': 'me'})
assert bad_comment.status_code == 400
assert 'comment body is required' in bad_comment.text

bad_upload = client.post('/board/tasks/1/attachments', data={})
assert bad_upload.status_code == 400
assert 'Please choose a file to upload.' in bad_upload.text

good_upload = client.post('/board/tasks/1/attachments', files={'upload_file': ('x.txt', io.BytesIO(b'hi'), 'text/plain')})
assert good_upload.status_code == 200
assert '📄' in good_upload.text

attachment = get_task(1)['attachments'][0]
assert client.get(f"/board/tasks/1/attachments/{attachment['id']}/download").status_code == 200
assert client.post(f"/board/tasks/1/attachments/{attachment['id']}/remove").status_code == 200
assert client.post('/board/tasks/1/move', data={'column_key': 'doing'}).status_code == 200
assert client.post('/board/tasks/1/update', data={'title': 'Updated target', 'description': 'desc', 'project_id': 'PR0002', 'priority': 'high', 'assignee': 'claw', 'due_at': '2026-03-20'}).status_code == 200
assert client.post('/board/tasks/1/archive').status_code == 200

print('Kanban regression test passed')
