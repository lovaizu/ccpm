"""Each record of a run as the learner is shown it, read from what Claude Code keeps of an agent's
conversation, and the records of a run found by its agents."""

import json
import os
import unittest

from helpers import CALL, RESULT, RepoTest, records


class RecordTest(RepoTest):
    def setUp(self):
        super().setUp()
        self.path = self.given_record("agen", '{"given": []}', "turn:generator")

    def written(self, *entries):
        """The record with the entries written after its own, as Claude Code writes them."""
        with open(self.path, "a", encoding="utf-8") as f:
            f.writelines(json.dumps(e) + "\n" for e in entries)


class TestAsText(RecordTest):
    def test_each_part_is_shown_by_its_type_and_a_file_shown_whole_by_its_name(self):
        # Given: a record holding a tool used with words beyond ASCII, a tool result as a list
        # and as text, a part of a type of its own, a file Claude Code showed whole, an attachment
        # of another kind, and the copy of a request Claude Code keeps beside them
        parts = [
            {"type": "tool_use", "name": "Read", "input": {"file_path": "読む.md"}},
            {"type": "tool_result", "content": [{"type": "text", "text": "x" * 2500}]},
            {"type": "tool_result", "content": "done"},
            {"type": "web_search_tool_result", "text": "found"},
        ]
        shown_file = {"type": "edited_text_file", "filename": "R.md", "snippet": "1\t# csvtidy"}
        self.written(
            {"type": "assistant", "message": {"content": parts}},
            {"type": "attachment", "attachment": shown_file},
            {"type": "attachment", "attachment": {"type": "date", "filename": "d"}},
            {"type": "api-request-blob", "message": {"content": "copied request"}},
        )
        # When: it is shown as text
        shown = records.as_text(self.path)
        # Then: each part is shown by its type, the file shown whole by its name, and neither the
        # other attachment nor the copy
        self.assertIn('[user] {"given": []}', shown)
        self.assertIn('[tool_use Read] {"file_path": "読む.md"}', shown)
        self.assertIn("[tool_result] " + "x" * 2500 + "\n", shown)
        self.assertIn("[tool_result] done", shown)
        self.assertIn("[web_search_tool_result] found", shown)
        self.assertIn("[shown R.md] 1\t# csvtidy", shown)
        self.assertNotIn("copied request", shown)
        self.assertEqual(shown.count("[shown"), 1)

    def test_a_part_or_a_result_s_part_of_no_object_is_left_out(self):
        # Given: a record whose message holds a part that is no object, and a tool result whose
        # parts are not all objects, as the property tests found
        result = {"type": "tool_result", "content": [None, {"type": "text", "text": "done"}]}
        self.written({"type": "user", "message": {"content": [None, result]}})
        # When: it is shown as text
        shown = records.as_text(self.path)
        # Then: each part of no object is left out, the rest shown
        self.assertTrue(shown.endswith("[text] I open it.\n[tool_result] done\n"), shown)

    def test_a_line_still_being_written_is_left_out(self):
        # Given: a record whose last line is half written, as one Claude Code is still writing
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"type": "assistant", "message": {"content": "late"}})[:20])
        # When: it is shown as text
        shown = records.as_text(self.path)
        # Then: every whole entry is shown, the half-written line left out
        self.assertEqual(shown, '[user] {"given": []}\n[text] I open it.\n[text] I open it.\n')


class TestWrapped(unittest.TestCase):
    def test_a_line_longer_than_a_read_shows_is_cut_at_its_blanks(self):
        # Given: a line of many words, longer than a read shows, and a word longer than that
        text = " ".join(["word"] * 400) + "\n" + "x" * 2500
        # When: it is wrapped for the learner
        wrapped = records.wrapped(text)
        # Then: the line is cut at its blanks, every word kept, and the long word stands alone
        self.assertTrue(all(len(line) <= 1000 for line in wrapped.splitlines()[:-1]))
        self.assertEqual(wrapped.count("word"), 400)
        self.assertTrue(wrapped.endswith("\n" + "x" * 2500 + "\n"))

    def test_a_line_as_long_as_a_read_shows_is_kept_as_it_is(self):
        # Given: a short line holding a tab and ending in a blank, a line of a thousand characters,
        # the last a blank, and one a character longer
        # When: they are wrapped for the learner
        # Then: the first two are kept as they are, and the third cut at its blank
        self.assertEqual(records.wrapped("a\tb "), "a\tb \n")
        self.assertEqual(records.wrapped("a" * 999 + " "), "a" * 999 + " \n")
        self.assertEqual(records.wrapped("a" * 999 + " b"), "a" * 999 + "\nb\n")


class TestFound(RecordTest):
    def test_a_role_s_record_is_found_by_its_agent_id(self):
        # Given: the record of an agent, kept where Claude Code keeps it
        # When: it is looked for by the agent's ID, and by an ID of no record
        # Then: it is found, and none for the other
        self.assertEqual((records.find("agen"), records.find("anone")), (self.path, None))

    def test_the_orchestrator_s_record_is_the_latest_naming_the_result(self):
        # Given: beside a role's record, agents of another type, a meta file not JSON or not an
        # object, a meta file of a record gone, an orchestrator whose prompt is no call or names
        # another result, and two orchestrators naming the result
        self.write(os.path.join(self.session, "agent-abad.meta.json"), "x")
        self.write(os.path.join(self.session, "agent-alist.meta.json"), "[]")
        self.write(os.path.join(self.session, "agent-alist.jsonl"), "")
        self.write(os.path.join(self.session, "agent-agone.meta.json"), '{"agentType": "turn:up"}')
        decoys = [
            self.given_record("aother", json.dumps(CALL), "turn:generator"),
            self.given_record("azz", json.dumps(CALL), "turn:zz"),
            self.given_record("anotjson", "not a call", "turn:up"),
            self.given_record("aelse", json.dumps(dict(CALL, result="else.json")), "turn:up"),
        ]
        older = self.given_record("aold", json.dumps(CALL), "turn:up")
        newer = self.given_record("anew", json.dumps(CALL), "turn:up")
        os.utime(older, (1, 1))
        # Each record the orchestrator's is not is the latest of all.
        for decoy in decoys:
            os.utime(decoy, (4e9, 4e9))
        # When: the orchestrator's record is looked for beside the role's
        # Then: it is the latest orchestrator's naming the result
        self.assertEqual(records.orchestrator([self.path], RESULT), newer)

    def test_no_orchestrator_naming_the_result_gives_none(self):
        # Given: a role's record alone
        # When: the orchestrator's record is looked for beside it
        # Then: there is none
        self.assertIsNone(records.orchestrator([self.path], RESULT))


if __name__ == "__main__":
    unittest.main()
