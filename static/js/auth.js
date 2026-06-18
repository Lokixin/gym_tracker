const authForm = document.querySelector("[data-auth-mode]");
const authMessage = document.querySelector("[data-auth-message]");

const authEndpoints = {
  login: window.LOGIN_ENDPOINT ?? "/api/users/token",
  register: window.REGISTER_ENDPOINT ?? "/api/users",
};

authForm?.addEventListener("submit", async (event) => {
  event.preventDefault();

  const mode = authForm.dataset.authMode;
  const submitButton = authForm.querySelector('button[type="submit"]');
  const defaultLabel = submitButton?.dataset.defaultLabel ?? "Continue";

  clearMessage();

  if (!authForm.checkValidity()) {
    authForm.reportValidity();
    return;
  }

  const formData = new FormData(authForm);
  const password = String(formData.get("password") ?? "");
  const confirmedPassword = String(formData.get("confirm_password") ?? "");

  if (mode === "register" && password !== confirmedPassword) {
    showMessage("Passwords do not match.", "error");
    return;
  }

  setLoading(submitButton, true, mode === "register" ? "Creating..." : "Logging in...");

  try {
    if (mode === "register") {
      await registerUser(formData);
      showMessage("Account created. Logging you in...", "success");
    }

    await loginUser(formData);
    window.location.assign("/app/workouts/list");
  } catch (error) {
    showMessage(error.message || "Something went wrong. Try again.", "error");
  } finally {
    setLoading(submitButton, false, defaultLabel);
  }
});

async function registerUser(formData) {
  const payload = {
    username: String(formData.get("username") ?? "").trim(),
    email: String(formData.get("email") ?? "").trim(),
    plain_text_password: String(formData.get("password") ?? ""),
  };

  const response = await fetch(authEndpoints.register, {
    method: "POST",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  await ensureOk(response, "Could not create the account.");
}

async function loginUser(formData) {
  const body = new URLSearchParams();
  body.set("username", String(formData.get("username") ?? "").trim());
  body.set("password", String(formData.get("password") ?? ""));

  const response = await fetch(authEndpoints.login, {
    method: "POST",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body,
  });

  await ensureOk(response, "Incorrect username or password.");
}

async function ensureOk(response, fallbackMessage) {
  if (response.ok) {
    return;
  }

  let body;
  try {
    body = await response.json();
  } catch {
    throw new Error(fallbackMessage);
  }

  const detail = Array.isArray(body.detail)
    ? body.detail.map((item) => item.msg).filter(Boolean).join(" ")
    : body.detail;

  throw new Error(detail || fallbackMessage);
}

function setLoading(button, isLoading, label) {
  if (!button) {
    return;
  }

  button.disabled = isLoading;
  button.textContent = label;
  button.classList.toggle("is-loading", isLoading);
}

function showMessage(message, type) {
  if (!authMessage) {
    return;
  }

  authMessage.textContent = message;
  authMessage.className = `form-message ${type}`;
}

function clearMessage() {
  if (!authMessage) {
    return;
  }

  authMessage.textContent = "";
  authMessage.className = "form-message";
}
