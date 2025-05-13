import uuid

from sqlalchemy import Column, DateTime, Integer, Text, func
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
    __tablename__ = "message_board"

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
