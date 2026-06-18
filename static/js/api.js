function getCookieValue(name) {
  const regex = new RegExp(`(^| )${name}=([^;]+)`);
  const match = document.cookie.match(regex);
  return match ? match[2] : undefined;
}

function csrfFetch(resource, options = {}) {
  const headers = new Headers(options.headers || {});
  const authJwt = getCookieValue("auth_jwt");
  const csrfToken = getCookieValue("csrf_token");

  if (authJwt && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${authJwt}`);
  }
  if (csrfToken && !headers.has("X-CSRF-Token")) {
    headers.set("X-CSRF-Token", csrfToken);
  }

  return fetch(resource, { ...options, headers });
}

window.getCookieValue = getCookieValue;
window.csrfFetch = csrfFetch;
