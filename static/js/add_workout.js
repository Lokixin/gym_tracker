// ====== basic helpers ======
const $  = (q, root=document) => root.querySelector(q);
const $$ = (q, root=document) => Array.from(root.querySelectorAll(q));

const exerciseInput  = $("#exercise_name");
const datalist       = $("#exercises-list");
const help           = $("#exercise_help");
const addExerciseBtn = $("#add_new_exercise");
const builder        = $("#builder");
const form           = $("#submit_workout");
const clearBtn       = $("#clear_all");

let exerciseCounter = 0;

// Configure endpoints if needed
window.EXERCISE_SUGGESTIONS_ENDPOINT = window.EXERCISE_SUGGESTIONS_ENDPOINT ?? "http://localhost:5555/search/exercises";
window.CREATE_WORKOUT_ENDPOINT       = window.CREATE_WORKOUT_ENDPOINT ?? "http://localhost:5555/workouts/by_date";

/* ---------- Validation helpers ---------- */
function isInDatalist(name){
  name = String(name || "").trim();
  if (!name) return false;
  // Exact match against option value
  for (const opt of datalist.children) {
    if (opt.value === name) return true;
  }
  return false;
}

function getMetadataIdFor(name){
  name = String(name || "").trim();
  for (const opt of datalist.children) {
    if (opt.value === name) return opt.id || null;
  }
  return null;
}

function setInputValidity(valid){
  exerciseInput.classList.toggle("invalid", !valid && exerciseInput.value.trim() !== "");
  help.textContent = valid ? "Looks good — press Add exercise." : "Please pick an exercise from the suggestions.";
  help.classList.toggle("error", !valid && exerciseInput.value.trim() !== "");
  addExerciseBtn.disabled = !valid;
}

function updateAddButtonState(){
  const valid = isInDatalist(exerciseInput.value);
  setInputValidity(valid);
}

/* ---------- Suggestions (datalist) ---------- */
let suggestAbort;
exerciseInput.addEventListener("input", async (e) => {
  const q = e.target.value.trim();

  // Live validate against current datalist first
  updateAddButtonState();

  // Fetch suggestions only when enough chars
  if (!window.EXERCISE_SUGGESTIONS_ENDPOINT || q.length < 3) {
    if (q.length < 3) {
      datalist.innerHTML = "";
      setInputValidity(false);
    }
    return;
  }

  try { suggestAbort?.abort(); } catch {}
  suggestAbort = new AbortController();

  try {
    const url = new URL(window.EXERCISE_SUGGESTIONS_ENDPOINT);
    url.searchParams.set("exercise_name", q);
    const res = await fetch(url, { signal: suggestAbort.signal, headers: { "Accept": "application/json" } });
    if (!res.ok) throw new Error(`suggestions failed: ${res.status}`);
    const items = await res.json(); // [{id:name}, ...]
    datalist.innerHTML = "";
    (items || []).slice(0, 20).forEach(obj => {
      const [id, name] = Object.entries(obj)[0];
      const opt = document.createElement("option");
      opt.id = id;
      opt.value = name;
      datalist.appendChild(opt);
    });
  } catch (err) {
    if (err.name !== "AbortError") console.warn(err);
  } finally {
    // After refreshing options, re-check validity
    updateAddButtonState();
  }
});

// Also validate on blur/change (when a browser inserts the datalist value)
exerciseInput.addEventListener("change", updateAddButtonState);
exerciseInput.addEventListener("blur", updateAddButtonState);

/* ---------- Exercise cards ---------- */
addExerciseBtn.addEventListener("click", () => {
  const name = exerciseInput.value.trim();
  const valid = isInDatalist(name);
  if (!valid) {
    setInputValidity(false);
    exerciseInput.focus();
    return; // hard stop — cannot add
  }

  const metadataId = getMetadataIdFor(name);
  if (!metadataId) {
    setInputValidity(false);
    exerciseInput.focus();
    return; // safety
  }

  const card = createExerciseCard(name, metadataId);
  builder.appendChild(card);

  // reset input + suggestions + button
  exerciseInput.value = "";
  datalist.innerHTML = "";
  updateAddButtonState();
});

clearBtn?.addEventListener("click", () => {
  builder.innerHTML = "";
  exerciseCounter = 0;
  exerciseInput.value = "";
  datalist.innerHTML = "";
  updateAddButtonState();
});

// Build card (same structure/style as the listing page)
function createExerciseCard(name, metadataId) {
  const exId = `ex-${++exerciseCounter}`;
  const card = document.createElement("article");
  card.className = "card";
  card.dataset.exId = exId;
  card.dataset.metadataId = metadataId;

  // Header
  const top = el("div", "top");
  const left = el("div");
  const title = el("div", "name");
  title.innerHTML = `<span class="ex-title">${escapeHtml(name)}</span>
                     <button type="button" class="rename" title="Rename">Rename</button>`;
  left.appendChild(title);

  const count = el("div", "count");
  count.innerHTML = `<div><span class="set-count">0</span> sets</div>`;
  top.append(left, count);
  card.appendChild(top);

  // Badges hook (optional—fill based on metadata if you fetch it)
  const badges = el("div", "badges");
  card.appendChild(badges);

  // Vertical sets list
  const sets = el("div", "sets");
  card.appendChild(sets);

  // Footer actions
  const actions = el("div", "actions");
  actions.innerHTML = `
    <button type="button" class="btn" data-act="add-set">＋ Add set</button>
    <button type="button" class="btn ghost" data-act="remove-ex">Remove exercise</button>
  `;
  card.appendChild(actions);

  // Events
  actions.querySelector('[data-act="add-set"]').addEventListener("click", () => addSetRow(card));
  actions.querySelector('[data-act="remove-ex"]').addEventListener("click", () => { card.remove(); });

  title.querySelector(".rename").addEventListener("click", () => {
    const current = card.querySelector(".ex-title").textContent.trim();
    // You could block renaming too, but usually renaming the label is fine.
    const next = prompt("Exercise name (label only):", current) ?? current;
    card.querySelector(".ex-title").textContent = next;
  });

  // Start with one set
  addSetRow(card);
  return card;
}

function addSetRow(card) {
  const sets = card.querySelector(".sets");
  const metadataId = card.dataset.metadataId; // guaranteed to exist now
  const index = sets.children.length; // 0..n

  const row = el("div", "set");

  const repsName   = `${metadataId}.reps.${index}`;
  const weightName = `${metadataId}.weights.${index}`;
  const failName   = `${metadataId}.to_failure.${index}`;

  row.innerHTML = `
    <label class="sub" for="${slug(weightName)}">Weight (kg)</label>
    <input type="number" id="${slug(weightName)}" name="${weightName}" min="0" step="0.5" value="0">

    <label class="sub" for="${slug(repsName)}">Reps</label>
    <input type="number" id="${slug(repsName)}" name="${repsName}" min="1" step="1" value="10">

    <label class="switch">
      <input type="checkbox" name="${failName}">
      Failure
    </label>

    <button type="button" class="remove">Remove</button>
  `;

  row.querySelector(".remove").addEventListener("click", () => {
    row.remove();
    updateSetCount(card);
    reindexSetNames(card, metadataId);
  });

  sets.appendChild(row);
  updateSetCount(card);
}

function updateSetCount(card) {
  card.querySelector(".set-count").textContent = card.querySelectorAll(".sets .set").length;
}

function reindexSetNames(card, metadataId) {
  $$(".sets .set", card).forEach((row, i) => {
    const reps  = row.querySelector('input[name*=".reps."]');
    const w     = row.querySelector('input[name*=".weights."]');
    const fail  = row.querySelector('input[name*=".to_failure."]');

    const repsName   = `${metadataId}.reps.${i}`;
    const weightName = `${metadataId}.weights.${i}`;
    const failName   = `${metadataId}.to_failure.${i}`;

    reps.name  = repsName;   reps.id  = slug(repsName);
    w.name     = weightName; w.id     = slug(weightName);
    fail.name  = failName;
  });
}

/* ---------- submit ---------- */
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  // Prevent empty submission
  if (!builder.children.length) {
    alert("Add at least one exercise.");
    return;
  }

  const fd = new FormData(form);
  const payload = { workout_entries: Object.fromEntries(fd.entries()) };
  console.log(payload)

  try {
    const res = await fetch(window.CREATE_WORKOUT_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Accept": "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await res.json();
    console.log("Created workout:", body);
    alert("Workout created!");
    builder.innerHTML = "";
  } catch (err) {
    console.error(err);
    alert("Failed to create workout.");
  }
});

/* ---------- utils ---------- */
function el(tag, className){ const n = document.createElement(tag); if (className) n.className = className; return n; }
function slug(s){ return String(s).replace(/[^a-z0-9:_-]+/gi, "_"); }
function escapeHtml(str){ return String(str).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m])); }

/* init */
updateAddButtonState();
