
const addExerciseButton = document.getElementById("add_new_exercise")
const exerciseInput = document.getElementById("exercise_name")
const exercisesFormContainer = document.getElementById("container")
const exercisesDataList = document.getElementById("exercises-list")
const submitWorkoutButton = document.getElementById("submit-workout-button")
let exerciseCounter = 0
let setCounter = 0
let currentExerciseName = ""


addExerciseButton.addEventListener("click", addExerciseToForm)
exerciseInput.addEventListener("input", autocompleteExerciseName)
submitWorkoutButton.addEventListener("click", (ev) => submitWorkout(ev))


async function autocompleteExerciseName(ev) {
    const currentText = ev.target.value;
    if (currentText.length < 3) {
        return;
    }

    const url = `http://localhost:5555/search/exercises?exercise_name=${currentText}`
    const res = await fetch(
        encodeURI(url),
        {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        }
    )
    const resBody = await res.json()
    resBody.forEach(exercise => {
        const exerciseOption = document.createElement("option")
        const text = document.createTextNode(Object.values(exercise)[0])
        exerciseOption.id = Object.keys(exercise)[0]
        exerciseOption.appendChild(text)
        exercisesDataList.appendChild(exerciseOption)
    })
}

function addSetToExercise(event, currentExerciseDiv, exerciseName, metadata_id) {
    if (exerciseName === currentExerciseName) {
        setCounter += 1
    } else {
        currentExerciseName = exerciseName
        setCounter = 0
    }

    const repsLabel = document.createElement("label");
    const weightLabel = document.createElement("label");
    const repsInput = document.createElement("input");
    const weightInput = document.createElement("input");

    const repsLabelText = document.createTextNode("Reps: ");
    const weightLabelText = document.createTextNode("Weight");

    repsInput.id = `${metadata_id}-reps-number-${setCounter}`
    repsInput.name = `${metadata_id}.reps.${setCounter}`
    weightInput.id = `${metadata_id}-weight-number-${setCounter}`
    weightInput.name = `${metadata_id}.weights.${setCounter}`

    repsLabel.for = `${metadata_id}-reps-number-${exerciseCounter}`
    weightLabel.for = `${metadata_id}-weight-number-${exerciseCounter}`

    repsLabel.appendChild(repsLabelText);
    weightLabel.appendChild(weightLabelText);

    currentExerciseDiv.appendChild(repsLabel);
    currentExerciseDiv.appendChild(repsInput);
    currentExerciseDiv.appendChild(weightLabel);
    currentExerciseDiv.appendChild(weightInput);

}

function addExerciseToForm(event) {
    if (exerciseInput.value === "" || exerciseInput.value.length === 0) {
        console.log("Temporal fix for blank names")
        return
    }
    const opts = exercisesDataList.children
    let metadata_id = -1

    for (let i = 0; i < opts.length; i++) {
        if (opts[i].value === exerciseInput.value) {
            metadata_id = opts[i].id
            break
        }
    }
    let currentName = exerciseInput.value
    const newExerciseContainer = document.createElement("div")
    const addSetButton = document.createElement("button")
    const buttonText = document.createTextNode("Add new set")
    const exerciseNameText = document.createTextNode(currentName)

    // Repeticiones x Peso

    addSetButton.type = "button"
    addSetButton.addEventListener("click", (ev) => addSetToExercise(ev, newExerciseContainer, currentName, metadata_id))

    addSetButton.appendChild(buttonText)
    newExerciseContainer.appendChild(exerciseNameText)
    newExerciseContainer.appendChild(addSetButton)
    exercisesFormContainer.appendChild(newExerciseContainer)
    exerciseInput.value = ""
    exercisesDataList.innerHTML = ""
    exerciseCounter += 1;
}

async function submitWorkout(ev) {
    console.log("Preventing default behaviour")
    ev.preventDefault()
    const submitWorkoutForm = document.getElementById("submit_workout")

    const formData = new FormData(submitWorkoutForm)
    const payload = {"workout_entries": Object.fromEntries(formData.entries())}
    console.log(payload)

    const url = `http://localhost:5555/workouts/by_date`
    const res = await fetch(
        encodeURI(url),
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            body: JSON.stringify(payload)
        }
    )
    const resBody = await res.json()
    console.log(resBody)
}

