"""new_day.py

Program to create a new daily log file in the WDIDT format.
"""

import datetime
import getpass
import json
import logging
import os
from pathlib import Path
import platform
import subprocess
from typing import Dict, Any, Optional

import click

from wdidt.new_day import create_new_day


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
    "-A",
    "--attributes",
    type=Optional[Dict[str, Any]],
    default=None,
    help="Added attributes to render the daily log with. Format: {key1:value1,key2:value2}",
)
@click.option(
    "-c",
    "--config-file",
    type=click.Path(exists=False, file_okay=True, dir_okay=False, path_type=str),
    default=(Path.home().joinpath(".wdidt", "config.json").absolute()),
    help="Optional configuration file to use. Default location is ~/.wdidt/config.json.",
)
@click.option(
    "-d",
    "--dry-run",
    is_flag=True,
    help="Run without creating the new daily log. Report what would be written.",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Always create the log file, even if it exists.",
)
@click.option(
    "-l",
    "--launch-editor",
    is_flag=True,
    help="Launch the editor to edit the new daily log file after creation.",
)
@click.option(
    "-r",
    "--root-dir",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, path_type=str),
    default=str(Path.home().joinpath(".wdidt").absolute()),
    help="Root directory for the WDIDT logs. Defaults to ~/.wdidt.",
)
@click.version_option("0.1", "-v", "--version", message="%(version)s")
@click.option(
    "-V",
    "--verbose",
    is_flag=True,
    help="Show verbose logs during processing.",
)
def main(
    ago: int,
    force: bool,
    verbose: bool,
    dry_run: bool,
    attributes: Optional[Dict[str, Any]],
    root_dir: Path,
    config_file: Path,
    launch_editor: bool = False,
):
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
        f"    config file={config_file}\n"
        f"    launch_editor={launch_editor}\n"
    )

    config = {}
    if config_file:
        if Path(config_file).exists():
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

    # make sure we have the attributes from the config file...
    attribs = config.get("attributes", {})
    # override the attributes from those specified on the command line
    cmd_attribs = {}
    if attributes:
        try:
            cmd_attribs = json.loads(attributes)
            log.debug(f"Attributes parsed from command line: {cmd_attribs}")
        except json.JSONDecodeError as e:
            log.exception(f"Failed to parse attributes: {e}")
            raise click.BadParameter("Invalid format for attributes. Use JSON format.")
    attribs.update(cmd_attribs)
    # ensure we have a name attribute
    if "name" not in attribs:
        attribs.update({"name": getpass.getuser()})
        log.warning(
            "No 'name' attribute found in configuration file nor command line. Using the current user name."
        )

    root_folder = Path(root_dir).absolute()
    log.debug(f"Root folder is set to {root_folder}")
    root_folder.mkdir(parents=True, exist_ok=True)

    log_file = create_new_day(
        log_day=log_day,
        force=force,
        dry_run=dry_run,
        attribs=attribs,
        verbose=verbose,
        root_dir=root_folder,
    )

    if launch_editor:
        if dry_run:
            log.warning(
                f"[Dry Run] Would have created a log file at: {log_file} - cannot launch editor."
            )
        else:
            log.debug(f"Launching editor for log file: {log_file}")
            if platform.system() == "Windows":
                os.startfile(str(log_file))
            elif platform.system() == "Darwin":
                subprocess.run(["open", str(log_file)])
            else:
                subprocess.run(["xdg-open", str(log_file)])


if __name__ == "__main__":
    main()
