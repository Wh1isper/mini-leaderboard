from __future__ import annotations

import dotenv

dotenv.load_dotenv()

import os

from pydantic import BaseModel, ConfigDict


def get_config() -> Config:
    return Config.from_env()


DEFAULT_TOKEN = ""


class Config(BaseModel):
    model_config = ConfigDict(frozen=True)

    api_token: str
    db_url: str

    @classmethod
    def from_env(cls) -> Config:
        return cls(
            api_token=os.getenv("API_TOKEN", DEFAULT_TOKEN),
            db_url=os.getenv("DB_URL", "postgres:postgres@localhost:5432/postgres"),
        )

    def get_db_url(
        self,
    ):
        """
        Now psycopg3 support async mode so we don't need to use asyncpg
        """
        # Remove postgresql+asyncpg:// or postgresql+psycopg2:// if already present
        db_url = (
            self.db_url.replace("postgresql+asyncpg://", "")
            .replace("postgresql+psycopg2://", "")
            .replace("postgresql+psycopg://", "")
        )
        return f"postgresql+psycopg://{db_url}"
