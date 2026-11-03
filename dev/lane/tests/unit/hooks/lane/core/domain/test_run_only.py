"""run_only: a command goes through only where it is, whole, one of the commands the lane names,
the plugin's folder put in for `${CLAUDE_PLUGIN_ROOT}` as Claude Code puts it in the step."""

import unittest

from helpers import run_only

ROOT = "/p/changelog"


def allows(command: str, takes: list) -> bool:
    """Whether run_only taking the commands lets the command through, run in /w."""
    return run_only.allows(command, takes, ROOT, "/w")


class TestAllows(unittest.TestCase):
    def test_a_command_named_goes_through(self):
        for command in ("git log --oneline", "git diff", "  git log --oneline\n"):
            with self.subTest(command=command):
                # Given: run_only naming git log --oneline and git diff
                # When: the subagent runs one of them, or one with blanks around it
                # Then: it goes through
                self.assertTrue(allows(command, ["git log --oneline", "git diff"]))

    def test_any_other_command_is_stopped(self):
        for command in (
            "git commit -m entries",
            "git log --oneline -5",
            "git log  --oneline",
            "cd /w && git log --oneline",
            "git log --oneline; git commit -m m",
            "git log",
            "",
        ):
            with self.subTest(command=command):
                # Given: run_only naming git log --oneline
                # When: the subagent runs another command, the command with more words, other
                # blanks between them, after another, before another, fewer words, or nothing
                # Then: it is stopped, as only the command named, whole, goes through
                self.assertFalse(allows(command, ["git log --oneline"]))

    def test_a_command_naming_the_plugins_folder_is_matched_as_the_subagent_reads_it(self):
        take = "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py writer done"
        for command, through in (
            (f"python3 {ROOT}/hooks/lane/result.py writer done", True),
            (take, False),
        ):
            with self.subTest(command=command):
                # Given: run_only naming a script by the plugin's folder
                # When: the subagent runs it by the folder Claude Code put in, or as written
                # Then: the folder put in goes through, as the subagent read it, and the other not
                self.assertEqual(allows(command, [take]), through)


if __name__ == "__main__":
    unittest.main()
