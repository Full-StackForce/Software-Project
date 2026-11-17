"""Run in a fresh process: python -m unittest discover -s tests -v.

Replace the engine and session binding BEFORE importing the application. Only a
new temporary SQLite file is used; the configured MySQL connection is forbidden.
"""
import importlib
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text

from dependencies import database


def forbidden_connection():
    raise AssertionError("Tests must never connect to the configured database")


# Engine construction has no network side effects. Block its connection creator
# before application imports/startup, then rebind the existing session factory.
database.engine.pool._creator = forbidden_connection
TEST_DIRECTORY = tempfile.TemporaryDirectory(prefix="pulsepoint-auth-tests-")
TEST_ENGINE = create_engine(
    "sqlite:///" + str(Path(TEST_DIRECTORY.name) / "isolated.sqlite3"),
    connect_args={"check_same_thread": False},
)


@event.listens_for(TEST_ENGINE, "connect")
def enable_foreign_keys(connection, record):
    connection.execute("PRAGMA foreign_keys=ON")


database.engine = TEST_ENGINE
database.SessionLocal.configure(bind=TEST_ENGINE)
from main import app  # noqa: E402
from dependencies.migrations import ensure_auth_columns  # noqa: E402
from dependencies.security import COOKIE_NAME, hash_password, token_digest, verify_password  # noqa: E402
from models.auth_session import AuthSession  # noqa: E402
from models.user import User  # noqa: E402


HEADERS = {"X-PulsePoint-Request": "1"}
PASSWORD = "Fictional test password 42!"


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        assert TEST_ENGINE.dialect.name == "sqlite"
        assert Path(TEST_ENGINE.url.database).parent == Path(TEST_DIRECTORY.name)
        database.Base.metadata.drop_all(TEST_ENGINE)
        database.Base.metadata.create_all(TEST_ENGINE)
        importlib.import_module("controllers.goal_controller")._goals.clear()
        self.client = TestClient(app, headers=HEADERS)
        self.other = TestClient(app, headers=HEADERS)
        self.addCleanup(self.client.close)
        self.addCleanup(self.other.close)

    def signup(self, client=None, email="avery@example.com"):
        client = client or self.client
        response = client.post("/users/", json={"email": email, "password": PASSWORD, "name": "Avery Test"})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertNotIn("password", response.text)
        return response.json()["id"]

    def login(self, client=None, email="avery@example.com", password=PASSWORD):
        client = client or self.client
        response = client.post("/auth/login", json={"email": email, "password": password})
        self.assertEqual(response.status_code, 200, response.text)
        return response

    def two_users(self):
        first = self.signup()
        second = self.signup(self.other, "jordan@example.com")
        self.login()
        self.login(self.other, "jordan@example.com")
        return first, second

    def resources(self, owner_id):
        workout = self.client.post("/workouts/", json={"type": "Cardio", "duration_minutes": 30, "mood_level": 3})
        habit = self.client.post("/habits/", json={"name": "Read fiction", "frequency": "daily", "target_value": 1, "track_method": "checkbox"})
        goal = self.client.post("/goals/", json={"title": "Read regularly", "description": "Fictional goal", "goal_type": "habit_count", "target_value": 4})
        for response in (workout, habit, goal):
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.json()["user_id"], owner_id)
        return workout.json()["id"], habit.json()["id"], goal.json()["id"]

    def test_signup_hashes_and_duplicate_account(self):
        uid = self.signup()
        with database.SessionLocal() as db:
            user = db.get(User, uid)
            self.assertEqual(user.password_scheme, "argon2id")
            self.assertTrue(verify_password(user.password, PASSWORD, user.password_scheme))
            self.assertNotEqual(user.password, PASSWORD)
        response = self.client.post("/users/", json={"email": "avery@example.com", "password": PASSWORD})
        self.assertEqual(response.status_code, 409)

    def test_invalid_signup_and_validation_do_not_echo_passwords(self):
        for payload in [{"email": "invalid", "password": PASSWORD}, {"email": "a@example.com", "password": "short"}, {"email": "a@example.com"}]:
            with self.subTest(payload_keys=list(payload)):
                response = self.client.post("/users/", json=payload)
                self.assertEqual(response.status_code, 422)
                self.assertNotIn(PASSWORD, response.text)
                self.assertNotIn('"input"', response.text)
        with database.SessionLocal() as db:
            self.assertEqual(db.query(User).count(), 0)

    def test_login_cookie_correct_incorrect_and_unknown(self):
        uid = self.signup()
        for email, password in [("avery@example.com", "wrong"), ("missing@example.com", PASSWORD)]:
            response = self.client.post("/auth/login", json={"email": email, "password": password})
            self.assertEqual(response.status_code, 401)
            self.assertNotIn(COOKIE_NAME, self.client.cookies)
        response = self.login()
        cookie = response.headers["set-cookie"]
        self.assertIn("HttpOnly", cookie)
        self.assertIn("SameSite=strict", cookie)
        self.assertNotIn(PASSWORD, response.text)
        self.assertEqual(self.client.get("/auth/me").json()["user_id"], uid)
        token = self.client.cookies.get(COOKIE_NAME)
        with database.SessionLocal() as db:
            self.assertIsNotNone(db.get(AuthSession, token_digest(token)))
            self.assertIsNone(db.get(AuthSession, token))

    def test_legacy_password_upgrades_only_after_success_and_preserves_data(self):
        # A literal hash-looking legacy password must still be treated as text.
        legacy_password = "$argon2id$literal-old-password"
        with database.SessionLocal() as db:
            user = User(email="legacy@example.com", username="legacy", password=legacy_password, password_scheme="legacy_plaintext")
            db.add(user); db.commit(); uid = user.id
        response = self.client.post("/auth/login", json={"email": "legacy@example.com", "password": "wrong"})
        self.assertEqual(response.status_code, 401)
        with database.SessionLocal() as db:
            self.assertEqual(db.get(User, uid).password_scheme, "legacy_plaintext")
        self.login(email="legacy@example.com", password=legacy_password)
        with database.SessionLocal() as db:
            user = db.get(User, uid)
            self.assertEqual(user.password_scheme, "argon2id")
            self.assertTrue(verify_password(user.password, legacy_password, user.password_scheme))
        self.login(email="legacy@example.com", password=legacy_password)
        self.assertEqual(self.client.get("/auth/me").json()["user_id"], uid)

    def test_logout_revokes_replay_and_rotation_revokes_old_cookie(self):
        self.signup(); self.login()
        old_token = self.client.cookies.get(COOKIE_NAME)
        self.login()
        with TestClient(app, headers=HEADERS, cookies={COOKIE_NAME: old_token}) as replay:
            self.assertEqual(replay.get("/auth/me").status_code, 401)
        token = self.client.cookies.get(COOKIE_NAME)
        self.assertEqual(self.client.post("/auth/logout").status_code, 200)
        self.assertEqual(self.client.get("/auth/me").status_code, 401)
        with TestClient(app, headers=HEADERS, cookies={COOKIE_NAME: token}) as replay:
            self.assertEqual(replay.get("/auth/me").status_code, 401)
        self.assertEqual(self.client.post("/auth/logout").status_code, 200)

    def test_expired_and_forged_sessions(self):
        self.signup(); self.login()
        token = self.client.cookies.get(COOKIE_NAME)
        with database.SessionLocal() as db:
            db.get(AuthSession, token_digest(token)).expires_at = datetime.now(UTC).replace(tzinfo=None) - timedelta(seconds=1)
            db.commit()
        self.assertEqual(self.client.get("/auth/me").status_code, 401)
        self.client.cookies.clear(); self.client.cookies.set(COOKIE_NAME, "forged")
        self.assertEqual(self.client.get("/auth/me").status_code, 401)

    def test_personal_endpoints_require_authentication(self):
        paths = ["/auth/me", "/auth/me/1", "/users/", "/users/1", "/users/1/details", "/users/1/weight-logs", "/workouts/", "/workouts/1", "/workouts/user/1", "/habits/", "/habits/1", "/habits/user/1", "/goals/", "/goals/1", "/dashboard/", "/dashboard/user/1", "/challenges/", "/challenges/streaks/1", "/challenges/stats/1", "/challenges/weekly/1"]
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 401)
        for path, payload in [("/workouts/", {"type":"Cardio","duration_minutes":30,"mood_level":3}), ("/habits/", {"name":"Read","frequency":"daily","target_value":1}), ("/goals/", {"title":"Read","description":"Test","goal_type":"habit_count","target_value":1}), ("/users/1/weight-logs", {"weight_kg":70}), ("/habits/1/log", {"completed_today":True}), ("/challenges/1/complete/1", None), ("/challenges/weekly/1/progress/1?increment=1",None)]:
            with self.subTest(path=path):
                self.assertEqual(self.client.post(path, json=payload).status_code, 401)
        for path in ["/users/1", "/workouts/1", "/habits/1", "/goals/1"]:
            self.assertEqual(self.client.put(path, json={}).status_code, 401)
            self.assertEqual(self.client.delete(path).status_code, 401)

    def test_cross_user_reads_updates_deletes_are_denied(self):
        owner, other = self.two_users()
        wid, hid, gid = self.resources(owner)
        for path in [f"/workouts/{wid}", f"/habits/{hid}", f"/goals/{gid}", f"/users/{owner}"]:
            with self.subTest(path=path):
                self.assertEqual(self.other.get(path).status_code, 404)
                self.assertEqual(self.other.put(path, json={}).status_code, 404)
                self.assertEqual(self.other.delete(path).status_code, 404)
                self.assertEqual(self.client.get(path).status_code, 200)
        for path in [f"/auth/me/{owner}", f"/users/{owner}/details", f"/users/{owner}/weight-logs", f"/dashboard/user/{owner}", f"/workouts/user/{owner}", f"/habits/user/{owner}", f"/challenges/streaks/{owner}", f"/challenges/stats/{owner}", f"/challenges/weekly/{owner}"]:
            with self.subTest(path=path):
                self.assertEqual(self.other.get(path).status_code, 404)
        for path, payload in [(f"/habits/{hid}/log", {"completed_today":True}), (f"/users/{owner}/weight-logs", {"weight_kg":72}), (f"/challenges/1/complete/{owner}",None), (f"/challenges/weekly/1/progress/{owner}?increment=1",None)]:
            self.assertEqual(self.other.post(path, json=payload).status_code, 404)
        self.assertFalse(self.client.get(f"/habits/{hid}").json()["completed_today"])

    def test_create_ownership_comes_from_cookie_not_submitted_user_id(self):
        owner, other = self.two_users()
        for path, payload in [("/workouts/", {"type":"Cardio","duration_minutes":30,"mood_level":3}), ("/habits/", {"name":"Read","frequency":"daily","target_value":1}), ("/goals/", {"title":"Read","description":"Test","goal_type":"habit_count","target_value":1})]:
            response = self.client.post(path, json={**payload, "user_id":other})
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.json()["user_id"], owner)

    def test_collection_and_dashboard_are_user_scoped(self):
        owner, other = self.two_users(); self.resources(owner)
        for path in ["/workouts/", "/habits/", "/goals/"]:
            for client, uid in [(self.client,owner),(self.other,other)]:
                self.assertTrue(all(row["user_id"] == uid for row in client.get(path).json()))
        self.assertEqual(self.client.get("/dashboard/").json()["total_workouts"],1)
        self.assertEqual(self.other.get("/dashboard/").json()["total_workouts"],0)
        self.assertEqual([u["id"] for u in self.other.get("/users/").json()],[other])

    def test_owner_can_update_complete_and_delete_own_records(self):
        uid = self.signup(); self.login()
        wid, hid, gid = self.resources(uid)
        for path, payload, key, expected in [
            (f"/workouts/{wid}", {"duration_minutes":45}, "duration_minutes", 45),
            (f"/habits/{hid}", {"name":"Read a novel"}, "name", "Read a novel"),
            (f"/goals/{gid}", {"title":"A reading goal"}, "title", "A reading goal"),
        ]:
            response = self.client.put(path, json=payload)
            self.assertEqual(response.status_code,200,response.text)
            self.assertEqual(response.json()[key],expected)
        response = self.client.post(f"/habits/{hid}/log",json={"completed_today":True})
        self.assertEqual(response.status_code,200,response.text)
        self.assertTrue(response.json()["completed_today"])
        response = self.client.post(f"/users/{uid}/weight-logs",json={"weight_kg":72})
        self.assertEqual(response.status_code,200,response.text)
        for path in [f"/workouts/{wid}",f"/habits/{hid}",f"/goals/{gid}"]:
            self.assertEqual(self.client.delete(path).status_code,200)
            self.assertEqual(self.client.get(path).status_code,404)

    def test_hash_cannot_be_used_as_password_and_secrets_never_leave_responses(self):
        uid = self.signup()
        with database.SessionLocal() as db:
            stored_hash = db.get(User,uid).password
        response = self.client.post("/auth/login",json={"email":"avery@example.com","password":stored_hash})
        self.assertEqual(response.status_code,401)
        self.login(); self.resources(uid)
        for path in ["/auth/me","/users/",f"/users/{uid}",f"/users/{uid}/details","/workouts/","/habits/","/goals/","/dashboard/"]:
            response = self.client.get(path)
            self.assertEqual(response.status_code,200,response.text)
            self.assertNotIn(PASSWORD,response.text)
            self.assertNotIn(stored_hash,response.text)
            self.assertNotIn('"password"',response.text)

    def test_password_change_hashes_and_revokes_all_sessions(self):
        uid = self.signup(); self.login()
        self.login(self.other)
        response = self.client.put(f"/users/{uid}",json={"password":"Another fictional password!"})
        self.assertEqual(response.status_code,200,response.text)
        self.assertNotIn("password",response.text)
        for client in [self.client,self.other]:
            self.assertEqual(client.get("/auth/me").status_code,401)
        self.login(password="Another fictional password!")
        self.assertEqual(self.client.get(f"/users/{uid}/details?fields=password").status_code,400)
        self.assertEqual(self.client.get(f"/users/{uid}/details?fields=password_scheme").status_code,400)

    def test_csrf_protection_and_private_cache(self):
        response = TestClient(app).post("/auth/login",json={"email":"a@example.com","password":PASSWORD})
        self.assertEqual(response.status_code,403)
        for origin in ["https://example.org","http://testserver:9999","null"]:
            response = self.client.post("/users/",json={"email":"a@example.com","password":PASSWORD},headers={"Origin":origin})
            self.assertEqual(response.status_code,403)
        self.signup(); self.login()
        self.assertEqual(self.client.get("/auth/me").headers["cache-control"],"no-store")

    def test_https_cookie_is_secure(self):
        self.signup()
        with TestClient(app,base_url="https://testserver",headers=HEADERS) as client:
            self.assertIn("Secure",self.login(client).headers["set-cookie"])

    def test_additive_migration_is_repeatable_and_preserves_legacy(self):
        # Completely separate old-schema fixture, not the app/test database.
        legacy_engine = create_engine("sqlite://")
        with legacy_engine.begin() as conn:
            conn.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, password VARCHAR(255) NOT NULL)"))
            conn.execute(text("INSERT INTO users VALUES (1, 'fictional legacy secret')"))
        ensure_auth_columns(legacy_engine); ensure_auth_columns(legacy_engine)
        with legacy_engine.connect() as conn:
            self.assertEqual(conn.execute(text("SELECT password, password_scheme FROM users")).one(), ("fictional legacy secret","legacy_plaintext"))
        legacy_engine.dispose()


if __name__ == "__main__":
    unittest.main()
