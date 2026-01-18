from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gym_tracker.domain.models.base import Base


class ExerciseMetadata(Base):
    __tablename__ = "exercises_metadata"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    primary_muscle_group_id: Mapped[int | None] = mapped_column(
        ForeignKey("muscle_groups.id")
    )

    primary_muscle_group: Mapped["MuscleGroup"] = relationship(
        back_populates="primary_exercises"
    )
    secondary_muscle_groups: Mapped[list["MetadataSecondaryMuscleGroup"]] = (
        relationship(back_populates="exercise_metadata")
    )
    full_exercises: Mapped[list["FullExercise"]] = relationship(
        back_populates="exercise_metadata"
    )
