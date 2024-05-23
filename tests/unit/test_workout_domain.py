from gym_tracker.domain.model import (
    ExerciseMetadata,
    MuscleGroup,
    ExerciseSet,
    Exercise,
    Workout,
)


def test_add_set_to_exercise() -> None:
    exercise_metadata = ExerciseMetadata(
        name="Press de banca",
        primary_muscle_group=MuscleGroup.PECK,
        secondary_muscle_groups=[MuscleGroup.SHOULDERS, MuscleGroup.TRICEPS],
    )
    exercise_set = ExerciseSet(
        weight=80,
        repetitions=10,
        to_failure=True,
    )
    exercise = Exercise(exercise_metadata=exercise_metadata, exercise_sets=[])

    exercise.add_exercise_set(exercise_set)

    expected_exercise_sets = [exercise_set]
    assert exercise.exercise_sets == expected_exercise_sets


def test_add_exercise_to_workout() -> None:
    exercise_metadata = ExerciseMetadata(
        name="Press de banca",
        primary_muscle_group=MuscleGroup.PECK,
        secondary_muscle_groups=[MuscleGroup.SHOULDERS, MuscleGroup.TRICEPS],
    )
    exercise_set = ExerciseSet(
        weight=80,
        repetitions=10,
        to_failure=True,
    )
    exercise = Exercise(
        exercise_metadata=exercise_metadata, exercise_sets=[exercise_set]
    )
    workout = Workout(exercises=[])

    workout.add_exercise(exercise)

    expected_exercises = [exercise]
    assert workout.exercises == expected_exercises


def test_workout_sets_given_date() -> None:
    date = "2024-05-23T21:24:11.765570+02:00"
    workout = Workout(exercises=[], date=date)

    assert workout.date == date


def test_workout_sets_date_automatically(mock_pendulum_now) -> None:
    workout = Workout(exercises=[], date=None)

    assert workout.date == mock_pendulum_now.to_rfc3339_string()
