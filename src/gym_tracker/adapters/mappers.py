import datetime
from typing import Any

from psycopg.rows import Row

from gym_tracker.domain.model import Workout, Exercise, ExerciseMetadata, ExerciseSet


def pgsql_to_workout_object_mapper(
    psql_workout: list[Row], date: datetime.date, duration: int
) -> Workout:
    exercises_by_name: dict[str, Exercise] = {}
    for _row in psql_workout:
        exercise_metadata = ExerciseMetadata(
            name=_row[3], primary_muscle_group=_row[4], secondary_muscle_groups=_row[-1]
        )
        exercise_set = ExerciseSet(
            weight=_row[0], repetitions=_row[1], to_failure=_row[2]
        )
        if exercise_metadata.name not in exercises_by_name:
            full_exercise = Exercise(
                exercise_metadata=exercise_metadata, exercise_sets=[exercise_set]
            )
            exercises_by_name[exercise_metadata.name] = full_exercise
        else:
            exercises_by_name[exercise_metadata.name].add_exercise_set(exercise_set)
    return Workout(
        exercises=list(exercises_by_name.values()), date=str(date), duration=duration
    )
