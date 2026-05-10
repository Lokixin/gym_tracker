from collections.abc import Generator
import os

import psycopg
import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from gym_tracker.domain.models.base import Base
from gym_tracker.domain.models.exercise_metadata import ExerciseMetadata
from gym_tracker.domain.models.metadata_secondary_muscle_group import (
    MetadataSecondaryMuscleGroup,
)
from gym_tracker.domain.models.muscle_group import MuscleGroup


@pytest.fixture(scope="session")
def database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        pytest.fail("DATABASE_URL is required for integration tests")
    return url


@pytest.fixture(scope="session")
def psycopg_url(database_url: str) -> str:
    return database_url.replace("postgresql+psycopg://", "postgresql://")


@pytest.fixture(scope="session")
def test_engine(database_url: str) -> Generator[Engine, None, None]:
    engine = create_engine(database_url)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture()
def db_session(test_engine: Engine) -> Generator[Session, None, None]:
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)

    session_factory = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(test_engine)


@pytest.fixture()
def db_connection(psycopg_url: str) -> Generator[psycopg.Connection, None, None]:
    with psycopg.connect(psycopg_url, autocommit=True) as connection:
        yield connection


@pytest.fixture()
def seeded_metadata(db_session: Session) -> dict[str, int]:
    chest = MuscleGroup(muscle_group="Chest")
    triceps = MuscleGroup(muscle_group="Triceps")
    db_session.add_all([chest, triceps])
    db_session.flush()

    bench = ExerciseMetadata(
        name="Bench Press",
        primary_muscle_group_id=chest.id,
    )
    db_session.add(bench)
    db_session.flush()

    db_session.add(
        MetadataSecondaryMuscleGroup(
            metadata_id=bench.id,
            muscle_group_id=triceps.id,
        )
    )
    bench_id = bench.id
    db_session.commit()
    return {"bench_press": bench_id}
