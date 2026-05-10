from gym_tracker.adapters.mappers import map_workout_for_to_dto, workout_from_db_to_dto
from gym_tracker.adapters.repositories import ExerciseRow, WorkoutInfoRow


def test_map_workout_form_to_dto_groups_sets_by_series() -> None:
    result = map_workout_for_to_dto(
        {
            "1.weights.0": "80.5",
            "1.reps.0": "10",
            "1.to_failure.0": "on",
            "1.weights.1": "70",
            "1.reps.1": "8",
        }
    )

    assert result == {
        "1": [
            {"weight": 80.5, "repetitions": 10, "to_failure": True},
            {"weight": 70.0, "repetitions": 8, "to_failure": False},
        ]
    }


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
