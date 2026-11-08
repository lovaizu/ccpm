"""The tests of lefthook.yml: the commits and CI check the prose by one version of lovaizu/checks,
each pattern left out of the check matches a file that git holds, and the pre-push job gets what
git gives the hook."""

from __future__ import annotations

import fnmatch
import os
import re
import subprocess
import unittest

from helpers import TOP


def read(*path):
    with open(os.path.join(TOP, *path)) as file:
        return file.read()


class LefthookTest(unittest.TestCase):
    def test_ci_checks_by_the_version_the_commits_check_by(self):
        # Given: the version lefthook.yml names, and the version the step of CI names.
        [named] = re.findall(r"^    ref: (\S+)$", read("lefthook.yml"), re.MULTILINE)
        [ci] = re.findall(
            r"uses: lovaizu/checks@[0-9a-f]{40} # (\S+)$",
            read(".github/workflows/tests.yml"),
            re.MULTILINE,
        )
        # Then: the two match.
        self.assertEqual(ci, named)

    def test_each_pattern_left_out_matches_a_file_git_holds(self):
        # Given: the patterns that pre-commit leaves out, and the files git holds.
        text = read("lefthook.yml")
        block = text[text.index("pre-commit:\n  exclude:\n") :].split("\n\n")[0]
        left = re.findall(r'^    - "([^"]+)"$', block, re.MULTILINE)
        held = set(
            subprocess.run(
                ["git", "ls-files"], cwd=TOP, capture_output=True, text=True, check=True
            ).stdout.splitlines()
        )
        # Then: each pattern matches a file git holds, so that none stays on the list once its
        # files go.
        self.assertTrue(left)
        self.assertEqual([glob for glob in left if not fnmatch.filter(held, glob)], [])

    def test_the_pre_push_job_gets_what_git_gives_the_hook(self):
        # Given: the pre-push job.
        text = read("lefthook.yml")
        job = text[text.index("pre-push:\n") :]
        # Then: it runs pre-push.sh with the standard input git gives the hook, the commits pushed.
        self.assertIn("run: sh dev/scripts/pre-push.sh\n", job)
        self.assertIn("use_stdin: true\n", job)


if __name__ == "__main__":
    unittest.main()
