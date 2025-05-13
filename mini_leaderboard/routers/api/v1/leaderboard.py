from fastapi import APIRouter, Depends, Query, Response, status

from mini_leaderboard.controllers.leaderboard import (
    LeaderboardController,
    get_leaderboard_controller,
)
from mini_leaderboard.routers.api.params import (
    AddLeaderboardParams,
    LeaderboardResponse,
)

router = APIRouter(
    tags=["leaderboard"],
    prefix="/api/v1/leaderboard",
)


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_leaderboard(
    params: AddLeaderboardParams,
    leaderboard_controller: LeaderboardController = Depends(get_leaderboard_controller),
) -> Response:
    await leaderboard_controller.add_leaderboard(params)
    return Response(status_code=status.HTTP_201_CREATED)


@router.get("/list")
async def get_leaderboard(
    project_id: str = Query(..., description="Project identifier"),
    cursor: str | None = Query(
        default=None,
        description="Cursor for pagination, use `next_cursor` from previous response",
    ),
    page_size: int = Query(default=100, description="Page size for pagination"),
    leaderboard_controller: LeaderboardController = Depends(get_leaderboard_controller),
) -> LeaderboardResponse:
    return await leaderboard_controller.get_leaderboard(project_id, cursor, page_size)
