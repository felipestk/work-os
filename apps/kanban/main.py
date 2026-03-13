from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .services import BOARD_NAME, COLUMNS, column_counts, create_task, get_task, list_board_tasks, list_projects

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title='openclaw-workos kanban', version='0.1.0')
app.mount('/static', StaticFiles(directory=str(BASE_DIR / 'static')), name='static')
templates = Jinja2Templates(directory=str(BASE_DIR / 'templates'))


@app.get('/', response_class=HTMLResponse)
def root() -> RedirectResponse:
    return RedirectResponse(url='/board', status_code=302)


@app.get('/board', response_class=HTMLResponse)
def board(request: Request):
    grouped = list_board_tasks()
    return templates.TemplateResponse(
        request,
        'board.html',
        {
            'request': request,
            'board_name': BOARD_NAME,
            'columns': COLUMNS,
            'grouped': grouped,
            'counts': column_counts(grouped),
            'projects': list_projects(),
        },
    )


@app.post('/board/tasks', response_class=HTMLResponse)
def board_task_create(
    request: Request,
    title: str = Form(...),
    project_id: str = Form(...),
    column_key: str = Form('backlog'),
    description: str = Form(''),
):
    if not title.strip():
        raise HTTPException(status_code=400, detail='title is required')
    try:
        create_task(title=title, project_id=project_id.strip(), column_key=column_key, description=description)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    grouped = list_board_tasks()
    context = {
        'request': request,
        'columns': COLUMNS,
        'grouped': grouped,
        'counts': column_counts(grouped),
        'projects': list_projects(),
    }
    if request.headers.get('HX-Request') == 'true':
        return templates.TemplateResponse(request, 'partials/board_columns.html', context)
    return RedirectResponse(url='/board', status_code=303)


@app.get('/tasks/{task_id}', response_class=HTMLResponse)
def task_detail(request: Request, task_id: int):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail='task not found')
    return templates.TemplateResponse(request, 'partials/task_detail.html', {'request': request, 'task': task})
