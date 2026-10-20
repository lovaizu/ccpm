"""The entry every plugin's hooks run: each check on the event Claude Code hands it, from the folder
the event comes from, the use stopped with what the checks say."""

import io
import json
import os
import sys
import unittest

HOOKS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "common", "hooks"
)
sys.path.insert(0, os.path.normpath(HOOKS))
sys.path.insert(0, os.path.join(os.path.normpath(HOOKS), "..", "..", "dev", "common"))

import hook
import testing


class Says:
    """A check that says what it is given, recording where it ran."""

    def __init__(self, *said):
        self.said = list(said)
        self.ran_in = None

    def check(self, event):
        self.ran_in = os.getcwd()
        return self.said


class TestRun(testing.FolderTest):
    def ran(self, *checks):
        err = io.StringIO()
        event = {"cwd": self.base, "tool_name": "Bash", "tool_input": {}}
        os.chdir("/")
        code = hook.run("p", checks, io.StringIO(json.dumps(event)), err)
        return code, err.getvalue()

    def test_checks_saying_something_stop_with_what_each_says(self):
        # Given: two checks, each saying something
        # When: the entry runs them on an event
        # Then: it stops, with what both say, one to a line, headed by the plugin's name, each
        # check run from the folder the event comes from
        first, second = Says("a"), Says("b")
        self.assertEqual(self.ran(first, Says(), second), (hook.STOPPED, "p: a\nb\n"))
        self.assertEqual((first.ran_in, second.ran_in), (self.base, self.base))

    def test_checks_saying_nothing_let_the_use_go_on(self):
        # Given: checks that say nothing, or none
        # When: the entry runs them
        # Then: it gives 0 and writes nothing
        self.assertEqual(self.ran(Says(), Says()), (0, ""))
        self.assertEqual(self.ran(), (0, ""))


if __name__ == "__main__":
    unittest.main()
