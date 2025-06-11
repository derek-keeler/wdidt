"""Create a new day's log file."""

import logging
from pathlib import Path
from pprint import pformat
from datetime import date
from typing import Dict, Optional, Any

import jinja2

logging.basicConfig(
    format="[%(asctime)s]%(name)s.%(levelname)s: %(message)s", level=logging.ERROR
)

log = logging.getLogger(__name__)


def get_template(
    base_dir: Path,
    template_category: str = "daily",
    template_name: str = "default.md",
) -> Path:
    """Return the absolute path to the raw template for daily logs."""

    log.debug("get_template")

    return base_dir.joinpath(f"{template_category}/{template_name}.md")


def get_jinja_template(
    template_dir: Path,
    template_category: str = "daily",
    template_name: str = "default",
    template_ext: str = ".md",
) -> jinja2.Template:

    template = template_dir.joinpath(
        f"templates/{template_category}/{template_name}{template_ext}"
    )
    return jinja2.Template(template.read_text(encoding="utf8"))


def get_log_folder_for_month(log_folder_base: Path, now: date) -> Path:
    """Get the folder to contain today's log."""

    log.debug("get_log_folder_for_month")

    log_epoch_foldername = "day-tracking"
    log_month_foldername = now.strftime("%m_%B_%y")
    log.debug(f"folder name = {log_epoch_foldername}/{log_month_foldername}.")
    return log_folder_base.joinpath(log_epoch_foldername, log_month_foldername)


def create_new_log(
    now: date,
    template_content: str,
    log_folder: Path,
    force: bool = False,
    dry_run: bool = False,
) -> Path:
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
                f"[Dry Run] Would have created a logfile here: '{log_file_path.absolute()}'"
            )
        else:
            log_folder.mkdir(parents=True, exist_ok=True)
            # shutil.copy2(template_file, log_file_path)
            with open(log_file_path, "w") as template_file:
                template_file.write(template_content)

    return (
        log_file_path.absolute()
    )  # Return the absolute path of the created log file, or the intended path if dry_run is True.


def create_new_day(
    log_day: Optional[date],
    force: bool,
    dry_run: bool,
    attribs: Optional[Dict[str, Any]],
    verbose: bool,
    root_dir: Path,
) -> Path:
    """Create a new day's log file with the given attributes."""
    if verbose:
        log.setLevel(logging.DEBUG)

    log.debug("create_new_day")
    if log_day is None:
        day = date.today()
    else:
        day = log_day
    log.debug(f"Log day set to {day.strftime('%b_%d_%y')}")

    props: Dict[str, Any] = {}
    if attribs is not None:
        props = attribs
        log.debug("Properties aquired from command line:")
        log.debug(pformat(props, width=120))

    template_path = Path(__file__).parent.joinpath("templates")
    jenv = jinja2.Environment(
        loader=jinja2.FileSystemLoader(searchpath=template_path.absolute())
    )
    template = jenv.get_template("daily_default.md")
    log_folder: Path = get_log_folder_for_month(root_dir, day)
    template_values: Dict[str, Any] = {
        "date": day,
    }
    template_values.update(props)
    log.debug(f"Template values: {template_values}")
    txt = template.render(template_values)
    log_file = create_new_log(day, txt, log_folder, force, dry_run)

    return log_file
