"""new_day.py

Program to create a new daily log file in the WDIDT format.

Usage:
  new_day.py [-a <num_days> | --ago=<num_days>] [-f | --force] [-V | --verbose] [-d | --dry-run]
  new_day.py -h | --help
  new_day.ph -v | --version


Options:
  -h --help             Show this help and exit.
  -v --version          Show the version of this script and exit.
  -f --force            Always create the log file, even if it exists.
  -V --verbose          Show verbose logs during processing.
  -a --ago <num_days>   Create a log file for num_days ago.
  -d --dry-run          Run without creating the new daily log. Report what would be written.
"""

import datetime
import docopt
import logging
import os
import pathlib
import shutil
import sys

logging.basicConfig(
    format="[%(asctime)s]%(name)s.%(levelname)s: %(message)s", level=logging.ERROR
)


def get_template(base_dir: pathlib.Path) -> pathlib.Path:
    """Return the absolute path to the raw template for daily logs."""

    log.debug("get_template")
    return base_dir.joinpath("daily_schedule-j.md")


def get_log_folder_for_month(
    log_folder_base: pathlib.Path, now: datetime
) -> pathlib.Path:
    """Get the folder to contain today's log."""

    log.debug("get_log_folder_for_month")

    log_epoch_foldername = "day-tracking-juniper"
    log_month_foldername = now.strftime("%m_%B_%y")
    log.debug(f"folder name = {log_epoch_foldername}/{log_month_foldername}.")
    return log_folder_base.joinpath(log_epoch_foldername, log_month_foldername)


def create_new_log(
    now: datetime,
    template_file: pathlib.Path,
    log_folder: pathlib.Path,
    force: bool = False,
    dry_run: bool = False,
):
    """Copy the template to the log folder and update any dynamic elements within the file."""

    log.debug("create_new_log")

    log_file_name = now.strftime("%b_%d_%y.md").lower()
    log_file_path = log_folder.joinpath(log_file_name)
    if not log_file_path.exists() or force:
        log.debug(f"Creating log file at {log_file_path}")
        if dry_run and not log_folder.exists():
            print(f"[Dry Run] Would have created a folder '{log_folder.absolute()}'")

        if dry_run:
            print(
                f"[Dry Run] Would have created copy of file '{template_file.absolute()}'"
            )
            print(f"[Dry Run]    into file '{log_file_path.absolute()}'")
        else:
            log_folder.mkdir(parents=True, exist_ok=True)
            shutil.copy2(template_file, log_file_path)


def create_new_day(log_day: datetime, force: bool, dry_run: bool):
    log.debug("create_new_day")
    if log_day is None:
        log_day: datetime = datetime.date.today()
        log.debug(f'Default log day being used (today={log_day.strftime("%b_%d_%y")})')

    base_folder: pathlib.Path = pathlib.Path(__file__).resolve().parent
    template: pathlib.Path = get_template(base_folder)
    log_folder: pathlib.Path = get_log_folder_for_month(base_folder, log_day)
    create_new_log(log_day, template, log_folder, force, dry_run)


if __name__ == "__main__":
    opts = docopt.docopt(doc=__doc__, argv=sys.argv[1:], help=True, version="0.1")

    log_level = logging.INFO
    if opts.get("--verbose", False):
        log_level = logging.DEBUG

    log = logging.getLogger("new_day")
    log.setLevel(log_level)

    log.debug("Arguments given:")
    log.debug(opts)

    log_day = datetime.date.today()
    if opts.get("--ago", None):
        log_day = datetime.date.today() - datetime.timedelta(
            days=int(opts.get("--ago", 0))
        )
        log.debug(f"Log file day is being set to {log_day}.")

    create_new_day(log_day, opts.get("--force", False), opts.get("--dry-run", False))
