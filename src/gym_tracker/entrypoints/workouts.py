from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter

from gym_tracker.adapters.mappers import workout_object_to_dto
from gym_tracker.adapters.repositories import PostgresSQLRepo
from gym_tracker.entrypoints.dependencies import get_workouts_repo
from gym_tracker.entrypoints.dtos import WorkoutDTO

workouts_router = APIRouter(
    prefix="/workouts",
    tags=["workouts"],
)


@workouts_router.get("/by_date/{date}")
def get_workout_by_date(
    date: str, workouts_repo: PostgresSQLRepo = Depends(get_workouts_repo)
) -> WorkoutDTO:
    workout = workouts_repo.get_workout_by_date(date)
    if not workout:
        raise HTTPException(
            status_code=404, detail={"message": f"Workout Not Found for date {date}"}
        )
    return workout_object_to_dto(workout)
