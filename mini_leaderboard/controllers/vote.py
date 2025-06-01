from __future__ import annotations

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from mini_leaderboard.dbutils import get_db_session
from mini_leaderboard.orm import Vote
from mini_leaderboard.routers.api.params import AddVoteParams


def get_vote_controller(
    db: AsyncSession = Depends(get_db_session),
) -> VoteController:
    return VoteController(db)


class VoteController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_votes(self, project_id: str):
        """
        Get all votes for a specific project.
        """
        result = await self.db.execute(select(Vote).where(Vote.project_id == project_id))
        votes = result.scalars().all()
        return votes

    async def get_item_vote(self, project_id: str, item_id: str):
        """
        Get vote count for a specific item in a project.
        """
        result = await self.db.execute(select(Vote).where(Vote.project_id == project_id, Vote.item_id == item_id))
        vote = result.scalar_one_or_none()
        return vote.vote_count if vote else 0

    async def add_vote(self, params: AddVoteParams):
        """
        Add a vote for a specific item in a project.
        """
        # Using SQLAlchemy's insert...on conflict syntax for PostgreSQL
        stmt = insert(Vote).values(project_id=params.project_id, item_id=params.item_id, vote_count=1)

        # For PostgreSQL, use the constraint name
        stmt = stmt.on_conflict_do_update(constraint="uix_project_item", set_=dict(vote_count=Vote.vote_count + 1))  #  noqa: C408

        await self.db.execute(stmt)
        await self.db.commit()
        return None
