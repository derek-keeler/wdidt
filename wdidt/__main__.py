"""new_day.py

Program to create a new daily log file in the WDIDT format.
"""

import datetime
import logging


import click

from . import new_day

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
    help="Added attributes to render the daily log with.",
)
@click.version_option("0.1", "-v", "--version", message="%(version)s")
def main(ago, force, verbose, dry_run, attributes):
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
        f"    attributes={attributes}"
    )

    log_day: datetime.date = datetime.date.today()
    if ago:
        log_day = datetime.date.today() - datetime.timedelta(days=ago)
        log.debug(f"Log file day is being set to {log_day}.")

    new_day.create_new_day(
        log_day=log_day,
        force=force,
        dry_run=dry_run,
        attribs=attributes,
    )


if __name__ == "__main__":
    main()
