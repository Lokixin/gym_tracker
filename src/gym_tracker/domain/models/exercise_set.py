from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gym_tracker.domain.models.base import Base


class ExerciseSet(Base):
    __tablename__ = "exercise_sets"

    id: Mapped[int] = mapped_column(primary_key=True)
    weight: Mapped[float] = mapped_column(nullable=False)
    repetitions: Mapped[int] = mapped_column(nullable=False)
    to_failure: Mapped[bool | None] = mapped_column(default=False)
    full_exercise_id: Mapped[int] = mapped_column(
        ForeignKey("full_exercises.id"), nullable=False
    )

    full_exercise: Mapped["FullExercise"] = relationship(back_populates="exercise_sets")
