from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from dependencies.database import Base


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    # Only a digest is stored; a database read does not reveal the cookie token.
    token_hash = Column(String(64), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
