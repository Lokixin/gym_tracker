from fastapi import Depends, HTTPException, Query
from fastapi.routing import APIRouter
from starlette import status
from starlette.responses import JSONResponse

from gym_tracker.adapters.repositories import PostgresSQLRepo, RepositoryError
from gym_tracker.entrypoints.dependencies import get_workouts_repo
from gym_tracker.entrypoints.dtos import (
    WorkoutDTO,
    CreateWorkoutFromClient,
)
from gym_tracker.services.workouts_services import (
    get_workout_by_id_service,
    create_new_workout_service,
    WorkoutNotFoundError,
)

workouts_router = APIRouter(
    prefix="/workouts",
    tags=["workouts"],
)
date_query_parameter = Query(description="date of the workout", example="2024-10-07")


@workouts_router.get("/{workout_id}", response_model=WorkoutDTO)
def get_workout_by_id(
    workout_id: int, workouts_repo: PostgresSQLRepo = Depends(get_workouts_repo)
) -> WorkoutDTO:
    try:
        return get_workout_by_id_service(
            workout_id=workout_id, workouts_repo=workouts_repo
        )
    except WorkoutNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"Workout Not Found for {exc.lookup}"},
        ) from exc


@workouts_router.post("")
def create_new_workout(
    workout_body: CreateWorkoutFromClient,
    workouts_repo: PostgresSQLRepo = Depends(get_workouts_repo),
) -> JSONResponse:
    try:
        workout_id = create_new_workout_service(
            workout_body=workout_body, workouts_repo=workouts_repo
        )
    except RepositoryError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Unable to create workout"},
        ) from exc
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"id": workout_id})
