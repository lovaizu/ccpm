"""The tests of the orchestrator's conversations as rn reads them, what Claude Code keeps of each:
its own entries, each part of a message as a line, and the search of the session's for words."""

from __future__ import annotations

import json
import os
import shutil
import unittest
from typing import Any

from helpers import RepoTest, conversations, said, testing


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
        self.assertEqual(conversations.entries("c.jsonl"), kept[:3])

    def test_a_record_not_there_has_no_entries(self):
        # Given: no record at the path.
        # When: its entries are read.
        # Then: there are none.
        self.assertEqual(conversations.entries("gone.jsonl"), [])


class SaidTest(unittest.TestCase):
    def test_a_tool_s_words_are_said_as_they_were_written(self):
        # Given: a tool given a file with quotes and lines, one given a value that is no text, and
        # one given no object, each with words beyond ASCII.
        write = {"file_path": "R.md", "content": '{\n  "questions": []\n}\n'}
        # When: each is said as a line.
        # Then: each value given is said under its name, text as it is, so a quote of it is found
        # as it was written, any other value as JSON.
        self.assertEqual(
            [
                conversations.said({"type": "tool_use", "name": "Write", "input": write}),
                conversations.said(
                    {"type": "tool_use", "name": "Bash", "input": {"command": "ls", "p": ["読む"]}}
                ),
                conversations.said({"type": "tool_use", "name": "Odd", "input": ["読む"]}),
            ],
            [
                ("[tool_use Write]", 'file_path: R.md\ncontent: {\n  "questions": []\n}\n'),
                ("[tool_use Bash]", 'command: ls\np: ["読む"]'),
                ("[tool_use Odd]", '["読む"]'),
            ],
        )

    def test_a_part_of_words_is_said_by_its_type(self):
        # Given: a part of words, and a part of a type of its own with no words.
        # When: each is said as a line.
        # Then: each is said by its type, the one with no words with none.
        self.assertEqual(
            [
                conversations.said({"type": "text", "text": "I keep the move."}),
                conversations.said({"type": "thinking"}),
            ],
            [("[text]", "I keep the move."), ("[thinking]", "")],
        )


class SearchTest(RepoTest):
    """The orchestrator's conversations of the session searched for words."""

    def setUp(self) -> None:
        super().setUp()
        self.session()

    def found(self, words: str = "cart") -> list[dict[str, Any]]:
        """What rn found of the words in the session's conversations."""
        return self.ran("search", words)["found"]

    def agent(self, conversation: str, name: str, at: str, meta: dict[str, Any]) -> None:
        """Writes the record of an agent the conversation started, saying its name at the time,
        with its meta file."""
        path = os.path.join(conversation[: -len(".jsonl")], "subagents", f"agent-{name}.jsonl")
        self.write(path, json.dumps(said(name, at, self.top)) + "\n")
        self.write_json(path[: -len(".jsonl")] + ".meta.json", meta)

    def test_each_part_holding_the_words_is_found_with_its_conversation_and_time(self):
        # Given: a conversation with the user's words, the orchestrator's thinking, words and tool
        # call, what the tool gave back, and words of the orchestrator's that do not hold them.
        entries = [
            said("/rn:up add a cart", "2026-10-20T09:00:00Z", self.top),
            dict(
                said("", "2026-10-20T09:01:00Z", self.top),
                type="assistant",
                message={
                    "content": [
                        {"type": "thinking", "thinking": "the cart"},
                        {"type": "text", "text": "Which cart?"},
                        {"type": "tool_use", "name": "Bash", "input": {"command": "grep cart"}},
                    ]
                },
            ),
            dict(
                said("", "2026-10-20T09:02:00Z", self.top),
                message={"content": [{"type": "tool_result", "content": "src/cart.py"}]},
            ),
            dict(
                said("", "2026-10-20T09:03:00Z", self.top),
                type="assistant",
                message={"content": [{"type": "text", "text": "Kept."}]},
            ),
        ]
        path = self.conversation("c", *entries)
        # When: the orchestrator searches the session's conversations for the words.
        # Then: rn gives the user's words, the orchestrator's and its tool call that hold them,
        # each with its conversation and the time it was kept; not what the tool gave back, which
        # the history keeps, nor the thinking, which no one was shown.
        self.assertEqual(
            self.found(),
            [
                {
                    "conversation": path,
                    "time": "2026-10-20T09:00:00Z",
                    "said": "[user] /rn:up add a cart",
                },
                {
                    "conversation": path,
                    "time": "2026-10-20T09:01:00Z",
                    "said": "[text] Which cart?",
                },
                {
                    "conversation": path,
                    "time": "2026-10-20T09:01:00Z",
                    "said": "[tool_use Bash] command: grep cart",
                },
            ],
        )

    def test_words_found_nowhere_give_none(self):
        # Given: a conversation that does not hold the words, and one of other words.
        self.conversation("c", said("/rn:up add login", "2026-10-20T09:00:00Z", self.top))
        # When: the orchestrator searches for them.
        # Then: rn finds none.
        self.assertEqual(self.found(), [])

    def test_no_conversation_kept_here_stops_as_it_could_not_search(self):
        for case, branches in (("none at all", []), ("one on another branch alone", ["other"])):
            with self.subTest(case=case):
                # Given: no record of a conversation run at the top on the branch, as when the
                # session ran on another machine.
                shutil.rmtree(self.project, ignore_errors=True)
                for branch in branches:
                    self.conversation("c", said("cart", "2026-10-20T09:00:00Z", self.top, branch))
                # When: the orchestrator searches.
                # Then: rn says it could not search, where the records are kept, and to go on
                # with the cause unchecked, apart from a search that found nothing.
                self.assertIn(
                    "rn: no record of a conversation run at the top of this repository on work is"
                    f" under {os.path.dirname(self.project)}, the folder Claude Code keeps them in,"
                    " so the session's conversations could not be searched, as when it ran on"
                    " another machine; tell the user a cause only they show is left unchecked,"
                    " and go on without it",
                    self.stopped("search", "cart"),
                )

    def test_words_beyond_ascii_are_found_and_printed_as_they_are(self):
        # Given: a conversation in Japanese.
        self.conversation("c", said("カートを足して", "2026-10-20T09:00:00Z", self.top))
        # When: the orchestrator searches for a word of it.
        # Then: rn finds it and prints it as it is.
        self.assertIn('"said": "[user] カートを足して"', self.printed("search", "カート"))

    def test_conversations_come_in_the_order_they_began(self):
        # Given: two conversations named against the order they began.
        self.conversation("b", said("first cart", "2026-10-20T09:00:00Z", self.top))
        self.conversation("a", said("second cart", "2026-10-20T10:00:00Z", self.top))
        # When: the orchestrator searches.
        # Then: each conversation comes in the order it began.
        self.assertEqual(
            [f["said"] for f in self.found()], ["[user] first cart", "[user] second cart"]
        )

    def test_a_conversation_begins_at_its_earliest_entry(self):
        # Given: a conversation whose first entry is later than its second, and one between.
        early = said("early cart", "2026-10-20T09:00:00Z", self.top)
        self.conversation("a", said("late cart", "2026-10-20T09:10:00Z", self.top), early)
        self.conversation("b", said("between cart", "2026-10-20T09:05:00Z", self.top))
        # When: the orchestrator searches.
        # Then: the conversation that began earliest comes first, its entries in their order.
        self.assertEqual(
            [f["said"] for f in self.found()],
            ["[user] late cart", "[user] early cart", "[user] between cart"],
        )

    def test_an_entry_without_a_time_is_passed_over_for_when_it_began(self):
        # Given: a conversation opening with an entry Claude Code keeps without a time.
        kept = {"type": "user", "message": {"content": "mode cart"}}
        self.conversation(
            "a",
            dict(kept, cwd=self.top, gitBranch="work"),
            said("later cart", "2026-10-20T09:10:00Z", self.top),
        )
        self.conversation("b", said("earlier cart", "2026-10-20T09:05:00Z", self.top))
        # When: the orchestrator searches.
        # Then: it begins at its first entry with a time, and the entry without one is found with
        # none.
        self.assertEqual(
            [(f["said"], f["time"]) for f in self.found()],
            [
                ("[user] earlier cart", "2026-10-20T09:05:00Z"),
                ("[user] mode cart", None),
                ("[user] later cart", "2026-10-20T09:10:00Z"),
            ],
        )

    def test_a_conversation_on_another_branch_is_left_out(self):
        # Given: a conversation on another branch beside the session's.
        self.conversation("a", said("main cart", "2026-10-20T09:00:00Z", self.top, "main"))
        self.conversation("b", said("work cart", "2026-10-20T09:05:00Z", self.top))
        # When: the orchestrator searches.
        # Then: the session's alone is searched.
        self.assertEqual([f["said"] for f in self.found()], ["[user] work cart"])

    def test_a_conversation_that_reached_the_branch_later_is_searched_whole(self):
        # Given: a conversation that began on the default branch, where the session is asked for,
        # and went on on the session's.
        self.conversation(
            "a",
            said("on main cart", "2026-10-20T09:00:00Z", self.top, "main"),
            said("on work cart", "2026-10-20T09:05:00Z", self.top),
        )
        # When: the orchestrator searches.
        # Then: it is searched whole.
        self.assertEqual(
            [f["said"] for f in self.found()], ["[user] on main cart", "[user] on work cart"]
        )

    def test_a_conversation_run_elsewhere_is_left_out(self):
        # Given: a conversation run in a folder below the top, beside one run at the top.
        below = os.path.join(self.top, "docs")
        self.conversation("a", said("below cart", "2026-10-20T09:00:00Z", below))
        self.conversation("b", said("top cart", "2026-10-20T09:05:00Z", self.top))
        # When: the orchestrator searches.
        # Then: the one run at the top alone is searched.
        self.assertEqual([f["said"] for f in self.found()], ["[user] top cart"])

    def test_the_agents_a_conversation_started_are_left_out(self):
        # Given: a conversation, an agent it started, and one that agent started in turn.
        conversation = self.conversation(
            "c", said("orchestrator cart", "2026-10-20T09:00:00Z", self.top)
        )
        self.agent(conversation, "up cart", "2026-10-20T09:01:00Z", {"agentType": "turn:up"})
        self.agent(conversation, "gen cart", "2026-10-20T09:02:00Z", {"parentAgentId": "up"})
        # When: the orchestrator searches.
        # Then: the conversation alone is searched, as the search covers the orchestrator's
        # conversations, where the user was asked and told, and what each agent made is in the
        # history.
        self.assertEqual([f["said"] for f in self.found()], ["[user] orchestrator cart"])

    def test_the_search_leaves_the_working_tree_as_it_was(self):
        # Given: a conversation's record.
        self.conversation("c", said("now cart", "2026-10-20T09:00:00Z", self.top))
        before = self.head()
        # When: the orchestrator searches.
        self.found()
        # Then: git sees no change to keep, and no commit is made.
        self.assertEqual((self.out("status", "--porcelain"), self.head()), ("", before))

    def test_empty_words_stop(self):
        # Given: a session.
        # When: the orchestrator searches for blanks.
        # Then: rn says they are empty.
        self.assertIn(
            "rn: the text to search for is empty; give it in words", self.stopped("search", " ")
        )

    def test_a_search_without_a_session_stops(self):
        # Given: a branch holding no session.
        self.git("checkout", "-q", "-b", "other", "main")
        # When: the orchestrator searches.
        # Then: rn says there is none.
        self.assertIn("holds no session", self.stopped("search", "cart"))


if __name__ == "__main__":
    unittest.main()
