
from fastapi import Depends, Query
from fastapi.routing import APIRouter
from starlette.responses import JSONResponse

from gym_tracker.adapters.repositories import PostgresSQLRepo
from gym_tracker.entrypoints.dependencies import get_workouts_repo
from gym_tracker.entrypoints.dtos import (
    WorkoutDTO,
    ExerciseDTO,
    ExerciseSetDTO,
    CreateWorkoutFromClient,
)
from gym_tracker.services.workouts_services import (
    get_workout_by_date_service,
    get_workout_by_id_service,
    create_new_workout_service,
    add_set_to_exercise_service,
    add_exercise_to_workout_service,
)

workouts_router = APIRouter(
    prefix="/workouts",
    tags=["workouts"],
)
date_query_parameter = Query(description="date of the workout", example="2024-10-07")


@workouts_router.get("/by_date/{date}", response_model=WorkoutDTO)
def get_workout_by_date(
    date: str, workouts_repo: PostgresSQLRepo = Depends(get_workouts_repo)
) -> WorkoutDTO:
    return get_workout_by_date_service(
        date=date,
        workouts_repo=workouts_repo,
    )


@workouts_router.get("/by_id/{workout_id}", response_model=WorkoutDTO)
def get_workout_by_id(
    workout_id: int, workouts_repo: PostgresSQLRepo = Depends(get_workouts_repo)
) -> WorkoutDTO:
    return get_workout_by_id_service(workout_id=workout_id, workouts_repo=workouts_repo)


@workouts_router.post("/by_date")
def create_new_workout(
    workout_body: CreateWorkoutFromClient,
    workouts_repo: PostgresSQLRepo = Depends(get_workouts_repo),
) -> JSONResponse:
    return create_new_workout_service(
        workout_body=workout_body, workouts_repo=workouts_repo
    )


@workouts_router.patch("/{workout_id}/add_exercise")
def add_exercise_to_workout(
    workout_id: int,
    exercise: ExerciseDTO,
    workouts_repo: PostgresSQLRepo = Depends(get_workouts_repo),
) -> JSONResponse:
    return add_exercise_to_workout_service(
        workout_id=workout_id, exercise=exercise, workouts_repo=workouts_repo
    )


@workouts_router.patch("/{exercise_id}/add_set")
def add_set_to_exercise(
    exercise_id: int,
    exercise_sets: list[ExerciseSetDTO],
    workouts_repo: PostgresSQLRepo = Depends(get_workouts_repo),
) -> JSONResponse:
    return add_set_to_exercise_service(
        exercise_id=exercise_id,
        exercise_sets=exercise_sets,
        workouts_repo=workouts_repo,
    )
