"""check.py run as a pinner runs it, `python3 <pin's folder>/scripts/check.py <design tree>`, from
the folder the pinner works in, on real files: the exit code and what it prints."""

import os
import subprocess
import sys
import unittest

import helpers
from helpers import decision, made

CHECK = os.path.join(helpers.SCRIPTS, "check.py")


class TestCheckCommand(helpers.testing.FolderTest):
    def ran(self, path: str) -> subprocess.CompletedProcess:
        """check.py run on the path as a command, from the test's folder."""
        return subprocess.run(
            [sys.executable, CHECK, path],
            capture_output=True,
            text=True,
            cwd=self.base,
            check=False,
        )

    def test_the_walkthrough_tree_holds(self):
        # Given: the README walkthrough's tree, kept where the walkthrough keeps it
        path = os.path.join(".pin", "20261103-notes-json", "design-tree.json")
        self.write_json(path, helpers.walkthrough())
        # When: check.py is run on it
        done = self.ran(path)
        # Then: it gives 0, and says the tree holds
        self.assertEqual(done.returncode, 0)
        self.assertIn(f"check.py: {path} holds:", done.stdout)

    def test_a_tree_that_does_not_hold_gives_1(self):
        # Given: a tree with a question no decision serves
        self.write_json("t.json", made(decision("D1"), questions=("Q1", "Q2")))
        # When: check.py is run on it
        done = self.ran("t.json")
        # Then: it gives 1, naming the question
        self.assertEqual(
            (done.returncode, done.stdout.splitlines()[-1]), (1, "- Q2 is served by no decision.")
        )

    def test_a_file_not_json_gives_2_on_the_error_output(self):
        # Given: a file that is not JSON
        self.write("t.json", "not json")
        # When: check.py is run on it
        done = self.ran("t.json")
        # Then: it gives 2, and says why on its error output alone
        self.assertEqual((done.returncode, done.stdout), (2, ""))
        self.assertTrue(
            done.stderr.startswith("check.py: could not check t.json:\n- it is not JSON")
        )


if __name__ == "__main__":
    unittest.main()
