from collections.abc import Generator

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from gym_tracker.adapters.repositories import PostgresSQLRepo
from gym_tracker.config import settings

DATABASE_URL = settings.database_url
CONNECTION_STRING = settings.psycopg_url

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
    return PostgresSQLRepo(session=session)
