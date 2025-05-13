import socket
import time
from pathlib import Path
from uuid import uuid4

import docker
import pytest
from click.testing import CliRunner
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from mini_leaderboard.app import app as APP
from mini_leaderboard.cli import drop, init
from mini_leaderboard.config import get_config

_HERE = Path(__file__).parent
MOCK_SERVER = _HERE / "mock_server.py"


@pytest.fixture(scope="session")
def docker_client():
    try:
        client = docker.from_env()
        client.ping()
        return client
    except:
        pytest.skip("Docker is not available")


def get_port():
    # Get an unoccupied port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def case_id():
    return uuid4().hex


@pytest.fixture(scope="session")
def pg_port(docker_client: docker.DockerClient):
    pg_port = get_port()
    container = None
    try:
        container = docker_client.containers.run(
            "pgvector/pgvector:pg16",
            detach=True,
            ports={"5432": pg_port},
            remove=True,
            environment={
                "POSTGRES_USER": "postgres",
                "POSTGRES_PASSWORD": "postgres",
                "POSTGRES_DB": "postgres",
            },
        )
        while True:
            # Execute `pg_isready -U postgres` in the container
            try:
                # Pg is ready
                r = container.exec_run("pg_isready -U postgres")
                assert r.exit_code == 0
                assert b"accepting connections" in r.output
                # Try to connect db
                engine = create_engine(f"postgresql+psycopg://postgres:postgres@localhost:{pg_port}/postgres")
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
            except Exception:
                time.sleep(0.5)
            else:
                break
        runner = CliRunner()
        result = runner.invoke(init, env={"DB_URL": f"postgres:postgres@localhost:{pg_port}/postgres"})
        assert result.exit_code == 0
        yield pg_port
    finally:
        if container:
            container.stop()


@pytest.fixture
async def app(pg_port, monkeypatch):
    monkeypatch.setenv("DB_URL", f"postgres:postgres@localhost:{pg_port}/postgres")
    runner = CliRunner()
    # Drop all before testing
    result = runner.invoke(drop, ["--yes"])
    assert result.exit_code == 0
    yield APP


@pytest.fixture
def client(app):
    config = get_config()
    with TestClient(
        app,
        headers=({"Authorization": f"Bearer {config.api_token}"} if config.api_token else {}),
    ) as client:
        yield client
