from fastapi import HTTPException
from starlette import status

from gym_tracker.adapters.mappers import (
    workout_from_db_to_dto,
    create_workout_body_to_repo_payload,
)
from gym_tracker.adapters.repositories import PostgresSQLRepo
from gym_tracker.entrypoints.dtos import (
    CreateWorkoutFromClient,
    WorkoutDTO,
)


def get_workout_by_date_service(
    date: str, workouts_repo: PostgresSQLRepo
) -> WorkoutDTO:
    if workout := workouts_repo.get_workout_by_date(date):
        return workout_from_db_to_dto(exercises=workout[0], workout_metadata=workout[1])
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"message": f"Workout Not Found for date {date}"},
    )


def get_workout_by_id_service(
    workout_id: int, workouts_repo: PostgresSQLRepo
) -> WorkoutDTO:
    if workout := workouts_repo.get_workout_by_id(workout_id):
        return workout_from_db_to_dto(exercises=workout[0], workout_metadata=workout[1])
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"message": f"Workout Not Found for id {workout_id}"},
    )


def create_new_workout_service(
    workout_body: CreateWorkoutFromClient,
    workouts_repo: PostgresSQLRepo,
) -> int:
    exercises = create_workout_body_to_repo_payload(workout_body)
    return workouts_repo.add_workout(
        exercises,
        workout_date=workout_body.date,
        workout_duration=workout_body.duration,
    )
