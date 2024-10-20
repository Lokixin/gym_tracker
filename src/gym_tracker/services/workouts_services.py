from fastapi import Depends, HTTPException
from starlette import status
from starlette.responses import JSONResponse

from gym_tracker.adapters.mappers import workout_from_db_to_dto
from gym_tracker.adapters.repositories import PostgresSQLRepo
from gym_tracker.domain.model import Workout
from gym_tracker.entrypoints.dependencies import get_workouts_repo
from gym_tracker.entrypoints.dtos import (
    WorkoutDTO,
    CreateWorkoutBody,
    ExerciseSetDTO,
    ExerciseDTO,
)


def get_workout_by_date_service(
    date: str, workouts_repo: PostgresSQLRepo = Depends(get_workouts_repo)
) -> WorkoutDTO:
    if workout := workouts_repo.get_workout_by_date(date):
        return workout_from_db_to_dto(exercises=workout[0], workout_metadata=workout[1])
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"message": f"Workout Not Found for date {date}"},
    )


def get_workout_by_id_service(
    workout_id: int, workouts_repo: PostgresSQLRepo = Depends(get_workouts_repo)
) -> WorkoutDTO:
    if workout := workouts_repo.get_workout_by_id(workout_id):
        return workout_from_db_to_dto(exercises=workout[0], workout_metadata=workout[1])
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"message": f"Workout Not Found for id {workout_id}"},
    )


def create_new_workout_service(
    workout_body: CreateWorkoutBody,
    workouts_repo: PostgresSQLRepo = Depends(get_workouts_repo),
) -> JSONResponse:
    new_workout = Workout(
        duration=workout_body.duration, date=workout_body.date, exercises=[]
    )
    workout_id = workouts_repo.add_workout(new_workout)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"id": workout_id})


def add_exercise_to_workout_service(
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


def add_set_to_exercise_service(
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
