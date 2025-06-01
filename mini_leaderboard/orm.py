import uuid

from sqlalchemy import Column, DateTime, Integer, Text, UniqueConstraint, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base  # noqa: F811

Base = declarative_base()


class Leaderboard(Base):
    __tablename__ = "leaderboard"

    id_ = Column(Integer, autoincrement=True, primary_key=True)

    leaderboard_id = Column(
        Text,
        nullable=False,
        index=True,
        default=lambda: uuid.uuid4().hex,
        unique=True,
    )
    project_id = Column(Text)
    name = Column(Text)
    score = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class MessageBoard(Base):
    __tablename__ = "messageboard"

    id_ = Column(Integer, autoincrement=True, primary_key=True)

    message_id = Column(
        Text,
        nullable=False,
        index=True,
        default=lambda: uuid.uuid4().hex,
        unique=True,
    )
    project_id = Column(Text)
    name = Column(Text)
    message = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Form(Base):
    __tablename__ = "form"

    id_ = Column(Integer, autoincrement=True, primary_key=True)
    project_id = Column(Text)

    # username, email, project link and social post link
    username = Column(Text, nullable=True)
    email = Column(Text, nullable=True)
    project_link = Column(Text, nullable=True)
    social_post_link = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Vote(Base):
    __tablename__ = "vote"

    id_ = Column(Integer, autoincrement=True, primary_key=True)
    project_id = Column(Text, nullable=False, index=True)
    item_id = Column(Text, nullable=False, index=True)
    vote_count = Column(Integer, default=1)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Composite unique constraint to ensure one vote record per project_id + item_id combination
    __table_args__ = (UniqueConstraint("project_id", "item_id", name="uix_project_item"),)
