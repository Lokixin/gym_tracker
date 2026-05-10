from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from gym_tracker.adapters.repositories import RepositoryError
from gym_tracker.entrypoints.dependencies import get_db_session, get_workouts_repo
from gym_tracker.entrypoints.fastapi_app import app


def test_create_workout_returns_inserted_id_and_persists_payload(
    db_session: Session,
    seeded_metadata: dict[str, int],
) -> None:
    def override_session() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = override_session
    try:
        client = TestClient(app)
        response = client.post(
            "/workouts",
            json={
                "date": "2024-06-16",
                "duration": 90,
                "exercises": [
                    {
                        "metadata_id": seeded_metadata["bench_press"],
                        "sets": [
                            {"weight": 80, "repetitions": 10, "to_failure": True},
                            {"weight": 75, "repetitions": 8},
                        ],
                    }
                ],
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


def test_get_missing_workout_returns_404(db_session: Session) -> None:
    def override_session() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = override_session
    try:
        client = TestClient(app)

        response = client.get("/workouts/999")

        assert response.status_code == 404
        assert response.json() == {
            "detail": {"message": "Workout Not Found for id 999"}
        }
    finally:
        app.dependency_overrides.clear()


def test_create_workout_returns_safe_error_when_repository_fails() -> None:
    class FailingRepo:
        def add_workout(self, *args: object, **kwargs: object) -> int:
            raise RepositoryError("boom")

    app.dependency_overrides[get_workouts_repo] = lambda: FailingRepo()
    try:
        client = TestClient(app, raise_server_exceptions=False)

        response = client.post(
            "/workouts",
            json={
                "date": "2024-06-16",
                "duration": 90,
                "exercises": [
                    {
                        "metadata_id": 1,
                        "sets": [
                            {"weight": 80, "repetitions": 10, "to_failure": False}
                        ],
                    }
                ],
            },
        )

        assert response.status_code == 500
        assert response.json() == {"detail": {"message": "Unable to create workout"}}
    finally:
        app.dependency_overrides.clear()


def test_search_exercises_uses_dependency_overridden_session(
    db_session: Session,
    seeded_metadata: dict[str, int],
) -> None:
    def override_session() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = override_session
    try:
        client = TestClient(app)

        response = client.get("/search/exercises", params={"exercise_name": "press"})

        assert response.status_code == 200
        assert response.json() == [
            {"id": seeded_metadata["bench_press"], "name": "Bench Press"}
        ]
    finally:
        app.dependency_overrides.clear()
