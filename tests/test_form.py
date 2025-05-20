import pytest

from mini_leaderboard.routers.api.params import AddFormParams, CountFormResponse


@pytest.fixture
def project_id():
    return "test-project"


def test_add_and_count_form(client, project_id):
    """Test adding a new form entry."""
    # Create a form entry
    response = client.post(
        "/api/v1/form/submit",
        json=AddFormParams(
            project_id=project_id,
            username="Test User",
            email="test@user",
            project_link="https://example.com",
            social_post_link="https://twitter.com/example",
        ).model_dump(),
    )
    assert response.status_code == 201

    # Count the form entries
    response = client.get(
        "/api/v1/form/count",
        params={"project_id": project_id},
    )
    assert response.status_code == 200
    assert CountFormResponse.model_validate(response.json()).count == 1

    # Count the form entries
    response = client.get(
        "/api/v1/form/count",
        params={"project_id": "unknown_project"},
    )
    assert response.status_code == 200
    assert CountFormResponse.model_validate(response.json()).count == 0


def test_add_and_count_form_no_name(client, project_id):
    """Test adding a new form entry."""
    # Create a form entry
    response = client.post(
        "/api/v1/form/submit",
        json=AddFormParams(
            project_id=project_id,
            email="test@user",
            project_link="https://example.com",
            social_post_link="https://twitter.com/example",
        ).model_dump(),
    )
    assert response.status_code == 201

    # Count the form entries
    response = client.get(
        "/api/v1/form/count",
        params={"project_id": project_id},
    )
    assert response.status_code == 200
    assert CountFormResponse.model_validate(response.json()).count == 1

    # Count the form entries
    response = client.get(
        "/api/v1/form/count",
        params={"project_id": "unknown_project"},
    )
    assert response.status_code == 200
    assert CountFormResponse.model_validate(response.json()).count == 0
