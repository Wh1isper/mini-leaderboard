from __future__ import annotations

import os
from contextlib import asynccontextmanager, contextmanager

try:
    from functools import cache
except ImportError:
    from functools import lru_cache as cache

from collections.abc import AsyncGenerator
from glob import glob
from pathlib import Path
from subprocess import check_call
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

import alembic.command
import alembic.config
from alembic.script import ScriptDirectory
from fastapi import Depends
from sqlalchemy import create_engine, delete, exc, inspect, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session

from mini_leaderboard.config import Config, get_config
from mini_leaderboard.log import logger
from mini_leaderboard.orm import Base

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

_here = os.path.abspath(os.path.dirname(__file__))

ALEMBIC_INI_TEMPLATE_PATH = os.path.join(_here, "alembic.ini")
ALEMBIC_DIR = os.path.join(_here, "alembic")


def write_alembic_ini(alembic_ini="alembic.ini", db_url="sqlite:///mini_leaderboard.sqlite"):
    """Write a complete alembic.ini from our template.

    Parameters
    ----------
    alembic_ini : str
        path to the alembic.ini file that should be written.
    db_url : str
        The SQLAlchemy database url, e.g. `sqlite:///mini_leaderboard.sqlite`.
    """
    with open(ALEMBIC_INI_TEMPLATE_PATH) as f:
        alembic_ini_tpl = f.read()

    with open(alembic_ini, "w") as f:
        f.write(
            alembic_ini_tpl.format(
                alembic_dir=ALEMBIC_DIR,
                # If there are any %s in the URL, they should be replaced with %%, since ConfigParser
                # by default uses %() for substitution. You'll get %s in your URL when you have usernames
                # with special chars (such as '@') that need to be URL encoded. URL Encoding is done with %s.
                # YAY for nested templates?
                db_url=str(db_url).replace("%", "%%"),
            )
        )


@contextmanager
def _temp_alembic_ini(db_url):
    """Context manager for temporary alembic directory

    Temporarily write an alembic.ini file for use with alembic migration scripts.

    Context manager yields alembic.ini path.

    Parameters
    ----------
    db_url : str
        The SQLAlchemy database url, e.g. `sqlite:///mini_leaderboard.sqlite`.

    Returns
    -------
    alembic_ini: str
        The path to the temporary alembic.ini that we have created.
        This file will be cleaned up on exit from the context manager.
    """
    with TemporaryDirectory() as td:
        alembic_ini = os.path.join(td, "alembic.ini")
        write_alembic_ini(alembic_ini, db_url)
        yield alembic_ini


@contextmanager
def chdir(path):
    """Context manager to temporarily change directory"""
    old_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_dir)


def upgrade(db_url, revision="head"):
    """Upgrade the given database to revision.

    db_url: str
        The SQLAlchemy database url, e.g. `sqlite:///mini_leaderboard.sqlite`.
    revision: str [default: head]
        The alembic revision to upgrade to.
    """
    with _temp_alembic_ini(db_url) as alembic_ini:
        check_call(["alembic", "-c", alembic_ini, "upgrade", revision])


class DatabaseSchemaMismatch(Exception):
    pass


def _clear_revision(engine, url):
    inspector = inspect(engine)
    if inspector.has_table("alembic_version"):
        with engine.begin() as connection:
            connection.execute(text("delete from alembic_version"))

    with _temp_alembic_ini(url) as ini:
        cfg = alembic.config.Config(ini)
        scripts = ScriptDirectory.from_config(cfg)
        old_versions_files = Path(scripts.versions) / "*.py"
        # Remove *.py from old_versions
        for old_versions_file in glob(old_versions_files.as_posix()):
            os.remove(old_versions_file)
        logger.info(f"Removed old versions: {old_versions_files}")

        logger.info(f"Creating new revision: {ini}")
        alembic.command.revision(config=cfg, autogenerate=True, message="init")


def get_db_log_url(db_url):
    urlinfo = urlparse(db_url)
    if urlinfo.password:
        # avoid logging the database password
        urlinfo = urlinfo._replace(netloc=f"{urlinfo.username}:[redacted]@{urlinfo.hostname}:{urlinfo.port}")
        db_log_url = urlinfo.geturl()
    else:
        db_log_url = db_url
    return db_log_url


def upgrade_in_place(db_url):
    """This is a dark magic function that upgrades the database in-place."""
    # run check-db-revision first

    db_log_url = get_db_log_url(db_url)
    logger.info(f"Initializing database: {db_log_url}")
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)

    with chdir(_here):
        _clear_revision(engine, db_url)
        logger.info(f"Upgrading database: {db_log_url}")
        upgrade(db_url)


def drop_all_data(db_url):
    db_log_url = get_db_log_url(db_url)
    logger.info(f"Dropping database: {db_log_url}")
    engine = create_engine(db_url)
    for t in Base.metadata.tables.values():
        logger.info(f"Delete table data: {t}")
        with Session(engine) as session:
            session.execute(delete(t))
            session.commit()


@cache
def get_engine(config: Config):
    logger.info("Creating database engine")
    return create_async_engine(
        config.get_db_url(),
        pool_pre_ping=True,  # Verify connections before using them
        pool_size=5,
        max_overflow=5,
        pool_recycle=60,
    )


@asynccontextmanager
async def init_engine(config: Config):
    engine = get_engine(config)
    yield engine
    await engine.dispose()
    logger.info("Database engine disposed")


def create_sessionmaker(config: Config):
    return async_sessionmaker(
        get_engine(config),
        expire_on_commit=False,
        autoflush=True,
    )


async def get_db_session(
    config: Config = Depends(get_config),
) -> AsyncGenerator[AsyncSession, None]:
    """
    For fastapi dependency injection
    """
    async with create_sessionmaker(config)() as session:
        try:
            yield session
            await session.commit()
        except exc.SQLAlchemyError:
            await session.rollback()
            raise


@asynccontextmanager
async def open_db_session(
    config: Config,
    engine_kwargs: dict[str, Any] | None = None,
) -> AsyncGenerator[AsyncSession, None]:
    """
    A helper function to open a database session

    NOTE: This is not optimized for performance as not reuse engine for polling connections
          Use get_db_session as Depend via fastapi dependency injection
    """
    engine = create_async_engine(
        config.get_db_url() ** (engine_kwargs or {}),
    )
    factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=True)
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except exc.SQLAlchemyError:
            await session.rollback()
            raise
