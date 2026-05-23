import logging
from collections import namedtuple
from datetime import date, datetime, timezone

from psycopg import Connection
from sqlalchemy import select
from sqlalchemy.orm import Session

from gym_tracker.adapters.workouts_queries import (
    insert_exercise_metadata,
)
from gym_tracker.domain.model import (
    ExerciseMetadata,
)
from gym_tracker.domain.models.exercise_metadata import (
    ExerciseMetadata as ExerciseMetadataModel,
)
from gym_tracker.domain.models.exercise_set import ExerciseSet as ExerciseSetModel
from gym_tracker.domain.models.full_exercise import FullExercise
from gym_tracker.domain.models.metadata_secondary_muscle_group import (
    MetadataSecondaryMuscleGroup,
)
from gym_tracker.domain.models.muscle_group import MuscleGroup
from gym_tracker.domain.models.workout import Workout


logger = logging.getLogger(__name__)

ExerciseRow = namedtuple(
    "ExerciseRow",
    "weight, reps, to_failure, name, primary_muscle_group, secondary_muscle_groups",
)
WorkoutInfoRow = namedtuple("WorkoutInfoRow", "date, duration")
SearchExerciseRow = namedtuple("SearchExerciseRow", "id, name")


class RepositoryError(Exception):
    pass


class PostgresSQLRepo:
    def __init__(self, session: Session, connection: Connection | None = None) -> None:
        self.conn = connection
        self.session = session

    def _require_connection(self) -> Connection:
        if self.conn is None:
            raise RuntimeError(
                "A psycopg connection is required for this legacy method"
            )
        return self.conn

    def add_many_exercises_metadata(
        self, exercises_metadata: list[ExerciseMetadata]
    ) -> int:
        with self._require_connection().cursor() as cursor:
            values = [
                (
                    exercise_metadata.name,
                    exercise_metadata.primary_muscle_group,
                    exercise_metadata.secondary_muscle_groups,
                )
                for exercise_metadata in exercises_metadata
            ]
            cursor.executemany(insert_exercise_metadata, values)
            return cursor.rowcount

    def add_workout(
        self,
        exercises: dict[str, list[dict[str, int | float | bool]]],
        workout_date: str | None = None,
        workout_duration: int | None = 0,
        user_id: int | None = None,
    ) -> int:
        if not workout_date:
            workout_date_value = datetime.now(timezone.utc).date()
        else:
            workout_date_value = date.fromisoformat(workout_date[:10])
        owns_transaction = not self.session.in_transaction()
        try:
            if owns_transaction:
                with self.session.begin():
                    return self._add_workout_records(
                        exercises=exercises,
                        workout_date=workout_date_value,
                        workout_duration=workout_duration,
                    )

            return self._add_workout_records(
                exercises=exercises,
                workout_date=workout_date_value,
                workout_duration=workout_duration,
                user_id=user_id,
            )
        except Exception as exc:
            logger.exception(
                "Failed to add workout", extra={"workout_date": workout_date}
            )
            raise RepositoryError("Failed to add workout") from exc

    def _add_workout_records(
        self,
        exercises: dict[str, list[dict[str, int | float | bool]]],
        workout_date: date,
        workout_duration: int | None,
        user_id: int | None = None,
    ) -> int:
        workout = Workout(
            date=workout_date, duration=workout_duration or 0, user_id=user_id
        )
        self.session.add(workout)
        self.session.flush()

        for metadata_id, exercise_sets in exercises.items():
            full_exercise = FullExercise(
                metadata_id=int(metadata_id),
                workout_id=workout.id,
            )
            self.session.add(full_exercise)
            self.session.flush()

            if exercise_sets:
                self.session.add_all(
                    [
                        ExerciseSetModel(
                            weight=float(exercise_set["weight"]),
                            repetitions=int(exercise_set["repetitions"]),
                            to_failure=bool(exercise_set.get("to_failure", False)),
                            full_exercise_id=full_exercise.id,
                        )
                        for exercise_set in exercise_sets
                    ]
                )
        logger.warning("WORKOUT %s ID CREATED", workout.id)
        self.session.commit()
        return workout.id

    def get_workout_by_date(
        self, date: str
    ) -> tuple[list[ExerciseRow], WorkoutInfoRow] | None:
        workout_statement = select(Workout.id).where(Workout.date == date)
        workout_id = self.session.execute(workout_statement).scalar_one_or_none()
        if workout_id is None:
            return None
        return self.get_workout_by_id(workout_id)

    def get_workout_by_id(
        self, workout_id: int
    ) -> tuple[list[ExerciseRow], WorkoutInfoRow] | None:
        workout_statement = select(Workout.date, Workout.duration).where(
            Workout.id == workout_id
        )
        workout_metadata = self.session.execute(workout_statement).first()
        if not workout_metadata:
            return None
        workout_info = WorkoutInfoRow(*workout_metadata)

        exercise_ids_statement = select(FullExercise.id).where(
            FullExercise.workout_id == workout_id
        )
        exercise_ids = self.session.execute(exercise_ids_statement).scalars().all()
        if not exercise_ids:
            return [], workout_info

        exercises_statement = (
            select(
                ExerciseSetModel.weight,
                ExerciseSetModel.repetitions,
                ExerciseSetModel.to_failure,
                ExerciseMetadataModel.name,
                MuscleGroup.muscle_group,
                ExerciseMetadataModel.id,
            )
            .join(FullExercise, ExerciseSetModel.full_exercise_id == FullExercise.id)
            .join(
                ExerciseMetadataModel,
                FullExercise.metadata_id == ExerciseMetadataModel.id,
            )
            .join(
                MuscleGroup,
                ExerciseMetadataModel.primary_muscle_group_id == MuscleGroup.id,
            )
            .where(ExerciseSetModel.full_exercise_id.in_(exercise_ids))
            .order_by(ExerciseSetModel.id)
        )
        exercises_rows = self.session.execute(exercises_statement).all()
        metadata_ids = {row[5] for row in exercises_rows}

        secondary_statement = (
            select(
                MetadataSecondaryMuscleGroup.metadata_id,
                MuscleGroup.muscle_group,
            )
            .join(
                MuscleGroup,
                MetadataSecondaryMuscleGroup.muscle_group_id == MuscleGroup.id,
            )
            .where(MetadataSecondaryMuscleGroup.metadata_id.in_(metadata_ids))
        )
        secondary_rows = self.session.execute(secondary_statement).all()
        secondary_map: dict[int, list[str]] = {}
        for metadata_id, muscle_group in secondary_rows:
            secondary_map.setdefault(metadata_id, []).append(muscle_group)

        exercises = [
            ExerciseRow(
                weight=row[0],
                reps=row[1],
                to_failure=row[2],
                name=row[3],
                primary_muscle_group=row[4],
                secondary_muscle_groups=secondary_map.get(row[5], []),
            )
            for row in exercises_rows
        ]
        return exercises, workout_info

    def get_exercises_name(self, search_term: str) -> list[SearchExerciseRow]:
        search_pattern = f"%{search_term}%"
        statement = (
            select(ExerciseMetadataModel.id, ExerciseMetadataModel.name)
            .where(ExerciseMetadataModel.name.ilike(search_pattern))
            .order_by(ExerciseMetadataModel.name)
            .limit(10)
        )
        results = self.session.execute(statement).all()
        return [
            SearchExerciseRow(id=exercise_id, name=exercise_name)
            for exercise_id, exercise_name in results
        ]

    def get_existing_workouts_dates(self, user_id: int) -> list[dict[str, str | int]]:
        statement = (
            select(Workout.id, Workout.date)
            .filter(Workout.user_id == user_id)
            .order_by(Workout.date.desc())
        )
        results = self.session.execute(statement).all()
        return [
            {"id": workout_id, "date": str(workout_date)}
            for workout_id, workout_date in results
        ]
