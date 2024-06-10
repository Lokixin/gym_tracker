import psycopg
from psycopg import Cursor

from gym_tracker.domain.model import MuscleGroup, ExerciseMetadata


create_workouts_db = """CREATE DATABASE workouts"""

create_muscle_group_table = """CREATE TABLE muscle_groups (
    id SERIAL PRIMARY KEY,
    muscle_group VARCHAR(50) UNIQUE NOT NULL
);"""

select_muscle_group_by_name = (
    """SELECT id, muscle_group FROM muscle_groups WHERE muscle_group = ANY(%s);"""
)


insert_muscle_group = """INSERT INTO muscle_groups (muscle_group) VALUES (%s);"""

create_exercises_metadata_table = """CREATE TABLE exercises_metadata (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    primary_muscle_group_id INT,
    FOREIGN KEY(primary_muscle_group_id) REFERENCES muscle_groups(id)
);
"""

insert_exercise_metadata = """
    INSERT INTO exercises_metadata 
    (name, primary_muscle_group_id) VALUES (%s, %s)
    RETURNING id;
"""

select_exercise_metadata = """SELECT * FROM exercises_metadata"""
select_exercise_metadata_by_name = """
    SELECT (id, name, primary_muscle_group_id) FROM exercises_metadata WHERE name LIKE %s
"""
select_muscle_group_by_id = """
    SELECT muscle_group FROM muscle_groups WHERE id=%s;
"""
metadata_by_name_inner_join_primary_muscle_group = """
    SELECT exercises_metadata.id, exercises_metadata.name, muscle_groups.muscle_group FROM exercises_metadata 
    INNER JOIN muscle_groups ON exercises_metadata.primary_muscle_group_id=muscle_groups.id
    WHERE exercises_metadata.name LIKE %s;
"""

select_combined = """
    SELECT muscle_group FROM muscle_groups WHERE id = ANY(
        SELECT muscle_group_id FROM metadata_secondary_muscle_group WHERE metadata_id = %s
    );
"""

create_metadata_and_secondary_table = """
CREATE TABLE metadata_secondary_muscle_group (
    metadata_id INT NOT NULL,
    muscle_group_id INT NOT NULL,
    FOREIGN KEY(metadata_id) REFERENCES exercises_metadata(id),
    FOREIGN KEY(muscle_group_id) REFERENCES muscle_groups(id),
    PRIMARY KEY(metadata_id, muscle_group_id)
);
"""

insert_secondary_muscle_groups = """
    INSERT INTO metadata_secondary_muscle_group (metadata_id, muscle_group_id)
    VALUES (%s, %s);
"""

select_secondary_muscle_groups = """
    SELECT muscle_group_id FROM metadata_secondary_muscle_group WHERE metadata_id = %s;
"""

select_any_muscle_groups = """
    SELECT muscle_group FROM muscle_groups WHERE id = ANY(%s);
"""



def insert_exercise_metadata_by_name(
    cursor: psycopg.Cursor, exercise_name: str, muscle_group: MuscleGroup
) -> None:
    cursor.execute(select_muscle_group_by_name, (muscle_group.value,))
    muscle_group_id = cursor.fetchone()[0]
    cursor.execute(insert_exercise_metadata, (exercise_name, muscle_group_id))


def make_exercise_metadata_from_db(
    cursor: Cursor,
) -> ExerciseMetadata:
    cursor.execute(select_exercise_metadata)
    metadata = cursor.fetchone()
    primary_muscle_group_id = metadata[2]
    cursor.execute(select_muscle_group_by_id, (primary_muscle_group_id,))
    muscle_group = cursor.fetchone()
    exercise_metadata = ExerciseMetadata(
        name=metadata[1],
        primary_muscle_group=muscle_group[0],
        secondary_muscle_groups=[],
    )
    return exercise_metadata


# Esta función está bastante, la podemos reciclar y refactorizar
def get_exercise_metadata_by_name(cursor: Cursor, name: str) -> ExerciseMetadata:
    cursor.execute(select_exercise_metadata_by_name, (name,))
    # id, name, primary_muscle_group_id
    exercise_metadata_tuple = cursor.fetchone()
    cursor.execute(select_muscle_group_by_id, (exercise_metadata_tuple[0][0],))
    muscle_group_name = cursor.fetchone()[0]
    cursor.execute(select_secondary_muscle_groups, (exercise_metadata_tuple[0][0],))
    secondary_muscle_groups_ids = cursor.fetchall()
    secondary_musclegroups = cursor.execute(
        select_any_muscle_groups,
        [
            [_id[0] for _id in secondary_muscle_groups_ids],
        ],
    )
    secondary_musclegroups = cursor.fetchall()
    exercise_metadata = ExerciseMetadata(
        name=exercise_metadata_tuple[0][1],
        primary_muscle_group=muscle_group_name,
        secondary_muscle_groups=[
            muscle_group[0] for muscle_group in secondary_musclegroups
        ],
    )
    return exercise_metadata
