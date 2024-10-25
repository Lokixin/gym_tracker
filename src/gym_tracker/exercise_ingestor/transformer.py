import csv

from gym_tracker.domain.model import ExerciseMetadata, ALL_MUSCLES
from gym_tracker.entrypoints.dependencies import get_workouts_repo, postgres_client


def load_exercises_from_csv(path_to_data: str):
    all_exercises = []
    with open(path_to_data, "r", encoding="utf-8", newline="") as fp:
        reader = csv.reader(fp)
        for _row in reader:
            if _row[0] == "name":
                continue
            name, primary, secondary = _row
            primary = parse_muscle_groups(primary)
            secondary = parse_muscle_groups(secondary)
            if len(primary) == 0:
                print("No primary muscle group for: ", name)
                continue
            secondary = secondary if secondary != [""] else []
            if len(primary) > 1:
                secondary += primary[1:]
                del primary[1:]

            exercise_meta = ExerciseMetadata(
                name=name,
                primary_muscle_group=primary[0],
                secondary_muscle_groups=secondary,
            )
            if exercise_meta not in all_exercises:
                all_exercises.append(exercise_meta)
    return all_exercises


def parse_muscle_groups(muscle_groups: str) -> list[str]:
    filtered = filter(
        lambda x: x in ALL_MUSCLES,
        (
            muscle.replace("'", "").strip("[").strip("]").strip()
            for muscle in muscle_groups.split(",")
        ),
    )
    return list(filtered)


if __name__ == "__main__":
    exercises = load_exercises_from_csv("temp_db.csv")
    print(postgres_client.info.status)

    repo = get_workouts_repo()
    res2 = repo.add_many_exercises_metadata(exercises)
    print(res2)
    assert True
