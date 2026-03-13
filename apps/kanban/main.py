from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .services import (
    BOARD_NAME,
    COLUMNS,
    PRIORITY_OPTIONS,
    archive_task,
    build_filters,
    column_counts,
    create_customer_and_project,
    create_task,
    get_task,
    list_board_tasks,
    list_filter_options,
    list_projects,
    move_task,
    search_customers,
    search_projects,
    update_task,
)

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title='openclaw-workos kanban', version='0.5.0')
app.mount('/static', StaticFiles(directory=str(BASE_DIR / 'static')), name='static')
templates = Jinja2Templates(directory=str(BASE_DIR / 'templates'))


def board_context(request: Request, filters: dict[str, str] | None = None):
    active_filters = build_filters(**(filters or {}))
    grouped = list_board_tasks(filters=active_filters)
    filter_options = list_filter_options()
    return {
        'request': request,
        'board_name': BOARD_NAME,
        'columns': COLUMNS,
        'grouped': grouped,
        'counts': column_counts(grouped),
        'projects': list_projects(),
        'filters': active_filters,
        'assignee_options': filter_options['assignees'],
        'customer_options': filter_options['customers'],
    }


def render_board_response(request: Request, filters: dict[str, str] | None = None):
    template = 'partials/board_shell.html' if request.headers.get('HX-Request') == 'true' else 'board.html'
    return templates.TemplateResponse(request, template, board_context(request, filters))


def task_detail_context(request: Request, task_id: int):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail='task not found')
    return {
        'request': request,
        'task': task,
        'columns': COLUMNS,
        'projects': list_projects(),
        'priority_options': PRIORITY_OPTIONS,
    }


@app.get('/', response_class=HTMLResponse)
def root() -> RedirectResponse:
    return RedirectResponse(url='/board', status_code=302)


@app.get('/board', response_class=HTMLResponse)
def board(request: Request, project_id: str = '', assignee: str = '', customer_name: str = '', q: str = ''):
    return render_board_response(request, build_filters(project_id, assignee, customer_name, q))


@app.get('/board/projects/search', response_class=HTMLResponse)
def board_projects_search(request: Request, q: str = Query('')):
    return templates.TemplateResponse(
        request,
        'partials/project_picker_results.html',
        {'request': request, 'projects': search_projects(q), 'query': (q or '').strip()},
    )


@app.get('/board/customers/search', response_class=HTMLResponse)
def board_customers_search(request: Request, q: str = Query('')):
    return templates.TemplateResponse(
        request,
        'partials/customer_picker_results.html',
        {'request': request, 'customers': search_customers(q), 'query': (q or '').strip()},
    )


@app.get('/board/project-create', response_class=HTMLResponse)
def board_project_create_modal(request: Request, origin: str = Query('quick-add'), target: str = Query('project_id')):
    return templates.TemplateResponse(
        request,
        'partials/project_create_modal.html',
        {'request': request, 'origin': origin, 'target': target, 'customers': search_customers('')},
    )


@app.post('/board/project-create', response_class=HTMLResponse)
def board_project_create_submit(
    request: Request,
    customer_name: str = Form(...),
    project_title: str = Form(...),
    origin: str = Form('quick-add'),
    target: str = Form('project_id'),
):
    try:
        project = create_customer_and_project(customer_name=customer_name, project_title=project_title, owner='kanban')
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return templates.TemplateResponse(
        request,
        'partials/project_picker_selected.html',
        {'request': request, 'project': project, 'origin': origin, 'target': target},
    )


@app.post('/board/tasks', response_class=HTMLResponse)
def board_task_create(
    request: Request,
    title: str = Form(...),
    project_id: str = Form(''),
    description: str = Form(''),
    column_key: str = Form('backlog'),
):
    if not title.strip():
        raise HTTPException(status_code=400, detail='title is required')
    try:
        create_task(title=title, project_id=project_id.strip(), column_key=column_key, description=description)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return render_board_response(request)


@app.post('/board/tasks/{task_id}/move', response_class=HTMLResponse)
def board_task_move(request: Request, task_id: int, column_key: str = Form(...)):
    try:
        move_task(task_id, column_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return render_board_response(request)


@app.post('/board/tasks/{task_id}/archive', response_class=HTMLResponse)
def board_task_archive(request: Request, task_id: int):
    try:
        archive_task(task_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return render_board_response(request)


@app.post('/board/tasks/{task_id}/update', response_class=HTMLResponse)
def board_task_update(
    request: Request,
    task_id: int,
    title: str = Form(...),
    description: str = Form(''),
    project_id: str = Form(''),
    priority: str = Form(''),
    assignee: str = Form(''),
    due_at: str = Form(''),
):
    if not title.strip():
        raise HTTPException(status_code=400, detail='title is required')
    try:
        update_task(
            task_id,
            title=title,
            description=description,
            project_id=project_id.strip(),
            priority=priority,
            assignee=assignee,
            due_at=due_at,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return templates.TemplateResponse(request, 'partials/task_detail.html', task_detail_context(request, task_id))


@app.get('/tasks/{task_id}', response_class=HTMLResponse)
def task_detail(request: Request, task_id: int):
    return templates.TemplateResponse(request, 'partials/task_detail.html', task_detail_context(request, task_id))
