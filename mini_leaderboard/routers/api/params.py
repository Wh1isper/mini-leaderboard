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
