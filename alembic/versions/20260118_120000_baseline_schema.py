"""Baseline schema

Revision ID: 20260118_120000
Revises:
Create Date: 2026-01-18 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "20260118_120000"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "muscle_groups",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("muscle_group", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("muscle_group"),
    )
    op.create_table(
        "workouts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("duration", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "exercises_metadata",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("primary_muscle_group_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["primary_muscle_group_id"], ["muscle_groups.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "full_exercises",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("metadata_id", sa.Integer(), nullable=False),
        sa.Column("workout_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["metadata_id"], ["exercises_metadata.id"]),
        sa.ForeignKeyConstraint(["workout_id"], ["workouts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "metadata_secondary_muscle_group",
        sa.Column("metadata_id", sa.Integer(), nullable=False),
        sa.Column("muscle_group_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["metadata_id"], ["exercises_metadata.id"]),
        sa.ForeignKeyConstraint(["muscle_group_id"], ["muscle_groups.id"]),
        sa.PrimaryKeyConstraint("metadata_id", "muscle_group_id"),
    )
    op.create_table(
        "exercise_sets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("repetitions", sa.Integer(), nullable=False),
        sa.Column("to_failure", sa.Boolean(), nullable=True),
        sa.Column("full_exercise_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["full_exercise_id"], ["full_exercises.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("exercise_sets")
    op.drop_table("metadata_secondary_muscle_group")
    op.drop_table("full_exercises")
    op.drop_table("exercises_metadata")
    op.drop_table("workouts")
    op.drop_table("muscle_groups")
