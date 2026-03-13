from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .services import (
    BOARD_NAME,
    COLUMNS,
    archive_task,
    column_counts,
    create_task,
    get_task,
    list_board_tasks,
    list_projects,
    move_task,
)

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title='openclaw-workos kanban', version='0.2.0')
app.mount('/static', StaticFiles(directory=str(BASE_DIR / 'static')), name='static')
templates = Jinja2Templates(directory=str(BASE_DIR / 'templates'))


def board_context(request: Request):
    grouped = list_board_tasks()
    return {
        'request': request,
        'board_name': BOARD_NAME,
        'columns': COLUMNS,
        'grouped': grouped,
        'counts': column_counts(grouped),
        'projects': list_projects(),
    }


@app.get('/', response_class=HTMLResponse)
def root() -> RedirectResponse:
    return RedirectResponse(url='/board', status_code=302)


@app.get('/board', response_class=HTMLResponse)
def board(request: Request):
    return templates.TemplateResponse(request, 'board.html', board_context(request))


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
    if request.headers.get('HX-Request') == 'true':
        return templates.TemplateResponse(request, 'partials/board_columns.html', board_context(request))
    return RedirectResponse(url='/board', status_code=303)


@app.post('/board/tasks/{task_id}/move', response_class=HTMLResponse)
def board_task_move(request: Request, task_id: int, column_key: str = Form(...)):
    try:
        move_task(task_id, column_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if request.headers.get('HX-Request') == 'true':
        return templates.TemplateResponse(request, 'partials/board_columns.html', board_context(request))
    return RedirectResponse(url='/board', status_code=303)


@app.post('/board/tasks/{task_id}/archive', response_class=HTMLResponse)
def board_task_archive(request: Request, task_id: int):
    try:
        archive_task(task_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if request.headers.get('HX-Request') == 'true':
        return templates.TemplateResponse(request, 'partials/board_columns.html', board_context(request))
    return RedirectResponse(url='/board', status_code=303)


@app.get('/tasks/{task_id}', response_class=HTMLResponse)
def task_detail(request: Request, task_id: int):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail='task not found')
    return templates.TemplateResponse(request, 'partials/task_detail.html', {'request': request, 'task': task, 'columns': COLUMNS})
