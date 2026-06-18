import logging

from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from gym_tracker.adapters.repositories import PostgresSQLRepo
from gym_tracker.entrypoints.auth import (
    User,
    get_current_user_by_cookie,
)
from gym_tracker.entrypoints.dependencies import get_workouts_repo


client_router = APIRouter(prefix="/app")
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)


@client_router.get("/workouts/list")
def get_workouts_by_date_view(
    request: Request,
    repo: PostgresSQLRepo = Depends(get_workouts_repo),
    current_user: User = Depends(get_current_user_by_cookie),
) -> HTMLResponse:
    logger.warning("Request headers: %s", request.headers)
    workouts = repo.get_existing_workouts_dates(current_user.id)
    return templates.TemplateResponse(
        request=request,
        name="read_workouts.html",
        context={"workouts": workouts},
    )


@client_router.get("/workouts/add")
def add_new_workout_view(
    request: Request, current_user: User = Depends(get_current_user_by_cookie)
) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="add_workouts.html")
