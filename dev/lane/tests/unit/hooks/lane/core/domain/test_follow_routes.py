"""follow_routes: the orchestrator starts only the subagent it is told to start while a start is
due, and makes no other call then; starts none while one runs in the background, its other calls
going on; and is free once no start is left."""

import unittest

from helpers import follow_routes, routes

DUE = routes.Next("start", "reviewer", ("writer", "written"))
WAIT = routes.Next("wait", "writer", None)
END = routes.Next("end", "", ("reviewer", "good"))


def start(name: str) -> dict:
    """The input of an Agent call starting the subagent of the type."""
    return {"description": "d", "prompt": "p", "subagent_type": name}


class TestAllows(unittest.TestCase):
    def test_while_a_start_is_due_only_that_start_goes_through(self):
        for tool, given, through in (
            ("Agent", start("changelog:reviewer"), True),
            ("Agent", start("changelog:writer"), False),
            ("Agent", start("reviewer"), False),
            ("Agent", {"description": "d", "prompt": "p"}, False),
            ("Read", {"file_path": "CHANGELOG.md"}, False),
        ):
            with self.subTest(given=given):
                # Given: reviewer due
                # When: lead starts reviewer, writer, reviewer by its bare name, a subagent of
                # no type, or reads a file
                # Then: only the start of changelog:reviewer goes through
                self.assertEqual(follow_routes.allows(tool, given, DUE, "changelog"), through)

    def test_while_a_subagent_runs_in_the_background_only_a_start_is_stopped(self):
        for tool, given, through in (
            ("Agent", start("changelog:reviewer"), False),
            ("Agent", start("Explore"), False),
            ("Read", {"file_path": "CHANGELOG.md"}, True),
        ):
            with self.subTest(given=given):
                # Given: writer running in the background
                # When: lead starts a subagent of the plugin or another, or reads a file
                # Then: each start is stopped, and the read goes through
                self.assertEqual(follow_routes.allows(tool, given, WAIT, "changelog"), through)

    def test_while_runs_of_a_fanned_out_subagent_go_only_more_of_them_may_start(self):
        more = routes.Next("wait", "reviewer", None, more=True)
        for tool, given, through in (
            ("Agent", start("changelog:reviewer"), True),
            ("Agent", start("changelog:writer"), False),
            ("Read", {"file_path": "CHANGELOG.md"}, True),
        ):
            with self.subTest(given=given):
                # Given: runs of reviewer, fanned out, running in the background
                # When: lead starts reviewer again, starts writer, or reads a file
                # Then: the further run of reviewer and the read go through, and writer is stopped
                self.assertEqual(follow_routes.allows(tool, given, more, "changelog"), through)

    def test_once_no_start_is_left_every_call_goes_through(self):
        # Given: reviewer's `good`
        # When: lead starts writer
        # Then: it goes through, lead being free
        self.assertTrue(follow_routes.allows("Agent", start("changelog:writer"), END, "changelog"))


class TestEnds(unittest.TestCase):
    def test_the_orchestrator_ends_only_while_no_start_is_due(self):
        for found, ends in ((DUE, False), (WAIT, True), (END, True)):
            with self.subTest(found=found):
                # Given: a start due, a subagent running in the background, or no start left
                # When: lead is about to end
                # Then: it is kept going only while the start is due
                self.assertEqual(follow_routes.ends(found), ends)


class TestStarted(unittest.TestCase):
    def test_the_subagent_a_call_starts_is_named_where_it_is_one_of_the_routes(self):
        for tool, given, name in (
            ("Agent", start("changelog:writer"), "writer"),
            ("Agent", start("changelog:other"), None),
            ("Agent", start("other:writer"), None),
            ("Agent", {"prompt": "p"}, None),
            ("Read", start("changelog:writer"), None),
        ):
            with self.subTest(given=given, tool=tool):
                # Given: the routes of lead, writer and reviewer
                # When: a call starts writer, a subagent of the plugin no route names, one of
                # another plugin, one of no type, or is no Agent call
                # Then: only the first is a start of the routes, of writer
                found = follow_routes.started(tool, given, ["writer", "reviewer"], "changelog")
                self.assertEqual(found, name)


if __name__ == "__main__":
    unittest.main()
