from collections.abc import Generator

import psycopg
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from gym_tracker.adapters.repositories import PostgresSQLRepo

CONNECTION_STRING = "dbname=workouts host=postgres user=admin password=admin"
DATABASE_URL = "postgresql+psycopg://admin:admin@postgres/workouts"

postgres_client = psycopg.connect(CONNECTION_STRING, autocommit=True)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_workouts_repo(
    session: Session = Depends(get_db_session),
) -> PostgresSQLRepo:
    return PostgresSQLRepo(postgres_client, session)
