import datetime

from sqlalchemy import Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gym_tracker.domain.models.base import Base


class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    duration: Mapped[int] = mapped_column(nullable=False)

    full_exercises: Mapped[list["FullExercise"]] = relationship(
        back_populates="workout"
    )
