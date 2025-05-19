from fastapi import APIRouter, Depends, Query, Response, status

from mini_leaderboard.controllers.form import (
    FormController,
    get_form_controller,
)
from mini_leaderboard.routers.api.params import (
    AddFormParams,
    CountFormResponse,
)

router = APIRouter(
    tags=["form"],
    prefix="/api/v1/form",
)


@router.get("/count")
async def count(
    project_id: str = Query(..., description="Project identifier"),
    form_controller: FormController = Depends(get_form_controller),
):
    """
    Get the count of leaderboard entries for a specific project.
    """
    return CountFormResponse(count=await form_controller.count(project_id=project_id))


@router.post(
    "/submit",
    status_code=status.HTTP_201_CREATED,
    response_model=None,
)
async def submit_form(
    params: AddFormParams,
    form_controller: FormController = Depends(get_form_controller),
) -> Response:
    await form_controller.submit_form(params)
    return Response(status_code=status.HTTP_201_CREATED)
