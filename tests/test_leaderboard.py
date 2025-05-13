def test_add_leaderboard(client):
    """Test adding a new leaderboard entry."""
    # Create a leaderboard entry
    response = client.post(
        "/api/v1/leaderboard/add",
        json={"name": "Test User", "score": 100, "project_id": "test-project"},
    )
    assert response.status_code == 201


def test_get_leaderboard_empty(client):
    """Test getting an empty leaderboard."""
    response = client.get("/api/v1/leaderboard/list")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 0
    assert data["next_cursor"] is None


def test_get_leaderboard(client):
    """Test getting leaderboard entries."""
    # Create multiple leaderboard entries
    entries = [{"name": f"User {i}", "score": 100 - i * 10, "project_id": "test-project"} for i in range(5)]

    for entry in entries:
        response = client.post("/api/v1/leaderboard/add", json=entry)
        assert response.status_code == 201

    # Get the leaderboard
    response = client.get("/api/v1/leaderboard/list")
    assert response.status_code == 200
    data = response.json()

    # Check the data
    assert "data" in data
    assert len(data["data"]) == 5
    assert data["next_cursor"] is None

    # Check that entries are sorted by score (descending)
    scores = [entry["score"] for entry in data["data"]]
    assert scores == sorted(scores, reverse=True)


def test_get_leaderboard_pagination(client):
    """Test leaderboard pagination with cursor."""
    # Create exactly 150 entries (more than the default page size of 100)
    entries = []
    for i in range(150):  # Default page size is 100
        entries.append({"name": f"User {i}", "score": 1000 - i, "project_id": "test-project"})

    for entry in entries:
        response = client.post("/api/v1/leaderboard/add", json=entry)
        assert response.status_code == 201

    # Verify we have 150 entries
    response = client.get("/api/v1/leaderboard/list?page_size=1000")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 150

    # Get the first page with default page size
    response = client.get("/api/v1/leaderboard/list")
    assert response.status_code == 200
    data = response.json()

    # Check the first page
    assert len(data["data"]) == 100
    assert data["next_cursor"] is not None

    # Get the second page using the cursor
    cursor = data["next_cursor"]
    response = client.get(f"/api/v1/leaderboard/list?cursor={cursor}")
    assert response.status_code == 200
    data = response.json()

    # Check the second page
    assert len(data["data"]) == 50
    assert data["next_cursor"] is None


def test_get_leaderboard_with_custom_page_size(client):
    """Test leaderboard with custom page size."""
    # Create exactly 25 entries
    entries = []
    for i in range(25):
        entries.append({"name": f"User {i}", "score": 500 - i, "project_id": "test-project"})

    for entry in entries:
        response = client.post("/api/v1/leaderboard/add", json=entry)
        assert response.status_code == 201

    # Verify we have 25 entries
    response = client.get("/api/v1/leaderboard/list?page_size=1000")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 25

    # Get with custom page size
    response = client.get("/api/v1/leaderboard/list?page_size=10")
    assert response.status_code == 200
    data = response.json()

    # Check the response
    assert len(data["data"]) == 10
    assert data["next_cursor"] is not None

    # Get the next page
    cursor = data["next_cursor"]
    response = client.get(f"/api/v1/leaderboard/list?cursor={cursor}&page_size=10")
    assert response.status_code == 200
    data = response.json()

    # Check the second page
    assert len(data["data"]) == 10
    assert data["next_cursor"] is not None

    # Get the final page
    cursor = data["next_cursor"]
    response = client.get(f"/api/v1/leaderboard/list?cursor={cursor}&page_size=10")
    assert response.status_code == 200
    data = response.json()

    # Check the final page
    assert len(data["data"]) == 5
    assert data["next_cursor"] is None
