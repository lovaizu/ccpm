"""The tests of what the learnings are made from: what Claude Code keeps of a conversation as rn
reads it, the stretch's records shown, and every learning given to be put to the user."""

from __future__ import annotations

import json
import os
import unittest

from helpers import (
    CONVERSATIONS,
    FOLDER,
    HISTORY,
    LEARNINGS,
    STEERING,
    LearningTest,
    RepoTest,
    call_at,
    records,
    said,
    steered,
    testing,
)


class EntriesTest(testing.FolderTest):
    def test_the_conversation_s_own_entries_are_read_without_copies_or_a_line_half_written(self):
        # Given: a record of the user's words, the assistant's, an attachment, the copy of a
        # request Claude Code keeps beside them, and a last line half written, as one Claude Code
        # is still writing.
        kept = [
            {"type": "user", "message": {"content": "go"}},
            {"type": "assistant", "message": {"content": "gone"}},
            {"type": "attachment", "attachment": {"type": "date"}},
            {"type": "api-request-blob", "message": {"content": "copied request"}},
        ]
        late = json.dumps({"type": "assistant", "message": {"content": "late"}})[:20]
        self.write("c.jsonl", "".join(json.dumps(e) + "\n" for e in kept) + late)
        # When: its entries are read.
        # Then: they are the conversation's own, whole, without the copy.
        self.assertEqual(records.entries("c.jsonl"), kept[:3])

    def test_a_record_not_there_has_no_entries(self):
        # Given: no record at the path.
        # When: its entries are read.
        # Then: there are none.
        self.assertEqual(records.entries("gone.jsonl"), [])


class SaidTest(unittest.TestCase):
    def test_a_tool_s_words_are_shown_as_they_were_written(self):
        # Given: a tool given a file with quotes and lines, one given a value that is no text, and
        # one given no object, each with words beyond ASCII.
        write = {"file_path": "R.md", "content": '{\n  "questions": []\n}\n'}
        # When: each is shown as a line.
        # Then: each value given is shown under its name, text as it is, so a quote of it is found
        # as it was written, any other value as JSON.
        self.assertEqual(
            [
                records.said({"type": "tool_use", "name": "Write", "input": write}),
                records.said(
                    {"type": "tool_use", "name": "Bash", "input": {"command": "ls", "p": ["読む"]}}
                ),
                records.said({"type": "tool_use", "name": "Odd", "input": ["読む"]}),
            ],
            [
                '[tool_use Write] file_path: R.md\ncontent: {\n  "questions": []\n}\n',
                '[tool_use Bash] command: ls\np: ["読む"]',
                '[tool_use Odd] ["読む"]',
            ],
        )

    def test_a_part_of_words_is_shown_by_its_type(self):
        # Given: a part of words, and a part of a type of its own with no words.
        # When: each is shown as a line.
        # Then: each is shown by its type, the one with no words with none.
        self.assertEqual(
            [
                records.said({"type": "text", "text": "I keep the move."}),
                records.said({"type": "thinking"}),
            ],
            ["[text] I keep the move.", "[thinking] "],
        )


class WrappedTest(unittest.TestCase):
    def test_a_line_longer_than_a_read_shows_is_cut_at_its_blanks(self):
        # Given: a line of many words, longer than a read shows, and a word longer than that.
        text = " ".join(["word"] * 400) + "\n" + "x" * 2500
        # When: it is wrapped.
        wrapped = records.wrapped(text)
        # Then: the line is cut at its blanks, every word kept, and the long word stands alone.
        self.assertTrue(all(len(line) <= 1000 for line in wrapped.splitlines()[:-1]))
        self.assertEqual(wrapped.count("word"), 400)
        self.assertTrue(wrapped.endswith("\n" + "x" * 2500 + "\n"))

    def test_a_line_as_long_as_a_read_shows_is_kept_as_it_is(self):
        # Given: a short line holding a tab and ending in a blank, a line of a thousand characters,
        # the last a blank, and one a character longer.
        # When: they are wrapped.
        # Then: the first two are kept as they are, and the third cut at its blank.
        self.assertEqual(records.wrapped("a\tb "), "a\tb \n")
        self.assertEqual(records.wrapped("a" * 999 + " "), "a" * 999 + " \n")
        self.assertEqual(records.wrapped("a" * 999 + " b"), "a" * 999 + "\nb\n")


class RecordsTest(LearningTest):
    def test_records_gives_the_history_the_sessions_files_and_the_conversations(self):
        # Given: a session kept with its steering, its learnings, a call and a research result,
        # and a conversation of the orchestrator.
        self.write(LEARNINGS, "- L1: Kept.\n")
        self.call("0001", "plan", result={"items": []}, part="# Add login\n")
        self.write(f"{FOLDER}/research/login.md", "# Login\n")
        self.kept()
        self.conversation("c1", said("/rn:up add login", "2026-10-20T09:00:00Z", self.top))
        # When: the orchestrator has the records shown.
        # Then: rn gives the history, then each file in the session's folder in the order of their
        # paths, then the conversation, each a text in the git folder.
        self.assertEqual(
            self.records(),
            [
                "record/history.txt",
                f"record/{call_at('0001')}",
                f"record/{call_at('0001', 'result.json')}",
                f"record/{call_at('0001', 'steering.md')}",
                f"record/{LEARNINGS}",
                f"record/{FOLDER}/research/login.md",
                f"record/{STEERING}",
                "conversations/c1.txt",
            ],
        )

    def test_the_history_holds_each_commit_with_its_message_and_the_files_it_changed(self):
        # Given: a move kept with its message, which changed a file.
        self.write("README.md", "# app\n\nMIT\n")
        self.commit_with("README: say MIT")
        # When: the orchestrator has the records shown.
        self.show()
        # Then: the history gives each commit, oldest first, with its message and the files it
        # changed, not their lines.
        history = self.read(HISTORY)
        self.assertEqual(
            (
                history.startswith(f"$ git log --reverse --stat {self.left_at()}..HEAD\n"),
                "    README: say MIT" in history,
                "README.md | 2 ++" in history,
                "+MIT" in history,
            ),
            (True, True, True, False),
        )

    def test_the_history_holds_each_steering_rewritten_by_its_commit(self):
        # Given: a move that rewrote the steering.
        self.write(STEERING, steered(next_step="3. Sign off."))
        self.commit_with("plan: made")
        head = self.out("rev-parse", "--short", "HEAD").strip()
        # When: the orchestrator has the records shown.
        self.show()
        # Then: after the commits, the history gives each change to the steering under the commit
        # that made it, without its message again.
        changes = self.read(HISTORY).split(f" -- {STEERING}\n")[1]
        self.assertEqual(
            (f"\n{head}\n" in changes, "+3. Sign off." in changes, "plan: made" in changes),
            (True, True, False),
        )

    def test_no_conversation_kept_here_shows_the_record_alone(self):
        # Given: no record of a conversation for the repository.
        # When: the orchestrator has the records shown.
        # Then: rn gives the record alone.
        self.assertEqual(self.records(), ["record/history.txt", f"record/{STEERING}"])

    def test_the_records_are_shown_afresh(self):
        # Given: a text shown by an earlier run.
        self.write(f"{CONVERSATIONS}/old.txt", "old")
        # When: the orchestrator has the records shown.
        self.show()
        # Then: what the earlier run left is gone.
        self.assertFalse(os.path.exists(CONVERSATIONS))

    def test_the_stretch_starts_after_the_last_learnings_call_returned(self):
        # Given: a move, a learnings call returned, a move after it, and a learnings call not
        # returned.
        self.commit_with("plan: approved")
        kept = self.learnt("0001")
        self.commit_with("deliverable: sent back")
        self.call("0002", "learnings", "learnings")
        self.kept()
        # When: the orchestrator has the records shown.
        self.show()
        # Then: the history runs from the commit that kept the learnings call's result.
        history = self.read(HISTORY)
        self.assertEqual(
            (
                history.startswith(f"$ git log --reverse --stat {kept}..HEAD\n"),
                "plan: approved" in history,
                "deliverable: sent back" in history,
            ),
            (True, False, True),
        )

    def test_the_stretch_starts_where_the_branch_left_with_no_learnings_call_returned(self):
        # Given: a call on the finished work returned and kept.
        self.call("0001", "deliverable", "deliverable", result={})
        self.kept()
        # When: the orchestrator has the records shown.
        self.show()
        # Then: the history runs from the commit the branch left the default branch at.
        self.assertIn(f"$ git log --reverse --stat {self.left_at()}..HEAD\n", self.read(HISTORY))

    def test_the_stretch_starts_after_the_last_learnings_call_whatever_was_returned_after(self):
        # Given: a learnings call returned, then a call on the plan, a work named after the
        # learnings, returned.
        kept = self.learnt("0001")
        self.call("0002", "plan", "learnings", result={})
        self.kept()
        # When: the orchestrator has the records shown.
        self.show()
        # Then: the history runs from the commit that kept the learnings call's result.
        self.assertIn(f"$ git log --reverse --stat {kept}..HEAD\n", self.read(HISTORY))

    def test_the_stretch_starts_after_the_later_of_two_learnings_calls(self):
        # Given: two learnings calls returned, a move between them.
        self.learnt("0001")
        self.commit_with("design: approved")
        kept = self.learnt("0002")
        # When: the orchestrator has the records shown.
        self.show()
        # Then: the history runs from the commit that kept the later.
        self.assertIn(f"$ git log --reverse --stat {kept}..HEAD\n", self.read(HISTORY))

    def test_a_conversation_shows_its_entries_from_the_stretchs_start(self):
        # Given: a learnings call returned, and a conversation with an entry before, one at that
        # very time and one after.
        self.learnt("0001")
        self.conversation(
            "c",
            said("before", "2026-10-20T09:29:59.999Z", self.top),
            said("at", "2026-10-20T09:30:00.000Z", self.top),
            said("after", "2026-10-20T10:00:00.000Z", self.top),
        )
        # When: the orchestrator has the records shown.
        # Then: the entries at and after the start alone are shown.
        self.assertEqual(self.shown(), ["[user] at\n[user] after\n"])

    def test_a_conversation_all_before_the_stretch_is_left_out(self):
        # Given: a learnings call returned, a conversation ended before it and one after.
        self.learnt("0001")
        self.conversation("a", said("old", "2026-10-20T09:00:00Z", self.top))
        self.conversation("b", said("new", "2026-10-20T10:00:00Z", self.top))
        # When: the orchestrator has the records shown.
        # Then: the one in the stretch alone is shown.
        self.assertEqual(self.shown(), ["[user] new\n"])

    def test_a_conversation_shows_the_words_and_tool_calls_without_what_tools_gave_back(self):
        # Given: a conversation with the user's words, the orchestrator's, a tool call and what it
        # gave back, and a part of the orchestrator's thinking.
        entries = [
            said("/rn:up", "2026-10-20T09:00:00Z", self.top),
            dict(
                said("", "2026-10-20T09:01:00Z", self.top),
                type="assistant",
                message={
                    "content": [
                        {"type": "thinking", "thinking": "hmm"},
                        {"type": "text", "text": "I keep the move."},
                        {"type": "tool_use", "name": "Bash", "input": {"command": "rn.py state"}},
                    ]
                },
            ),
            dict(
                said("", "2026-10-20T09:02:00Z", self.top),
                message={"content": [{"type": "tool_result", "content": "kept 4f2c9a1"}]},
            ),
        ]
        self.conversation("c", *entries)
        # When: the orchestrator has the records shown.
        # Then: the words and the call are shown, one to a line, and nothing else.
        self.assertEqual(
            self.shown(),
            ["[user] /rn:up\n[text] I keep the move.\n[tool_use Bash] command: rn.py state\n"],
        )

    def test_records_with_a_move_not_kept_stop(self):
        # Given: a change not kept.
        self.write("notes.md", "x\n")
        # When: the orchestrator has the records shown.
        # Then: rn stops, saying to keep the move first.
        self.assertIn("keep the move with `rn.py state", self.stopped("ccs", "learnings"))

    def test_conversations_come_in_the_order_they_began(self):
        # Given: two conversations named against the order they began.
        self.conversation("b", said("first", "2026-10-20T09:00:00Z", self.top))
        self.conversation("a", said("second", "2026-10-20T10:00:00Z", self.top))
        # When: the orchestrator has the records shown.
        # Then: each conversation comes in the order it began.
        self.assertEqual(self.shown(), ["[user] first\n", "[user] second\n"])

    def test_a_conversation_begins_at_its_earliest_entry(self):
        # Given: a conversation whose first entry is later than its second, and one between.
        early = said("early", "2026-10-20T09:00:00Z", self.top)
        self.conversation("a", said("late", "2026-10-20T09:10:00Z", self.top), early)
        self.conversation("b", said("between", "2026-10-20T09:05:00Z", self.top))
        # When: the orchestrator has the records shown.
        # Then: the conversation that began earliest comes first.
        self.assertEqual(self.shown(), ["[user] late\n[user] early\n", "[user] between\n"])

    def test_an_entry_without_a_time_is_passed_over(self):
        # Given: a conversation opening with an entry Claude Code keeps without a time.
        kept = {"type": "mode", "mode": "normal"}
        self.conversation("a", kept, said("later", "2026-10-20T09:10:00Z", self.top))
        self.conversation("b", said("earlier", "2026-10-20T09:05:00Z", self.top))
        # When: the orchestrator has the records shown.
        # Then: it begins at its first entry with a time.
        self.assertEqual(self.shown(), ["[user] earlier\n", "[user] later\n"])

    def test_a_conversation_on_another_branch_is_left_out(self):
        # Given: a conversation on another branch beside the session's.
        self.conversation("a", said("main", "2026-10-20T09:00:00Z", self.top, "main"))
        self.conversation("b", said("work", "2026-10-20T09:05:00Z", self.top))
        # When: the orchestrator has the records shown.
        # Then: the session's alone is shown.
        self.assertEqual(self.shown(), ["[user] work\n"])

    def test_a_conversation_that_reached_the_branch_later_is_taken_whole(self):
        # Given: a conversation that began on the default branch and went on on the session's.
        self.conversation(
            "a",
            said("on main", "2026-10-20T09:00:00Z", self.top, "main"),
            said("on work", "2026-10-20T09:05:00Z", self.top),
        )
        # When: the orchestrator has the records shown.
        # Then: it is shown whole.
        self.assertEqual(self.shown(), ["[user] on main\n[user] on work\n"])

    def test_a_conversation_run_elsewhere_is_left_out(self):
        # Given: a conversation run in a folder below the top, beside one run at the top.
        below = os.path.join(self.top, "docs")
        self.conversation("a", said("below", "2026-10-20T09:00:00Z", below))
        self.conversation("b", said("top", "2026-10-20T09:05:00Z", self.top))
        # When: the orchestrator has the records shown.
        # Then: the one run at the top alone is shown.
        self.assertEqual(self.shown(), ["[user] top\n"])

    def test_the_agents_a_conversation_started_are_left_out(self):
        # Given: a conversation, an agent it started, and one that agent started in turn.
        conversation = self.conversation(
            "c", said("orchestrator", "2026-10-20T09:00:00Z", self.top)
        )
        self.agent(conversation, "up", "2026-10-20T09:01:00Z", {"agentType": "turn:up"})
        self.agent(conversation, "gen", "2026-10-20T09:02:00Z", {"parentAgentId": "up"})
        # When: the orchestrator has the records shown.
        # Then: the conversation alone is shown, as turn's learner reads turn's runs.
        self.assertEqual(self.shown(), ["[user] orchestrator\n"])

    def test_the_records_shown_leave_the_working_tree_as_it_was(self):
        # Given: a conversation's record.
        self.conversation("c", said("now", "2026-10-20T09:00:00Z", self.top))
        # When: the orchestrator has the records shown.
        self.show()
        # Then: git sees no change to keep.
        self.assertEqual(self.out("status", "--porcelain"), "")

    def test_records_without_a_session_stop(self):
        # Given: a branch holding no session.
        self.git("checkout", "-q", "-b", "other", "main")
        # When: the orchestrator has the records shown.
        # Then: rn stops, saying how to start one.
        self.assertIn("holds no session", self.stopped("ccs", "learnings"))


class LearningsTest(RepoTest):
    def test_learnings_gives_the_sessions_by_id_each_as_one_line(self):
        # Given: the session's learnings, the first over two lines.
        self.session()
        self.write(LEARNINGS, "- L1: A slip.\n  Its words.\n- L2: Another.\n")
        self.kept()
        # When: the orchestrator asks for the learnings.
        # Then: rn gives the session's by ID, each as one line, and nothing else.
        self.assertEqual(
            self.ran("learnings"), {"learnings": {"L1": "A slip. Its words.", "L2": "Another."}}
        )

    def test_learnings_are_printed_with_text_beyond_ascii_as_it_is(self):
        # Given: the session's learnings, one in Japanese.
        self.session()
        self.write(LEARNINGS, "- L1: 遅い。\n")
        self.kept()
        # When: the orchestrator asks for the learnings.
        # Then: rn prints it as it is, for the orchestrator to read.
        self.assertIn('"L1": "遅い。"', self.printed("learnings"))

    def test_learnings_without_a_session_stop(self):
        # Given: a branch holding no session.
        # When: the orchestrator asks for the learnings.
        # Then: rn says there is none.
        self.assertIn("holds no session", self.stopped("learnings"))


if __name__ == "__main__":
    unittest.main()
