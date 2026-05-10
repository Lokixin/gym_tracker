from collections.abc import Generator

import psycopg
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from gym_tracker.entrypoints.dependencies import get_db_connection, get_db_session
from gym_tracker.entrypoints.fastapi_app import app


def test_create_workout_returns_inserted_id_and_persists_payload(
    db_connection: psycopg.Connection,
    db_session: Session,
    seeded_metadata: dict[str, int],
) -> None:
    def override_session() -> Generator[Session, None, None]:
        yield db_session

    def override_connection() -> Generator[psycopg.Connection, None, None]:
        yield db_connection

    app.dependency_overrides[get_db_session] = override_session
    app.dependency_overrides[get_db_connection] = override_connection
    try:
        client = TestClient(app)
        response = client.post(
            "/workouts",
            json={
                "date": "2024-06-16",
                "duration": 90,
                "workout_entries": {
                    f"{seeded_metadata['bench_press']}.weights.0": "80",
                    f"{seeded_metadata['bench_press']}.reps.0": "10",
                    f"{seeded_metadata['bench_press']}.to_failure.0": "on",
                    f"{seeded_metadata['bench_press']}.weights.1": "75",
                    f"{seeded_metadata['bench_press']}.reps.1": "8",
                },
            },
        )

        assert response.status_code == 201
        workout_id = response.json()["id"]
        assert isinstance(workout_id, int)

        read_response = client.get(f"/workouts/{workout_id}")
        assert read_response.status_code == 200
        assert read_response.json() == {
            "date": "2024-06-16",
            "duration": 90,
            "exercises": [
                {
                    "exercise_metadata": {
                        "name": "Bench Press",
                        "primary_muscle_group": "Chest",
                        "secondary_muscle_groups": ["Triceps"],
                    },
                    "exercise_sets": [
                        {"weight": 80.0, "repetitions": 10, "to_failure": True},
                        {"weight": 75.0, "repetitions": 8, "to_failure": False},
                    ],
                }
            ],
        }
    finally:
        app.dependency_overrides.clear()
