from gym_tracker.adapters.mappers import (
    create_workout_body_to_repo_payload,
    workout_from_db_to_dto,
)
from gym_tracker.adapters.repositories import ExerciseRow, WorkoutInfoRow
from gym_tracker.entrypoints.dtos import (
    CreateWorkoutExerciseDTO,
    CreateWorkoutFromClient,
    ExerciseSetDTO,
)
import pytest
from pydantic import ValidationError


def test_create_workout_body_to_repo_payload_groups_sets_by_metadata_id() -> None:
    result = create_workout_body_to_repo_payload(
        CreateWorkoutFromClient(
            date="2024-06-16",
            duration=90,
            exercises=[
                CreateWorkoutExerciseDTO(
                    metadata_id=1,
                    sets=[
                        ExerciseSetDTO(weight=80.5, repetitions=10, to_failure=True),
                        ExerciseSetDTO(weight=70, repetitions=8),
                    ],
                )
            ],
        )
    )

    assert result == {
        "1": [
            {"weight": 80.5, "repetitions": 10, "to_failure": True},
            {"weight": 70.0, "repetitions": 8, "to_failure": False},
        ]
    }


def test_create_workout_body_rejects_missing_set_fields() -> None:
    with pytest.raises(ValidationError):
        CreateWorkoutFromClient.model_validate(
            {
                "date": "2024-06-16",
                "duration": 90,
                "exercises": [{"metadata_id": 1, "sets": [{"weight": 80}]}],
            }
        )


def test_workout_from_db_to_dto_groups_sets_by_exercise() -> None:
    dto = workout_from_db_to_dto(
        exercises=[
            ExerciseRow(80, 10, True, "Bench Press", "Chest", ["Triceps"]),
            ExerciseRow(75, 8, False, "Bench Press", "Chest", ["Triceps"]),
        ],
        workout_metadata=WorkoutInfoRow("2024-06-16", 90),
    )

    assert dto.date == "2024-06-16"
    assert dto.duration == 90
    assert len(dto.exercises) == 1
    assert dto.exercises[0].exercise_metadata.name == "Bench Press"
    assert len(dto.exercises[0].exercise_sets) == 2
