# Step 2: authentication and record ownership

Implemented November 17, 2026, after the failures recorded in [the baseline](baseline.md). These changes are portfolio improvements built on the team's existing application and frontend, not claims about original authorship. Team credits remain unchanged.

## Changes and reasons

- **Password storage:** `argon2-cffi==25.1.0` hashes new and changed passwords with Argon2id. Verification uses the library; successful logins rehash when parameters need updating. Password changes revoke all sessions for that account. Account creation and its initial weight log now share one commit.
- **Existing accounts:** A separate `users.password_scheme` flag distinguishes legacy plaintext from hashes. A legacy account can still sign in with its unchanged password; successful login replaces that value with an Argon2id hash and marks the scheme. Wrong passwords do not migrate the account. This also handles an old plaintext password that happens to look like a hash. Account IDs, profile fields, workouts, and habits are retained.
- **Sessions:** Login issues a random 32-byte opaque token in an HttpOnly, SameSite=Strict cookie. The database stores only its SHA-256 digest, user ID, and 24-hour expiration. HTTPS uses a Secure cookie; local HTTP remains usable. Login rotates the presenting session token. Logout removes the database session and clears the cookie, so replay fails. Other devices remain signed in unless the password changes.
- **Request protection:** Mutating requests require `X-PulsePoint-Request: 1`. The browser wrapper supplies it. Cross-origin changes and `Sec-Fetch-Site: cross-site` are rejected, and wildcard credentialed CORS was removed. Personal responses use `Cache-Control: no-store`.
- **Ownership:** Workouts, habits, goals, profiles, weight logs, dashboard data, and personal challenge operations require a valid session. Lists return only the signed-in user's data. Legacy path IDs must match the session user, and record IDs must belong to that user. Another user's record returns 404. Create requests derive ownership from the session; a submitted `user_id` is ignored and is optional for compatibility.
- **Responses:** Existing response field allowlists exclude passwords, hashes, schemes, and session digests. Validation responses omit Pydantic input/context, which can otherwise contain submitted credentials.
- **Frontend:** The shared API client uses the current local origin, sends session cookies and request protection headers, and redirects expired sessions to local login. Protected screens check `/auth/me` rather than trusting localStorage. User display fields may still be cached locally, but cannot grant access. Both logout buttons now call the server. Signup keeps its password draft in memory and removes only the old `pulsePassword` key; unrelated browser data is preserved.

The hashing implementation follows the library's [verification and rehashing API](https://argon2-cffi.readthedocs.io/en/stable/api.html).

## Additive schema transition

The existing startup schema initializer now runs the inspected, repeatable `ensure_auth_columns()` migration from `dependencies/migrations.py` and creates `auth_sessions` through SQLAlchemy metadata.

For an existing `users` table missing the flag, the migration executes:

```sql
ALTER TABLE users ADD COLUMN password_scheme VARCHAR(30)
NOT NULL DEFAULT 'legacy_plaintext';
```

It checks for the column first, so repeated startup does not repeat the alteration. Newly created ORM accounts explicitly use `argon2id`. The new `auth_sessions` table contains `token_hash`, `user_id` (foreign key to users), and `expires_at`, with indexes on user and expiration. There are no destructive table changes or password-column resizing requirements.

This migration was applied to the local MySQL database when restarting the application. The earlier fictional account's next login upgraded its password, and browser checks confirmed its saved workout and completed habit remained. No real account password was read for testing. Inactive legacy accounts still retain their old storage until their next successful login; this is a deliberate transition limitation, not a completed bulk password migration. Do not remove legacy verification before those accounts have migrated or an explicit reset process is available.

Do not roll back only the application code after hashes have been written: the old plaintext comparator cannot authenticate hashed accounts. Preserve a secure database backup through the user's normal backup process before a deployment migration; no backup containing credentials was created in the repository.

## Local startup and API usage

From the repository root, with the existing `.env` and local MySQL database:

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/`. Use the same hostname throughout a session; browser cookies for `localhost` and `127.0.0.1` are separate.

- `POST /users/`: public signup, with the request protection header.
- `POST /auth/login`: email/password JSON, with the header; sets the session cookie.
- `GET /auth/me`: current authenticated user.
- `POST /auth/logout`: revoke the presenting session, with the header; safe to repeat.
- Personal APIs: send the cookie; send the header on POST/PUT/DELETE. Command-line clients must retain the login cookie and supply the header too. No API token belongs in localStorage.

## Verification

Install test-only dependencies and run in a fresh process:

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
```

The suite replaces the engine and rebinds the session factory **before** importing the application. It blocks connections from the configured engine and uses a newly created temporary SQLite file, with foreign keys enabled. Schema resets affect only that temporary file. It never uses the existing MySQL database.

Coverage includes valid/invalid/duplicate signup, correct/incorrect/unknown login, explicit legacy transition, hash-as-password rejection, cookie attributes, token digest storage, token rotation, expiration, forged sessions, logout replay, password-change revocation, unauthenticated personal APIs, cross-user reads/updates/deletes, forged ownership, scoped collections/dashboard totals, allowed owner operations, response secrecy, request protection, and repeatable migration.

The final test result and browser findings are recorded in [the Step 2 verification record](authentication-verification.md). This focused authentication suite starts the testing work; the broader persistence, validation, reset, and calculation suite in Step 4 remains pending.

## Remaining scope

- Step 3 still needs transaction and validation work across existing controllers, daily/weekly habit semantics, and goal persistence. Goals currently remain in process memory; authentication does not make them durable.
- Browser layout/accessibility, local bundling of external assets, and loading/error polish remain in Steps 5–6. A pre-existing `home-tailwind.js` initialization error was observed during this browser run.
- No email password reset, public deployment hardening, or login rate limiting has been added. Sessions expire absolutely after 24 hours; expired rows are rejected but not yet purged automatically.
- Local HTTP is for local use. Any future hosted deployment needs HTTPS and explicit host/proxy configuration; no hosting or paid service was introduced.
