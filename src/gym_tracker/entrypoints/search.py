from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from gym_tracker.adapters.repositories import PostgresSQLRepo
from gym_tracker.entrypoints.dependencies import get_workouts_repo

search_router = APIRouter(prefix="/search")


@search_router.get("/exercises")
def autocomplete_exercises(
    exercise_name: str, repo: PostgresSQLRepo = Depends(get_workouts_repo)
) -> JSONResponse:
    results = repo.get_exercises_name(exercise_name)
    results = sorted(results, key=lambda x: len(x))
    return JSONResponse(content=results)
