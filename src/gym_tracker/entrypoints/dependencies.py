from collections.abc import Generator
import os

import psycopg
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from gym_tracker.adapters.repositories import PostgresSQLRepo

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://admin:admin@postgres/workouts")
CONNECTION_STRING = DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")
postgres_client: psycopg.Connection = None  # type: ignore[assignment]

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_db_connection() -> Generator[psycopg.Connection, None, None]:
    with psycopg.connect(CONNECTION_STRING, autocommit=True) as connection:
        yield connection


def get_workouts_repo(
    session: Session = Depends(get_db_session),
    connection: psycopg.Connection = Depends(get_db_connection),
) -> PostgresSQLRepo:
    return PostgresSQLRepo(connection, session)
