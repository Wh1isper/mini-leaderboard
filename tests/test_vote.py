import pytest

from mini_leaderboard.routers.api.params import AddVoteParams, VoteCountResponse, VoteListResponse


@pytest.fixture
def project_id():
    return "test-project"


@pytest.fixture
def item_id():
    return "test-item"


def test_add_and_get_vote(client, project_id, item_id):
    """Test adding a vote and getting its count."""
    # Add a vote
    response = client.post(
        "/api/v1/vote/add",
        json=AddVoteParams(
            project_id=project_id,
            item_id=item_id,
        ).model_dump(),
    )
    assert response.status_code == 201

    # Get the vote count for the item
    response = client.get(
        "/api/v1/vote/count",
        params={"project_id": project_id, "item_id": item_id},
    )
    assert response.status_code == 200
    assert VoteCountResponse.model_validate(response.json()).vote_count == 1

    # Add another vote for the same item
    response = client.post(
        "/api/v1/vote/add",
        json=AddVoteParams(
            project_id=project_id,
            item_id=item_id,
        ).model_dump(),
    )
    assert response.status_code == 201

    # Get the vote count again, should be 2 now
    response = client.get(
        "/api/v1/vote/count",
        params={"project_id": project_id, "item_id": item_id},
    )
    assert response.status_code == 200
    assert VoteCountResponse.model_validate(response.json()).vote_count == 2


def test_get_nonexistent_vote(client, project_id):
    """Test getting vote count for a nonexistent item."""
    # Get vote count for a nonexistent item
    response = client.get(
        "/api/v1/vote/count",
        params={"project_id": project_id, "item_id": "nonexistent-item"},
    )
    assert response.status_code == 200
    assert VoteCountResponse.model_validate(response.json()).vote_count == 0


def test_list_votes(client, project_id):
    """Test listing all votes for a project."""
    # Add votes for multiple items
    items = ["item1", "item2", "item3"]

    for item_id in items:
        # Add a vote for each item
        response = client.post(
            "/api/v1/vote/add",
            json=AddVoteParams(
                project_id=project_id,
                item_id=item_id,
            ).model_dump(),
        )
        assert response.status_code == 201

        # Add a second vote for the first item
        if item_id == "item1":
            response = client.post(
                "/api/v1/vote/add",
                json=AddVoteParams(
                    project_id=project_id,
                    item_id=item_id,
                ).model_dump(),
            )
            assert response.status_code == 201

    # List all votes for the project
    response = client.get(
        "/api/v1/vote/list",
        params={"project_id": project_id},
    )
    assert response.status_code == 200

    vote_list = VoteListResponse.model_validate(response.json())
    assert len(vote_list.data) == 3  # Should have 3 items

    # Check vote counts
    vote_counts = {vote.item_id: vote.vote_count for vote in vote_list.data}
    assert vote_counts["item1"] == 2
    assert vote_counts["item2"] == 1
    assert vote_counts["item3"] == 1


def test_list_votes_empty_project(client):
    """Test listing votes for a project with no votes."""
    # List votes for a project with no votes
    response = client.get(
        "/api/v1/vote/list",
        params={"project_id": "empty-project"},
    )
    assert response.status_code == 200

    vote_list = VoteListResponse.model_validate(response.json())
    assert len(vote_list.data) == 0  # Should have no items
