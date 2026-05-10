import pytest

from .conftest import validate_test_database_url


def test_database_url_guard_rejects_non_test_database() -> None:
    with pytest.raises(pytest.fail.Exception, match="ending in _test"):
        validate_test_database_url(
            "postgresql+psycopg://admin:admin@localhost/workouts"
        )


def test_database_url_guard_accepts_test_database() -> None:
    validate_test_database_url(
        "postgresql+psycopg://admin:admin@localhost/workouts_test"
    )
