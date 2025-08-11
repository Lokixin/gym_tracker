from typing import Annotated

from pydantic import BaseModel, Field

from gym_tracker.domain.model import MuscleGroup


class ExerciseSetDTO(BaseModel):
    weight: Annotated[float, Field(..., examples=[100])]
    repetitions: Annotated[int, Field(..., examples=[10])]
    to_failure: Annotated[bool, Field(..., examples=[False])] | None = False


class ExerciseMetadataDTO(BaseModel):
    name: Annotated[str, Field(..., examples=["bench press"])]
    primary_muscle_group: MuscleGroup
    secondary_muscle_groups: Annotated[
        list[MuscleGroup], Field(..., examples=[["back", "biceps"]])
    ]


class ExerciseDTO(BaseModel):
    exercise_metadata: Annotated[
        ExerciseMetadataDTO,
        Field(
            ...,
            examples=[
                {
                    "name": "bench press",
                    "primary_muscle_group": "peck",
                    "secondary_muscle_groups": ["shoulders", "triceps"],
                }
            ],
        ),
    ]
    exercise_sets: list[ExerciseSetDTO]


class WorkoutDTO(BaseModel):
    date: Annotated[str, Field(..., examples=["2024-06-16"])]
    duration: Annotated[int, Field(..., examples=[120])]
    exercises: list[ExerciseDTO]


class CreateWorkoutBody(BaseModel):
    date: Annotated[str, Field(..., examples=["2024-06-16"])] | None = None
    duration: Annotated[int, Field(..., examples=[90])] | None = 0


class CreateWorkoutFromClient(BaseModel):
    workout_entries: dict[str, float | int]
