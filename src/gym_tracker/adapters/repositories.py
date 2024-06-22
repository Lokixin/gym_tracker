import logging
from typing import LiteralString

import psycopg
from psycopg import Connection

from gym_tracker.domain.model import (
    ExerciseMetadata,
    Workout,
    Exercise,
    ExerciseSet,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


select_metadata_by_name = """
    WITH exercise_data AS (
        SELECT 
            em.id,
            em.name AS exercise_name,
            mg.muscle_group AS primary_muscle_group
        FROM exercises_metadata em
        INNER JOIN muscle_groups mg ON em.primary_muscle_group_id = mg.id
        WHERE em.name LIKE %s
    )
    SELECT 
        ed.exercise_name,
        ed.primary_muscle_group,
        ARRAY_AGG(mg2.muscle_group) AS secondary_muscle_groups
    FROM exercise_data ed
    LEFT JOIN metadata_secondary_muscle_group msmg ON ed.id = msmg.metadata_id
    LEFT JOIN muscle_groups mg2 ON msmg.muscle_group_id = mg2.id
    GROUP BY ed.exercise_name, ed.primary_muscle_group;
"""

find_muscle_groups_ids: LiteralString = """
    WITH primary_insert AS (
        INSERT 
            INTO exercises_metadata (name, primary_muscle_group_id)
        SELECT 
            %s AS exercise_name,
            id AS primary_muscle_id
        FROM muscle_groups 
            WHERE muscle_groups.muscle_group = %s
        RETURNING id
    ),
    secondary_insert AS (
        INSERT 
            INTO metadata_secondary_muscle_group (metadata_id, muscle_group_id)
        SELECT
            primary_insert.id,
            muscle_groups.id
        FROM primary_insert, muscle_groups
            WHERE muscle_groups.muscle_group = ANY(%s)
    )
    SELECT id FROM primary_insert
"""


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
                find_muscle_groups_ids,
                [exercise_metadata.name, primary_muscle_group, secondary_muscle_group],
            )
            result = cursor.fetchone()
            return result

    def add_workout(self, workout: Workout) -> int:
        add_workout_query: LiteralString = """
            INSERT INTO WORKOUTS (date, duration) values (%s, %s)
            RETURNING id;
        """
        with self.conn.cursor() as cursor:
            cursor.execute(add_workout_query, (workout.date, workout.duration))
            inserted_id = cursor.fetchone()[0]
            return inserted_id

    def add_exercise_to_workout(self, exercise: Exercise, workout_id: int) -> int:
        exercise_name = exercise.exercise_metadata.name
        query: LiteralString = """
            INSERT INTO full_exercises (metadata_id, workout_id) 
            VALUES ((SELECT id FROM exercises_metadata WHERE name LIKE %s), %s)
            RETURNING id;
        """
        with self.conn.cursor() as cursor:
            cursor.execute(query, (exercise_name, workout_id))
            inserted_id = cursor.fetchone()[0]
            return inserted_id

    def add_sets_to_exercise(
        self, exercise_sets: list[ExerciseSet], exercise_id: int
    ) -> None:
        query: LiteralString = """
            INSERT INTO exercise_sets (weight, repetitions, to_failure, full_exercise_id) 
            VALUES (
                %s, %s, %s, %s
            );
        """
        with self.conn.cursor() as cursor:
            cursor.executemany(
                query,
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

    def get_workout_by_date(self, date: str):
        query: LiteralString = """
            WITH workout AS (
                SELECT id, date, duration FROM workouts WHERE date = %s
            ),
            metadata AS (
                SELECT id, metadata_id FROM full_exercises WHERE workout_id = (SELECT id FROM workout)
            )
            SELECT 
                exercise_sets.weight, 
                exercise_sets.repetitions,
                exercise_sets.to_failure, 
                exercises_metadata.name,
                muscle_groups.muscle_group,
                ARRAY_AGG(mg2.muscle_group) AS secondary_muscle_groups
            FROM exercise_sets 
                LEFT JOIN full_exercises ON exercise_sets.full_exercise_id = full_exercises.id
                LEFT JOIN exercises_metadata ON exercises_metadata.id = full_exercises.metadata_id
                LEFT JOIN muscle_groups ON muscle_groups.id = exercises_metadata.primary_muscle_group_id
                LEFT JOIN metadata_secondary_muscle_group msmg ON exercises_metadata.id = msmg.metadata_id
                LEFT JOIN muscle_groups mg2 ON msmg.muscle_group_id = mg2.id
            WHERE full_exercise_id = ANY(SELECT id FROM metadata)
                GROUP BY exercises_metadata.name, 
                exercises_metadata.primary_muscle_group_id, 
                exercise_sets.weight, 
                exercise_sets.repetitions, 
                exercise_sets.to_failure, 
                exercise_sets.full_exercise_id, 
                full_exercises.metadata_id, 
                exercises_metadata.id, 
                muscle_groups.muscle_group;
        """
        with self.conn.cursor() as cursor:
            cursor.execute(query, (date,))
            res = cursor.fetchall()
            return res


if __name__ == "__main__":
    connection_string = "dbname=workouts host=localhost user=admin password=admin"
    with psycopg.connect(connection_string, autocommit=True) as conn:
        repo = PostgresSQLRepo(connection=conn)
        res = repo.get_workout_by_date(date="2024-06-16")
        print(res)
