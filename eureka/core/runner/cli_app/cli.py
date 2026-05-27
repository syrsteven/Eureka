from pathlib import Path

import click
import yaml

from eureka.core.runner.cli_app.main import run_eureka
from eureka.core.runner.client_lib.shared_click_commands import (
    DEFAULT_SETTINGS_FILE,
    make_settings,
)
from eureka.core.runner.client_lib.utils import coroutine, handle_exceptions


@click.group()
def Eureka():
    """Temporary command group for v2 commands."""
    pass


eureka.add_command(make_settings)


@eureka.command()
@click.option(
    "--settings-file",
    type=click.Path(),
    default=DEFAULT_SETTINGS_FILE,
)
@click.option(
    "--pdb",
    is_flag=True,
    help="Drop into a debugger if an error is raised.",
)
@coroutine
async def run(settings_file: str, pdb: bool) -> None:
    """Run the Eureka agent."""
    click.echo("Running Eureka agent...")
    settings_file: Path = Path(settings_file)
    settings = {}
    if settings_file.exists():
        settings = yaml.safe_load(settings_file.read_text())
    main = handle_exceptions(run_eureka, with_debugger=pdb)
    await main(settings)


if __name__ == "__main__":
    Eureka()
