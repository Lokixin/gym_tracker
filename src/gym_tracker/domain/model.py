from enum import StrEnum, auto
from dataclasses import dataclass
from typing import cast

import pendulum
from pendulum import DateTime


class MuscleGroup(StrEnum):
    SHOULDERS = auto()
    BACK = auto()
    PECK = auto()
    BICEPS = auto()
    TRICEPS = auto()
    QUADRICEPS = auto()
    CALVES = auto()
    ABS = auto()
    HAMSTRING = auto()
    GLUTEUS = auto()


@dataclass
class ExerciseMetadata:
    name: str
    primary_muscle_group: MuscleGroup
    secondary_muscle_groups: list[MuscleGroup]

    def __repr__(self) -> str:
        return (
            f"Name={self.name} primary_muscle={self.primary_muscle_group} "
            f"secondary_muscles={self.secondary_muscle_groups}"
        )


@dataclass
class ExerciseSet:
    weight: float
    repetitions: int
    to_failure: bool | None = False


class Exercise:
    def __init__(
        self,
        exercise_metadata: ExerciseMetadata,
        exercise_sets: list[ExerciseSet],
    ) -> None:
        self.exercise_metadata = exercise_metadata
        self.exercise_sets = exercise_sets

    def add_exercise_set(self, exercise_set: ExerciseSet) -> None:
        self.exercise_sets.append(exercise_set)


class Workout:
    def __init__(self, exercises: list[Exercise], date: str | None = None) -> None:
        self.exercises = exercises
        self.date = self._get_formatted_date(date)

    def add_exercise(self, exercise: Exercise) -> None:
        self.exercises.append(exercise)

    def _get_formatted_date(self, date: str | None) -> str:
        if not date:
            return pendulum.now().to_rfc3339_string()
        parsed_date = cast(DateTime, pendulum.parse(date))
        return parsed_date.to_rfc3339_string()
