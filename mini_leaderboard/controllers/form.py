from __future__ import annotations

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from mini_leaderboard.dbutils import get_db_session
from mini_leaderboard.orm import Form
from mini_leaderboard.routers.api.params import AddFormParams


def get_form_controller(
    db: AsyncSession = Depends(get_db_session),
) -> FormController:
    return FormController(db)


class FormController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def count(
        self,
        project_id: str,
    ) -> int:
        """
        Count the number of form entries for a specific project.
        """
        result = await self.db.execute(select(func.count()).select_from(Form).where(Form.project_id == project_id))
        count = result.scalar_one_or_none()
        return count or 0

    async def submit_form(self, params: AddFormParams) -> None:
        form = Form(
            username=params.username,
            email=params.email,
            project_link=params.project_link,
            social_post_link=params.social_post_link,
            project_id=params.project_id,
        )
        self.db.add(form)

        await self.db.commit()
        return None
