"""A tool call read as one action: a Bash call as the commands it runs and the files they read and
write, in the forms the steps tell and the AI writes, a call of the Read or Grep tool as a read of
what it reads, and a call of a tool that writes a file as a write of it; each with the calls its
subagent made before it."""

from __future__ import annotations

import unittest

import helpers
from helpers import HERE, call, testing


def runs(command):
    """The commands a Bash call of the command runs, as the guard reads it."""
    return helpers.acted("Bash", {"command": command})


class TestBash(unittest.TestCase):
    def test_a_bash_call_runs_its_command_with_its_words(self):
        # Given: a Bash call of one command
        # When: it is read
        # Then: it is a run of that command, its words as the shell takes them
        given = {"command": "git commit -m 'a b'"}
        words = [["git", "commit", "-m", "a b"]]
        self.assertEqual(runs(given["command"]), call.Call("run", words, tool="Bash", given=given))

    def test_each_statement_is_a_command_run(self):
        # Given: a Bash call of statements joined by separators
        # When: it is read
        # Then: each statement is a command it runs, in order
        self.assertEqual(
            runs("npm test && npm publish; echo done").what,
            [["npm", "test"], ["npm", "publish"], ["echo", "done"]],
        )

    def test_gits_own_options_before_its_command_are_left_out(self):
        # Given: git with its own options before its command, one taking the next word
        # When: it is read
        # Then: the command run is git's command, as the step names it
        for command in ("git -C notes commit -m m", "git -c a=b --no-pager commit -m m"):
            with self.subTest(command=command):
                self.assertEqual(runs(command).what, [["git", "commit", "-m", "m"]])

    def test_gits_own_options_taking_the_next_word_by_their_long_names_are_left_out(self):
        # Given: git with each of its own long options that take the next word before its command
        # When: it is read
        # Then: the command run is git's command, as the step names it
        command = "git --git-dir .git --work-tree . --namespace n --config-env a.b=C commit -m m"
        self.assertEqual(runs(command).what, [["git", "commit", "-m", "m"]])

    def test_assignments_and_env_before_a_command_are_left_out(self):
        # Given: a command after assignments, after env with its options, one taking the next
        # word, and assignments, or after both
        # When: it is read
        # Then: the command run is the one after them, as the step names it
        for command in (
            "A=b C_1=d git commit -m m",
            "env git commit -m m",
            "env -i -u A -C x B=c git commit -m m",
            "A=b env git commit -m m",
        ):
            with self.subTest(command=command):
                self.assertEqual(runs(command).what, [["git", "commit", "-m", "m"]])

    def test_a_word_not_an_assignment_or_env_alone_is_the_command_run(self):
        # Given: a word with `=` that is no assignment, a name begun with a digit or holding a
        # sign, or with nothing before `=`; and env or an assignment with no command after it
        # When: it is read
        # Then: the words are the command run, as they are
        for words in (["1A=b", "x"], ["a-b=c", "x"], ["=b", "x"], ["env"], ["env", "-i"], ["A=b"]):
            with self.subTest(words=words):
                self.assertEqual(runs(" ".join(words)).what, [words])

    def test_a_cd_before_a_command_is_no_command_run(self):
        # Given: a cd before the command, as the AI writes it to run it in another folder
        # When: it is read
        # Then: the command alone is run
        self.assertEqual(runs("cd notes && git commit").what, [["git", "commit"]])

    def test_a_redirect_and_its_target_are_no_words_of_the_command(self):
        # Given: a command whose output is redirected
        # When: it is read
        # Then: its words leave the redirect and its target out
        self.assertEqual(runs("npm publish > out.txt 2>&1").what, [["npm", "publish"]])

    def test_a_bash_call_without_a_command_runs_nothing(self):
        # Given: a Bash call whose input holds no command
        made = helpers.acted("Bash", {})
        # When: it is read
        # Then: it is a run of no command
        self.assertEqual(made, call.Call("run", [], tool="Bash", given={}))


class TestWrite(unittest.TestCase):
    def test_a_tool_that_writes_a_file_is_a_write_of_its_path(self):
        for tool, field in (
            ("Write", "file_path"),
            ("Edit", "file_path"),
            ("NotebookEdit", "notebook_path"),
        ):
            with self.subTest(tool=tool):
                # Given: a call of a tool that writes the file its input names
                made = helpers.acted(tool, {field: "/r/CHANGELOG.md"})
                # When: it is read
                # Then: it is a write of that file, running nothing
                written = call.Call("write", [], ("/r/CHANGELOG.md",))
                expected = written._replace(tool=tool, given=made.given)
                self.assertEqual(made, expected)

    def test_a_path_relative_to_the_folder_is_written_there(self):
        # Given: a Write naming its file from the folder the call is made in
        made = helpers.acted("Write", {"file_path": "a/../b.md"})
        # When: it is read
        # Then: the file written is the one the path names from that folder
        self.assertEqual(made.written, ("/r/b.md",))

    def test_a_write_naming_no_file_writes_none(self):
        # Given: a Write whose input names no file
        made = helpers.acted("Write", {})
        # When: it is read
        # Then: it is a write of no file
        self.assertEqual(made, call.Call("write", [], (), tool="Write", given={}))

    def test_a_bash_call_writes_what_its_commands_write(self):
        # Given: a Bash call whose commands write by a redirect and by cp
        # When: it is read
        # Then: it writes each target, as the shell reads them
        found = runs("echo x > out.txt && cp a.md b.md")
        self.assertEqual(found.written, ("/r/out.txt", "/r/b.md"))


class TestOtherTools(unittest.TestCase):
    def test_a_call_of_a_tool_no_lane_watches_is_no_action(self):
        for tool in ("AskUserQuestion", "TodoWrite"):
            with self.subTest(tool=tool):
                # Given: a call of a tool no lane of this version reads, its input holding a command
                made = helpers.acted(tool, {"command": "git commit"})
                # When: it is read
                # Then: it is no action, and runs nothing
                expected = call.Call("", [], tool=tool, given=made.given)
                self.assertEqual(made, expected)


class TestReads(unittest.TestCase):
    def test_the_read_tool_reads_its_file_the_lines_told_by_its_result(self):
        # Given: a Read call of a file, by its path from the folder and by its whole path
        # When: what it reads is read
        # Then: it reads the file, its lines not told by its input
        for named in ("a", "/r/a"):
            with self.subTest(named=named):
                self.assertEqual(call.reads("Read", {"file_path": named}, HERE), [("/r/a", None)])

    def test_the_grep_tool_reads_its_path_or_the_folder_it_runs_in(self):
        # Given: a Grep call naming a folder, and one naming none
        # When: what each reads is read
        # Then: it reads the folder named, or the one it runs in, its lines not told by its input
        for given, read in (({"pattern": "x", "path": "d"}, "/r/d"), ({"pattern": "x"}, "/r")):
            with self.subTest(given=given):
                self.assertEqual(call.reads("Grep", given, HERE), [(read, None)])

    def test_a_bash_call_reads_what_its_commands_read(self):
        # Given: a Bash call printing lines of a file
        # When: what it reads is read
        # Then: it reads those lines of the file
        given = {"command": "head -n 5 a"}
        self.assertEqual(call.reads("Bash", given, HERE), [("/r/a", (1, 5))])

    def test_a_call_naming_no_file_it_reads_reads_nothing(self):
        # Given: a Read call naming no path, or one the words do not settle; a Bash call with no
        # command; and calls of tools that read no file, one with a command in its input
        # When: what each reads is read
        # Then: it reads nothing
        for tool, given in (
            ("Read", {}),
            ("Read", {"file_path": "$HOME/a"}),
            ("Bash", {}),
            ("Agent", {"file_path": "a"}),
            ("AskUserQuestion", {"command": "cat a"}),
            ("Write", {"file_path": "a"}),
        ):
            with self.subTest(tool=tool, given=given):
                self.assertEqual(call.reads(tool, given, HERE), [])


class TestReadCall(unittest.TestCase):
    def test_a_call_of_a_tool_that_reads_is_a_read_of_what_it_reads(self):
        for tool, given, read in (
            ("Read", {"file_path": "a"}, "/r/a"),
            ("Grep", {"pattern": "x", "path": "d"}, "/r/d"),
        ):
            with self.subTest(tool=tool):
                # Given: a call of the Read or the Grep tool
                made = helpers.acted(tool, given)
                # When: it is read
                # Then: it is a read of what it reads, its lines not told, running nothing
                expected = call.Call("read", [], (), ((read, None),), tool=tool, given=given)
                self.assertEqual(made, expected)

    def test_a_bash_call_is_a_run_reading_what_its_commands_read(self):
        # Given: a Bash call printing lines of a file
        # When: it is read
        # Then: it is a run reading those lines of the file
        self.assertEqual(runs("head -n 5 a").reads, (("/r/a", (1, 5)),))

    def test_lines_not_told_are_those_numbered_in_what_the_call_gave_back(self):
        # Given: a Read call that gave back lines 3 and 4, each after its number and a tab, as the
        # Read tool gives them
        # When: it is read with what it gave back
        # Then: it reads the lines from the first numbered to the last
        found = call.alone("Read", {"file_path": "a"}, HERE, "3\tx\n4\ty\n")
        self.assertEqual(found.reads, (("/r/a", (3, 4)),))

    def test_lines_not_told_and_none_numbered_are_not_known(self):
        # Given: a Read call that gave back no numbered line, such as a stop for a file too large
        # When: it is read with what it gave back
        # Then: the lines it read are not known
        found = call.alone("Read", {"file_path": "a"}, HERE, "File content exceeds 256KB.")
        self.assertEqual(found.reads, (("/r/a", None),))

    def test_lines_the_input_tells_are_kept_whatever_came_back(self):
        # Given: a Bash call printing the first 5 lines, which gave back other numbered lines
        # When: it is read with what it gave back
        # Then: it reads the lines its input tells
        found = call.alone("Bash", {"command": "head -n 5 a"}, HERE, "7\tx\n")
        self.assertEqual(found.reads, (("/r/a", (1, 5)),))


class TestMade(helpers.PluginTest):
    def test_a_call_is_read_with_the_calls_its_subagent_made_before_it(self):
        # Given: a subagent's record of two Bash calls
        status = "cd notes && git status"
        self.record([helpers.bash("ls"), helpers.bash(status)])
        # When: its next call is read
        made = helpers.call_of(self.event("git commit"))
        # Then: it is the call, read as itself, with each call before it read as the guard reads
        # a call, in order
        self.assertEqual(made.what, [["git", "commit"]])
        before = [
            call.Call("run", [["ls"]], tool="Bash", given={"command": "ls"}, ends=("\n",)),
            call.Call(
                "run", [["git", "status"]], tool="Bash", given={"command": status}, ends=("\n",)
            ),
        ]
        self.assertEqual(made.before, tuple(before))

    def test_a_call_before_is_read_with_what_it_gave_back(self):
        # Given: a subagent's record of a Read call that gave back the first two lines
        self.record([("Read", {"file_path": "a"}, "1\tx\n2\ty\n")])
        # When: its next call is read
        made = helpers.call_of(self.event("ls"))
        # Then: the call before reads those lines
        read = call.Call("read", [], (), ((f"{self.base}/a", (1, 2)),))
        given = {"file_path": "a"}
        made_before = read._replace(tool="Read", given=given, result="1\tx\n2\ty\n")
        self.assertEqual(made.before, (made_before,))

    def test_a_call_whose_record_is_not_found_has_nothing_before_it(self):
        # Given: no record of the subagent where Claude Code keeps it
        # When: its call is read
        made = helpers.call_of(self.event("ls"))
        # Then: no call is read before it and no message as reaching the subagent, as a lane
        # resting on the record is stopped by its IN first, the record not found
        self.assertEqual((made.before, made.heard), ((), ()))

    def test_a_call_read_alone_knows_nothing_before_it(self):
        # Given: a subagent's record of a call
        self.record([helpers.bash("ls")])
        # When: its next call is read alone
        # Then: what came before is not read
        self.assertEqual(call.alone("Bash", {"command": "pwd"}, self.base).before, ())

    def test_a_call_before_is_read_with_whether_it_failed(self):
        # Given: a subagent's record of a command that failed
        self.record([helpers.failing("false")])
        # When: its next call is read
        # Then: the call before failed
        self.assertEqual([c.failed for c in helpers.call_of(self.event("ls")).before], [True])

    def test_a_call_is_read_with_the_messages_that_reached_its_subagent(self):
        # Given: a subagent's record of its asking, and a message from main since
        ask = ("SendMessage", {"to": "main", "message": "May I?"}, "")
        self.record([ask, helpers.from_main("OK")])
        # When: its next call is read
        # Then: it holds the message, the call before it none
        made = helpers.call_of(self.event("ls"))
        heard = [made.heard, *(c.heard for c in made.before)]
        self.assertEqual(heard, [("OK",), ()])


class TestHandOn(unittest.TestCase):
    def test_a_call_of_the_agent_tool_or_sendmessage_hands_on_its_text(self):
        for tool, given in (
            ("Agent", {"subagent_type": "x:y", "prompt": "Do it."}),
            ("SendMessage", {"to": "main", "message": "Do it.", "summary": "s"}),
        ):
            with self.subTest(tool=tool):
                # Given: a call of a tool that hands text on to another agent
                made = helpers.acted(tool, given)
                # When: it is read
                # Then: it is a hand-on of its text, running nothing
                self.assertEqual(
                    (made.action, made.what, call.handed(made)), ("hand on", [], "Do it.")
                )

    def test_a_reply_that_ended_its_turn_hands_on_its_text(self):
        # Given: the subagent's reply ending its turn, as its record is read
        done = helpers.record.Done(
            helpers.record.REPLY, {helpers.record.SAID: "Is that so?"}, HERE, ""
        )
        # When: it is read as an action
        made = call.made(done)
        # Then: it is a hand-on of its text, running nothing
        self.assertEqual(
            (made.action, made.what, call.handed(made)), ("hand on", [], "Is that so?")
        )

    def test_a_hand_on_of_no_text_hands_on_nothing(self):
        for given in ({"to": "main"}, {"to": "main", "message": {"type": "shutdown"}}):
            with self.subTest(given=given):
                # Given: a SendMessage of no message, or of one that is no text
                made = helpers.acted("SendMessage", given)
                # When: what it hands on is read
                # Then: it is nothing
                self.assertEqual(call.handed(made), "")

    def test_a_call_that_is_no_hand_on_hands_on_nothing(self):
        for tool in ("Bash", "AskUserQuestion"):
            with self.subTest(tool=tool):
                # Given: a run, or a call of no action, whose input holds a field named as a
                # hand-on's
                given = {"command": "ls", "prompt": "x"}
                made = helpers.acted(tool, given)
                # When: what it hands on is read
                # Then: it is nothing
                self.assertEqual(call.handed(made), "")


class TestText(testing.FolderTest):
    """The text the file a call writes holds once it is written, for a call made in `base`."""

    def text(self, tool: str, given: dict) -> str | None:
        """The text a call of the tool with the input, made in `base`, writes."""
        return helpers.acted(tool, given, self.base).text

    def test_a_write_holds_its_content(self):
        # Given: a Write of a file with its content
        # When: it is read
        # Then: the text written is the content
        self.assertEqual(self.text("Write", {"file_path": "a.md", "content": "x\n"}), "x\n")

    def test_an_edit_holds_the_files_text_with_the_edit_made_once(self):
        # Given: a file holding the old text twice
        self.write("a.md", "old old\n")
        # When: an Edit replaces it, not every one
        # Then: the text written is the file's with the first replaced
        given = {"file_path": "a.md", "old_string": "old", "new_string": "new"}
        self.assertEqual(self.text("Edit", given), "new old\n")

    def test_an_edit_replacing_all_holds_every_one_replaced(self):
        # Given: a file holding the old text twice
        self.write("a.md", "old old\n")
        # When: an Edit replaces every one
        given = {"file_path": "a.md", "old_string": "old", "new_string": "new", "replace_all": True}
        # Then: the text written has both replaced
        self.assertEqual(self.text("Edit", given), "new new\n")

    def test_an_edit_of_text_not_in_the_file_writes_none(self):
        # Given: a file without the old text, and no file at all
        self.write("a.md", "x\n")
        for path in ("a.md", "none.md"):
            with self.subTest(path=path):
                # When: an Edit would replace it
                given = {"file_path": path, "old_string": "old", "new_string": "new"}
                # Then: no text is written, as the tool writes nothing
                self.assertIsNone(self.text("Edit", given))

    def test_an_edit_of_a_file_not_there_from_nothing_holds_the_new_text(self):
        # Given: no file at the path
        # When: an Edit replaces nothing with text
        given = {"file_path": "new.md", "old_string": "", "new_string": "x"}
        # Then: the text written is the new text
        self.assertEqual(self.text("Edit", given), "x")

    def test_a_call_whose_text_is_not_given_writes_none_known(self):
        self.write("a.md", "x\n")
        edit = {"file_path": "a.md", "old_string": "x", "new_string": "y", "content": "z"}
        for tool, given in (
            ("Write", {"file_path": "a.md"}),
            ("Edit", {"file_path": "a.md", "old_string": "x"}),
            ("Edit", {"file_path": "a.md", "new_string": "x"}),
            ("Bash", {"command": "echo x > a.md"}),
            ("Read", {"file_path": "a.md"}),
            ("AskUserQuestion", edit),
            ("mcp__files__edit", edit),
        ):
            with self.subTest(tool=tool, given=given):
                # Given: a call whose input gives no text, or that writes by a command, or of
                # another tool whose input holds what Write's and Edit's do
                # When: it is read
                # Then: its text is not known
                self.assertIsNone(self.text(tool, given))


class TestEnded(helpers.PluginTest):
    def test_each_call_made_is_read_in_order_with_whether_it_failed(self):
        # Given: a record of a Write of a file, then a Bash call giving back an error
        self.record([helpers.writing("a.md"), helpers.failing("false")])
        # When: how the subagent is about to end is read
        made = helpers.end_of(self.stopped("done")).made
        # Then: each call is read as its action, the second failed, its command ended by the line
        a = f"{self.base}/a.md"
        found = [(m.action, m.what, m.written, m.failed, m.ends) for m in made or []]
        self.assertEqual(
            found, [("write", [], (a,), False, ()), ("run", [["false"]], (), True, ("\n",))]
        )

    def test_what_ends_each_command_of_a_run_is_read(self):
        # Given: a record of a Bash call of three commands, joined by && and a pipe
        self.record([helpers.bash("cd x && make test | tail -3")])
        # When: how the subagent is about to end is read
        made = helpers.end_of(self.stopped()).made or []
        # Then: the run holds what ends each command but the cd, a line's end after the last
        found = [(m.what, m.ends) for m in made]
        self.assertEqual(found, [([["make", "test"], ["tail", "-3"]], ("|", "\n"))])

    def test_the_last_reply_is_the_events(self):
        # Given: a SubagentStop event of the reply `done`
        self.record([])
        # When: how the subagent is about to end is read
        # Then: its last reply is the event's
        self.assertEqual(helpers.end_of(self.stopped("done")).reply, "done")

    def test_no_last_reply_is_read_as_none_said(self):
        # Given: a SubagentStop event whose last reply is null, as after a SubagentHandback
        self.record([])
        # When: how the subagent is about to end is read
        # Then: its last reply says nothing
        self.assertEqual(
            helpers.end_of({**self.stopped(), "last_assistant_message": None}).reply, ""
        )

    def test_no_record_found_is_not_known(self):
        for active in (False, True):
            with self.subTest(active=active):
                # Given: a SubagentStop event whose record is not there, kept going by a stop hook
                # or not
                # When: how the subagent is about to end is read
                end = helpers.end_of(self.stopped(active=active))
                # Then: no call is read as made, nor is it read as having answered, as a lane
                # held at the end rests on the record and is stopped by its IN first
                self.assertEqual((end.made, end.answered), ((), False))

    def test_answered_only_where_kept_going_by_a_stop_hook_and_no_call_since(self):
        rules = {
            # (kept going by a stop hook, told with no call since): answered
            (True, True): True,
            (True, False): False,
            (False, True): False,
            (False, False): False,
        }
        for (active, still), answered in rules.items():
            with self.subTest(active=active, still=still):
                # Given: an event kept going by a stop hook or not, of a record whose last telling
                # has no call after it or one
                self.record([helpers.bash("ls"), "told"] + ([] if still else [helpers.bash("ls")]))
                # When: how the subagent is about to end is read
                # Then: it answered with words only where both hold
                self.assertEqual(helpers.end_of(self.stopped(active=active)).answered, answered)


class TestChanged(unittest.TestCase):
    def test_a_call_changed_a_file_it_wrote_unless_a_writing_tool_failed(self):
        rules = [
            # (the call, the file): changed
            (("Write", {"file_path": "/r/a"}, False), "/r/a", True),
            (("Write", {"file_path": "/r/a"}, True), "/r/a", False),
            (("Write", {"file_path": "/r/a"}, False), "/r/b", False),
            (("Bash", {"command": "echo > a"}, True), "/r/a", True),
            (("Bash", {"command": "echo > a"}, False), "/r/b", False),
        ]
        for (tool, given, failed), file, changed in rules:
            with self.subTest(tool=tool, failed=failed, file=file):
                # Given: a call of a tool that writes, or of Bash, failed or not
                made = call.alone(tool, given, HERE)._replace(failed=failed)
                # When: whether it changed the file is read
                # Then: it did where it wrote it, unless the tool that writes gave back an error
                self.assertEqual(call.changed(made, file), changed)


if __name__ == "__main__":
    unittest.main()
