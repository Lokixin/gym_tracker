from fastapi import APIRouter, Depends

from gym_tracker.adapters.repositories import PostgresSQLRepo
from gym_tracker.entrypoints.dependencies import get_workouts_repo
from gym_tracker.entrypoints.dtos import SearchExerciseResultDTO

search_router = APIRouter(prefix="/search")


@search_router.get("/exercises")
def autocomplete_exercises(
    exercise_name: str, repo: PostgresSQLRepo = Depends(get_workouts_repo)
) -> list[SearchExerciseResultDTO]:
    results = repo.get_exercises_name(exercise_name)
    return [
        SearchExerciseResultDTO(id=result.id, name=result.name) for result in results
    ]
