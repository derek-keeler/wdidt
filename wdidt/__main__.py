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

from . import new_day

logging.basicConfig(
    format="[%(asctime)s]%(name)s.%(levelname)s: %(message)s", level=logging.ERROR
)

log = logging.getLogger(__name__)

if __name__ == "__main__":
    opts = docopt.docopt(doc=__doc__, argv=sys.argv[1:], help=True, version="0.1")

    log_level = logging.INFO
    if opts.get("--verbose", False):
        log_level = logging.DEBUG

    log.setLevel(log_level)

    log.debug("Arguments given:")
    log.debug(opts)

    log_day = datetime.date.today()
    if opts.get("--ago", None):
        log_day = datetime.date.today() - datetime.timedelta(
            days=int(opts.get("--ago", 0))
        )
        log.debug(f"Log file day is being set to {log_day}.")

    new_day.create_new_day(log_day, opts.get("--force", False), opts.get("--dry-run", False))
