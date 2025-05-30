"""new_day.py

Program to create a new daily log file in the WDIDT format.
"""

import datetime
import json
import logging
from pathlib import Path

import click

from wdidt.new_day import create_new_day
import getpass

logging.basicConfig(
    format="[%(asctime)s]%(name)s.%(levelname)s: %(message)s", level=logging.ERROR
)

log = logging.getLogger(__name__)


@click.command()
@click.option(
    "-a",
    "--ago",
    type=int,
    default=0,
    help="Create a log file for num_days ago.",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Always create the log file, even if it exists.",
)
@click.option(
    "-V",
    "--verbose",
    is_flag=True,
    help="Show verbose logs during processing.",
)
@click.option(
    "-d",
    "--dry-run",
    is_flag=True,
    help="Run without creating the new daily log. Report what would be written.",
)
@click.option(
    "-A",
    "--attributes",
    default=None,
    help="Added attributes to render the daily log with. Format: {key1:value1,key2:value2}",
)
@click.option(
    "-r",
    "--root-dir",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, path_type=str),
    default=str(Path.home().joinpath(".wdidt").absolute()),
    help="Root directory for the WDIDT logs. Defaults to ~/.wdidt.",
)
@click.option(
    "-c",
    "--config-file",
    type=click.Path(exists=False, file_okay=True, dir_okay=False, path_type=str),
    default=(Path.home().joinpath(".wdidt", "config.json").absolute()),
    help="Optional configuration file to use. Default location is ~/.wdidt/config.json.",
)
@click.version_option("0.1", "-v", "--version", message="%(version)s")
def main(ago, force, verbose, dry_run, attributes, root_dir, config_file):
    """Program to create a new daily log file in the WDIDT format."""
    log_level = logging.INFO
    if verbose:
        log_level = logging.DEBUG
    log.setLevel(log_level)

    log.debug(
        f"Arguments given:\n"
        f"    ago={ago}\n"
        f"    force={force}\n"
        f"    verbose={verbose}\n"
        f"    dry_run={dry_run}\n"
        f"    attributes={attributes}\n"
        f"    wdidt logfile root={root_dir}\n"
        f"    config file={config_file}"
    )

    config = {}
    if config_file:
        if not Path(config_file).exists():
            log.info(f"Using configuration file: {config_file}")
            config.update(json.loads(Path(config_file).read_text()))
        else:
            log.info(
                f"Configuration file {config_file} does not exist.\n  - Creating a default configuration file."
            )
            config = {
                "attributes": {"name": getpass.getuser()},
                "root-dir": str(Path.home().joinpath(".wdidt").absolute()),
            }
            # create the directory for the config file if it does not exist
            config_file_path = Path(config_file)
            config_file_path.parent.mkdir(parents=True, exist_ok=True)
            # Write a default configuration file if it does not exist
            config_file_path.write_text(json.dumps(config, indent=4))

    log_day: datetime.date = datetime.date.today()
    if ago:
        log_day = datetime.date.today() - datetime.timedelta(days=ago)
        log.debug(f"Log file day is being set to {log_day}.")

    # make sure we have the attributes from the config file, and at minimum the 'name' attribute.
    attributes = config.get("attributes", {})
    if "name" not in attributes:
        attributes.update({"name": getpass.getuser()})

    root_folder = Path(root_dir).absolute()
    log.debug(f"Root folder is set to {root_folder}")
    root_folder.mkdir(parents=True, exist_ok=True)

    create_new_day(
        log_day=log_day,
        force=force,
        dry_run=dry_run,
        attribs=attributes,
        verbose=verbose,
        root_dir=root_folder,
    )


if __name__ == "__main__":
    main()
