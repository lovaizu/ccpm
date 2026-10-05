"""Tests for pith's result check, run as pith runs it: the entry script, from the repository root."""

import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRY = os.path.join(PLUGIN_ROOT, "skills", "pith", "scripts", "check_result.py")

ESSENTIALS = textwrap.dedent("""\
    # README

    Who reads this and why.

    - What did you take as the gain on reading the opening?

        Why the question matters, with a list inside it:

        - not a question

    - How far did you get installing from this README alone?

    ```
    - not a question either
    ```
    """)

WORK = textwrap.dedent("""\
    # tool

    You stop watching the build:
    tool tells you only when you must decide.

    ## Install

    Run `pip install tool`.
    """)

GOOD_RESULT = textwrap.dedent("""\
    # Check: docs/README.md

    Target: docs/README.md
    Receiver and purpose: someone new deciding whether to use tool
    Aim: the reader sees the gain first and can install alone.

    ## readme.md: What did you take as the gain on reading the opening?

    Report: I read that I can stop
    watching the build.

    - Good: `docs/README.md:3-4` the reader sees the gain at once
      - Evidence (work): "You stop watching the build: tool tells you"

    ## readme.md: How far did you get installing from this README alone?

    Report: I ran pip install, then looked elsewhere for a config file.

    - More: `docs/README.md:8` the reader leaves the README to find the config
      - Evidence (report): "looked elsewhere for a config file"
      - Left because: the config is not decided yet
    """)


class CheckResultTest(unittest.TestCase):

    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.write("docs/README.md", WORK)
        self.write("essentials/readme.md", ESSENTIALS)

    def tearDown(self):
        shutil.rmtree(self.root)

    def write(self, path, text):
        full = os.path.join(self.root, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(text)

    def run_check(self, result_text):
        self.write(".writ/open/01-report-readme.md", result_text)
        return subprocess.run(
            [sys.executable, ENTRY, ".writ/open/01-report-readme.md", "essentials/readme.md"],
            cwd=self.root, capture_output=True, text=True)

    def assertProblems(self, result, *fragments):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        lines = result.stdout.strip().splitlines()
        self.assertEqual(len(lines), len(fragments), result.stdout)
        for line, fragment in zip(lines, fragments):
            self.assertIn(fragment, line)
            self.assertTrue(line.startswith(".writ/open/01-report-readme.md"), line)

    def test_given_a_result_in_form_when_checked_then_passes_with_no_output(self):
        # Given
        text = GOOD_RESULT
        # When
        result = self.run_check(text)
        # Then
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")

    def test_given_no_essentials_file_when_checked_then_stops_with_usage(self):
        # Given
        command = [sys.executable, ENTRY, ".writ/open/01-report-readme.md"]
        # When
        result = subprocess.run(command, cwd=self.root, capture_output=True, text=True)
        # Then
        self.assertEqual(result.returncode, 2)
        self.assertIn("usage: check_result.py", result.stderr)

    def test_given_a_missing_essentials_file_when_checked_then_stops(self):
        # Given
        self.write(".writ/open/01-report-readme.md", GOOD_RESULT)
        command = [sys.executable, ENTRY, ".writ/open/01-report-readme.md", "essentials/design.md"]
        # When
        result = subprocess.run(command, cwd=self.root, capture_output=True, text=True)
        # Then
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "essentials/design.md: no such file\n")

    # every question answered

    def test_given_a_question_written_over_two_lines_when_checked_then_read_as_one(self):
        # Given
        self.write("essentials/readme.md", ESSENTIALS.replace(
            "- How far did you get installing from this README alone?",
            "- How far did you get installing\nfrom this README alone?"))
        # When
        result = self.run_check(GOOD_RESULT)
        # Then
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_given_a_question_without_section_when_checked_then_stops(self):
        # Given
        text = GOOD_RESULT.split("## readme.md: How far")[0]
        # When
        result = self.run_check(text)
        # Then
        self.assertProblems(result, "no section `## readme.md: How far did you get")

    def test_given_a_section_without_good_or_more_when_checked_then_stops(self):
        # Given
        text = GOOD_RESULT.split("- More:")[0]
        # When
        result = self.run_check(text)
        # Then
        self.assertProblems(result, ":15: no Good or More")

    def test_given_a_question_reworded_when_checked_then_stops(self):
        # Given
        text = GOOD_RESULT.replace("on reading the opening", "from the opening")
        # When
        result = self.run_check(text)
        # Then
        self.assertProblems(result, "no section `## readme.md: What did you take")

    # locations exist

    def test_given_a_location_in_a_missing_file_when_checked_then_stops(self):
        # Given
        text = GOOD_RESULT.replace("`docs/README.md:8`", "`docs/INSTALL.md:8`")
        # When
        result = self.run_check(text)
        # Then
        self.assertProblems(result, ":19: More location `docs/INSTALL.md:8`: no such file")

    def test_given_a_line_past_the_end_when_checked_then_stops(self):
        # Given
        text = GOOD_RESULT.replace("`docs/README.md:3-4`", "`docs/README.md:3-40`")
        # When
        result = self.run_check(text)
        # Then
        self.assertProblems(result, ":12: Good location `docs/README.md:3-40`: outside")

    def test_given_an_item_without_location_when_checked_then_stops(self):
        # Given
        text = GOOD_RESULT.replace("`docs/README.md:8` ", "")
        # When
        result = self.run_check(text)
        # Then
        self.assertProblems(result, ":19: More has no location")

    def test_given_a_location_not_in_path_line_form_when_checked_then_stops(self):
        # Given
        text = GOOD_RESULT.replace("`docs/README.md:3-4`", "`docs/README.md, opening`")
        # When
        result = self.run_check(text)
        # Then
        self.assertProblems(result, ":12: Good location `docs/README.md, opening` is not `path:line`",
                            ":13: evidence (work) has no located file to look in")

    # evidence found

    def test_given_evidence_not_in_quotes_when_checked_then_stops(self):
        # Given
        text = GOOD_RESULT.replace('"looked elsewhere for a config file"', "looked elsewhere")
        # When
        result = self.run_check(text)
        # Then
        self.assertProblems(result, ':20: evidence (report) is not a quote in "..."')

    def test_given_work_evidence_not_in_the_file_when_checked_then_stops(self):
        # Given
        text = GOOD_RESULT.replace("You stop watching the build", "You never watch the build")
        # When
        result = self.run_check(text)
        # Then
        self.assertProblems(result, ":13: evidence (work) not found in docs/README.md")

    def test_given_report_evidence_not_in_the_report_when_checked_then_stops(self):
        # Given
        text = GOOD_RESULT.replace('"looked elsewhere for a config file"', '"could not install"')
        # When
        result = self.run_check(text)
        # Then
        self.assertProblems(result, ":20: evidence (report) not found")

    def test_given_report_evidence_from_another_section_when_checked_then_stops(self):
        # Given
        text = GOOD_RESULT.replace('"looked elsewhere for a config file"', '"I can stop"')
        # When
        result = self.run_check(text)
        # Then
        self.assertProblems(result, ":20: evidence (report) not found")

    def test_given_an_item_without_evidence_when_checked_then_stops(self):
        # Given
        text = GOOD_RESULT.replace('  - Evidence (work): "You stop watching the build: tool tells you"\n', "")
        # When
        result = self.run_check(text)
        # Then
        self.assertProblems(result, ":12: Good has no evidence")


if __name__ == "__main__":
    unittest.main()
