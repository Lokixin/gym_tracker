import datetime

from psycopg.rows import Row

from gym_tracker.adapters.repositories import ExerciseRow, WorkoutInfoRow
from gym_tracker.domain.model import Workout, ExerciseMetadata, ExerciseSet
from gym_tracker.entrypoints.dtos import (
    WorkoutDTO,
    ExerciseDTO,
    ExerciseSetDTO,
    ExerciseMetadataDTO,
)


def pgsql_to_workout_object_mapper(
    psql_workout: list[Row], date: datetime.date, duration: int
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
            secondary_muscle_groups=exercise.exercise_metadata.secondary_muscle_groups,
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


def map_workout_for_to_dto(workout_entries: dict[str, int | float]) -> dict:
    output = {}
    for key, value in workout_entries.items():
        exercise_name, attr, series = key.split(".")
        if attr == "reps":
            value = int(value)
        if exercise_name not in output:
            output[exercise_name] = [{attr: value}]
        else:
            if attr not in output[exercise_name][len(output[exercise_name]) - 1]:
                output[exercise_name][len(output[exercise_name]) - 1][attr] = value
            else:
                output[exercise_name].append({attr: value})
    return output
