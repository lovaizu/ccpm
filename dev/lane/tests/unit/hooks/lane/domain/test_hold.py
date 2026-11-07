"""hold: a command is held only where it is one the lane names, whole, as the subagent reads it."""

import unittest

import helpers
from helpers import hold


class TestAllows(unittest.TestCase):
    def test_a_command_named_whole_is_held_and_any_other_is_not(self):
        for command, held in (("git push", True), ("git push\n", True), ("git push -f", False)):
            with self.subTest(command=command):
                # Given: hold naming git push
                # When: the subagent runs it, ended by a line break, or another command
                # Then: git push is held, and the other is not
                self.assertEqual(hold.allows(command, ["git push"], "/p", "/w"), held)
        # And: a command naming the plugin's folder is matched as the subagent reads it
        named = f"{helpers.GIVE} writer x"
        self.assertTrue(hold.allows("python3 /p/hooks/lane/result.py writer x", [named], "/p", "/"))


if __name__ == "__main__":
    unittest.main()
