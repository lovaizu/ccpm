"""What the subagent did before, read from its record, the file Claude Code keeps beside the
session's, in the shape Claude Code 2.1.306 writes it."""

import json
import os
import unittest

import helpers
from helpers import record


class RecordTest(helpers.PluginTest):
    def setUp(self) -> None:
        super().setUp()
        self.file = os.path.join(self.base, "session", "subagents", "agent-a1.jsonl")

    def done(self):
        """What the subagent did, read from the record the test has written."""
        found = record.done(self.event("ls"))
        assert found is not None, "the record written was not found"
        return found


class TestPath(RecordTest):
    def test_the_record_is_the_subagents_file_beside_the_sessions(self):
        # Given: an event of the subagent a1 in the session whose record is session.jsonl
        # When: where its record is is read
        # Then: it is session/subagents/agent-a1.jsonl, where Claude Code writes it
        self.assertEqual(record.path(self.event("ls")), self.file)

    def test_an_event_naming_no_session_or_no_subagent_has_no_record(self):
        no_session = {k: v for k, v in self.event("ls").items() if k != "transcript_path"}
        for event in (
            {**self.event("ls"), "transcript_path": None},
            {**self.event("ls"), "agent_id": None},
            {**self.event("ls"), "agent_id": 1},
            no_session,
            self.event("ls", agent_type=None),
        ):
            with self.subTest(event=event):
                # Given: an event naming the session's record or the subagent by no text, or not
                # at all, as in the main conversation
                # When: where its record is is read
                # Then: there is none
                self.assertIsNone(record.path(event))


class TestDone(RecordTest):
    def test_each_call_is_read_in_order_with_its_input_folder_and_result(self):
        # Given: a record of a Read given back, and a Bash call not yet back, each request as sent
        # repeating its call after it
        calls = [("Read", {"file_path": "a"}, "1\tx"), ("Bash", {"command": "ls"}, None)]
        self.write(self.file, helpers.recorded("/w", calls))
        # When: what the subagent did is read
        # Then: each call comes once, in order, with what the AI gave it and the folder it ran in,
        # and what it gave back, nothing for the call not back, the request as sent left out
        self.assertEqual(
            self.done(),
            [
                record.Done("Read", {"file_path": "a"}, "/w", "1\tx"),
                record.Done("Bash", {"command": "ls"}, "/w", ""),
            ],
        )

    def test_a_record_of_the_prompt_alone_holds_no_call(self):
        # Given: the record of a subagent that has made no call yet, its prompt alone
        self.record([])
        # When: what the subagent did is read
        # Then: it did nothing
        self.assertEqual(self.done(), [])

    def test_a_call_whose_entry_names_no_folder_ran_in_the_events(self):
        # Given: a tool use whose entry names no folder
        use = {"type": "tool_use", "id": "t", "name": "Read", "input": {"file_path": "a"}}
        self.write(self.file, json.dumps({"type": "assistant", "message": {"content": [use]}}))
        # When: what the subagent did is read
        # Then: the call ran in the event's folder
        self.assertEqual(self.done(), [record.Done("Read", {"file_path": "a"}, self.base, "")])

    def test_a_result_not_of_text_is_read_as_none(self):
        # Given: a tool result given back as a list of blocks
        self.write(self.file, helpers.recorded("/w", [("Read", {}, [{"type": "image"}])]))
        # When: what the subagent did is read
        # Then: the call gave back no text
        self.assertEqual(self.done()[0].result, "")

    def test_lines_not_in_the_records_shape_are_left_out(self):
        # Given: a record whose lines are not JSON, not objects, hold no message, a message of no
        # content list, a block that is no object, a block of another type, and a tool use of no
        # name or no input
        use = {"type": "tool_use", "id": "t", "name": "Read", "input": {}}
        lines = [
            "not json",
            "{",
            "[]",
            {"type": "assistant"},
            {"type": "assistant", "message": "text"},
            {"type": "assistant", "message": {"content": ["text"]}},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "t"}]}},
            {"type": "assistant", "message": {"content": [{**use, "id": "t1", "name": 1}]}},
            {"type": "assistant", "message": {"content": [{**use, "id": "t2", "input": "x"}]}},
            {"type": "user", "message": {"content": [{"type": "tool_result", "content": "x"}]}},
        ]
        text = "\n".join(line if isinstance(line, str) else json.dumps(line) for line in lines)
        self.write(self.file, text + "\n" + helpers.recorded("/w", [("Bash", {}, "ok")]))
        # When: what the subagent did is read
        # Then: the call in the record's shape alone is read
        self.assertEqual(self.done(), [record.Done("Bash", {}, "/w", "ok")])

    def test_a_result_given_back_as_an_error_is_read_as_failed(self):
        # Given: a record of a Bash call given back as an error, one given back with none, and one
        # not yet back
        calls = [helpers.failing("false"), helpers.bash("true"), ("Bash", {}, None)]
        self.write(self.file, helpers.recorded("/w", calls))
        # When: what the subagent did is read
        # Then: the first failed, the others did not
        self.assertEqual([d.failed for d in self.done()], [True, False, False])

    def test_no_record_found_is_not_known(self):
        for event in (self.event("ls"), self.event("ls", agent_type=None)):
            with self.subTest(event=event):
                # Given: an event whose record is not there, or that names none
                # When: what the subagent did is read
                # Then: it is not known, told apart from a record of no calls
                self.assertIsNone(record.done(event))


class TestAnswered(RecordTest):
    def answered(self, calls):
        """Whether the subagent of a record of the calls and tellings has answered with words."""
        self.record(calls)
        return record.answered(self.event("ls"))

    def test_told_and_no_call_since_is_answered(self):
        for calls in (["told"], [helpers.bash("ls"), "told"], ["told", helpers.bash("ls"), "told"]):
            with self.subTest(calls=calls):
                # Given: a record whose last telling by a stop hook has no tool use after it
                # When: whether the subagent answered with words is read
                # Then: it did
                self.assertTrue(self.answered(calls))

    def test_a_reply_in_words_after_the_telling_keeps_it_answered(self):
        # Given: a record told by a stop hook, then the subagent's reply in words
        self.record(["told"])
        reply = {"type": "text", "text": "Done."}
        with open(self.file, "a", encoding="utf-8") as f:
            f.write(json.dumps({"type": "assistant", "message": {"content": [reply]}}) + "\n")
        # When: whether the subagent answered with words is read
        # Then: it did
        self.assertTrue(record.answered(self.event("ls")))

    def test_a_call_since_the_last_telling_is_no_answer_in_words(self):
        for calls in ([], [helpers.bash("ls")], ["told", helpers.bash("ls")]):
            with self.subTest(calls=calls):
                # Given: a record told nothing, or with a tool use after its last telling
                # When: whether the subagent answered with words is read
                # Then: it did not
                self.assertFalse(self.answered(calls))

    def test_only_a_users_text_of_a_stop_hooks_telling_is_one(self):
        said = {"role": "user", "content": "Stop hook feedback:\nx"}
        for line in (
            "not json",
            "[]",
            json.dumps({"type": "user", "message": {"content": "Do your steps."}}),
            json.dumps({"type": "assistant", "message": said}),
            json.dumps({"type": "user", "message": {"content": [said]}}),
            json.dumps({"type": "user", "message": "Stop hook feedback:"}),
        ):
            with self.subTest(line=line):
                # Given: a record of a line that is no stop hook's telling: no JSON, no object, a
                # user's other text, the text from the assistant, in a list or not in a message
                self.write(self.file, line + "\n")
                # When: whether the subagent answered with words is read
                # Then: it did not, as it was never told
                self.assertFalse(record.answered(self.event("ls")))

    def test_no_record_found_is_no_answer(self):
        # Given: an event whose record is not there
        # When: whether the subagent answered with words is read
        # Then: it did not
        self.assertFalse(record.answered(self.event("ls")))


if __name__ == "__main__":
    unittest.main()
