from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from gym_tracker.adapters.repositories import PostgresSQLRepo
from gym_tracker.entrypoints.dependencies import get_workouts_repo


client_router = APIRouter(prefix="/app")
templates = Jinja2Templates(directory="templates")


@client_router.get("/workouts/list")
def get_workouts_by_date_view(
    request: Request, repo: PostgresSQLRepo = Depends(get_workouts_repo)
) -> HTMLResponse:
    workouts = repo.get_existing_workouts_dates()
    return templates.TemplateResponse(
        request=request,
        name="read_workouts.html",
        context={"workouts": workouts},
    )


@client_router.get("/workouts/add")
def add_new_workout_view(
    request: Request,
) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="add_workouts.html")
