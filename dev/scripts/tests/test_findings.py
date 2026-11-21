"""The tests of dev/scripts/findings.sh: `held` passes a check's output on where it passes, and,
where it fails, says what the check of its kind is for around the findings, and gives the check's
exit code."""

from __future__ import annotations

import os
import subprocess
import unittest

from helpers import TOP

SCRIPT = os.path.join(TOP, "dev", "scripts", "findings.sh")


def held(kind: str, command: str) -> subprocess.CompletedProcess[str]:
    """What `held <kind>` gives on the shell command, run as check.sh sources it."""
    return subprocess.run(
        ["sh", "-c", f'. "{SCRIPT}"; held {kind} sh -c "$0"', command],
        capture_output=True,
        text=True,
        check=False,
    )


class HeldTest(unittest.TestCase):
    def test_a_check_that_passes_gives_its_output_alone_and_0(self):
        # When: a check that prints a line and passes runs under held.
        done = held("design", "echo all clear")
        # Then: held prints the line alone, and gives 0.
        self.assertEqual((done.returncode, done.stdout), (0, "all clear\n"))

    def test_a_design_check_that_fails_gives_its_findings_between_what_it_is_for(self):
        # When: a check of the design that prints a finding and exits 3 runs under held.
        done = held("design", "echo 'a.py:1: too complex'; exit 3")
        # Then: the finding stands after what the check is for and before its short form, and
        # held gives the check's exit code.
        self.assertEqual(done.returncode, 3, "the check's exit code")
        before, finding, after = done.stdout.split("\n\n")
        self.assertIn("refactor-code/best-practice.md", before, "the design text first")
        self.assertEqual(finding, "a.py:1: too complex")
        self.assertEqual(
            after,
            "Change the design for its maintainer. Don't change code only to clear a finding.\n",
        )

    def test_a_tests_check_that_fails_gives_its_findings_between_what_it_is_for(self):
        # When: a check of the tests that prints a finding and exits 1 runs under held.
        done = held("tests", "echo 'mutant 7 survived'; exit 1")
        # Then: the finding stands after what the check is for and before its short form.
        self.assertEqual(done.returncode, 1, "the check's exit code")
        before, finding, after = done.stdout.split("\n\n")
        self.assertIn("code/best-practice.md", before, "the tests text first")
        self.assertEqual(finding, "mutant 7 survived")
        self.assertEqual(
            after, "Mend the design or the code. Don't add a test only to clear a finding.\n"
        )


if __name__ == "__main__":
    unittest.main()
