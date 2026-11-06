"""follow_routes: within a run, the main conversation makes only the start it is told to make while
a start is due; makes none while a subagent runs in the background, but more starts of one fanned
out; and makes any once no start is left. A start is an Agent call of a subagent, or a Skill call
of a dependency's skill."""

import unittest

from helpers import follow_routes, routes

DUE = routes.Next("start", "reviewer", ("writer", "written"))
WAIT = routes.Next("wait", "writer", None)
END = routes.Next("end", "", ("reviewer", "good"))


def start(name: str) -> dict:
    """The input of an Agent call starting the subagent of the type."""
    return {"description": "d", "prompt": "p", "subagent_type": name}


class TestResumes(unittest.TestCase):
    def test_only_a_message_sent_to_one_of_the_runs_resumes_it(self):
        for tool, given, resumes in (
            ("SendMessage", {"to": "w1", "message": "m"}, True),
            ("SendMessage", {"to": "w2", "message": "m"}, False),
            ("SendMessage", {"message": "m"}, False),
            # Tools named before and after SendMessage, given a `to` of the run.
            ("Read", {"to": "w1"}, False),
            ("Write", {"to": "w1"}, False),
        ):
            with self.subTest(tool=tool, given=given):
                # Given: the run w1 among the runs
                # When: lead sends a message to w1, to another run, to none, or calls another
                # tool given w1
                # Then: only the message to w1 resumes one of the runs
                self.assertEqual(follow_routes.resumes(tool, given, ["w1"]), resumes)


class TestAllows(unittest.TestCase):
    def test_while_a_start_is_due_only_that_start_goes_through(self):
        for tool, given, through in (
            ("Agent", start("changelog:reviewer"), True),
            ("Agent", start("changelog:writer"), False),
            ("Agent", start("reviewer"), False),
            ("Agent", {"description": "d", "prompt": "p"}, False),
            ("Skill", {"skill": "changelog:reviewer"}, False),
        ):
            with self.subTest(given=given):
                # Given: reviewer due
                # When: the main conversation starts reviewer, writer, reviewer by its bare name,
                # a subagent of no type, or calls a skill of reviewer's name
                # Then: only the start of changelog:reviewer goes through
                self.assertEqual(follow_routes.allows(tool, given, DUE, "changelog"), through)

    def test_while_a_subagent_runs_in_the_background_every_start_is_stopped(self):
        for tool, given, through in (
            ("Agent", start("changelog:reviewer"), False),
            ("Agent", start("changelog:writer"), False),
        ):
            with self.subTest(given=given):
                # Given: writer running in the background
                # When: the main conversation starts reviewer, or writer again
                # Then: each start is stopped
                self.assertEqual(follow_routes.allows(tool, given, WAIT, "changelog"), through)

    def test_while_runs_of_a_fanned_out_subagent_go_only_more_of_them_may_start(self):
        more = routes.Next("wait", "reviewer", None, more=True)
        for tool, given, through in (
            ("Agent", start("changelog:reviewer"), True),
            ("Agent", start("changelog:writer"), False),
        ):
            with self.subTest(given=given):
                # Given: starts of reviewer, fanned out, running in the background
                # When: the main conversation starts reviewer again, or starts writer
                # Then: the further start of reviewer goes through, and writer is stopped
                self.assertEqual(follow_routes.allows(tool, given, more, "changelog"), through)

    def test_once_no_start_is_left_every_call_goes_through(self):
        # Given: reviewer's `good`
        # When: the main conversation starts writer
        # Then: it goes through, the run being over
        self.assertTrue(follow_routes.allows("Agent", start("changelog:writer"), END, "changelog"))


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
                # Given: the routes of write, writer and reviewer
                # When: a call starts writer, a subagent of the plugin no route names, one of
                # another plugin, one of no type, or is no Agent call
                # Then: only the first is a start of the routes, of writer
                found = follow_routes.started(tool, given, ["writer", "reviewer"], "changelog")
                self.assertEqual(found, name)


class TestDependency(unittest.TestCase):
    def test_a_start_of_a_dependencys_subagent_is_found_by_its_type(self):
        # Given: the main conversation's Agent call starting checker's examiner
        given = {"subagent_type": "checker:examiner", "prompt": "p"}
        # When: the subagent it starts is asked for, among writer and examiner
        found = follow_routes.started("Agent", given, ["writer", "checker:examiner"], "changelog")
        # Then: it is examiner, by the name the routes give it
        self.assertEqual(found, "checker:examiner")

    def test_a_skill_call_starts_only_a_dependencys_skill_the_routes_name(self):
        named = ["writer", "checker:check"]
        for given, name in (
            ({"skill": "checker:check"}, "checker:check"),
            ({"skill": "changelog:writer"}, None),
            ({"skill": "checker:other"}, None),
            ({}, None),
        ):
            with self.subTest(given=given):
                # Given: the routes naming writer and checker's skill check
                # When: a Skill call calls check, a skill of writer's name, another of checker's,
                # or none
                # Then: only the first is a start of the routes, of check
                self.assertEqual(follow_routes.started("Skill", given, named, "changelog"), name)


if __name__ == "__main__":
    unittest.main()
