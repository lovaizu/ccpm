"""Each call of a subagent with lanes, kept as it comes back in a file of its session in the
system's temporary folder, so the guard holds the subagent to the calls of the reply being handed,
which Claude Code's record does not hold yet; read after the record's entries, each until the
record holds it."""

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
        self.assertEqual(called.Kept().check(event), [])

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
        # Given: a call kept, and the record holding it once its reply ended, giving back other
        # text
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
        expected = ("told", "notes: Take the next move `scripts/next.py` printed.")
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
