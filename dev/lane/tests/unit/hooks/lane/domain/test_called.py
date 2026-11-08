"""The cases of called.py's contract: what Lane keeps of a session in its record, and how the starts
of a run join one another."""

import os
import tempfile
import time
from unittest import mock

from helpers import called, testing


def run(*entries):
    """The run that the entries keep, after a run of write begins."""
    found = called.run([{"kind": "run", "skill": "write"}, *entries])
    assert found is not None
    return found


def start(agent, role="writer", prompt="", status="async_launched"):
    return {"kind": "start", "agent": agent, "role": role, "prompt": prompt, "status": status}


def result(agent, given, role="writer"):
    return {"kind": "result", "agent": agent, "role": role, "result": given}


def ended(agent):
    return {"kind": "ended", "agent": agent}


class TestRecord(testing.FolderTest):
    def setUp(self):
        super().setUp()
        patcher = mock.patch.object(tempfile, "tempdir", self.base)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_a_session_keeps_its_record_in_a_folder_of_its_own_in_the_temporary_folder(self):
        found = called.record("s1", "changelog")
        day = time.strftime("%Y%m%d")
        self.assertEqual(found.folder, os.path.join(self.base, "lane", f"{day}-s1-changelog"))

    def test_a_record_made_on_an_earlier_day_is_found_again(self):
        os.makedirs(os.path.join(self.base, "lane", "20261101-s1-changelog"))
        self.assertTrue(called.record("s1", "changelog").folder.endswith("20261101-s1-changelog"))

    def test_each_entry_added_is_read_back_in_its_order(self):
        found = called.record("s1", "changelog")
        found.add({"kind": "a"})
        found.add({"kind": "b"})
        self.assertEqual(called.record("s1", "changelog").entries(), [{"kind": "a"}, {"kind": "b"}])

    def test_a_record_with_no_entry_reads_as_none(self):
        self.assertEqual(called.record("s1", "changelog").entries(), [])

    def test_each_plugin_keeps_a_record_of_its_own(self):
        called.record("s1", "changelog").add({"kind": "a"})
        self.assertEqual(called.record("s1", "checker").entries(), [])


class TestRun(testing.FolderTest):
    def test_no_run_begun_is_no_run(self):
        self.assertIsNone(called.run([]))

    def test_a_run_that_ended_is_no_run(self):
        self.assertIsNone(called.run([{"kind": "run", "skill": "write"}, {"kind": "end"}]))

    def test_a_run_keeps_its_skill(self):
        self.assertEqual(run().skill, "write")

    def test_a_new_run_takes_the_place_of_the_one_before(self):
        found = run(start("a1"), {"kind": "run", "skill": "write"})
        self.assertEqual(found.groups, [])

    def test_a_start_running_is_kept_as_running(self):
        self.assertEqual(
            run(start("a1")).groups,
            [called.Group("writer", (called.Start("a1", "writer", "", True, None),))],
        )

    def test_a_start_that_ended_with_a_result_keeps_it(self):
        found = run(start("a1"), result("a1", "written"), ended("a1"))
        self.assertEqual(
            found.groups[0].starts[0], called.Start("a1", "writer", "", False, "written")
        )

    def test_a_later_result_takes_the_place_of_an_earlier_one(self):
        found = run(start("a1"), result("a1", "asks"), result("a1", "written"), ended("a1"))
        self.assertEqual(found.groups[0].starts[0].result, "written")

    def test_a_start_that_ended_before_its_call_came_back_is_not_running(self):
        found = run(result("a1", "written"), ended("a1"), start("a1", status="completed"))
        self.assertEqual(
            found.groups[0].starts[0], called.Start("a1", "writer", "", False, "written")
        )

    def test_a_message_resumes_a_start_with_no_result_yet(self):
        found = run(
            start("a1"),
            result("a1", "asks"),
            ended("a1"),
            {"kind": "message", "agent": "a1", "text": "x"},
        )
        self.assertEqual(found.groups[0].starts[0][3:], (True, None))

    def test_starts_of_another_role_make_a_group_of_their_own(self):
        found = run(start("a1"), result("a1", "written"), ended("a1"), start("r1", "reviewer"))
        self.assertEqual([g.role for g in found.groups], ["writer", "reviewer"])

    def test_a_start_made_while_one_of_its_role_runs_joins_it(self):
        found = run(start("r1", "reviewer"), start("r2", "reviewer"))
        self.assertEqual([len(g.starts) for g in found.groups], [2])

    def test_a_start_made_after_every_start_of_its_role_ended_makes_a_new_group(self):
        found = run(
            start("r1", "reviewer"),
            result("r1", "more", "reviewer"),
            ended("r1"),
            start("r2", "reviewer"),
        )
        self.assertEqual([len(g.starts) for g in found.groups], [1, 1])

    def test_a_start_made_again_takes_the_place_of_one_with_no_result(self):
        found = run(start("r1", "reviewer"), ended("r1"), start("r2", "reviewer"))
        self.assertEqual([s.agent for s in found.groups[0].starts], ["r2"])

    def test_a_dependencys_skill_begun_is_a_move_running_until_its_result(self):
        found = run({"kind": "skill", "skill": "checker:check"})
        self.assertEqual(
            found.groups[0].starts[0], called.Start(None, "checker:check", "", True, None)
        )

    def test_the_result_of_a_dependencys_skill_ends_its_move(self):
        found = run(
            {"kind": "skill", "skill": "checker:check"}, result(None, "done", "checker:check")
        )
        self.assertEqual(found.groups[0].starts[0][3:], (False, "done"))

    def test_the_last_text_given_for_a_role_is_kept(self):
        given = [{"kind": "given", "role": "writer", "text": t} for t in ("a", "b")]
        self.assertEqual(run(*given).given, {"writer": "b"})

    def test_the_persons_words_since_the_last_message_are_kept(self):
        found = run(
            {"kind": "words", "text": "old"},
            {"kind": "message", "agent": "a1", "text": "m"},
            {"kind": "words", "text": "yes"},
        )
        self.assertEqual(found.words, ["yes"])


class TestTexts(testing.FolderTest):
    def test_a_start_has_its_prompt_and_each_message_sent_after(self):
        entries = [start("a1", prompt="p"), {"kind": "message", "agent": "a1", "text": "m"}]
        self.assertEqual(called.texts(entries, "a1"), ["p", "m"])

    def test_a_message_to_another_start_is_none_of_its_texts(self):
        entries = [start("a1", prompt="p"), {"kind": "message", "agent": "a2", "text": "m"}]
        self.assertEqual(called.texts(entries, "a1"), ["p"])

    def test_an_agent_not_yet_kept_has_no_texts(self):
        self.assertIsNone(called.texts([], "a1"))
