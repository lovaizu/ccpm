"""The calls kept: each call of a subagent as it came back, each result it gave and each start and
end of its runs, under its agent_id in the session's folder of the system's temporary folder, read
back for the run it is in."""

import os
import shutil
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

    def test_an_entry_is_kept_in_the_first_days_folder_of_the_session(self):
        # Given: the session's folders of two days, as one going on past midnight left them
        for day in ("20261104", "20261103"):
            os.makedirs(os.path.join(self.base, "lane", f"{day}-s1"))
        # When: an entry is kept
        self.keep("a1", called.START)
        # Then: it is in the first day's folder
        first = os.path.join(self.base, "lane", "20261103-s1", "a1.jsonl")
        self.assertEqual(called.read(first), [called.START])

    def test_an_entry_is_kept_as_its_text_reads(self):
        # Given: a message of text out of ASCII
        # When: it is kept
        self.keep("a1", called.message("über"))
        # Then: its line holds the text as it reads, as UTF-8
        (folder,) = os.listdir(os.path.join(self.base, "lane"))
        line = self.read(os.path.join(self.base, "lane", folder, "a1.jsonl"))
        self.assertEqual(line, '{"kind": "message", "text": "über"}\n')

    def test_an_agent_with_nothing_kept_has_nothing(self):
        # Given: nothing kept
        # When: an agent's entries are read
        # Then: there are none
        self.assertEqual(called.kept("s1", "a1"), [])

    def test_reading_makes_no_folder(self):
        # Given: nothing kept in the session
        # When: an agent's entries and texts are read
        called.kept("s1", "a1")
        called.texts("s1", "a1")
        # Then: no folder is made for the session
        self.assertFalse(os.path.exists(os.path.join(self.base, "lane")))

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


class TestLeftWithoutResult(CalledTest):
    def test_an_agent_left_without_a_result_is_one_whose_run_ended_giving_none(self):
        gave = called.gave("written")
        for entries, left in (
            ((called.START, called.END), True),
            ((called.START, gave, called.END), False),
            ((called.START, called.END, called.START, gave, called.END), True),
            ((called.START, gave, called.END, called.START, called.END), True),
            ((called.START,), False),
            ((), False),
        ):
            with self.subTest(entries=entries):
                # Given: a run that ended with no result, one that gave a result, one resumed
                # after it ended with none or with one, one still running, or none kept
                self.keep("a1", *entries)
                # When: whether a run of it ended with no result is read
                # Then: it is, where any of its runs ended giving none
                self.assertEqual(called.left_without_result("s1", "a1"), left)
                shutil.rmtree(os.path.join(self.base, "lane"), ignore_errors=True)


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


class TestGiven(CalledTest):
    def test_a_runs_texts_are_its_prompt_and_each_message_after(self):
        # Given: a run given its prompt, and a message sent to it
        self.keep("a1", called.START, called.given("p"), called.message("m"))
        # When: its texts are read
        # Then: they are the prompt, then the message
        self.assertEqual(called.texts("s1", "a1"), ["p", "m"])

    def test_a_run_given_no_prompt_yet_has_no_texts(self):
        # Given: a run started, sent a message, before its start came back with its prompt
        self.keep("a1", called.START, called.message("m"))
        # When: its texts are read
        # Then: there are none yet, as its prompt is not known
        self.assertIsNone(called.texts("s1", "a1"))
        self.assertIsNone(called.texts("s1", "a2"))

    def test_the_calls_kept_are_those_of_every_run_or_of_the_run_it_is_in(self):
        # Given: a call before the run's start and one after
        first, second = (
            called.call("Read", {"file_path": "a"}),
            called.call("Read", {"file_path": "b"}),
        )
        self.keep("a1", first, called.START, second, called.END)
        # When: the calls are read
        # Then: all are given, or those of the run alone
        self.assertEqual(called.calls("s1", "a1"), [first, second])
        self.assertEqual(called.calls("s1", "a1", True), [second])


class TestRecord(unittest.TestCase):
    def test_each_plugins_guard_keeps_a_session_apart(self):
        # Given: the session s1, and the plugins changelog and checker
        # When: the record each keeps of it is named
        # Then: each is its own, the session first
        self.assertEqual(called.record("changelog", "s1"), "s1-changelog")
        self.assertNotEqual(called.record("checker", "s1"), called.record("changelog", "s1"))


if __name__ == "__main__":
    unittest.main()
