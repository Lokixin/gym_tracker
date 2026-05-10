import logging
from collections import namedtuple
from datetime import date, datetime, timezone
from typing import LiteralString

from psycopg import Connection
from sqlalchemy import select
from sqlalchemy.orm import Session

from gym_tracker.adapters.admin_queries import insert_muscle_group
from gym_tracker.adapters.workouts_queries import (
    select_metadata_by_name,
    insert_exercise_metadata,
    insert_exercise_to_workout,
    insert_sets_to_exercise,
    select_workout_by_date,
    select_workout_date_and_duration,
    insert_exercise_by_id_to_workout,
)
from gym_tracker.domain.model import (
    ExerciseMetadata,
    Exercise,
    ExerciseSet,
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


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ExerciseRow = namedtuple(
    "ExerciseRow",
    "weight, reps, to_failure, name, primary_muscle_group, secondary_muscle_groups",
)
WorkoutInfoRow = namedtuple("WorkoutInfoRow", "date, duration")


class PostgresSQLRepo:
    def __init__(self, connection: Connection, session: Session) -> None:
        self.conn = connection
        self.session = session

    def get_exercise_metadata_by_name(self, name: str) -> ExerciseMetadata:
        with self.conn.cursor() as cursor:
            cursor.execute(select_metadata_by_name, (name,))
            metadata_tuple = cursor.fetchone()
            exercise_metadata = ExerciseMetadata(
                name=metadata_tuple[0],
                primary_muscle_group=metadata_tuple[1],
                secondary_muscle_groups=metadata_tuple[2],
            )
            return exercise_metadata

    def add_exercise_metadata(self, exercise_metadata: ExerciseMetadata) -> tuple[int]:
        with self.conn.cursor() as cursor:
            primary_muscle_group = exercise_metadata.primary_muscle_group.value
            secondary_muscle_group = [
                str(mg.value) for mg in exercise_metadata.secondary_muscle_groups
            ]
            cursor.execute(
                insert_exercise_metadata,
                [exercise_metadata.name, primary_muscle_group, secondary_muscle_group],
            )
            result = cursor.fetchone()
            return result

    def add_many_exercises_metadata(
        self, exercises_metadata: list[ExerciseMetadata]
    ) -> int:
        with self.conn.cursor() as cursor:
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
    ) -> int:
        if not workout_date:
            workout_date_value = datetime.now(timezone.utc).date()
        else:
            workout_date_value = date.fromisoformat(workout_date[:10])
        with self.session.begin():
            workout = Workout(
                date=workout_date_value,
                duration=workout_duration or 0,
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

            return workout.id

    def add_exercise_to_workout(self, exercise: Exercise, workout_id: int) -> int:
        exercise_name = exercise.exercise_metadata.name
        with self.conn.cursor() as cursor:
            cursor.execute(insert_exercise_to_workout, (exercise_name, workout_id))
            inserted_id = cursor.fetchone()[0]
            return inserted_id

    def add_exercise_by_id_to_workout(
        self, exercise_metadata_id: int, workout_id: int
    ) -> int:
        with self.conn.cursor() as cursor:
            cursor.execute(
                insert_exercise_by_id_to_workout, (exercise_metadata_id, workout_id)
            )
            inserted_id = cursor.fetchone()[0]
            return inserted_id

    def add_sets_to_exercise(
        self, exercise_sets: list[ExerciseSet], exercise_id: int
    ) -> None:
        with self.conn.cursor() as cursor:
            cursor.executemany(
                insert_sets_to_exercise,
                [
                    (
                        exercise_set.weight,
                        exercise_set.repetitions,
                        exercise_set.to_failure,
                        exercise_id,
                    )
                    for exercise_set in exercise_sets
                ],
            )

    def add_exercise_with_sets_to_workout(
        self, exercise: Exercise, workout_id: int
    ) -> int:
        exercise_id = self.add_exercise_to_workout(
            exercise=exercise, workout_id=workout_id
        )
        self.add_sets_to_exercise(
            exercise_sets=exercise.exercise_sets, exercise_id=exercise_id
        )
        return exercise_id

    def add_muscle_groups(self, muscle_groups: set[str]) -> int:
        with self.conn.cursor() as cursor:
            cursor.executemany(
                insert_muscle_group, [(muscle,) for muscle in muscle_groups]
            )
            return 0

    def get_workout_by_date(
        self, date: str
    ) -> tuple[list[ExerciseRow], WorkoutInfoRow] | None:
        with self.conn.cursor() as cursor:
            cursor.execute(select_workout_date_and_duration, (date,))
            if workout_metadata := cursor.fetchone():
                workout_info = WorkoutInfoRow(*workout_metadata)
            else:
                return None
            cursor.execute(select_workout_by_date, (date,))
            exercises = [ExerciseRow(*_row) for _row in cursor.fetchall()]
            return exercises, workout_info

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

    def get_exercises_name(self, search_term: str) -> list[dict[int, str]]:
        search_query: LiteralString = (
            """SELECT id, name FROM exercises_metadata WHERE name ILIKE %s LIMIT 10;"""
        )
        with self.conn.cursor() as cursor:
            cursor.execute(search_query, (f"%{search_term}%",))
            results = [{exercise[0]: exercise[1]} for exercise in cursor.fetchall()]
            return results

    def get_existing_workouts_dates(self) -> list[dict[str, str | int]]:
        statement = select(Workout.id, Workout.date).order_by(Workout.date.desc())
        results = self.session.execute(statement).all()
        return [
            {"id": workout_id, "date": str(workout_date)}
            for workout_id, workout_date in results
        ]
