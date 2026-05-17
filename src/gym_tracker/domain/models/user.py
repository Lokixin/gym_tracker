from datetime import datetime, timezone

from sqlalchemy import Column, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gym_tracker.domain.models import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    enabled: Mapped[bool] = mapped_column(nullable=False, default=True)
    workouts: Mapped[list["Workout"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"User ({self.id}): {self.username} {self.email}"
