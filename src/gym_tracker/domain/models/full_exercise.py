from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gym_tracker.domain.models.base import Base


class FullExercise(Base):
    __tablename__ = "full_exercises"

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
