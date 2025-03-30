""" Database models """

# External libraries
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Local imports
from src.models.base import Base, SerializerMixin


# Users table
class Users(Base, SerializerMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime)

    sessions = relationship("Sessions", back_populates="users")


# Sessions table
class Sessions(Base, SerializerMixin):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    label = Column(String, nullable=False)
    url = Column(String, nullable=False)
    url_hash = Column(String, nullable=False)
    session_id = Column(String)
    fk_users_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime)

    users = relationship("Users", back_populates="sessions")
