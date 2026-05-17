import datetime

from sqlalchemy import Date, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gym_tracker.domain.models.base import Base


class Workout(Base):
    __tablename__ = "workouts"
    __table_args__ = (Index("ix_workouts_date", "date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    duration: Mapped[int] = mapped_column(nullable=False)

    full_exercises: Mapped[list["FullExercise"]] = relationship(
        back_populates="workout"
    )
    user: Mapped["User"] = relationship(back_populates="workouts")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
