import datetime
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

    def __str__(self) -> str:
        set_str = f"{self.weight}kgs x {self.repetitions}"
        if not self.to_failure:
            return set_str
        return f"{set_str} (reached failure)"


class Exercise:
    def __init__(
        self,
        exercise_metadata: ExerciseMetadata,
        exercise_sets: list[ExerciseSet],
    ) -> None:
        self.exercise_metadata = exercise_metadata
        self.exercise_sets = exercise_sets

    def __str__(self) -> str:
        exercise_str = f"\t{self.exercise_metadata.name}: "
        for exercise_set in self.exercise_sets:
            exercise_str += f"\n\t\t- {exercise_set}"
        exercise_str += "\n\n"
        return exercise_str

    def add_exercise_set(self, exercise_set: ExerciseSet) -> None:
        self.exercise_sets.append(exercise_set)


class Workout:
    def __init__(
        self, exercises: list[Exercise], duration: int, date: str | None = None
    ) -> None:
        self.exercises = exercises
        self.date = self._get_formatted_date(date)
        self.duration = duration

    def __str__(self) -> str:
        workout_str = f"Workout from day {self.simple_date} "
        if self.duration:
            workout_str += f"({self.duration}) minutes"
        workout_str += ":\n"
        for exercise in self.exercises:
            workout_str += str(exercise)
        return workout_str

    def add_exercise(self, exercise: Exercise) -> None:
        self.exercises.append(exercise)

    def add_set_to_exercise(
        self, exercise_set: ExerciseSet, exercise_metadata: ExerciseMetadata
    ) -> None:
        for exercise in self.exercises:
            if exercise.exercise_metadata.name == exercise_metadata.name:
                exercise.add_exercise_set(exercise_set)
                return
        self.add_exercise(
            Exercise(exercise_metadata=exercise_metadata, exercise_sets=[exercise_set])
        )

    def _get_formatted_date(self, date: str | None) -> str:
        if not date:
            return pendulum.now().to_rfc3339_string()
        parsed_date = cast(DateTime, pendulum.parse(date))
        return parsed_date.to_rfc3339_string()

    @property
    def simple_date(self) -> str:
        return datetime.datetime.fromisoformat(self.date).strftime("%Y-%m-%d")
