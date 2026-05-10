from __future__ import annotations

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gym_tracker.domain.models.base import Base


class FullExercise(Base):
    __tablename__ = "full_exercises"
    __table_args__ = (
        Index("ix_full_exercises_metadata_id", "metadata_id"),
        Index("ix_full_exercises_workout_id", "workout_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    metadata_id: Mapped[int] = mapped_column(
        ForeignKey("exercises_metadata.id"), nullable=False
    )
    workout_id: Mapped[int] = mapped_column(ForeignKey("workouts.id"), nullable=False)

    exercise_metadata: Mapped["ExerciseMetadata"] = relationship(
        back_populates="full_exercises"
    )
    workout: Mapped["Workout"] = relationship(back_populates="full_exercises")
    exercise_sets: Mapped[list["ExerciseSet"]] = relationship(
        back_populates="full_exercise"
    )
