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

    def test_no_record_found_is_not_known(self):
        for event in (self.event("ls"), self.event("ls", agent_type=None)):
            with self.subTest(event=event):
                # Given: an event whose record is not there, or that names none
                # When: what the subagent did is read
                # Then: it is not known, told apart from a record of no calls
                self.assertIsNone(record.done(event))

    def test_a_call_failed_is_told_by_its_result_marked_an_error(self):
        # Given: a record of a command that exited 1, one that exited 0, and a result marked an
        # error by no true value, as Claude Code marks them
        calls = [
            ("Bash", {"command": "false"}, "Exit code 1\nbroken", True),
            ("Bash", {"command": "true"}, "", False),
            ("Bash", {"command": "x"}, "", "true"),
            ("Bash", {"command": "y"}, "", 1),
        ]
        self.write(self.file, helpers.recorded("/w", calls))
        # When: what the subagent did is read
        # Then: the first alone failed
        self.assertEqual([d.failed for d in self.done()], [True, False, False, False])


class TestHeard(RecordTest):
    # The subagent asking its caller, by SendMessage.
    ASK = ("SendMessage", {"to": "main", "message": "May I?"}, '{"success":true}')

    def heard(self, calls):
        """The messages that reached the subagent since it last asked, from its record of the
        calls and messages."""
        self.write(self.file, helpers.recorded("/w", calls))
        return record.heard(self.event("ls"))

    def test_a_subagent_that_has_not_asked_heard_its_prompt(self):
        # Given: a record of a call, the subagent not having asked
        # When: what reached it is read
        # Then: its prompt did
        self.assertEqual(self.heard([helpers.bash("ls")]), [helpers.PROMPT])

    def test_a_subagent_that_asked_heard_nothing_before_it(self):
        # Given: a record of the subagent asking, after a message from main
        # When: what reached it is read
        # Then: nothing did since it asked
        self.assertEqual(self.heard([helpers.from_main("OK"), self.ASK]), [])

    def test_each_message_sent_since_it_asked_is_heard_alone_in_order(self):
        # Given: a record of the subagent asking, then a message from main and one from another
        # subagent, each in the words Claude Code puts around it
        calls = [self.ASK, helpers.from_main("Change step 3."), helpers.from_subagent("OK")]
        # When: what reached it is read
        # Then: each message did, without the words around it, in order
        self.assertEqual(self.heard(calls), ["Change step 3.", "OK"])

    def test_a_message_from_main_not_in_its_words_is_heard_whole(self):
        # Given: a message from main that Claude Code put in other words
        entry = {**helpers.from_main(""), "message": {"role": "user", "content": "OK, go on."}}
        # When: what reached the subagent is read
        # Then: the message is heard whole
        self.assertEqual(self.heard([self.ASK, entry]), ["OK, go on."])

    def test_entries_that_bring_no_message_are_not_heard(self):
        # Given: entries of text that are no message sent to the subagent: of another origin, of
        # no origin but meta, of an origin that is no object, from a subagent with no body; and
        # entries not in the record's shape
        meta = {"type": "user", "isMeta": True, "message": {"content": "Caveat"}}
        notified = {**meta, "origin": {"kind": "task-notification"}}
        no_body = {**meta, "origin": {"kind": "peer"}}
        odd_origin = {**meta, "origin": "coordinator"}
        reply = {"type": "assistant", "message": {"content": "OK"}}
        no_text = {"type": "user", "message": {"content": [{"type": "text", "text": "OK"}]}}
        lines = [json.dumps(e) for e in (meta, notified, no_body, odd_origin, reply, no_text)]
        self.write(self.file, "\n".join(["not json", "[]", *lines]))
        # When: what reached the subagent is read
        # Then: nothing did
        self.assertEqual(record.heard(self.event("ls")), [])

    def test_no_record_found_is_not_known(self):
        for event in (self.event("ls"), self.event("ls", agent_type=None)):
            with self.subTest(event=event):
                # Given: an event whose record is not there, or that names none
                # When: what reached the subagent is read
                # Then: it is not known, told apart from nothing heard
                self.assertIsNone(record.heard(event))


if __name__ == "__main__":
    unittest.main()
