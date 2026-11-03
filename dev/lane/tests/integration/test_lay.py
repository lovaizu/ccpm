"""lay.py run as the developer AI runs it, on a copy of the README's plugin `changelog` taken from
the README's walkthrough, with a stand-in for Claude Code's `claude` on PATH: what `lay.py print`
and `lay.py write` print, set beside what the walkthrough shows, and the files written."""

import os
import re
import subprocess
import sys
import unittest

import helpers
from helpers import testing

LAY = os.path.join(helpers.SCRIPTS, "lay.py")
with open(os.path.join(helpers.LANE, "README.md"), encoding="utf-8") as f:
    README = f.read().split("\n## Walkthrough")[1].split("\n## How it works")[0]
# The walkthrough's blocks, in order: the manifest, writer, the proposal, and the two runs.
BLOCKS = re.findall(r"```[a-z]+\n(.*?)```", README, re.DOTALL)
MANIFEST, WRITER, PROPOSAL, PRINTED, WROTE = BLOCKS
# A stand-in for `claude`, whose `plugin validate` passes.
CLAUDE = "#!/bin/sh\necho '✔ Validation passed'\n"


def shown(block: str) -> str:
    """What the walkthrough shows a run printing, the line of the command left out."""
    return block.split("\n", 1)[1]


class TestLay(testing.FolderTest):
    def setUp(self) -> None:
        super().setUp()
        self.write(os.path.join("changelog", ".claude-plugin", "plugin.json"), MANIFEST)
        self.write(os.path.join("changelog", "agents", "writer.md"), WRITER)
        self.write(helpers.PROPOSED, PROPOSAL)
        self.write(os.path.join("bin", "claude"), CLAUDE)
        os.chmod(os.path.join("bin", "claude"), 0o755)
        self.env = {
            **os.environ,
            "PATH": os.path.join(self.base, "bin") + os.pathsep + os.environ["PATH"],
        }

    def lay(self, action: str, path: str) -> subprocess.CompletedProcess:
        """lay.py run with the action on the path at the root of the repository, base."""
        return subprocess.run(
            [sys.executable, LAY, action, path],
            capture_output=True,
            text=True,
            env=self.env,
            check=False,
        )

    def test_print_prints_what_the_walkthrough_shows(self):
        # Given: the walkthrough's plugin and proposal
        # When: lay.py print is run on the proposal
        done = self.lay("print", helpers.PROPOSED)
        # Then: it prints what the walkthrough shows, and exits 0
        self.assertEqual((done.returncode, done.stdout), (0, shown(PRINTED)))

    def test_write_prints_what_the_walkthrough_shows_and_writes_steps_as_printed(self):
        # Given: the walkthrough's plugin and proposal
        # When: lay.py write is run on the proposal
        done = self.lay("write", helpers.PROPOSED)
        # Then: it prints what the walkthrough shows, the repository's folder put in, and exits 0
        said = shown(WROTE).replace("<the repository>", self.base)
        self.assertEqual((done.returncode, done.stdout), (0, said))
        # And: steps 2 and 3 read as print showed them, and the hook and the lanes are written
        steps = shown(PRINTED).split("\n\n", 1)[1]
        self.assertIn(steps, self.read(os.path.join("changelog", "agents", "writer.md")))
        hooks = self.read_json(os.path.join("changelog", "hooks", "hooks.json"))
        self.assertEqual(hooks, {"hooks": {"PreToolUse": [helpers.ENTRY]}})
        self.assertEqual(
            self.read_json(os.path.join("changelog", "hooks", "lanes.json")), helpers.RULES
        )

    def test_a_stop_is_printed_and_exits_1(self):
        # Given: no claude on PATH
        self.env["PATH"] = os.path.dirname(sys.executable)
        # When: lay.py write is run on the proposal
        done = self.lay("write", helpers.PROPOSED)
        # Then: it says so, and exits 1
        self.assertEqual(
            (done.returncode, done.stdout),
            (1, "lay.py: claude is not on PATH; install Claude Code and run again.\n"),
        )


if __name__ == "__main__":
    unittest.main()
