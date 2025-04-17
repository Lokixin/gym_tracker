
const addExerciseButton = document.getElementById("add_new_exercise")
const exerciseInput = document.getElementById("exercise_name")
const exercisesFormContainer = document.getElementById("container")
let exerciseCounter = 0;

addExerciseButton.addEventListener("click", addExerciseToForm)

function addSetToExercise(event, currentExerciseDiv) {
    console.log(currentExerciseDiv)
    const repsLabel = document.createElement("label");
    const weightLabel = document.createElement("label");
    const repsInput = document.createElement("input");
    const weightInput = document.createElement("input");

    const repsLabelText = document.createTextNode("Reps: ");
    const weightLabelText = document.createTextNode("Weight");

    repsInput.id = `reps-number-${exerciseCounter}`
    weightInput.id = `weight-number-${exerciseCounter}`
    repsLabel.for = `reps-number-${exerciseCounter}`
    weightLabel.for = `weight-number-${exerciseCounter}`

    repsLabel.appendChild(repsLabelText);
    weightLabel.appendChild(weightLabelText);

    currentExerciseDiv.appendChild(repsLabel);
    currentExerciseDiv.appendChild(repsInput);
    currentExerciseDiv.appendChild(weightLabel);
    currentExerciseDiv.appendChild(weightInput);

    exerciseCounter += 1;
}

function addExerciseToForm(event) {
    if (exerciseInput.value === "" || exerciseInput.value.length === 0) {
        console.log("Temporal fix for blank names")
        return
    }
    const newExerciseContainer = document.createElement("div")
    const addSetButton = document.createElement("button")
    const buttonText = document.createTextNode("Add new set")
    const exerciseNameText = document.createTextNode(exerciseInput.value)


    // Repeticiones x Peso

    addSetButton.type = "button"
    addSetButton.addEventListener("click", (ev) => addSetToExercise(ev, newExerciseContainer))

    addSetButton.appendChild(buttonText)
    newExerciseContainer.appendChild(exerciseNameText)
    newExerciseContainer.appendChild(addSetButton)
    exercisesFormContainer.appendChild(newExerciseContainer)
    exerciseInput.value = ""
}

