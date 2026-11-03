"""The calls kept: each call of a subagent as it came back, each result it gave and each start and
end of its runs, under its agent_id in the session's folder of the system's temporary folder, read
back for the run it is in."""

import os
import unittest
from unittest import mock

import helpers
from helpers import called, routes


def on(day: str):
    """time.strftime as it formats on the day."""
    return lambda form: form.replace("%Y%m%d", day)


class CalledTest(helpers.PluginTest):
    def keep(self, agent: str, *entries: dict) -> None:
        """Keeps each entry under the agent's ID in session s1."""
        for entry in entries:
            called.keep("s1", agent, entry)


class TestKeep(CalledTest):
    def test_entries_are_kept_in_order_under_the_agent_in_the_sessions_folder(self):
        # Given: no entry kept yet
        # When: writer's start and its result are kept
        self.keep("a1", called.START, called.gave("written"))
        # Then: they are read back in order, from lane/<yyyymmdd>-s1/a1.jsonl
        self.assertEqual(called.kept("s1", "a1"), [called.START, called.gave("written")])
        (folder,) = os.listdir(os.path.join(self.base, "lane"))
        self.assertRegex(folder, r"^[0-9]{8}-s1$")
        self.assertTrue(os.path.isfile(os.path.join(self.base, "lane", folder, "a1.jsonl")))

    def test_the_sessions_folder_is_kept_over_a_change_of_day(self):
        # Given: an entry kept on one day
        with mock.patch.object(called.time, "strftime", side_effect=on("20261103")):
            self.keep("a1", called.START)
        # When: another is kept the next day
        with mock.patch.object(called.time, "strftime", side_effect=on("20261104")):
            self.keep("a1", called.END)
            # Then: both are in the folder of the first
            self.assertEqual(called.kept("s1", "a1"), [called.START, called.END])
        self.assertEqual(os.listdir(os.path.join(self.base, "lane")), ["20261103-s1"])

    def test_an_agent_with_nothing_kept_has_nothing(self):
        # Given: nothing kept
        # When: an agent's entries are read
        # Then: there are none
        self.assertEqual(called.kept("s1", "a1"), [])

    def test_entries_that_cannot_be_read_are_refused(self):
        # Given: a line that is no JSON object among the entries
        self.keep("a1", called.START)
        (folder,) = os.listdir(os.path.join(self.base, "lane"))
        with open(os.path.join(self.base, "lane", folder, "a1.jsonl"), "a") as f:
            f.write("[1]\n")
        # When: they are read
        # Then: they are refused, naming the file
        with self.assertRaises(ValueError) as refused:
            called.kept("s1", "a1")
        self.assertIn(
            f"lane/{folder}/a1.jsonl holds a line that is no entry", str(refused.exception)
        )

    def test_an_id_that_cannot_name_a_file_is_refused(self):
        for session, agent in (("..", "a1"), ("s1", "a/b"), ("s1", "")):
            # Given: a session or agent ID that would name a file elsewhere, or none
            # When: an entry is kept under it
            # Then: it is refused
            with self.subTest(session=session, agent=agent), self.assertRaises(ValueError):
                called.keep(session, agent, called.START)


class TestThisRun(CalledTest):
    def test_the_result_is_the_last_given_in_the_run(self):
        # Given: writer giving `written` twice, the later after a call
        call = called.call("Bash", {"command": "ls"})
        self.keep("a1", called.START, called.gave("more"), call, called.gave("written"))
        # When: its result is read
        # Then: it is the later
        self.assertEqual(called.result("s1", "a1"), "written")

    def test_a_resumed_run_has_none_of_the_earlier_runs_result_or_end(self):
        # Given: a run that gave `written` and ended, then a start again, as on a resume
        self.keep("a1", called.START, called.gave("written"), called.END, called.START)
        # When: its result and end are read
        # Then: there are none, as the resumed run gives its own
        self.assertIsNone(called.result("s1", "a1"))
        self.assertFalse(called.ended("s1", "a1"))

    def test_a_run_ended_is_read_so(self):
        # Given: a run that ended
        self.keep("a1", called.START, called.END)
        # When: whether it ended is read
        # Then: it did
        self.assertTrue(called.ended("s1", "a1"))


class TestStarts(CalledTest):
    def test_the_starts_are_the_agent_calls_of_routed_subagents_as_they_came_back(self):
        # Given: lead's start of writer as it came back, a read, and a start of Explore
        writer = called.call("Agent", {"subagent_type": "changelog:writer"}, helpers.back("w1"))
        explore = called.call("Agent", {"subagent_type": "Explore"}, helpers.back("x1"))
        self.keep("lead1", called.START, writer, called.call("Read", {}), explore)
        # When: lead's starts of the routes are read
        found = called.starts("s1", "lead1", ["writer", "reviewer"], "changelog")
        # Then: they are writer's alone, with its status and ID
        self.assertEqual(found, [routes.Start("writer", "completed", "w1")])


if __name__ == "__main__":
    unittest.main()
