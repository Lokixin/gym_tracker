# Frontend User Auth Tasks

## Goal

Add self-registration and login screens, keep JWTs out of JavaScript, and make workout pages operate only for the authenticated user.

## Tasks

1. Add auth templates
   - Add `templates/login.html`.
   - Add `templates/register.html`.
   - Keep visual style consistent with existing workout pages.
   - Include clear validation and error display regions.

2. Add app routes for auth pages
   - Add `GET /app/login`.
   - Add `GET /app/register`.
   - Redirect already-authenticated users to `/app/workouts/list`.

3. Protect app workout views
   - Require authentication for `/app/workouts/list`.
   - Require authentication for `/app/workouts/add`.
   - Redirect unauthenticated users to `/app/login`.
   - Continue server-rendering the user's workout list if cookies are available server-side.

4. Add login JavaScript
   - Submit credentials to `POST /auth/token` as `application/x-www-form-urlencoded`.
   - Use email as the OAuth2 `username` field.
   - Do not store JWTs in `localStorage`, `sessionStorage`, or JS memory.
   - Rely on the backend's `HttpOnly` auth cookie.
   - Redirect to `/app/workouts/list` after successful login.
   - Show generic errors for failed login.

5. Add registration JavaScript
   - Submit email and password to `POST /auth/register`.
   - Do not store JWTs in frontend-accessible storage.
   - Rely on backend-set auth and CSRF cookies.
   - Redirect to `/app/workouts/list` after successful registration.
   - Show safe validation errors for duplicate or invalid registration attempts.

6. Add logout UI and behavior
   - Add logout control to authenticated pages.
   - Submit `POST /auth/logout`.
   - Include CSRF header on logout.
   - Redirect to `/app/login` after successful logout.

7. Add CSRF helper
   - Add a helper to read the non-HttpOnly `csrf_token` cookie.
   - Add `X-CSRF-Token` to unsafe requests.
   - Use the helper for `POST /workouts` and `POST /auth/logout`.
   - Keep JWT cookie unreadable by frontend code.

8. Add authenticated fetch helper
   - Wrap `fetch` for same-origin API calls.
   - Redirect to `/app/login` on `401`.
   - Include CSRF token automatically for unsafe methods.
   - Keep GET requests simple and cache-safe.

9. Update add workout page
   - Update `static/js/add_workout.js` to use authenticated fetch.
   - Include CSRF token for `POST /workouts`.
   - Redirect to login if the user is unauthenticated.
   - Keep current workout form behavior unchanged otherwise.

10. Update read workouts page
    - Ensure `static/js/read_workouts.js` handles `401` by redirecting to login.
    - Keep workout-by-id fetches same-origin so cookies are sent automatically.
    - If the backend adds `GET /workouts`, populate the workout dropdown client-side from that endpoint.

11. Update shared frontend config
    - Add auth endpoint constants in `static/js/config.js`.
    - Add or reference shared helper script before page-specific scripts.
    - Keep endpoint defaults relative for same-origin deployment.

12. Update templates for authenticated pages
    - Add logout control to `read_workouts.html`.
    - Add logout control to `add_workouts.html`.
    - Optionally display the current user's email if provided by the backend.
    - Ensure pages remain usable on mobile and desktop.

13. Add frontend-facing tests
    - Test login page renders.
    - Test registration page renders.
    - Test unauthenticated app pages redirect to login.
    - Test authenticated app pages render.
    - Test workout list only contains current user's workouts when server-rendered.

14. Manual verification
    - Visit `/app/register` and create an account.
    - Confirm redirect to `/app/workouts/list`.
    - Create a workout.
    - Confirm the workout appears in the list.
    - Log out.
    - Confirm protected pages redirect to login.
    - Log in again.
    - Confirm only that user's workouts are visible.
