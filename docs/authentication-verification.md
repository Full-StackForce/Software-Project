# Step 2 verification record

Verified November 17, 2026. See [authentication design and transition](authentication.md) for implementation details and commands.

## Automated checks

- `.venv/bin/python -m unittest discover -s tests -v`: **16 tests passed** in the final run, against a fresh temporary SQLite database with foreign keys enabled. The configured MySQL engine's connection creator is blocked before importing the app.
- `.venv/bin/python -m pip check`: **No broken requirements found**.
- Node syntax checks: shared client, home JavaScript, and extracted inline scripts for signup, login, dashboard, and challenges passed.
- Python compilation checks passed.

The test run emits two compatibility/deprecation warnings: the installed Starlette recommends a different future test client transport (`httpx2`), and the existing workout controller uses `datetime.utcnow()`. Neither prevented the tests from passing; they are retained as compatibility work for the later steps. New session timestamps use explicit UTC converted to the naive UTC representation used by the database column.

## Local MySQL and browser checks

Used installed headless Chrome with a separate temporary profile. All application API traffic stayed on `http://127.0.0.1:8000`; requests to the expired domain were intercepted, and none were attempted. Existing public Tailwind, font, and Chart.js assets were allowed to load; these have not yet been bundled locally.

| Check | Result |
| --- | --- |
| Existing fictional baseline account login | Passed through the browser; scheme changed from `legacy_plaintext` to `argon2id`. |
| Preserve baseline records through upgrade | Browser still loaded the original workout and completed custom habit. |
| Legacy-account logout | Redirected to local `/login`; cached user ID cleared. |
| New four-step signup | Passed and redirected to local login. |
| Persistent password draft | `pulsePassword` absent after moving past the identity step. |
| New account login | Passed; session cookie not readable through `document.cookie`. |
| Workout creation | Browser saved one workout and showed a success notification. |
| Custom checkbox habit | Browser created and completed the fictional habit. |
| Persistence after refresh | Browser reloaded the workout and completed checkbox habit. |
| Dashboard | Displayed “Welcome back, Morgan Auth Test.” and one workout; Chart.js loaded. |
| Challenges screen | Loaded the authenticated user's display name. No challenge completions were written in this smoke check. |
| Logout | Server logout completed; redirected to local login, cached ID cleared, `/auth/me` returned 401. |
| Forged localStorage ID | Navigating to home redirected back to login without an authenticated cookie. |
| Login again | Browser reloaded the saved workout and completed checkbox habit. |

The browser run also captured a pre-existing `ReferenceError: tailwind is not defined` in `frontend/js/home-tailwind.js`. The page loads that configuration script before the Tailwind CDN script. Record this for Step 5; this run verifies the listed functional flows, not complete visual correctness.

## Data and working-tree preservation

- Earlier working changes to `.gitignore`, `dependencies/config.py`, and `.env.example` were preserved.
- No commits or pushes. No credentials printed, existing user data deleted, or paid service introduced.
- The schema upgrade added the password scheme flag and session table. The Step 1 fictional account was upgraded through normal login, retaining its records.
- One additional fictional browser account was retained: Morgan Auth Test, `portfolio.auth.9ba2f984@example.com`, user ID 3. It has the normal signup/login records, one workout with notes `Fictional Step 2 browser workout`, and a completed custom habit named `Fictional Step 2 stretch`.
- Both browser smoke-check sessions were logged out. Automated tests use and reset only their isolated temporary database.
- Screenshots and browser automation scripts are temporary local artifacts, not portfolio screenshots or a replacement for the repository tests.

Cross-user mutation checks were performed only in the isolated test database. Broader daily-reset, partial-failure, persistence, and dashboard edge-case regression work remains in Steps 3–4.
