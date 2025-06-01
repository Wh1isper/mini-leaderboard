from fastapi import APIRouter, Depends, Query, Response, status

from mini_leaderboard.controllers.vote import (
    VoteController,
    get_vote_controller,
)
from mini_leaderboard.routers.api.params import (
    AddVoteParams,
    OneVote,
    VoteCountResponse,
    VoteListResponse,
)

router = APIRouter(
    tags=["vote"],
    prefix="/api/v1/vote",
)


@router.get("/list", response_model=VoteListResponse)
async def list_votes(
    project_id: str = Query(..., description="Project identifier"),
    vote_controller: VoteController = Depends(get_vote_controller),
):
    """
    Get all votes for a specific project.
    """
    votes = await vote_controller.get_all_votes(project_id=project_id)
    return VoteListResponse(
        data=[OneVote(project_id=vote.project_id, item_id=vote.item_id, vote_count=vote.vote_count) for vote in votes]
    )


@router.get("/count", response_model=VoteCountResponse)
async def get_vote_count(
    project_id: str = Query(..., description="Project identifier"),
    item_id: str = Query(..., description="Item identifier"),
    vote_controller: VoteController = Depends(get_vote_controller),
):
    """
    Get vote count for a specific item in a project.
    """
    count = await vote_controller.get_item_vote(project_id=project_id, item_id=item_id)
    return VoteCountResponse(vote_count=count)


@router.post(
    "/add",
    status_code=status.HTTP_201_CREATED,
    response_model=None,
)
async def add_vote(
    params: AddVoteParams,
    vote_controller: VoteController = Depends(get_vote_controller),
) -> Response:
    """
    Add a vote for a specific item in a project.
    """
    await vote_controller.add_vote(params)
    return Response(status_code=status.HTTP_201_CREATED)
