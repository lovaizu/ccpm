"""The tests of dev/scripts/mermaid.sh: it fails on a Mermaid diagram that GitHub can't draw, and
fails, saying why, where it can't parse the diagrams at all, as a skipped check would pass them."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest

from helpers import GIT_ENV, TOP, without

SCRIPT = os.path.join(TOP, "dev", "scripts", "mermaid.sh")


class MermaidTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="mermaid-")
        self.addCleanup(shutil.rmtree, self.dir)
        self.repo = os.path.join(self.dir, "repo")
        self.env = dict(os.environ, **GIT_ENV)
        subprocess.run(["git", "init", "-q", self.repo], env=self.env, check=True)

    def holding(self, diagram):
        """The repository, with a document that holds the diagram."""
        with open(os.path.join(self.repo, "doc.md"), "w") as file:
            file.write(f"# Doc\n\n```mermaid\n{diagram}\n```\n")
        subprocess.run(["git", "add", "doc.md"], cwd=self.repo, env=self.env, check=True)

    def run_on(self, script=SCRIPT, env=None):
        return subprocess.run(
            ["sh", script],
            cwd=self.repo,
            env=env or self.env,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_a_diagram_github_draws_passes(self):
        # Given: a diagram that parses.
        self.holding("flowchart LR\n  a --> b")
        # When: the check runs.
        done = self.run_on()
        # Then: it passes.
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def test_a_diagram_github_cannot_draw_fails_with_its_file(self):
        # Given: a diagram that doesn't parse.
        self.holding("flowchart LR\n  a -->")
        # When: the check runs.
        done = self.run_on()
        # Then: it fails, and names the document.
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("doc.md", done.stdout + done.stderr)

    def test_no_parser_fails_and_says_how_to_get_it(self):
        # Given: a copy of the check with no node_modules beside it.
        copy = os.path.join(self.dir, "scripts")
        os.makedirs(copy)
        shutil.copy(SCRIPT, copy)
        self.holding("flowchart LR\n  a --> b")
        # When: it runs.
        done = self.run_on(os.path.join(copy, "mermaid.sh"))
        # Then: it fails, and says to run npm ci there.
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("npm ci --ignore-scripts", done.stderr)

    def test_no_node_fails_and_says_how_to_get_it(self):
        # Given: no node on PATH.
        env = dict(self.env, PATH=without(self.env["PATH"], "node", os.path.join(self.dir, "bin")))
        self.holding("flowchart LR\n  a --> b")
        # When: the check runs.
        done = self.run_on(env=env)
        # Then: it fails, and says to install Node.js.
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("install Node.js", done.stderr)


if __name__ == "__main__":
    unittest.main()
