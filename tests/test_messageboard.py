import pytest


@pytest.fixture
def project_id():
    return "test-project"


def test_add_messageboard(client, project_id):
    """Test adding a new messageboard entry."""
    # Create a messageboard entry
    response = client.post(
        "/api/v1/messageboard/add",
        json={"name": "Test User", "message": "Hello, world!", "project_id": project_id},
    )
    assert response.status_code == 201


def test_get_messageboard_empty(client, project_id):
    """Test getting an empty messageboard."""
    response = client.get("/api/v1/messageboard/list", params={"project_id": project_id})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 0
    assert data["next_cursor"] is None


def test_get_messageboard(client, project_id):
    """Test getting messageboard entries."""
    # Create multiple messageboard entries
    entries = [{"name": f"User {i}", "message": f"Message {i}", "project_id": project_id} for i in range(5)]

    for entry in entries:
        response = client.post("/api/v1/messageboard/add", json=entry)
        assert response.status_code == 201

    # Get the messageboard
    response = client.get("/api/v1/messageboard/list", params={"project_id": project_id})
    assert response.status_code == 200
    data = response.json()

    # Check the data
    assert "data" in data
    assert len(data["data"]) == 5
    assert data["next_cursor"] is None

    # Check that entries are sorted by created_at (newest first)
    # Since we're creating them in sequence, the first entry should be the last one created
    assert data["data"][0]["name"] == "User 4"
    assert data["data"][4]["name"] == "User 0"


def test_get_messageboard_pagination(client, project_id):
    """Test messageboard pagination with cursor."""
    # Create exactly 150 entries (more than the default page size of 100)
    entries = []
    for i in range(150):
        entries.append({"name": f"User {i}", "message": f"Message {i}", "project_id": project_id})

    for entry in entries:
        response = client.post("/api/v1/messageboard/add", json=entry)
        assert response.status_code == 201

    # Verify we have 150 entries
    response = client.get("/api/v1/messageboard/list", params={"project_id": project_id, "page_size": 1000})
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 150

    # Get the first page with default page size
    response = client.get("/api/v1/messageboard/list", params={"project_id": project_id})
    assert response.status_code == 200
    data = response.json()

    # Check the first page
    assert len(data["data"]) == 100
    assert data["next_cursor"] is not None

    # Get the second page using the cursor
    cursor = data["next_cursor"]
    response = client.get("/api/v1/messageboard/list", params={"project_id": project_id, "cursor": cursor})
    assert response.status_code == 200
    data = response.json()

    # Check the second page
    # Since we're ordering by created_at DESC, we expect to get the remaining 50 entries
    assert len(data["data"]) == 50
    assert data["next_cursor"] is None


def test_get_messageboard_with_custom_page_size(client, project_id):
    """Test messageboard with custom page size."""
    # Create exactly 25 entries
    entries = []
    for i in range(25):
        entries.append({"name": f"User {i}", "message": f"Message {i}", "project_id": project_id})

    for entry in entries:
        response = client.post("/api/v1/messageboard/add", json=entry)
        assert response.status_code == 201

    # Verify we have 25 entries
    response = client.get("/api/v1/messageboard/list", params={"project_id": project_id, "page_size": 1000})
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 25

    # Get with custom page size
    response = client.get("/api/v1/messageboard/list", params={"project_id": project_id, "page_size": 10})
    assert response.status_code == 200
    data = response.json()

    # Check the response
    assert len(data["data"]) == 10
    assert data["next_cursor"] is not None

    # Get the next page
    cursor = data["next_cursor"]
    response = client.get(
        "/api/v1/messageboard/list", params={"project_id": project_id, "cursor": cursor, "page_size": 10}
    )
    assert response.status_code == 200
    data = response.json()

    # Check the second page
    # With 25 total entries and 10 on the first page, we expect 10 on the second page
    # and 5 on the third page
    assert len(data["data"]) == 10
    assert data["next_cursor"] is not None

    # Get the final page
    cursor = data["next_cursor"]
    response = client.get(
        "/api/v1/messageboard/list", params={"project_id": project_id, "cursor": cursor, "page_size": 10}
    )
    assert response.status_code == 200
    data = response.json()

    # Check the final page
    assert len(data["data"]) == 5
    assert data["next_cursor"] is None


def test_get_messageboard_with_search(client, project_id):
    """Test messageboard search functionality."""
    # Create entries with specific content for search testing
    entries = [
        {"name": "Alice", "message": "Hello world", "project_id": project_id},
        {"name": "Bob", "message": "Testing search", "project_id": project_id},
        {"name": "Charlie", "message": "Another message", "project_id": project_id},
        {"name": "David", "message": "Hello Alice", "project_id": project_id},
        {"name": "Search User", "message": "Regular message", "project_id": project_id},
    ]

    for entry in entries:
        response = client.post("/api/v1/messageboard/add", json=entry)
        assert response.status_code == 201

    # Search by name
    response = client.get("/api/v1/messageboard/list", params={"project_id": project_id, "search_keyword": "Alice"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 2  # Should match "Alice" and "Hello Alice"

    # Search by message content
    response = client.get("/api/v1/messageboard/list", params={"project_id": project_id, "search_keyword": "search"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 2  # Should match "Testing search" and "Search User"
