"""A held command on a run, each path of its sequence in dev/lane/architecture.md from start to
end: writer holding `git add CHANGELOG.md` for the person's approval beside the README's lanes,
laid by `lay.py write` on a copy of `changelog`, the hooks' commands as laid run in sh by a double
of Claude Code, which puts the command to the person, a set answer, as its permission prompt
does."""

import subprocess
import unittest

import helpers
from helpers import testing

WRITER = testing.Run("changelog:writer", "w1")
ADD = "git add CHANGELOG.md"
SAID = f"changelog: Run `{ADD}` only with the person's approval."


class TestHeldCommand(helpers.RunTest):
    def setUp(self) -> None:
        super().setUp()
        given = self.ux_proposal("changelog.json")
        held = {"lane": "hold", "takes": [ADD]}
        given["subagents"][0]["steps"][1]["lanes"].append(held)
        self.lay(given)
        self.claude.start(None, WRITER, "Write the entries and stage them.")
        self.claude.call(WRITER, "Write", {"file_path": "CHANGELOG.md", "content": "x\n"})

    def staged(self) -> str:
        """The files staged in the project."""
        done = subprocess.run(
            ["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True
        )
        return done.stdout

    def held(self, yes: bool) -> testing.Told:
        """writer's run of the held command, the person answering yes or no."""
        self.claude.answers = [yes]
        return self.claude.call(WRITER, "Bash", {"command": ADD, "description": "d"})

    def test_the_person_says_yes_and_the_command_runs(self):
        # Given: writer holding git add CHANGELOG.md, CHANGELOG.md written
        # When: writer runs it, and the person says yes
        told = self.held(True)
        # Then: it was asked of the person with hold's sentence, and it ran
        self.assertEqual((told.decision(), told.reason(), told.made), ("ask", SAID, True))
        self.assertEqual(self.staged(), "CHANGELOG.md\n")
        self.assertEqual(self.claude.answers, [])

    def test_the_person_says_no_and_the_command_does_not_run(self):
        # Given: writer holding git add CHANGELOG.md, CHANGELOG.md written
        # When: writer runs it, and the person says no
        told = self.held(False)
        # Then: it was asked of the person with hold's sentence, and it did not run
        self.assertEqual((told.decision(), told.reason(), told.made), ("ask", SAID, False))
        self.assertEqual(self.staged(), "")


if __name__ == "__main__":
    unittest.main()
