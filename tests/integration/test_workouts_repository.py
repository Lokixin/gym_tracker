from psycopg import Connection
from sqlalchemy import select
from sqlalchemy.orm import Session

from gym_tracker.adapters.repositories import PostgresSQLRepo
from gym_tracker.domain.models.workout import Workout


def test_add_workout_inserts_workout_exercises_and_sets(
    db_connection: Connection,
    db_session: Session,
    seeded_metadata: dict[str, int],
) -> None:
    repo = PostgresSQLRepo(db_connection, db_session)

    workout_id = repo.add_workout(
        {
            str(seeded_metadata["bench_press"]): [
                {"weight": 80.0, "repetitions": 10, "to_failure": True},
                {"weight": 75.0, "repetitions": 8, "to_failure": False},
            ]
        },
        workout_date="2024-06-16",
        workout_duration=90,
    )

    workout = repo.get_workout_by_id(workout_id)

    assert workout is not None
    exercises, metadata = workout
    assert metadata.date.isoformat() == "2024-06-16"
    assert metadata.duration == 90
    assert [(row.weight, row.reps, row.to_failure) for row in exercises] == [
        (80.0, 10, True),
        (75.0, 8, False),
    ]
    assert exercises[0].name == "Bench Press"
    assert exercises[0].primary_muscle_group == "Chest"
    assert exercises[0].secondary_muscle_groups == ["Triceps"]


def test_add_workout_works_when_session_already_has_transaction(
    db_connection: Connection,
    db_session: Session,
    seeded_metadata: dict[str, int],
) -> None:
    repo = PostgresSQLRepo(db_connection, db_session)
    db_session.execute(select(Workout.id))

    workout_id = repo.add_workout(
        {
            str(seeded_metadata["bench_press"]): [
                {"weight": 80.0, "repetitions": 10, "to_failure": True},
            ]
        },
        workout_date="2024-06-16",
        workout_duration=90,
    )

    assert workout_id > 0
