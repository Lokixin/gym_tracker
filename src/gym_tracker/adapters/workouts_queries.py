from typing import LiteralString


select_metadata_by_name: LiteralString = """
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

insert_exercise_metadata: LiteralString = """
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

insert_workout: LiteralString = """
    INSERT INTO WORKOUTS (date, duration) values (%s, %s)
    RETURNING id;
"""

insert_exercise_to_workout: LiteralString = """
    INSERT INTO full_exercises (metadata_id, workout_id) 
    VALUES ((SELECT id FROM exercises_metadata WHERE name LIKE %s), %s)
    RETURNING id;
"""

insert_exercise_by_id_to_workout: LiteralString = """
    INSERT INTO full_exercises (metadata_id, workout_id) 
    VALUES (%s, %s)
    RETURNING id;
"""

insert_sets_to_exercise: LiteralString = """
    INSERT INTO exercise_sets (weight, repetitions, to_failure, full_exercise_id) 
    VALUES (
        %s, %s, %s, %s
    );
"""

select_workout_by_date: LiteralString = """
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
        exercise_sets.id,
        exercise_sets.weight, 
        exercise_sets.repetitions, 
        exercise_sets.to_failure, 
        exercise_sets.full_exercise_id, 
        full_exercises.metadata_id, 
        exercises_metadata.id, 
        muscle_groups.muscle_group
    ORDER BY exercise_sets.id;
"""

select_workout_date_and_duration: LiteralString = """
    SELECT date, duration FROM workouts WHERE date = %s
"""

select_date_and_duration_by_id: LiteralString = """
    SELECT date, duration FROM workouts WHERE id = %s
"""

select_workout_by_id: LiteralString = """
    WITH workout AS (
        SELECT id, date, duration FROM workouts WHERE id = %s
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
        exercise_sets.id,
        exercises_metadata.primary_muscle_group_id, 
        exercise_sets.weight, 
        exercise_sets.repetitions, 
        exercise_sets.to_failure, 
        exercise_sets.full_exercise_id, 
        full_exercises.metadata_id, 
        exercises_metadata.id, 
        muscle_groups.muscle_group
    ORDER BY exercise_sets.id;
"""
