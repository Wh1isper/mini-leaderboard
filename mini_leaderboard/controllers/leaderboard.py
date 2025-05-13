from __future__ import annotations

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mini_leaderboard.dbutils import get_db_session
from mini_leaderboard.orm import Leaderboard
from mini_leaderboard.routers.api.params import (
    AddLeaderboardParams,
    LeaderboardResponse,
    OneLeaderboard,
)


def get_leaderboard_controller(
    db: AsyncSession = Depends(get_db_session),
) -> LeaderboardController:
    return LeaderboardController(db)


class LeaderboardController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_leaderboard(self, params: AddLeaderboardParams) -> None:
        leaderboard = Leaderboard(name=params.name, score=params.score, project_id=params.project_id)
        self.db.add(leaderboard)

        await self.db.commit()
        return None

    async def get_leaderboard(self, project_id: str, cursor: str | None, page_size: int) -> LeaderboardResponse:
        """cursor is leaderboard_id of Leaderboard"""
        # Create a query to select leaderboard records
        query = select(Leaderboard).where(Leaderboard.project_id == project_id)

        # If cursor is provided, filter to get records after the cursor
        if cursor:
            # First get the record corresponding to the cursor
            cursor_query = select(Leaderboard).where(Leaderboard.leaderboard_id == cursor)
            cursor_result = await self.db.execute(cursor_query)
            cursor_record = cursor_result.scalar_one_or_none()

            if cursor_record:
                # Filter to get records after this one (using id_ for stable ordering)
                query = query.where(Leaderboard.id_ > cursor_record.id_)

        # Order by score (descending) and id_ (for stable ordering)
        query = query.order_by(Leaderboard.score.desc(), Leaderboard.id_)

        # Limit to page_size + 1 (to check if there's a next page)
        query = query.limit(page_size + 1)

        # Execute the query
        result = await self.db.execute(query)
        records = result.scalars().all()

        # Determine if there's a next page
        has_next_page = len(records) > page_size
        if has_next_page:
            # Get the last record of the current page as the next cursor
            next_cursor = records[page_size - 1].leaderboard_id
            # Trim to page_size
            records = records[:page_size]
        else:
            next_cursor = None

        # Convert to OneLeaderboard objects
        data = [
            OneLeaderboard(
                leaderboard_id=record.leaderboard_id,
                name=record.name,
                score=record.score,
                created_at=record.created_at,
            )
            for record in records
        ]

        # Return the response
        return LeaderboardResponse(data=data, next_cursor=next_cursor)
