import click
import uvicorn

from mini_leaderboard.config import get_config
from mini_leaderboard.dbutils import drop_all_data, upgrade_in_place

from .app import app


@click.command()
@click.option("--host", type=click.STRING, default="0.0.0.0")  # noqa: S104
@click.option("--port", type=click.INT, default=8909)
def start(host, port):
    """
    Start the server.
    """
    uvicorn.run(app, host=host, port=port, timeout_graceful_shutdown=60)


@click.command()
def init():
    """
    Init and upgrade the database.
    """
    config = get_config()
    upgrade_in_place(config.get_db_url())


@click.group()
def cli():
    pass


@click.command()
@click.option("--yes", "-y", is_flag=True, default=False)
def drop(yes):
    """
    Drop all data before testing or other purposes.

    This command is not visible in the CLI. Only use it in tests for now.
    """
    if not yes:
        click.confirm("Are you sure you want to drop all data?", abort=True)

    click.echo("Dropping all data...")

    config = get_config()
    drop_all_data(config.get_db_url())


cli.add_command(start)
cli.add_command(init)
