from fastapi import APIRouter, Depends, Query, Response, status

from mini_leaderboard.controllers.messageboard import (
    MessageboardController,
    get_messageboard_controller,
)
from mini_leaderboard.routers.api.params import (
    AddMessageboardParams,
    MessageboardResponse,
)

router = APIRouter(
    tags=["messageboard"],
    prefix="/api/v1/messageboard",
)


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_messageboard(
    params: AddMessageboardParams,
    messageboard_controller: MessageboardController = Depends(get_messageboard_controller),
) -> Response:
    await messageboard_controller.add_messageboard(params)
    return Response(status_code=status.HTTP_201_CREATED)


@router.get("/list")
async def get_messageboard(
    project_id: str = Query(..., description="Project identifier"),
    cursor: str | None = Query(
        default=None,
        description="Cursor for pagination, use `next_cursor` from previous response",
    ),
    page_size: int = Query(default=100, description="Page size for pagination"),
    search_keyword: str | None = Query(
        default=None,
        description="Search keyword for messageboard entries",
    ),
    messageboard_controller: MessageboardController = Depends(get_messageboard_controller),
) -> MessageboardResponse:
    return await messageboard_controller.get_messageboard(project_id, cursor, page_size, search_keyword)
