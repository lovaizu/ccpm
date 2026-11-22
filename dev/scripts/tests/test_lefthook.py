"""The tests of ccpm's checks of lovaizu/repofiles: CI checks the prose by the version that the
commits check by, and the pre-push job gets what git gives the hook."""

from __future__ import annotations

import os
import re
import unittest

from helpers import TOP


def read(*path):
    with open(os.path.join(TOP, *path)) as file:
        return file.read()


class LefthookTest(unittest.TestCase):
    def test_the_nightly_run_checks_the_prose_by_the_commit_that_lint_checks_by(self):
        # Given: the step of lovaizu/repofiles in Lint, which setup.sh puts, and in Nightly.
        def step(workflow):
            return re.findall(
                r"uses: (lovaizu/repofiles@[0-9a-f]{40} # \S+)$",
                read(".github", "workflows", workflow),
                re.MULTILINE,
            )

        # Then: the two name the same commit and version.
        self.assertEqual(step("nightly.yml"), step("lint.yml"))

    def test_the_pre_push_job_gets_what_git_gives_the_hook(self):
        # Given: the pre-push job of ccpm's settings.
        text = read("lefthook-repo.yml")
        job = text[text.index("pre-push:\n") :]
        # Then: it runs pre-push.sh with the standard input git gives the hook, the commits pushed.
        self.assertIn("run: sh dev/scripts/pre-push.sh\n", job)
        self.assertIn("use_stdin: true\n", job)


if __name__ == "__main__":
    unittest.main()
