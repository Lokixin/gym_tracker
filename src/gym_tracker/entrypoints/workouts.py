from fastapi import Depends, HTTPException, Query, status
from fastapi.routing import APIRouter
from starlette.responses import JSONResponse

from gym_tracker.adapters.mappers import workout_object_to_dto
from gym_tracker.adapters.repositories import PostgresSQLRepo
from gym_tracker.domain.model import Workout
from gym_tracker.entrypoints.dependencies import get_workouts_repo
from gym_tracker.entrypoints.dtos import (
    WorkoutDTO,
    CreateWorkoutBody,
    ExerciseDTO,
    ExerciseSetDTO,
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
    workout = workouts_repo.get_workout_by_date(date)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"Workout Not Found for date {date}"},
        )
    return workout_object_to_dto(workout)


@workouts_router.get("/by_id/{workout_id}", response_model=WorkoutDTO)
def get_workout_by_id(
    workout_id: int, workouts_repo: PostgresSQLRepo = Depends(get_workouts_repo)
) -> WorkoutDTO:
    workout = workouts_repo.get_workout_by_id(workout_id)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"Workout Not Found for id {workout_id}"},
        )
    return workout_object_to_dto(workout)


@workouts_router.post("/by_date")
def create_new_workout(
    workout_body: CreateWorkoutBody,
    workouts_repo: PostgresSQLRepo = Depends(get_workouts_repo),
) -> JSONResponse:
    new_workout = Workout(
        duration=workout_body.duration, date=workout_body.date, exercises=[]
    )
    workout_id = workouts_repo.add_workout(new_workout)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"id": workout_id})


@workouts_router.patch("/{workout_id}/add_exercise")
def add_exercise_to_workout(
    workout_id: int,
    exercise: ExerciseDTO,
    workouts_repo: PostgresSQLRepo = Depends(get_workouts_repo),
) -> JSONResponse:
    if not exercise.exercise_sets:
        exercise_id = workouts_repo.add_exercise_to_workout(exercise, workout_id)
    else:
        exercise_id = workouts_repo.add_exercise_with_sets_to_workout(
            exercise, workout_id
        )
    return JSONResponse(status_code=status.HTTP_200_OK, content={"id": exercise_id})


@workouts_router.patch("/{exercise_id}/add_set")
def add_set_to_exercise(
    exercise_id: int,
    exercise_sets: list[ExerciseSetDTO],
    workouts_repo: PostgresSQLRepo = Depends(get_workouts_repo),
) -> JSONResponse:
    workouts_repo.add_sets_to_exercise(
        exercise_sets=exercise_sets, exercise_id=exercise_id
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"{len(exercise_sets)} sets added to exercise {exercise_id}"
        },
    )
