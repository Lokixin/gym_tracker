# Backend User Auth Tasks

## Goal

Add self-registration and secure authentication so every workout belongs to one user, and users can only access their own workouts.

## Tasks

1. Add auth dependencies
   - Add `pyjwt`.
   - Add `pwdlib[argon2]`.
   - Add `python-multipart` for `OAuth2PasswordRequestForm`.

2. Add auth settings
   - Add `JWT_SECRET_KEY`.
   - Add `JWT_ALGORITHM`, defaulting to `HS256`.
   - Add `ACCESS_TOKEN_EXPIRE_MINUTES`.
   - Add auth cookie settings: name, `Secure`, `SameSite`, path.
   - Add CSRF cookie settings: name, `Secure`, `SameSite`, path.

3. Add user model
   - Create `User` SQLAlchemy model.
   - Include `id`, `email`, `password_hash`, `created_at`, and `is_active`.
   - Enforce unique normalized email.
   - Add `User.workouts` relationship.
   - Add `Workout.user_id` and `Workout.user` relationship.

4. Add database migration
   - Create `users` table.
   - Add non-null `workouts.user_id` foreign key to `users.id`.
   - Add indexes for `users.email`, `workouts.user_id`, and `(workouts.user_id, workouts.date)`.
   - Do not add default-user backfill because there is no live database.

5. Add auth DTOs
   - Add registration request DTO.
   - Add token response DTO.
   - Add user response DTO.
   - Add token data DTO for JWT validation internals.

6. Add user persistence methods
   - Add `get_user_by_email`.
   - Add `get_user_by_id`.
   - Add `create_user`.
   - Map duplicate email failures to safe application errors.

7. Add auth service
   - Normalize email before persistence and login.
   - Hash passwords with `PasswordHash.recommended()`.
   - Verify passwords with a dummy hash when email does not exist.
   - Authenticate users with generic login failures.
   - Create JWTs with `sub = str(user.id)` and `exp`.
   - Decode and validate JWTs.

8. Add auth dependencies
   - Configure `OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)`.
   - Implement current-user dependency that accepts `Authorization: Bearer <token>`.
   - Add fallback support for the `HttpOnly` auth cookie.
   - Prefer Bearer header over cookie when both are present.
   - Return `401` with `WWW-Authenticate: Bearer` for invalid credentials.

9. Add CSRF protection
   - Set readable `csrf_token` cookie on login and registration.
   - Require `X-CSRF-Token` for unsafe cookie-authenticated requests.
   - Verify header value equals CSRF cookie value.
   - Do not require CSRF when authentication uses Bearer header only.

10. Add auth routes
    - Add `POST /auth/register`.
    - Add `POST /auth/token` using `OAuth2PasswordRequestForm`.
    - Add `POST /auth/logout`.
    - Add `GET /auth/me`.
    - Set auth and CSRF cookies for browser login/register.
    - Clear auth and CSRF cookies on logout.

11. Scope workout repository methods
    - Change `add_workout` to require `user_id`.
    - Change `get_workout_by_id` to require `user_id`.
    - Change `get_workout_by_date` to require `user_id`.
    - Change `get_existing_workouts_dates` to require `user_id`.
    - Ensure cross-user workout reads return `None` and become `404`.

12. Scope workout services and API routes
    - Inject current user into workout API routes.
    - Pass `current_user.id` into services and repository calls.
    - Keep unauthenticated workout API responses as `401`.
    - Keep cross-user workout reads as `404`.

13. Add optional workout list API
    - Add `GET /workouts` returning current user's workout dates.
    - Use this only if frontend needs client-side loading instead of server-rendered list data.

14. Update tests
    - Add user fixtures.
    - Add authenticated client fixtures for cookie and Bearer auth.
    - Test registration success and duplicate registration failure.
    - Test login success and generic login failure.
    - Test invalid and expired JWT handling.
    - Test cookie auth and Bearer auth.
    - Test logout clears cookies.
    - Test CSRF enforcement for cookie-authenticated unsafe requests.
    - Test CSRF is not required for Bearer-authenticated unsafe requests.
    - Test workout creation and reads are user-scoped.
    - Update existing workout API/repository tests to include users.

15. Verify backend
    - Run `poetry install`.
    - Run `poetry run pytest tests/unit tests/integration`.
    - Run `poetry run ruff check src tests`.
    - Run `poetry run mypy src tests`.
