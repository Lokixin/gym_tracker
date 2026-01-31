const workoutsByIdEndpoint = window.WORKOUTS_BY_ID_ENDPOINT ?? "/workouts/";

const dateSelector = document.getElementById("workouts_dates");
const selectedDate = document.getElementById("selected_date");
const workoutsList = document.getElementById("workout_exercises");
const workoutTitle = document.getElementById("workout_title");

dateSelector?.addEventListener("change", getWorkoutById);

function getSelectedLabel(selectElement) {
  if (!selectElement) {
    return "";
  }
  return selectElement.options[selectElement.selectedIndex]?.text || "";
}

function fmtDateChip(value) {
  try {
    const date = new Date(value);
    if (!isNaN(date)) {
      return date.toLocaleString([], {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      });
    }
  } catch {
    return String(value);
  }
  return String(value);
}

function setSelectedDate(value) {
  selectedDate.textContent = value ? fmtDateChip(value) : "";
  selectedDate.style.display = value ? "inline-flex" : "none";
}

async function fetchWorkoutById(workoutId) {
  const url = `${workoutsByIdEndpoint}/${encodeURIComponent(workoutId)}`;
  const response = await fetch(url, { method: "GET" });
  return response.json();
}

async function getWorkoutById(event) {
  const chosen = event.target.value;
  setSelectedDate(getSelectedLabel(event.target));

  if (!chosen) {
    renderWorkout({ exercises: [], date: "", duration: 0 });
    return;
  }

  const workout = await fetchWorkoutById(chosen);
  renderWorkout(workout);
}

function renderWorkout(workout) {
  workoutsList.innerHTML = "";

  const day = (workout.date ?? "").toString().slice(0, 10);
  const duration = workout.duration ?? 0;
  workoutTitle.textContent = `Workout • ${day} • ${duration} min`;

  (workout.exercises || []).forEach((exercise, index) => {
    workoutsList.appendChild(renderExerciseCard(exercise, index));
  });

  if (!workoutsList.children.length) {
    workoutsList.appendChild(renderEmptyState());
  }
}

function renderExerciseCard(exercise, index) {
  const card = document.createElement("article");
  card.className = "card";

  const top = document.createElement("div");
  top.className = "top";
  const left = document.createElement("div");
  const name = document.createElement("div");
  name.className = "name";
  name.textContent = exercise?.exercise_metadata?.name || `Exercise ${index + 1}`;
  left.appendChild(name);

  const count = document.createElement("div");
  count.className = "count";
  const totalSets = (exercise.exercise_sets || []).length;
  count.innerHTML = `<div>${totalSets} ${totalSets === 1 ? "set" : "sets"}</div>`;

  top.appendChild(left);
  top.appendChild(count);
  card.appendChild(top);

  const badges = renderBadges(exercise?.exercise_metadata);
  if (badges) {
    card.appendChild(badges);
  }

  card.appendChild(renderSets(exercise.exercise_sets || []));
  return card;
}

function renderBadges(metadata) {
  if (!metadata) {
    return null;
  }

  const badges = document.createElement("div");
  badges.className = "badges";

  const primary = metadata.primary_muscle_group;
  if (primary && String(primary).trim()) {
    badges.appendChild(renderBadge("primary", `Primary • ${primary}`));
  }

  const secondary = metadata.secondary_muscle_groups;
  if (secondary && String(secondary).trim()) {
    badges.appendChild(renderBadge("secondary", `Secondary • ${secondary}`));
  }

  return badges.children.length ? badges : null;
}

function renderBadge(type, label) {
  const badge = document.createElement("span");
  badge.className = `badge ${type}`;
  badge.textContent = label;
  return badge;
}

function renderSets(sets) {
  const setsWrap = document.createElement("div");
  setsWrap.className = "sets";
  sets.forEach((set) => {
    const row = document.createElement("span");
    row.className = "set";
    row.textContent = `${set.weight} kg × ${set.repetitions}`;
    if (set.to_failure) {
      row.classList.add("fail");
      row.textContent += " • failure";
    }
    setsWrap.appendChild(row);
  });
  return setsWrap;
}

function renderEmptyState() {
  const empty = document.createElement("div");
  empty.className = "chip";
  empty.textContent = "No exercises found for this workout.";
  return empty;
}
