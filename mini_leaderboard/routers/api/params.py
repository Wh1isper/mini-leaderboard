from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class OneLeaderboard(BaseModel):
    """Schema for a single leaderboard entry"""

    leaderboard_id: str = Field(..., description="Unique identifier for the leaderboard entry")
    name: str = Field(..., description="Name of the player or entity")
    score: int = Field(..., description="Score value for the leaderboard entry")
    created_at: datetime = Field(..., description="Datetime when the entry was created")


class LeaderboardResponse(BaseModel):
    """Schema for leaderboard response with pagination"""

    data: list[OneLeaderboard] = Field(..., description="List of leaderboard entries")
    next_cursor: str | None = Field(None, description="Cursor for pagination, null if no more entries")


class AddLeaderboardParams(BaseModel):
    """Schema for adding a new leaderboard entry"""

    name: str = Field(..., description="Name of the player or entity")
    score: int = Field(..., description="Score value for the leaderboard entry")
    project_id: str = Field(..., description="Project identifier the leaderboard entry belongs to")


class OneMessageboard(BaseModel):
    """Schema for a single messageboard entry"""

    messageboard_id: str = Field(..., description="Unique identifier for the messageboard entry")
    name: str = Field(..., description="Name of the player or entity")
    message: str = Field(..., description="Message value for the messageboard entry")
    created_at: datetime = Field(..., description="Datetime when the entry was created")


class MessageboardResponse(BaseModel):
    """Schema for messageboard response with pagination"""

    data: list[OneMessageboard] = Field(..., description="List of messageboard entries")
    next_cursor: str | None = Field(None, description="Cursor for pagination, null if no more entries")


class AddMessageboardParams(BaseModel):
    """Schema for adding a new messageboard entry"""

    name: str = Field(..., description="Name of the player or entity")
    message: str = Field(..., description="Message value for the messageboard entry")
    project_id: str = Field(..., description="Project identifier the messageboard entry belongs to")


class AddFormParams(BaseModel):
    """Schema for adding a new form entry"""

    project_id: str = Field(..., description="Project identifier the form entry belongs to")

    username: str = Field(..., description="Username of the entity")
    email: str = Field(..., description="Email of the entity")
    project_link: str = Field(..., description="Project link of the entity")
    social_post_link: str = Field(..., description="Social post link of the entity")


class CountFormResponse(BaseModel):
    """Schema for counting form entries"""

    count: int = Field(..., description="Count of form entries")
