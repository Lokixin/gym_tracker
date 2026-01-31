from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gym_tracker.domain.models.base import Base


class MuscleGroup(Base):
    __tablename__ = "muscle_groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    muscle_group: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    primary_exercises: Mapped[list["ExerciseMetadata"]] = relationship(
        back_populates="primary_muscle_group"
    )
    secondary_metadata_links: Mapped[list["MetadataSecondaryMuscleGroup"]] = (
        relationship(back_populates="muscle_group")
    )
