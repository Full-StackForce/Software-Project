"""Additive schema upgrades. Existing passwords and records are preserved."""
from sqlalchemy import inspect, text


def ensure_auth_columns(engine) -> None:
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "password_scheme" not in columns:
        with engine.begin() as connection:
            connection.execute(text(
                "ALTER TABLE users ADD COLUMN password_scheme VARCHAR(30) "
                "NOT NULL DEFAULT 'legacy_plaintext'"
            ))
