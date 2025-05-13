from __future__ import annotations

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mini_leaderboard.dbutils import get_db_session
from mini_leaderboard.orm import MessageBoard
from mini_leaderboard.routers.api.params import (
    AddMessageboardParams,
    MessageboardResponse,
    OneMessageboard,
)


def get_messageboard_controller(
    db: AsyncSession = Depends(get_db_session),
) -> MessageboardController:
    return MessageboardController(db)


class MessageboardController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_messageboard(self, params: AddMessageboardParams) -> None:
        messageboard = MessageBoard(name=params.name, message=params.message, project_id=params.project_id)
        self.db.add(messageboard)

        await self.db.commit()
        return None

    async def get_messageboard(
        self, project_id: str, cursor: str | None, page_size: int, search_keyword: str | None
    ) -> MessageboardResponse:
        """cursor is message_id of MessageBoard"""
        # Create a query to select messageboard records
        query = select(MessageBoard).where(MessageBoard.project_id == project_id)

        # Add search functionality if keyword provided
        if search_keyword:
            query = query.where(
                # Search in both name and message fields
                (MessageBoard.name.ilike(f"%{search_keyword}%")) | (MessageBoard.message.ilike(f"%{search_keyword}%"))
            )

        # If cursor is provided, filter to get records after the cursor
        if cursor:
            # First get the record corresponding to the cursor
            cursor_query = select(MessageBoard).where(MessageBoard.message_id == cursor)
            cursor_result = await self.db.execute(cursor_query)
            cursor_record = cursor_result.scalar_one_or_none()

            if cursor_record:
                # Filter to get records after this one (using id_ for stable ordering)
                # Since we're ordering by created_at DESC, we need to get records with smaller IDs
                query = query.where(MessageBoard.id_ < cursor_record.id_)

        # Order by creation time (newest first) and id_ (for stable ordering)
        query = query.order_by(MessageBoard.created_at.desc(), MessageBoard.id_)

        # Limit to page_size + 1 (to check if there's a next page)
        query = query.limit(page_size + 1)

        # Execute the query
        result = await self.db.execute(query)
        records = result.scalars().all()

        # Determine if there's a next page
        has_next_page = len(records) > page_size
        if has_next_page:
            # Get the last record of the current page as the next cursor
            next_cursor = records[page_size - 1].message_id
            # Trim to page_size
            records = records[:page_size]
        else:
            next_cursor = None

        # Convert to OneMessageboard objects
        data = [
            OneMessageboard(
                messageboard_id=record.message_id,
                name=record.name,
                message=record.message,
                created_at=record.created_at,
            )
            for record in records
        ]

        # Return the response
        return MessageboardResponse(data=data, next_cursor=next_cursor)
