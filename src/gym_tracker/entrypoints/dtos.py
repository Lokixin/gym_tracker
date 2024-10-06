from pydantic import BaseModel

from gym_tracker.domain.model import MuscleGroup


class ExerciseSetDTO(BaseModel):
    weight: float
    repetitions: int
    to_failure: bool | None = False


class ExerciseMetadataDTO(BaseModel):
    name: str
    primary_muscle_group: MuscleGroup
    secondary_muscle_groups: list[MuscleGroup]


class ExerciseDTO(BaseModel):
    exercise_metadata: ExerciseMetadataDTO
    exercise_sets: list[ExerciseSetDTO]


class WorkoutDTO(BaseModel):
    date: str
    duration: int
    exercises: list[ExerciseDTO]
