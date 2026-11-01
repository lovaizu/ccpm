"""Each call of a subagent with lanes, kept as it comes back in a file of its session in the
system's temporary folder, so the guard holds the subagent to the calls of the reply being handed,
whose results Claude Code's record may not hold yet; read after the record's entries, each until
the record holds its result."""

from __future__ import annotations

import json
import os
import unittest
from unittest import mock

import helpers
from helpers import called, record
from test_guard import GuardTest

# The day a call is kept on, as the clock gives it.
TODAY = "20261025"
# The output of a Bash call, as the version of Claude Code record.py names gives it back to
# PostToolUse.
OUTPUT = {"stdout": "out", "stderr": "", "interrupted": False, "isImage": False}
# A flow whose back is from changelog-writer, whose answer is kept as it ends.
ANSWERING = {
    "orchestrator": "notes-lead",
    "step": 1,
    "order": ["notes-writer", "changelog-writer"],
    "back": [{"from": "changelog-writer", "to": "notes-writer", "while": "more"}],
}
# The move the script follow_next takes prints.
MOVE = {"tool": "SendMessage", "input": {"to": "a2", "message": "go"}}


class CallsTest(helpers.PluginTest):
    def setUp(self) -> None:
        super().setUp()
        today = mock.patch.object(called.time, "strftime", return_value=TODAY)
        today.start()
        self.addCleanup(today.stop)
        self.file = os.path.join(self.tmp, "lane", f"{TODAY}-s1", "a1.jsonl")

    def keep(self, event: dict) -> None:
        """Runs the check lane's hooks run as a call comes back on the event; it says nothing."""
        self.assertEqual(called.Kept(self.plugin, helpers.AGENT).check(event), [])

    def kept(self, file: str | None = None) -> list:
        """Each line kept in the file, the subagent a1's of today where none is named."""
        with open(file or self.file, encoding="utf-8") as f:
            return [json.loads(line) for line in f]


class TestKept(CallsTest):
    def test_a_call_coming_back_is_kept_in_the_folder_of_its_session_and_day(self):
        # Given: a Bash call of the subagent a1 coming back in the session s1
        event = self.came_back("Bash", {"command": "ls"}, OUTPUT)
        # When: it is kept
        self.keep(event)
        # Then: lane/<today>-s1/a1.jsonl in the temporary folder holds it on a line, with its ID,
        # tool, input, folder, the text it gave back and that it did not fail
        kept = {
            "id": "toolu_k1",
            "tool": "Bash",
            "input": {"command": "ls"},
            "cwd": self.base,
            "result": "out",
            "failed": False,
        }
        self.assertEqual(self.kept(), [kept])

    def test_a_failed_call_is_kept_as_failed_with_its_error(self):
        # Given: a Bash call coming back failed
        event = self.came_back("Bash", {"command": "ls x"}, error="Exit code 2\nls: x: none")
        # When: it is kept
        self.keep(event)
        # Then: it is kept as failed, its error as what it gave back
        [kept] = self.kept()
        self.assertEqual((kept["result"], kept["failed"]), ("Exit code 2\nls: x: none", True))

    def test_calls_are_kept_in_the_order_they_came_back(self):
        # Given: two calls coming back one after another
        # When: each is kept
        for command in ("ls", "pwd"):
            self.keep(self.came_back("Bash", {"command": command}, OUTPUT))
        # Then: the file holds them in that order
        self.assertEqual([k["input"]["command"] for k in self.kept()], ["ls", "pwd"])

    def test_a_session_kept_from_an_earlier_day_keeps_its_folder(self):
        # Given: a call of the session kept two days before, its folder of the day before too,
        # and a folder of another session
        earlier = os.path.join(self.tmp, "lane", "20261023-s1", "a1.jsonl")
        self.write(earlier, "")
        for folder in ("20261024-s1", "20261024-s2"):
            os.makedirs(os.path.join(self.tmp, "lane", folder))
        # When: a call of the session is kept today
        self.keep(self.came_back("Bash", {"command": "ls"}, OUTPUT))
        # Then: it is kept in the session's first folder, and none is made today
        self.assertEqual(len(self.kept(earlier)), 1)
        self.assertFalse(os.path.exists(os.path.dirname(self.file)))

    def test_an_event_naming_no_session_or_subagent_by_an_id_keeps_nothing(self):
        event = self.came_back("Bash", {"command": "ls"}, OUTPUT)
        for what, wrong in {
            "no session": {k: v for k, v in event.items() if k != "session_id"},
            "no subagent": {k: v for k, v in event.items() if k != "agent_id"},
            "a session of no text": dict(event, session_id=1),
            "a session naming a folder above": dict(event, session_id="../s1"),
            "a subagent naming a folder": dict(event, agent_id="x/a1"),
        }.items():
            with self.subTest(what=what):
                # Given: a call coming back in an event so
                # When: it is kept
                self.keep(wrong)
                # Then: nothing is written in the temporary folder
                self.assertFalse(os.path.exists(self.tmp))


class TestGivenBack(CallsTest):
    """What a call gave back, as the text the AI is shown, in the form the record's tool result has
    for the same call, as the version record.py names gave both on a run."""

    def given_back(self, tool: str, back: object) -> str:
        """The text kept of a call of the tool that gave back what is given."""
        return called.given_back(self.came_back(tool, {}, back))

    def test_a_bash_call_gives_its_output_then_its_errors(self):
        for printed, text in (
            ({"stdout": "out1\nout2", "stderr": ""}, "out1\nout2"),
            ({"stdout": "", "stderr": "err"}, "err"),
            ({"stdout": "out", "stderr": "err"}, "out\nerr"),
        ):
            with self.subTest(printed=printed):
                # Given: a Bash call that printed so
                # When: what it gave back is read
                # Then: it is its output, then its errors on the next line
                self.assertEqual(self.given_back("Bash", {**OUTPUT, **printed}), text)

    def test_a_bash_call_that_printed_nothing_gives_the_words_claude_code_shows(self):
        for back in ({**OUTPUT, "stdout": ""}, {"stdout": None}, None):
            with self.subTest(back=back):
                # Given: a Bash call that printed nothing, or gave back nothing it reads
                # When: what it gave back is read
                # Then: it is what Claude Code shows the AI for no output
                self.assertEqual(self.given_back("Bash", back), "(Bash completed with no output)")

    def test_a_read_call_gives_each_line_numbered_from_the_first_it_read(self):
        for what, file, text in (
            (
                "the whole file",
                {"content": "one\ntwo\n", "startLine": 1, "numLines": 3, "totalLines": 3},
                "1\tone\n2\ttwo\n3\t",
            ),
            (
                "two lines of it",
                {"content": "two\nthree", "startLine": 2, "numLines": 2, "totalLines": 5},
                "2\ttwo\n3\tthree",
            ),
        ):
            with self.subTest(what=what):
                # Given: a Read call that read so
                back = {"type": "text", "file": {"filePath": "/r/lines.txt", **file}}
                # When: what it gave back is read
                # Then: it is each line, its number from the first it read, a tab and its text
                self.assertEqual(self.given_back("Read", back), text)

    def test_a_read_call_giving_back_no_text_and_first_line_gives_nothing(self):
        for back in (
            None,
            {"type": "text"},
            {"file": {"content": None, "startLine": 1}},
            {"file": {"content": "one", "startLine": None}},
        ):
            with self.subTest(back=back):
                # Given: a Read call that gave back no file's text and first line
                # When: what it gave back is read
                # Then: it is nothing
                self.assertEqual(self.given_back("Read", back), "")

    def test_a_call_of_another_tool_gives_nothing(self):
        # What a Bash call and a Read call give back, which a call of another tool is read by
        # neither as.
        back = {**OUTPUT, "file": {"content": "one", "startLine": 1}}
        for tool in ("Agent", "Grep", "SendMessage"):
            with self.subTest(tool=tool):
                # Given: a call of the Agent tool, the Grep tool or SendMessage, whose text no lane
                # reads, giving back what a Bash or Read call would
                # When: what it gave back is read
                # Then: it is nothing
                self.assertEqual(self.given_back(tool, back), "")

    def test_a_failed_call_gives_its_error(self):
        # Given: a call coming back failed
        event = self.came_back("Read", {}, error="File does not exist.")
        # When: what it gave back is read
        # Then: it is its error
        self.assertEqual(called.given_back(event), "File does not exist.")


class TestEntries(CallsTest):
    """The record's entries with the calls kept that it does not hold yet."""

    def done(self) -> list:
        """Each call the subagent made, as the guard reads them on a call after them."""
        return record.done(called.entries(self.event("ls")) or [], self.base)

    def test_kept_calls_the_record_does_not_hold_follow_its_entries_in_their_order(self):
        # Given: a record of one call, and two calls kept since, of a reply not yet ended
        self.record([helpers.bash("cat a.md")])
        for command in ("ls", "pwd"):
            self.keep(self.came_back("Bash", {"command": command}, OUTPUT))
        # When: what the subagent did is read
        # Then: it is the record's call, then each kept one in its order, with what it gave back
        self.assertEqual(
            [(d.given["command"], d.result) for d in self.done()],
            [("cat a.md", ""), ("ls", "out"), ("pwd", "out")],
        )

    def test_a_kept_call_the_record_holds_is_read_from_the_record_alone(self):
        # Given: a call kept, and the record holding it with its result, giving back other text
        self.keep(self.came_back("Bash", {"command": "ls"}, OUTPUT))
        self.write(
            os.path.join(self.base, "session", "subagents", "agent-a1.jsonl"),
            helpers.recorded(self.base, [])
            + "".join(
                json.dumps(e) + "\n"
                for e in called.as_entries(
                    {"id": "toolu_k1", "tool": "Bash", "input": {"command": "ls"}, "result": "rec"}
                )
            ),
        )
        # When: what the subagent did is read
        # Then: the call is read once, as the record holds it
        self.assertEqual([d.result for d in self.done()], ["rec"])

    def test_a_kept_call_whose_result_the_record_does_not_hold_yet_is_read_as_kept(self):
        # Given: a call kept, and the record holding its tool use and not yet its result
        self.keep(self.came_back("Bash", {"command": "ls"}, OUTPUT))
        [use, _] = called.as_entries({"id": "toolu_k1", "tool": "Bash", "input": {"command": "ls"}})
        self.write(
            os.path.join(self.base, "session", "subagents", "agent-a1.jsonl"),
            helpers.recorded(self.base, []) + json.dumps(use) + "\n",
        )
        # When: what the subagent did is read
        # Then: the call is read once, with what it gave back as kept
        self.assertEqual([(d.given, d.result) for d in self.done()], [({"command": "ls"}, "out")])

    def test_a_kept_call_is_read_as_the_record_would_hold_it(self):
        # Given: a failed Write and a Read kept, made in another folder
        elsewhere = os.path.join(self.base, "w")
        os.makedirs(elsewhere)
        write = {"file_path": "a.md", "content": "x"}
        self.keep(dict(self.came_back("Write", write, error="denied"), cwd=elsewhere))
        self.record([])
        # When: what the subagent did is read
        # Then: it is the call, its tool, input, folder, what it gave back and that it failed
        self.assertEqual(self.done(), [record.Done("Write", write, elsewhere, "denied", True)])

    def test_with_no_record_found_nothing_is_known(self):
        # Given: a call kept, and no record of the subagent where Claude Code keeps it
        self.keep(self.came_back("Bash", {"command": "ls"}, OUTPUT))
        # When: the entries are read
        # Then: none is known, as what the subagent was given is not
        self.assertIsNone(called.entries(self.event("ls")))

    def test_with_nothing_kept_or_no_session_named_the_record_is_read_alone(self):
        self.record([helpers.bash("cat a.md")])
        event = self.event("ls")
        for what, given in {
            "nothing kept": event,
            "no session": {k: v for k, v in event.items() if k != "session_id"},
        }.items():
            with self.subTest(what=what):
                # Given: the record of one call, and no call kept, or an event of no session
                # When: the entries are read
                # Then: they are the record's
                self.assertEqual(called.entries(given), record.entries(event))


class TestStarted(CallsTest):
    """Of an Agent call, the ID of the subagent it started, as Claude Code gives it back."""

    def test_an_agent_call_keeps_the_id_of_the_subagent_it_started(self):
        for what, back in {
            "run in the foreground": {"status": "completed", "agentId": "b7", "content": []},
            "started in the background": {"status": "async_launched", "agentId": "b7"},
        }.items():
            with self.subTest(what=what):
                # Given: an Agent call coming back, with the ID of the subagent it started
                if os.path.exists(self.file):
                    os.remove(self.file)
                given = {"subagent_type": "notes:changelog-reviewer", "prompt": "Review."}
                # When: it is kept
                self.keep(self.came_back("Agent", given, back))
                # Then: it is kept with that ID
                [kept] = self.kept()
                self.assertEqual((kept["tool"], kept["agent"]), ("Agent", "b7"))

    def test_a_call_giving_back_no_id_as_claude_code_gives_it_keeps_none(self):
        for what, (tool, back) in {
            "an Agent call of no ID": ("Agent", {"status": "completed"}),
            "an Agent call of an ID of no text": ("Agent", {"agentId": 7}),
            "an Agent call giving back no object": ("Agent", "done"),
            "another tool giving back an ID": ("Bash", {"agentId": "b7", "stdout": "out"}),
            # A tool named before Agent in order, and one after, giving back an ID.
            "a tool named before giving back an ID": ("Act", {"agentId": "b7"}),
            "a tool named after giving back an ID": ("Agents", {"agentId": "b7"}),
        }.items():
            with self.subTest(what=what):
                # Given: a call coming back with no subagent's ID as an Agent call gives it
                if os.path.exists(self.file):
                    os.remove(self.file)
                # When: it is kept
                self.keep(self.came_back(tool, {"prompt": "x"}, back))
                # Then: it is kept with no ID
                [kept] = self.kept()
                self.assertNotIn("agent", kept)


class TestAnswer(CallsTest):
    """The answer of a `from` subagent of the flow, kept as it ends, by its ID, in the folder of
    its session: the message it handed back with SubagentHandback where it made that call, and
    else its last reply, each end replacing the answer kept before."""

    def setUp(self) -> None:
        super().setUp()
        laid = {"flow": ANSWERING, "subagents": []}
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)

    def handed(self, message: object, agent: str = helpers.AGENT) -> None:
        """Keeps the subagent's call of SubagentHandback with the message, as it comes back."""
        event = self.came_back("SubagentHandback", {"message": message}, {"ok": True})
        self.assertEqual(called.Kept(self.plugin, agent).check(event), [])

    def ended(self, reply: str | None) -> None:
        """Keeps the subagent's answer as it is about to end with the reply."""
        called.ended(dict(self.stopped(), last_assistant_message=reply))

    def answer(self) -> str | None:
        """The answer kept of the subagent a1 in the session s1."""
        return called.answer("s1", "a1")

    def test_the_last_reply_is_kept_as_it_ends(self):
        # Given: the subagent ending with a reply
        # When: its answer is kept
        self.ended("Two entries.\nmore")
        # Then: the answer is the reply, kept in lane/<today>-s1/a1.reply.json
        self.assertEqual(self.answer(), "Two entries.\nmore")
        self.assertTrue(os.path.isfile(self.file.replace(".jsonl", ".reply.json")))

    def test_each_end_replaces_the_answer_kept_before(self):
        # Given: the subagent ending with a reply, kept going, then ending with another
        self.ended("more")
        # When: its answer is kept again
        self.ended("All entries hold.")
        # Then: the answer is the last
        self.assertEqual(self.answer(), "All entries hold.")

    def test_the_message_handed_back_is_kept_over_the_last_reply(self):
        for what, reply in (("a reply", "Handed back."), ("no reply", None)):
            with self.subTest(what=what):
                # Given: the subagent handing its report back with SubagentHandback
                self.handed("more")
                # When: it ends, with a reply or none, as Claude Code gives null after it
                self.ended(reply)
                # Then: the answer is the message it handed back
                self.assertEqual(self.answer(), "more")

    def test_a_reply_after_a_hand_back_ended_before_is_kept(self):
        # Given: the subagent having handed its report back and ended, then going on
        self.handed("more")
        self.ended(None)
        # When: it ends again with a reply
        self.ended("All entries hold.")
        # Then: the answer is that reply
        self.assertEqual(self.answer(), "All entries hold.")

    def test_an_end_of_no_reply_and_nothing_handed_back_keeps_an_empty_answer(self):
        # Given: the subagent ending with no reply, having handed nothing back
        # When: its answer is kept
        self.ended(None)
        # Then: the answer is empty
        self.assertEqual(self.answer(), "")

    def test_a_message_of_no_text_is_kept_empty(self):
        # Given: the subagent handing back a message that is no text
        self.handed(["more"])
        # When: it ends
        self.ended(None)
        # Then: the answer is empty
        self.assertEqual(self.answer(), "")

    def test_a_hand_back_of_a_subagent_that_is_no_from_keeps_no_answer(self):
        for what, agent, laid in (
            ("another subagent", "notes:notes-writer", None),
            ("no flow laid", helpers.AGENT, {"subagents": []}),
            ("hooks/lanes.json out of its form", helpers.AGENT, "{"),
        ):
            with self.subTest(what=what):
                # Given: a subagent that is no from of a flow laid, or a flow lane cannot read
                if laid is not None:
                    path = os.path.join(self.plugin, "hooks", "lanes.json")
                    self.write(path, laid if isinstance(laid, str) else json.dumps(laid))
                # When: it hands its report back
                self.handed("more", agent)
                # Then: no answer is kept, the call kept alone
                self.assertIsNone(self.answer())
                self.assertEqual(self.kept()[-1]["tool"], "SubagentHandback")

    def test_another_call_of_a_from_keeps_no_answer(self):
        # A tool named before SubagentHandback in order, and one after.
        for tool in ("Bash", "Write"):
            with self.subTest(tool=tool):
                # Given: the from subagent making a call of another tool, with a message
                # When: it comes back
                self.keep(self.came_back(tool, {"message": "more"}, OUTPUT))
                # Then: no answer is kept
                self.assertIsNone(self.answer())

    def test_an_answer_not_kept_or_out_of_its_form_is_none(self):
        for what, text in (
            ("not kept", None),
            ("no JSON", "{"),
            ("no object", "[]"),
            ("no answer", '{"handed": false}'),
            ("an answer of no text", '{"answer": 1, "handed": false}'),
        ):
            with self.subTest(what=what):
                # Given: no answer kept of the subagent, or one out of its form
                place = self.file.replace(".jsonl", ".reply.json")
                if os.path.exists(place):
                    os.remove(place)
                if text is not None:
                    self.write(place, text)
                # When: it is read
                # Then: there is none
                self.assertIsNone(self.answer())

    def test_an_answer_of_a_session_or_subagent_of_no_id_is_none(self):
        # Given: an answer kept of the subagent a1
        self.ended("more")
        # When: one is read naming the session or the subagent by no ID as Claude Code gives it
        # Then: there is none
        self.assertIsNone(called.answer("../s1", "a1"))
        self.assertIsNone(called.answer("s1", "x/a1"))

    def test_an_end_naming_no_session_or_subagent_by_an_id_keeps_nothing(self):
        # Given: an end in an event naming its subagent by no ID
        # When: its answer is kept
        called.ended(dict(self.stopped("more"), agent_id="x/a1"))
        # Then: nothing is written in the temporary folder
        self.assertFalse(os.path.exists(self.tmp))


class TestGuard(GuardTest):
    """The trial's slip: follow_next on step 3 taking `scripts/next.py`, the subagent taking the
    move it printed and running it again in one reply, before the record holds the move taken."""

    LAID = ((3, "follow_next", ["scripts/next.py"]),)

    def setUp(self) -> None:
        super().setUp()
        self.record([])
        self.run_next = {"command": f"python3 {self.plugin}/scripts/next.py"}

    def back(self, tool: str, given: dict, back: object = None, entry="posttooluse.py") -> None:
        """Runs the entry of a call coming back, as Claude Code runs it, on the call; it exits 0
        and says nothing."""
        event = self.came_back(tool, given, back, None if entry == "posttooluse.py" else "x")
        self.assertEqual(self.guard(json.dumps(event), (helpers.AGENT,), entry), ("", ""))

    def test_the_move_taken_in_the_same_reply_is_seen(self):
        # Given: the script's run in the record, printing the move, and the move taken come back
        # in a reply not yet ended
        self.record([("Bash", self.run_next, json.dumps(MOVE))])
        self.back("SendMessage", MOVE["input"], {"success": True})
        # When: the subagent runs the script again in the same reply
        # Then: the call goes on, nothing said
        self.assertEqual(self.guard(json.dumps(self.called("Bash", self.run_next))), ("", ""))

    def test_a_move_printed_in_the_same_reply_holds_the_next_call(self):
        # Given: the script run, printing the move, come back in a reply not yet ended
        self.back("Bash", self.run_next, {"stdout": json.dumps(MOVE), "stderr": ""})
        # When: the subagent makes another call
        # Then: it is stopped, told the sentence
        expected = ("told", "notes: Take each move `scripts/next.py` prints, until it prints none.")
        self.assertEqual(self.guard(self.stream("ls")), expected)

    def test_a_failed_call_is_kept_by_its_own_entry(self):
        # Given: the script run and come back failed
        self.back("Bash", self.run_next, entry="posttoolusefailure.py")
        # When: what the subagent did is read
        # Then: it holds the call, failed, with its error
        [done] = record.done(called.entries(self.event("ls")) or [], self.base)
        self.assertEqual((done.given, done.result, done.failed), (self.run_next, "x", True))

    def test_a_call_of_another_agent_is_not_kept(self):
        # Given: a call coming back in another subagent
        event = self.came_back("Bash", self.run_next, OUTPUT)
        stream = json.dumps(dict(event, agent_type="notes:other"))
        # When: the entry is run on it
        # Then: it exits 0, nothing kept
        self.assertEqual(self.guard(stream, (helpers.AGENT,), "posttooluse.py"), ("", ""))
        self.assertFalse(os.path.exists(self.tmp))


if __name__ == "__main__":
    unittest.main()
