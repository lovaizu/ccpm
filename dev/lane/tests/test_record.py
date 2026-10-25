"""What the subagent did before, read from its record, the file Claude Code keeps beside the
session's, in the shape the version of Claude Code record.py names writes it."""

import json
import os
import unittest
from unittest import mock

import helpers
from helpers import record, testing


class RecordTest(helpers.PluginTest):
    def setUp(self) -> None:
        super().setUp()
        self.file = os.path.join(self.base, "session", "subagents", "agent-a1.jsonl")

    def entries(self):
        """The entries of the record the test has written."""
        found = record.entries(self.event("ls"))
        self.assertIsNotNone(found, "the record written was not found")
        return found or []

    def done(self):
        """What the subagent did, read from the record the test has written, in the event's
        folder."""
        return record.done(self.entries(), self.base)


class KeptTest(testing.FolderTest):
    """Claude Code's records kept in a folder of the test's own, as CLAUDE_CONFIG_DIR names it."""

    def setUp(self) -> None:
        super().setUp()
        self.config = os.path.join(self.base, "config")
        patched = mock.patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": self.config})
        patched.start()
        self.addCleanup(patched.stop)
        self.projects = os.path.join(self.config, "projects")


class TestProjects(KeptTest):
    def test_the_records_are_kept_in_the_folder_claude_config_dir_names(self):
        # Given: CLAUDE_CONFIG_DIR naming a folder
        # When: where Claude Code keeps each project's records is read
        # Then: it is projects/ in that folder
        self.assertEqual(record.projects(), self.projects)

    def test_the_records_are_kept_in_the_home_folder_where_no_folder_is_named(self):
        for named in ({}, {"CLAUDE_CONFIG_DIR": ""}):
            env = {k: v for k, v in os.environ.items() if k != "CLAUDE_CONFIG_DIR"}
            with (
                self.subTest(named=named),
                mock.patch.dict(os.environ, {**env, "HOME": self.base, **named}, clear=True),
            ):
                # Given: CLAUDE_CONFIG_DIR not set, or set to nothing
                # When: where Claude Code keeps each project's records is read
                # Then: it is ~/.claude/projects
                self.assertEqual(record.projects(), os.path.join(self.base, ".claude", "projects"))


class TestFolders(KeptTest):
    """Where Claude Code keeps the records of a project, by the project's path."""

    def test_a_path_of_200_characters_names_its_folder_whole(self):
        # Given: a path of 200 characters
        top = "/" + "a" * 199
        # When: its folder is looked for
        # Then: it is named by the path, each character not a letter or digit as `-`
        self.assertEqual(record.folders(top), [os.path.join(self.projects, "-" + "a" * 199)])

    def test_a_longer_path_is_found_by_its_first_200_characters(self):
        # Given: a path of 201 characters, with the folder Claude Code made for it, its first 200
        # characters and a hash, beside one for another path of the same beginning
        top = "/" + "a" * 200
        for name in ("-" + "a" * 199 + "-h1", "-" + "a" * 200):
            os.makedirs(os.path.join(self.projects, name))
        # When: its folder is looked for
        # Then: the one of its first 200 characters and a hash is found
        self.assertEqual(
            record.folders(top), [os.path.join(self.projects, "-" + "a" * 199 + "-h1")]
        )

    def test_a_character_beyond_the_basic_plane_is_two(self):
        # Given: a path holding a character JavaScript counts as two
        # When: its folder is looked for
        # Then: it stands as two `-`, as Claude Code replaces each half
        self.assertEqual(record.folders("/a\U0001f600b"), [os.path.join(self.projects, "-a--b")])


class TestConversation(KeptTest):
    def test_a_conversation_is_kept_in_any_projects_folder_by_its_session(self):
        # Given: a session's ID, and none
        # When: where its conversation's record is kept is read
        # Then: it is the session's file in any project's folder, any session's where none is given
        self.assertEqual(record.conversation("s1"), os.path.join(self.projects, "*", "s1.jsonl"))
        self.assertEqual(record.conversation(), os.path.join(self.projects, "*", "*.jsonl"))

    def test_a_conversation_is_kept_in_the_folder_given(self):
        # Given: a session's ID and a project's folder
        # When: where its conversation's record is kept is read
        # Then: it is the session's file in that folder
        self.assertEqual(record.conversation("s1", "/p"), "/p/s1.jsonl")

    def test_a_subagent_is_kept_beside_its_conversation(self):
        # Given: the record of a conversation, and a pattern of any
        # When: where a subagent's record of it is kept is read
        # Then: it is subagents/agent-<id>.jsonl in the folder named as the conversation's record
        self.assertEqual(record.subagent("/p/s1.jsonl", "a1"), "/p/s1/subagents/agent-a1.jsonl")
        pattern = record.subagent(record.conversation(), "*")
        self.assertEqual(
            pattern, os.path.join(self.projects, "*", "*", "subagents", "agent-*.jsonl")
        )


class TestAgentType(KeptTest):
    def test_the_agent_type_is_the_one_its_meta_file_names(self):
        # Given: a record and its meta file naming its agent type
        self.write("agent-a1.meta.json", '{"agentType": "turn:up"}')
        # When: its agent type is read
        # Then: it is the one named
        self.assertEqual(record.agent_type("agent-a1.jsonl"), "turn:up")

    def test_a_meta_file_not_there_or_naming_no_type_gives_none(self):
        for meta in (None, "x", "[]", "{}", '{"agentType": 1}'):
            with self.subTest(meta=meta):
                # Given: a record whose meta file is not there, not JSON, no object, or names no
                # agent type as text
                if meta is not None:
                    self.write("agent-a1.meta.json", meta)
                # When: its agent type is read
                # Then: it is none
                self.assertEqual(record.agent_type("agent-a1.jsonl"), "")


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


class TestEntries(RecordTest):
    def test_each_line_that_is_a_json_object_is_an_entry_in_order(self):
        # Given: a record of lines that are JSON objects, among lines that are not JSON or no object
        self.write(self.file, '{"type": "a"}\nnot json\n[]\n{\n{"type": "b"}\n')
        # When: its entries are read
        # Then: each object is an entry, in order, the other lines left out
        self.assertEqual(self.entries(), [{"type": "a"}, {"type": "b"}])

    def test_no_record_found_is_not_known(self):
        for event in (self.event("ls"), self.event("ls", agent_type=None)):
            with self.subTest(event=event):
                # Given: an event whose record is not there, or that names none
                # When: the entries of its record are read
                # Then: they are not known, told apart from a record of no entries
                self.assertIsNone(record.entries(event))


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

    def test_a_reply_that_ended_its_turn_is_read_in_order_as_a_hand_on_of_its_text(self):
        # Given: a record of a Bash call, the subagent's reply ending its turn, and a Read
        calls = [helpers.bash("ls"), helpers.replied("Is that so?"), ("Read", {}, "")]
        self.write(self.file, helpers.recorded("/w", calls))
        # When: what the subagent did is read
        # Then: the reply stands between the calls, as a call of no tool holding its text
        self.assertEqual(
            self.done(),
            [
                record.Done("Bash", {"command": "ls"}, "/w", ""),
                record.Done(record.REPLY, {record.SAID: "Is that so?"}, self.base, ""),
                record.Done("Read", {}, "/w", ""),
            ],
        )

    def test_a_reply_of_several_texts_is_read_as_their_lines(self):
        # Given: a reply ending its turn whose message holds two texts, a text block of no text and
        # a block of another type
        entry = helpers.replied("a")
        others = [{"type": "image", "text": "x"}, {"type": "text"}, {"type": "text", "text": "b"}]
        entry["message"]["content"] += others
        self.write(self.file, helpers.recorded("/w", [entry]))
        # When: what the subagent did is read
        # Then: the reply holds the texts, a line each
        self.assertEqual(self.done()[0].given, {record.SAID: "a\nb"})

    def test_text_that_did_not_end_the_turn_is_no_reply(self):
        for stop in ("tool_use", None, "max_tokens"):
            with self.subTest(stop=stop):
                # Given: the subagent's text whose message stopped otherwise, or not yet
                entry = helpers.replied("Let me look.")
                entry["message"]["stop_reason"] = stop
                self.write(self.file, helpers.recorded("/w", [entry]))
                # When: what the subagent did is read
                # Then: it did nothing
                self.assertEqual(self.done(), [])

    def test_a_reply_a_stop_hook_kept_going_reached_no_one(self):
        # Given: a record of a reply, then a stop hook telling the subagent something
        self.record(["told"])
        # When: what the subagent did is read
        # Then: it did nothing, the reply never having left it
        self.assertEqual(self.done(), [])

    def test_a_result_given_back_as_an_error_is_read_as_failed(self):
        # Given: a record of a Bash call given back as an error, one given back with none, and one
        # not yet back
        calls = [helpers.failing("false"), helpers.bash("true"), ("Bash", {}, None)]
        self.write(self.file, helpers.recorded("/w", calls))
        # When: what the subagent did is read
        # Then: the first failed, the others did not
        self.assertEqual([d.failed for d in self.done()], [True, False, False])

    def test_a_call_a_hook_stopped_is_left_out_as_it_did_nothing(self):
        # Given: a record of a Bash call a PreToolUse hook stopped, then one failing of itself
        stopped = helpers.Failed("PreToolUse:Bash hook error: [python3 x.py]: notes: Do not run.")
        calls = [("Bash", {"command": "cat > a.md"}, stopped), helpers.failing("false")]
        self.write(self.file, helpers.recorded("/w", calls))
        # When: what the subagent did is read
        # Then: the call that failed of itself alone is there, as the stopped one never ran
        self.assertEqual([d.given for d in self.done()], [{"command": "false"}])

    def test_a_result_marked_an_error_by_no_true_value_is_not_failed(self):
        # Given: results marked an error by values other than true, as Claude Code never marks one
        uses, results = [], []
        for number, marked in enumerate(("true", 1)):
            use = {"type": "tool_use", "id": f"t{number}", "name": "Bash", "input": {}}
            back = {"type": "tool_result", "tool_use_id": f"t{number}", "is_error": marked}
            uses.append({"type": "assistant", "message": {"content": [use]}})
            results.append({"type": "user", "message": {"content": [back]}})
        self.write(self.file, helpers.recorded("/w", [*uses, *results]))
        # When: what the subagent did is read
        # Then: neither failed
        self.assertEqual([d.failed for d in self.done()], [False, False])


class TestPrompt(RecordTest):
    def test_the_prompt_is_the_text_of_the_first_user_entry(self):
        # Given: a record begun by the prompt, then a call and a message from the main conversation
        calls = [helpers.bash("ls"), helpers.from_main("Go on.")]
        self.write(self.file, helpers.recorded("/w", calls, '{"work": "a.md"}'))
        # When: its prompt is read
        # Then: it is the first entry's text
        self.assertEqual(record.prompt(self.entries()), '{"work": "a.md"}')

    def test_a_record_with_no_user_text_has_an_empty_prompt(self):
        # Given: a record of a call alone, no user entry of text
        self.write(self.file, helpers.recorded("/w", [helpers.bash("ls")]).split("\n", 1)[1])
        # When: its prompt is read
        # Then: it is empty
        self.assertEqual(record.prompt(self.entries()), "")


class TestHeard(RecordTest):
    # The subagent asking its caller, by SendMessage.
    ASK = ("SendMessage", {"to": "main", "message": "May I?"}, '{"success":true}')

    def heard(self, calls):
        """The messages that reached the subagent since it last asked, from its record of the
        calls and messages."""
        self.write(self.file, helpers.recorded("/w", calls))
        return record.heard(self.entries())

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

    def test_a_subagent_that_replied_ending_its_turn_heard_what_resumed_it(self):
        for resumed in (helpers.from_main("OK"), helpers.from_subagent("OK")):
            with self.subTest(resumed=resumed):
                # Given: a record of a message, the subagent's reply ending its turn, and a message
                # from main or another subagent that resumed it
                calls = [helpers.from_main("Go."), helpers.replied("May I?"), resumed]
                # When: what reached it is read
                # Then: the message since its reply did, as the reply asked
                self.assertEqual(self.heard(calls), ["OK"])

    def test_a_reply_a_stop_hook_kept_going_is_no_ask(self):
        # Given: a record of the subagent asking, a message since, then its reply kept going by a
        # stop hook
        # When: what reached it is read
        # Then: the message did still, as the reply never reached whoever it would ask
        self.assertEqual(self.heard([self.ASK, helpers.from_main("OK"), "told"]), ["OK"])

    def test_a_stop_hooks_telling_with_no_reply_before_it_undoes_no_ask(self):
        # Given: a record of the subagent asking, then a stop hook's telling with no reply before
        told = helpers.told("/w", "x")[1]
        # When: what reached it is read
        # Then: nothing did, the ask standing
        self.assertEqual(self.heard([helpers.from_main("OK"), self.ASK, told]), [])

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
        self.assertEqual(record.heard(self.entries()), [])


class TestAnswered(RecordTest):
    def answered(self, calls):
        """Whether the subagent of a record of the calls and tellings has answered with words."""
        self.record(calls)
        return record.answered(self.entries())

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
        self.assertTrue(record.answered(self.entries()))

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
                self.assertFalse(record.answered(self.entries()))


if __name__ == "__main__":
    unittest.main()
