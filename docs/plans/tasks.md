ROI-Sorted Refactor Backlog
1. Fix create-workout flow end-to-end.
   Impact: very high. Effort: low-medium.
   Evidence: frontend fallback posts to non-existent /workouts/by_date in static/js/add_workout.js:17; config.js uses /workouts in static/js/config.js:4; backend route is POST /workouts in src/gym_tracker/entrypoints/workouts.py:31; service always returns {"id": 1} in src/gym_tracker/services/workouts_services.py:45.
   Tasks: align endpoint config, return real inserted workout id, pass date/duration from UI/body, add API test for create workout.
2. Repair stale/broken tests and establish a minimum test baseline.
   Impact: very high. Effort: low.
   Evidence: Workout requires duration in src/gym_tracker/domain/model.py:106, but tests instantiate Workout(exercises=[]) in tests/unit/test_workout_domain.py:43; only four domain tests exist.
   Tasks: update current tests, add mapper tests, add FastAPI route tests with dependency overrides, add repository tests around create/read paths.
3. Simplify PostgresSQLRepo.add_workout.
   Impact: very high. Effort: medium.
   Evidence: add_workout returns at src/gym_tracker/adapters/repositories.py:124, making the raw SQL implementation below unreachable at repositories.py:131; method is annotated -> int but returns None; sets are never inserted in the active SQLAlchemy branch.
   Tasks: make one implementation path, insert workout/full exercises/sets in one transaction, return inserted id, remove unreachable block, add regression test.
4. Standardize database access on one style per path, preferably SQLAlchemy for app code.
   Impact: high. Effort: medium-high.
   Evidence: repo mixes global psycopg connection and SQLAlchemy session in src/gym_tracker/adapters/repositories.py:49; dependencies create both in src/gym_tracker/entrypoints/dependencies.py:13.
   Tasks: remove global shared psycopg client from request path, use request-scoped SQLAlchemy session, keep raw SQL only for admin/import scripts if needed, define repository interface boundaries.
5. Fix transaction/session handling.
   Impact: high. Effort: medium.
   Evidence: with self.session.begin() is combined with manual commit() and rollback() in src/gym_tracker/adapters/repositories.py:101-128; dependency uses a global psycopg.connect(..., autocommit=True) in dependencies.py:13.
   Tasks: let context manager commit/rollback, avoid swallowing exceptions, remove autocommit for write transactions, surface meaningful errors.
6. Move configuration out of hard-coded constants.
   Impact: high. Effort: low-medium.
   Evidence: DB credentials and host are hard-coded in src/gym_tracker/entrypoints/dependencies.py:10-11; scraper contains a large cookie constant in src/gym_tracker/exercise_ingestor/extractor.py:13.
   Tasks: add settings object using env vars, update Docker/local defaults, remove committed cookie/session data, document required env vars.
7. Add integration coverage for the repository and API.
   Impact: high. Effort: medium.
   Evidence: no tests cover src/gym_tracker/adapters/repositories.py, src/gym_tracker/entrypoints/workouts.py, or src/gym_tracker/entrypoints/search.py.
   Tasks: use test DB or dependency-overridden fake repo, cover create/read/search/list paths, verify error status codes, verify data shape.
8. Normalize domain model duplication.
   Impact: medium-high. Effort: medium-high.
   Evidence: legacy dataclass domain lives in src/gym_tracker/domain/model.py; ORM models live in src/gym_tracker/domain/models/; mappers bridge both in src/gym_tracker/adapters/mappers.py.
   Tasks: decide whether dataclasses remain as pure domain objects or DTOs replace them; remove unused overlap; ensure API, repository, and tests use clear types.
9. Fix data mapping bugs and naming inconsistencies.
   Impact: medium-high. Effort: low-medium.
   Evidence: frontend sends weights in static/js/add_workout.js:191, while DTO/domain use weight; mapper parses arbitrary dotted keys in src/gym_tracker/adapters/mappers.py:84; series is parsed but unused; checkbox absence may omit to_failure.
   Tasks: define explicit create-workout request schema, stop encoding structure into input names, validate set fields with Pydantic, normalize weight naming.
10. Improve search performance and result shape.
   Impact: medium. Effort: low-medium.
   Evidence: query uses ILIKE '%term%' in src/gym_tracker/adapters/repositories.py:309-312; results are returned as {id: name} dicts and sorted in Python in src/gym_tracker/entrypoints/search.py:17.
   Tasks: return [{id, name}], order in SQL, add index strategy such as trigram index for substring search or prefix search if acceptable.
11. Add DB indexes and constraints.
   Impact: medium. Effort: low-medium.
   Evidence: migration creates foreign keys but no indexes on workout_id, metadata_id, full_exercise_id, or workouts.date in alembic/versions/20260118_120000_baseline_schema.py.
   Tasks: add indexes for common joins/filters, consider unique constraints for one workout per date only if product behavior requires it, add cascade rules deliberately.
12. Clean up API layering.
   Impact: medium. Effort: medium.
   Evidence: service functions use FastAPI Depends directly in src/gym_tracker/services/workouts_services.py:18, coupling service layer to web framework; services return JSONResponse in workouts_services.py:42.
   Tasks: keep dependency injection in entrypoints, make services framework-agnostic, return domain/DTO values, let routes choose status codes.
13. Improve error handling and observability.
   Impact: medium. Effort: low.
   Evidence: repository logs and returns None on exceptions in src/gym_tracker/adapters/repositories.py:125-128; logging.basicConfig is called inside modules in repositories.py:39 and extractor.py:16.
   Tasks: remove module-level logging config, raise domain-specific exceptions, add request-safe error responses, add structured logs around DB operations.
14. Separate ingestion/admin scripts from runtime app.
   Impact: medium. Effort: medium.
   Evidence: src/gym_tracker/exercise_ingestor/transformer.py:4 imports runtime dependencies and global DB client; extractor.py writes temp_db.csv directly.
   Tasks: create CLI/script entrypoints, inject DB settings, isolate scraper dependencies, add parser tests for sample HTML/CSV.
15. Frontend cleanup after backend contract is stable.
   Impact: medium. Effort: medium.
   Evidence: duplicated endpoint defaults in static/js/config.js and static/js/add_workout.js; inline CSS in templates/read_workouts.html; possible double slash in read_workouts.js:41 if endpoint ends with /.
   Tasks: centralize endpoint config, remove hard-coded localhost fallbacks, move inline styles into CSS, add basic browser/manual smoke checklist.