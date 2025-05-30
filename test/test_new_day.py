import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from datetime import date
import tempfile
import shutil
import json

import wdidt.new_day as new_day


class TestNewDay(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.log_folder_base = Path(self.temp_dir)
        self.today = date(2025, 5, 29)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_get_template(self):
        base_dir = Path(__file__).parent / "templates"
        expected = base_dir / "daily/default.md"
        result = new_day.get_template(base_dir=base_dir, template_name="default")
        self.assertEqual(result, expected)

    def test_get_log_folder_for_month(self):
        folder = new_day.get_log_folder_for_month(self.log_folder_base, self.today)
        self.assertTrue(folder.as_posix().endswith("day-tracking/05_May_25"))

    def test_create_new_log_creates_file(self):
        log_folder = self.log_folder_base / "day-tracking/05_May_25"
        content = "test content"
        new_day.create_new_log(
            self.today, content, log_folder, force=True, dry_run=False
        )
        log_file = log_folder / "may_29_25.md"
        self.assertTrue(log_file.exists())
        with open(log_file) as f:
            self.assertEqual(f.read(), content)

    def test_create_new_log_dry_run(self):
        log_folder = self.log_folder_base / "day-tracking/05_May_25"
        content = "test content"
        with patch("builtins.print") as mock_print:
            new_day.create_new_log(
                self.today, content, log_folder, force=True, dry_run=True
            )
            mock_print.assert_any_call(
                f"[Dry Run] Would have created a logfile here: '{(log_folder / 'may_29_25.md').absolute()}'"
            )
        self.assertFalse((log_folder / "may_29_25.md").exists())

    def test_create_new_day_basic(self):
        # Setup a fake template file
        template_dir = Path(self.temp_dir) / "templates"
        template_dir.mkdir(parents=True, exist_ok=True)
        template_file = template_dir / "daily_default.md"
        template_file.write_text("Date: {{ date }}\n")
        # Patch Path(__file__).parent.joinpath to use our temp template dir
        with patch("wdidt.new_day.Path") as mock_path:
            mock_path.return_value = template_dir
            # Patch jinja2.Environment to use FileSystemLoader on our temp dir
            with patch(
                "jinja2.Environment.get_template",
                return_value=MagicMock(
                    render=MagicMock(return_value="Date: Thursday May 29, 2025\n")
                ),
            ):
                new_day.create_new_day(
                    log_day=self.today,
                    force=True,
                    dry_run=False,
                    attribs=None,
                    verbose=False,
                    root_dir=self.log_folder_base,
                )
        # Check file created
        log_folder = new_day.get_log_folder_for_month(self.log_folder_base, self.today)
        log_file = log_folder / "may_29_25.md"
        self.assertTrue(log_file.exists())

    def test_create_new_day_with_attribs(self):
        attribs = json.dumps({"extra": "value"})
        template_dir = Path(self.temp_dir) / "templates"
        template_dir.mkdir(parents=True, exist_ok=True)
        template_file = template_dir / "daily_default.md"
        template_file.write_text("Extra: {{ extra }}\n")
        with patch("wdidt.new_day.Path") as mock_path:
            mock_path.return_value = template_dir
            with patch(
                "jinja2.Environment.get_template",
                return_value=MagicMock(render=MagicMock(return_value="Extra: value\n")),
            ):
                new_day.create_new_day(
                    log_day=self.today,
                    force=True,
                    dry_run=False,
                    attribs=attribs,
                    verbose=False,
                    root_dir=self.log_folder_base,
                )
        log_folder = new_day.get_log_folder_for_month(self.log_folder_base, self.today)
        log_file = log_folder / "may_29_25.md"
        self.assertTrue(log_file.exists())
