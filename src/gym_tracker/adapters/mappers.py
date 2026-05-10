import datetime
from typing import Any

from gym_tracker.adapters.repositories import ExerciseRow, WorkoutInfoRow
from gym_tracker.domain.model import Workout, ExerciseMetadata, ExerciseSet
from gym_tracker.entrypoints.dtos import (
    WorkoutDTO,
    CreateWorkoutFromClient,
    ExerciseDTO,
    ExerciseMetadataDTO,
    ExerciseSetDTO,
)


def pgsql_to_workout_object_mapper(
    psql_workout: list[Any], date: datetime.date, duration: int
) -> Workout:
    current_workout = Workout(exercises=[], date=str(date), duration=duration)
    for _row in psql_workout:
        exercise_metadata = ExerciseMetadata(
            name=_row[3], primary_muscle_group=_row[4], secondary_muscle_groups=_row[-1]
        )
        exercise_set = ExerciseSet(
            weight=_row[0], repetitions=_row[1], to_failure=_row[2]
        )
        current_workout.add_set_to_exercise(
            exercise_metadata=exercise_metadata, exercise_set=exercise_set
        )
    return current_workout


def workout_object_to_dto(workout: Workout) -> WorkoutDTO:
    exercises = []
    for exercise in workout.exercises:
        sets = [
            ExerciseSetDTO(
                weight=_set.weight,
                repetitions=_set.repetitions,
                to_failure=_set.to_failure,
            )
            for _set in exercise.exercise_sets
        ]
        metadata = ExerciseMetadataDTO(
            name=exercise.exercise_metadata.name,
            primary_muscle_group=exercise.exercise_metadata.primary_muscle_group,
            secondary_muscle_groups=[
                str(muscle_group)
                for muscle_group in exercise.exercise_metadata.secondary_muscle_groups
            ],
        )
        _exercise = ExerciseDTO(
            exercise_metadata=metadata,
            exercise_sets=sets,
        )
        exercises.append(_exercise)
    return WorkoutDTO(
        date=workout.simple_date, duration=workout.duration, exercises=exercises
    )


def workout_from_db_to_dto(
    exercises: list[ExerciseRow], workout_metadata: WorkoutInfoRow
) -> WorkoutDTO:
    date, duration = workout_metadata
    current_workout = Workout(exercises=[], date=str(date), duration=duration)
    for exercise in exercises:
        exercise_metadata = ExerciseMetadata(
            name=exercise.name,
            primary_muscle_group=exercise.primary_muscle_group,
            secondary_muscle_groups=exercise.secondary_muscle_groups,
        )
        exercise_set = ExerciseSet(
            weight=exercise.weight,
            repetitions=exercise.reps,
            to_failure=exercise.to_failure,
        )
        current_workout.add_set_to_exercise(
            exercise_metadata=exercise_metadata, exercise_set=exercise_set
        )
    workout_dto = workout_object_to_dto(current_workout)
    return workout_dto


def create_workout_body_to_repo_payload(
    workout_body: CreateWorkoutFromClient,
) -> dict[str, list[dict[str, int | float | bool]]]:
    return {
        str(exercise.metadata_id): [
            {
                "weight": exercise_set.weight,
                "repetitions": exercise_set.repetitions,
                "to_failure": bool(exercise_set.to_failure),
            }
            for exercise_set in exercise.sets
        ]
        for exercise in workout_body.exercises
    }
