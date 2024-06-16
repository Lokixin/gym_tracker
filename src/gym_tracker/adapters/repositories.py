import logging
from typing import LiteralString

import psycopg
from psycopg import Connection

from gym_tracker.adapters.admin_queries import (
    select_exercise_metadata_by_name,
)
from gym_tracker.domain.model import ExerciseMetadata, MuscleGroup, Workout, Exercise

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
        pass


if __name__ == "__main__":
    connection_string = "dbname=workouts host=localhost user=admin password=admin"
    with psycopg.connect(connection_string, autocommit=True) as conn:
        repo = PostgresSQLRepo(connection=conn)
        workout = Workout(exercises=[], duration=0)
        res = repo.add_workout(workout)
        print(res)
