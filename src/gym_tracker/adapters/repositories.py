import logging
from collections import namedtuple

import psycopg
from psycopg import Connection

from gym_tracker.adapters.workouts_queries import (
    select_metadata_by_name,
    insert_exercise_metadata,
    insert_workout,
    insert_exercise_to_workout,
    insert_sets_to_exercise,
    select_workout_by_date,
    select_workout_date_and_duration,
    select_workout_by_id,
    select_date_and_duration_by_id,
)
from gym_tracker.domain.model import (
    ExerciseMetadata,
    Workout,
    Exercise,
    ExerciseSet,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ExerciseRow = namedtuple(
    "ExerciseRow",
    "weight, reps, to_failure, name, primary_muscle_group, secondary_muscle_groups",
)
WorkoutInfoRow = namedtuple("WorkoutInfoRow", "date, duration")


class PostgresSQLRepo:
    def __init__(self, connection: Connection) -> None:
        self.conn = connection

    def get_exercise_metadata_by_name(self, name: str) -> ExerciseMetadata:
        with self.conn.cursor() as cursor:
            cursor.execute(select_metadata_by_name, (name,))
            metadata_tuple = cursor.fetchone()
            exercise_metadata = ExerciseMetadata(
                name=metadata_tuple[0],
                primary_muscle_group=metadata_tuple[1],
                secondary_muscle_groups=metadata_tuple[2],
            )
            return exercise_metadata

    def add_exercise_metadata(self, exercise_metadata: ExerciseMetadata) -> tuple[int]:
        with self.conn.cursor() as cursor:
            primary_muscle_group = exercise_metadata.primary_muscle_group.value
            secondary_muscle_group = [
                str(mg.value) for mg in exercise_metadata.secondary_muscle_groups
            ]
            cursor.execute(
                insert_exercise_metadata,
                [exercise_metadata.name, primary_muscle_group, secondary_muscle_group],
            )
            result = cursor.fetchone()
            return result

    def add_workout(self, workout: Workout) -> int:
        with self.conn.cursor() as cursor:
            cursor.execute(insert_workout, (workout.date, workout.duration))
            inserted_id = cursor.fetchone()[0]
            return inserted_id

    def add_exercise_to_workout(self, exercise: Exercise, workout_id: int) -> int:
        exercise_name = exercise.exercise_metadata.name
        with self.conn.cursor() as cursor:
            cursor.execute(insert_exercise_to_workout, (exercise_name, workout_id))
            inserted_id = cursor.fetchone()[0]
            return inserted_id

    def add_sets_to_exercise(
        self, exercise_sets: list[ExerciseSet], exercise_id: int
    ) -> None:
        with self.conn.cursor() as cursor:
            cursor.executemany(
                insert_sets_to_exercise,
                [
                    (
                        exercise_set.weight,
                        exercise_set.repetitions,
                        exercise_set.to_failure,
                        exercise_id,
                    )
                    for exercise_set in exercise_sets
                ],
            )

    def add_exercise_with_sets_to_workout(
        self, exercise: Exercise, workout_id: int
    ) -> int:
        exercise_id = self.add_exercise_to_workout(
            exercise=exercise, workout_id=workout_id
        )
        self.add_sets_to_exercise(
            exercise_sets=exercise.exercise_sets, exercise_id=exercise_id
        )
        return exercise_id

    def get_workout_by_date(
        self, date: str
    ) -> tuple[list[ExerciseRow], WorkoutInfoRow] | None:
        with self.conn.cursor() as cursor:
            cursor.execute(select_workout_date_and_duration, (date,))
            if workout_metadata := cursor.fetchone():
                workout_info = WorkoutInfoRow(*workout_metadata)
            else:
                return None
            cursor.execute(select_workout_by_date, (date,))
            exercises = [ExerciseRow(*_row) for _row in cursor.fetchall()]
            return exercises, workout_info

    def get_workout_by_id(
        self, workout_id: int
    ) -> tuple[list[ExerciseRow], WorkoutInfoRow] | None:
        with self.conn.cursor() as cursor:
            cursor.execute(select_date_and_duration_by_id, (workout_id,))
            if workout_metadata := cursor.fetchone():
                workout_info = WorkoutInfoRow(*workout_metadata)
            else:
                return None
            cursor.execute(select_workout_by_id, (workout_id,))
            exercises = [ExerciseRow(*_row) for _row in cursor.fetchall()]
            cursor.execute(select_date_and_duration_by_id, (workout_id,))
            return exercises, workout_info


if __name__ == "__main__":
    connection_string = "dbname=workouts host=localhost user=admin password=admin"
    with psycopg.connect(connection_string, autocommit=True) as conn:
        repo = PostgresSQLRepo(connection=conn)
        res = repo.get_workout_by_id(1)
        print(res)
