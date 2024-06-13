import logging

import psycopg
from psycopg import Connection

from gym_tracker.adapters.admin_queries import (
    select_exercise_metadata_by_name,
    select_muscle_group_by_name,
    insert_exercise_metadata,
    insert_secondary_muscle_groups,
)
from gym_tracker.domain.model import ExerciseMetadata

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

    def add_exercise_metadata(self, exercise_metadata: ExerciseMetadata) -> None:
        if self._check_if_metadata_already_exists(exercise_metadata.name):
            logger.info(
                f"Metadata not added: Already exists for {exercise_metadata.name}"
            )
            return
        with self.conn.cursor() as cursor:
            cursor.execute(
                select_muscle_group_by_name,
                [
                    [
                        exercise_metadata.primary_muscle_group,
                        *exercise_metadata.secondary_muscle_groups,
                    ]
                ],
            )
            all_muscle_groups = cursor.fetchall()
            # find primary
            primary_muscle_group_id = -1
            primary_muscle_group_pos = -1

            for idx, muscle_group in enumerate(all_muscle_groups):
                if muscle_group[1] == exercise_metadata.primary_muscle_group.value:
                    primary_muscle_group_id = muscle_group[0]
                    primary_muscle_group_pos = idx
                    break

            all_muscle_groups.pop(primary_muscle_group_pos)
            secondary_muscle_groups_ids = [
                muscle_group[0] for muscle_group in all_muscle_groups
            ]
            cursor.execute(
                insert_exercise_metadata,
                (exercise_metadata.name, primary_muscle_group_id),
            )
            metadata_id = cursor.fetchone()[0]
            cursor.executemany(
                insert_secondary_muscle_groups,
                [(metadata_id, _id) for _id in secondary_muscle_groups_ids],
            )

    def _check_if_metadata_already_exists(self, exercise_name: str) -> bool:
        with self.conn.cursor() as cursor:
            cursor.execute(select_exercise_metadata_by_name, (exercise_name,))
            if cursor.fetchone():
                return True
            return False


if __name__ == "__main__":
    connection_string = "dbname=workouts host=localhost user=admin password=admin"
    with psycopg.connect(connection_string, autocommit=True) as conn:
        repo = PostgresSQLRepo(connection=conn)
        exercise_metadata = repo.get_exercise_metadata_by_name("pull ups")
        print(exercise_metadata)
