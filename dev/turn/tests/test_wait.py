"""How a role waits for a message without ending its turn: turn.py wait polls the files the message
follows, the generator's given, where the main conversation keeps an answer before sending it, and
the first user's work, which the generator mends before it replies, until one changes or the bound
passes, and prints which. The clock and the sleep are stood in for, so the bound passes at once."""

import json
import os
import time
import unittest
from unittest import mock

from helpers import CALL, StartedTest, wait

# What every wait says beside what it saw, written out again as the expected value.
AGAIN = "go on only once the reply has come as a message; until then run this wait again"


class Clock:
    """A clock for the wait: each sleep moves it on at once by its seconds and the lateness set,
    as a machine's sleep may last longer than asked, and counts the seconds asked; the action set
    for a sleep, by its number counted from 1, runs at the end of it. A wait that never ends fails
    at its hundredth sleep."""

    def __init__(self, test, actions=None, late=0):
        self.now = 1000.0
        self.slept = []
        self.actions = actions or {}
        self.late = late
        for name, stand_in in (("monotonic", lambda: self.now), ("sleep", self.sleep)):
            patched = mock.patch.object(time, name, side_effect=stand_in)
            patched.start()
            test.addCleanup(patched.stop)

    def sleep(self, seconds):
        if len(self.slept) == 100:
            raise AssertionError("the wait did not end")
        self.now += seconds + self.late
        self.slept.append(seconds)
        self.actions.get(len(self.slept), lambda: None)()


class WaitTest(StartedTest):
    def change(self, path, text, mtime=None):
        """Writes the text at the path, its time of change set where one is given."""
        self.write(path, text)
        if mtime is not None:
            os.utime(path, ns=(mtime, mtime))

    def waited(self, role, actions=None):
        """What turn.py wait prints for the role, with the clock stood in for, and the sleeps it
        slept."""
        clock = Clock(self, actions)
        return self.printed("wait", self.result, role), clock.slept


class TestGenerator(WaitTest):
    def test_a_change_to_a_file_of_the_generator_s_given_ends_its_wait(self):
        # Given: a run started, and the generator waiting
        # When: the decisions file the CCS names changes at the third poll
        decisions = self.here("notes/readme.decisions.md")
        printed, slept = self.waited(
            "generator", {3: lambda: self.change(decisions, "# Decisions\n\n- MIT\n")}
        )
        # Then: the wait ends there, naming the file by its whole path
        self.assertEqual(printed, {"changed": [decisions], "then": AGAIN})
        self.assertEqual(slept, [2, 2, 2])

    def test_a_change_to_the_ccs_ends_the_generator_s_wait(self):
        # Given: a run started, and the generator waiting
        # When: the main conversation adds a file to the CCS at the first poll
        ccs = self.here(CALL["ccs"])
        printed, _ = self.waited(
            "generator", {1: lambda: self.change(ccs, json.dumps({"more": []}))}
        )
        # Then: the wait ends, naming the CCS
        self.assertEqual(printed, {"changed": [ccs], "then": AGAIN})

    def test_with_nothing_changed_the_generator_waits_sixty_seconds_in_polls_of_two(self):
        # Given: a run started, and the generator waiting
        # When: no file changes
        printed, slept = self.waited("generator")
        # Then: it polls every two seconds until sixty have passed, and says it waited sixty
        self.assertEqual(printed, {"waited": 60, "then": AGAIN})
        self.assertEqual(slept, [2] * 30)

    def test_a_change_to_the_generator_s_own_reply_does_not_end_its_wait(self):
        # Given: a run started, and the generator waiting
        # When: its reply in the run's folder is written
        printed, _ = self.waited(
            "generator", {1: lambda: self.change(self.kept("generator.json"), "{}")}
        )
        # Then: it waits on to the bound, as the reply is none of its given
        self.assertEqual(printed, {"waited": 60, "then": AGAIN})


class TestFirstUser(WaitTest):
    def test_a_change_to_the_work_ends_the_first_user_s_wait(self):
        # Given: a run started, and the first user waiting
        # When: the generator mends the work at the second poll
        readme = self.here("README.md")
        printed, slept = self.waited(
            "first-user", {2: lambda: self.change(readme, "# csvtidy\n\nFor CSV files.\n")}
        )
        # Then: the wait ends there, naming the work's file
        self.assertEqual(printed, {"changed": [readme], "then": AGAIN})
        self.assertEqual(slept, [2, 2])

    def test_a_change_beside_the_work_does_not_end_the_first_user_s_wait(self):
        # Given: a run started, and the first user waiting
        # When: the CCS and the decisions file change, which the first user does not wait on
        def answered():
            self.change(self.here(CALL["ccs"]), json.dumps({"more": []}))
            self.change(self.here("notes/readme.decisions.md"), "- MIT\n")

        printed, _ = self.waited("first-user", {1: answered})
        # Then: it waits on to the bound
        self.assertEqual(printed, {"waited": 60, "then": AGAIN})


class TestStops(WaitTest):
    def test_a_role_turn_does_not_have_stops_naming_the_roles(self):
        # Given: a run started
        # When: the wait is asked for a role turn does not have
        out = self.stopped("wait", self.result, "orchestrator")
        # Then: it stops, naming the role given and the roles it takes
        self.assertEqual(
            out,
            "turn: turn.py wait takes the role `generator` or `first-user`, not `orchestrator`;"
            f" run `turn.py wait {self.result} generator` or"
            f" `turn.py wait {self.result} first-user`\n",
        )

    def test_a_wait_on_a_run_never_started_stops(self):
        # Given: no run kept for the result
        # When: the generator waits on it
        out = self.stopped("wait", self.here("other.json"), "generator")
        # Then: it stops, saying how to start one
        self.assertIn("no run is going with its result at", out)


class TestWaited(WaitTest):
    """The wait on paths as turn.py wait gives them, whatever the role."""

    def setUp(self):
        super().setUp()
        self.clock = Clock(self, {})

    def test_a_wait_whose_sleeps_last_longer_than_asked_ends_once_the_bound_has_passed(self):
        # Given: a machine whose every sleep lasts five seconds longer than asked
        self.clock.late = 5
        # When: nothing changes
        waited = wait.waited([self.here("README.md")])
        # Then: the wait ends at the first poll past sixty seconds, the ninth, seven seconds each
        self.assertEqual(waited, {"waited": 60, "then": AGAIN})
        self.assertEqual(self.clock.slept, [2] * 9)

    def test_a_file_changed_with_its_size_kept_is_seen_by_its_time(self):
        # Given: a file waited on, at a time of change set
        self.change("a.md", "one\n", mtime=10**18)
        # When: it is written with the same size at a later time
        self.clock.actions[1] = lambda: self.change("a.md", "two\n", mtime=10**18 + 1)
        # Then: the wait ends, naming it
        self.assertEqual(
            wait.waited([self.here("a.md")]), {"changed": [self.here("a.md")], "then": AGAIN}
        )

    def test_a_file_changed_with_its_time_kept_is_seen_by_its_size(self):
        # Given: a file waited on, at a time of change set
        self.change("a.md", "one\n", mtime=10**18)
        # When: it is written longer at the same time
        self.clock.actions[1] = lambda: self.change("a.md", "one two\n", mtime=10**18)
        # Then: the wait ends, naming it
        self.assertEqual(
            wait.waited([self.here("a.md")]), {"changed": [self.here("a.md")], "then": AGAIN}
        )

    def test_a_file_made_where_none_was_ends_the_wait(self):
        # Given: a path waited on with no file there yet, before one that is
        self.change("b.md", "b\n")
        # When: a file is written there
        self.clock.actions[1] = lambda: self.change("a.md", "a\n")
        # Then: the wait ends, naming it
        waited = wait.waited([self.here("a.md"), self.here("b.md")])
        self.assertEqual(waited, {"changed": [self.here("a.md")], "then": AGAIN})

    def test_a_file_removed_ends_the_wait(self):
        # Given: a file waited on
        self.change("a.md", "a\n")
        # When: it is removed
        self.clock.actions[1] = lambda: os.remove("a.md")
        # Then: the wait ends, naming it
        self.assertEqual(
            wait.waited([self.here("a.md")]), {"changed": [self.here("a.md")], "then": AGAIN}
        )

    def test_a_file_made_inside_a_folder_waited_on_ends_the_wait(self):
        # Given: a folder waited on, holding a file a level down
        self.change("docs/deep/a.md", "a\n")
        # When: a file is made in it a level down
        self.clock.actions[1] = lambda: self.change("docs/deep/b.md", "b\n")
        # Then: the wait ends, naming the file made
        waited = wait.waited([self.here("docs")])
        self.assertEqual(waited, {"changed": [self.here("docs/deep/b.md")], "then": AGAIN})

    def test_files_changed_at_one_poll_are_named_in_order(self):
        # Given: two files waited on, the later in order given first
        self.change("a.md", "a\n")
        self.change("b.md", "b\n")

        def both():
            self.change("b.md", "bb\n")
            self.change("a.md", "aa\n")

        # When: both change before the same poll
        self.clock.actions[1] = both
        # Then: the wait names both, in order of their paths
        waited = wait.waited([self.here("b.md"), self.here("a.md")])
        self.assertEqual(waited, {"changed": [self.here("a.md"), self.here("b.md")], "then": AGAIN})


if __name__ == "__main__":
    unittest.main()
