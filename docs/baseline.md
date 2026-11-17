# Step 1: local baseline

Baseline recorded November 17, 2026, before portfolio implementation changes.

## Scope and environment

- No `AGENTS.md` found in the project, its subdirectories outside `.venv`/`.git`, or its ancestor directories.
- Existing working changes preserved: `.gitignore`, `dependencies/config.py`, and untracked `.env.example`.
- No application code, dependencies, configuration, or existing user records changed for this baseline. No commits or pushes.
- Started the installed application with `.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000`, using the existing local MySQL configuration without printing credentials.
- Sandbox initially blocked localhost binding and database access. The server started successfully with local execution permission. This was an environment restriction, not an application defect.
- Used the installed Chrome in headless mode with a separate temporary profile and a local Python script using the installed `websockets` package. No paid services or additional packages used.
- Browser page requests outside `http://127.0.0.1:8000` were intercepted and blocked during signup, login, home, workout-save, and dashboard checks. External styling/chart dependencies were therefore unavailable; this run does not establish visual fidelity or responsive-layout quality.
- Added only fictional accounts and their generated records. They were retained rather than deleted. Broader tests requiring invalid writes or record mutations belong in an isolated database in Step 4.

## Observed results

| Check | Actual result |
| --- | --- |
| Application startup | Passed after local execution permission; local pages and API served successfully. |
| Signup through browser | Passed through the four-step interface; redirected to `/login`. |
| Login through browser | Passed; redirected to `/home` and stored a user ID locally. |
| Home data loading | Failed; zero loaded habits and workouts, and “Unable to connect to backend.” Requests targeted the expired external domain. |
| Workout creation through browser | Failed; “Failed to log workout.” No workout appeared in the local API afterward. |
| Habit checklist completion through browser | Blocked by failed habit loading; not verified end to end. |
| Dashboard page | HTML loaded, but data loading failed with “Unable to load dashboard right now.” Requests targeted the expired external domain. |
| Workout creation through local API | Passed, HTTP 200; saved a 30-minute Cardio workout with 195 calories. |
| Default habits through local API | Passed; hydration, sleep, and workout habits returned. |
| Custom daily checkbox habit through API | Creation and completion passed; HTTP 200, `completed_today=true`, `current_value=1`. |
| Persistence after browser refresh | Separate local API reads still returned the workout and completed habit. UI display remained blocked by the external API URL. |
| Persistence after another login | Another local API login returned HTTP 200; subsequent reads still returned the workout and completed habit. This was an API login, not a completed second browser login. |
| Logout through browser | Automation reached the confirmation dialog and timed out. Successful end-to-end logout was not verified. Source also shows an external login redirect and no server session invalidation. |
| Second fictional account | API signup and login both returned HTTP 200. |
| Dashboard API calculations | HTTP 200: one workout, two active habits, zero completed goals, one login day, hydration/sleep 0%, workout 25%. One saved workout divided by four target sessions agrees with 25%. Two active habits are the workout habit and completed checkbox habit under the current calculation. |
| Unauthenticated personal-record access | Separate requests with no cookie or token returned HTTP 200 for the fictional account's profile, workout, and habit. |
| Password storage | A comparison restricted to the fictional account confirmed its database password exactly matched the submitted password. No password values were printed or included here. |
| Signup draft storage | Browser check confirmed `localStorage.pulsePassword` existed while progressing through signup. No stored value was printed. |

## Actual failures and confirmed findings

### B1: local frontend uses expired API origin

- **Symptom:** Home cannot load records; workout save fails; dashboard shows an unavailable message.
- **Reproduction:** Start locally, create a fictional account, sign in, try logging a workout, and open `/dashboard`.
- **Evidence:** Browser attempted `https://pulsepointtrain.com/auth/me/1`, `/habits/user/1`, `/workouts/user/1`, `/dashboard/user/1`, and a workout-save preflight to `/workouts/`. Requests were blocked locally rather than sent to that host. No DNS or remote availability claim is made.
- **Cause established from source:** `frontend/js/app-common.js` hardcodes `API_BASE` to the external origin. Home and dashboard use that constant. `frontend/js/home.js` also directs logout to that origin.
- **Fix/verification:** Pending; no code changed in Step 1. The successful local API save and reads distinguish this failure from a demonstrated database persistence failure.

### B2: passwords are stored directly

- **Symptom:** The fictional account's stored password equals its input password; signup also retains the draft in persistent browser storage.
- **Reproduction:** Progress past the signup identity step and check only whether the draft storage key exists. After signup, compare only that fictional user's stored password to the supplied input without printing either value.
- **Cause established from source:** `controllers/user_controller.py` assigns `payload.password` directly, `routers/auth.py` uses direct equality, and `frontend/accounts.html` includes the password in its persisted profile map.
- **Fix/verification:** Pending Step 2, including a safe transition for existing accounts. No accounts were invalidated or migrated in Step 1.

### B3: personal records require no server authentication

- **Symptom:** Profile, workout, and habit requests succeed without a session or token.
- **Reproduction:** Send fresh unauthenticated GET requests to `/users/1`, `/workouts/1`, and `/habits/4`, using only this baseline's fictional IDs.
- **Evidence:** All returned HTTP 200. Logging in as a second fictional account supplies no access boundary; the same fresh unauthenticated workout request still succeeds.
- **Cause established from source:** These routes have no authentication dependency. Login returns user details, while frontend gating trusts a locally stored user ID.
- **Fix/verification:** Pending Step 2. Cross-user update/delete checks have not been performed against the existing database and must not be reported as passing.

## Retained fictional fixtures

- Avery Baseline: `portfolio.baseline.b266971b@example.com`, user ID 1.
- Jordan Baseline: `portfolio.baseline.8fd1f9a4@example.com`, user ID 2.
- API workout ID 1, owned by Avery; notes `Fictional baseline API workout`.
- Completed daily checkbox habit ID 4, owned by Avery; name `Baseline stretch b266971b`.
- Signup/login and habit loading also created their normal weight baseline, login activity, and default habit records. These are fictional fixture data, not pre-existing user data.
- Random fictional passwords are intentionally omitted.

## Limits and next step

This is a baseline investigation, not the isolated regression suite requested in Step 4. Daily rollover across dates, invalid inputs, atomicity, complete workout CRUD, cross-user mutations, mobile layout, and accessibility remain unverified. Browser screenshots of the failed home/dashboard states were captured temporarily, with external dependencies blocked; they are not portfolio screenshots.

Step 2 should implement password hashing with an explicit legacy-account transition, authenticated sessions/logout, ownership checks across personal-data routes, and compatible frontend authentication. Recheck browser flows once they use the local API. Keep these observed failures as regression targets rather than inventing incidents or metrics.
