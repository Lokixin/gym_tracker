import datetime

from psycopg.rows import Row

from gym_tracker.domain.model import Workout, ExerciseMetadata, ExerciseSet


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
