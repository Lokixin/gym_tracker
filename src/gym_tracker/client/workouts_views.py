from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from gym_tracker.adapters.repositories import PostgresSQLRepo
from gym_tracker.entrypoints.dependencies import get_workouts_repo

client_router = APIRouter(prefix="/client")
templates = Jinja2Templates(directory="templates")


@client_router.get("/workouts")
def home(
    request: Request, repo: PostgresSQLRepo = Depends(get_workouts_repo)
) -> HTMLResponse:
    workouts_dates = repo.get_existing_workouts_dates()
    return templates.TemplateResponse(
        request=request,
        name="read_workouts.html",
        context={"workouts_dates": workouts_dates},
    )


@client_router.get("/new_workout")
def add_new_workout(
    request: Request,
) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="add_workouts.html")
