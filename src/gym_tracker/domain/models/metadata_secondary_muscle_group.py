from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gym_tracker.domain.models.base import Base


class MetadataSecondaryMuscleGroup(Base):
    __tablename__ = "metadata_secondary_muscle_group"

    metadata_id: Mapped[int] = mapped_column(
        ForeignKey("exercises_metadata.id"), primary_key=True
    )
    muscle_group_id: Mapped[int] = mapped_column(
        ForeignKey("muscle_groups.id"), primary_key=True
    )

    exercise_metadata: Mapped["ExerciseMetadata"] = relationship(
        back_populates="secondary_muscle_groups"
    )
    muscle_group: Mapped["MuscleGroup"] = relationship(
        back_populates="secondary_metadata_links"
    )
