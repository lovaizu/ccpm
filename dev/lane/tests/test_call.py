"""A tool call read as one action: a Bash call as the commands it runs and the files they read and
write, in the forms the steps tell and the AI writes, a call of the Read or Grep tool as a read of
what it reads, and a call of a tool that writes a file as a write of it; each with the calls its
subagent made before it."""

import unittest

import helpers
from helpers import call, testing

# The folder each command runs in.
HERE = "/r"


def runs(command):
    """The commands a Bash call of the command runs, as the guard reads it."""
    return call.read({"cwd": HERE, "tool_name": "Bash", "tool_input": {"command": command}})


class TestBash(unittest.TestCase):
    def test_a_bash_call_runs_its_command_with_its_words(self):
        # Given: a Bash call of one command
        # When: it is read
        # Then: it is a run of that command, its words as the shell takes them
        self.assertEqual(
            runs("git commit -m 'a b'"), call.Call("run", [["git", "commit", "-m", "a b"]])
        )

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
        event = {"cwd": HERE, "tool_name": "Bash", "tool_input": {}}
        # When: it is read
        # Then: it is a run of no command
        self.assertEqual(call.read(event), call.Call("run", []))


class TestWrite(unittest.TestCase):
    def test_a_tool_that_writes_a_file_is_a_write_of_its_path(self):
        for tool, field in (
            ("Write", "file_path"),
            ("Edit", "file_path"),
            ("NotebookEdit", "notebook_path"),
        ):
            with self.subTest(tool=tool):
                # Given: a call of a tool that writes the file its input names
                event = {"cwd": HERE, "tool_name": tool, "tool_input": {field: "/r/CHANGELOG.md"}}
                # When: it is read
                # Then: it is a write of that file, running nothing
                self.assertEqual(call.read(event), call.Call("write", [], ("/r/CHANGELOG.md",)))

    def test_a_path_relative_to_the_folder_is_written_there(self):
        # Given: a Write naming its file from the folder the call is made in
        event = {"cwd": HERE, "tool_name": "Write", "tool_input": {"file_path": "a/../b.md"}}
        # When: it is read
        # Then: the file written is the one the path names from that folder
        self.assertEqual(call.read(event).written, ("/r/b.md",))

    def test_a_write_naming_no_file_writes_none(self):
        # Given: a Write whose input names no file
        event = {"cwd": HERE, "tool_name": "Write", "tool_input": {}}
        # When: it is read
        # Then: it is a write of no file
        self.assertEqual(call.read(event), call.Call("write", [], ()))

    def test_a_bash_call_writes_what_its_commands_write(self):
        # Given: a Bash call whose commands write by a redirect and by cp
        # When: it is read
        # Then: it writes each target, as the shell reads them
        found = runs("echo x > out.txt && cp a.md b.md")
        self.assertEqual(found.written, ("/r/out.txt", "/r/b.md"))


class TestOtherTools(unittest.TestCase):
    def test_a_call_of_a_tool_no_lane_watches_is_no_action(self):
        for tool in ("Agent", "TodoWrite"):
            with self.subTest(tool=tool):
                # Given: a call of a tool no lane of this version reads, its name sorting before
                # Bash or after
                event = {"cwd": HERE, "tool_name": tool, "tool_input": {"command": "git commit"}}
                # When: it is read
                # Then: it is no action, and runs nothing
                self.assertEqual(call.read(event), call.Call("", []))


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
        # command; and calls of tools that read no file, sorting before and after the readers
        # When: what each reads is read
        # Then: it reads nothing
        for tool, given in (
            ("Read", {}),
            ("Read", {"file_path": "$HOME/a"}),
            ("Bash", {}),
            ("Agent", {"file_path": "a"}),
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
                event = {"cwd": HERE, "tool_name": tool, "tool_input": given}
                # When: it is read
                # Then: it is a read of what it reads, its lines not told, running nothing
                self.assertEqual(call.read(event), call.Call("read", [], (), ((read, None),)))

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
        self.record([helpers.bash("ls"), helpers.bash("cd notes && git status")])
        # When: its next call is read
        made = call.read(self.event("git commit"))
        # Then: it is the call, read as itself, with each call before it read as the guard reads
        # a call, in order
        self.assertEqual(made.what, [["git", "commit"]])
        before = [call.Call("run", [["ls"]]), call.Call("run", [["git", "status"]])]
        self.assertEqual(made.before, before)

    def test_a_call_before_is_read_with_what_it_gave_back(self):
        # Given: a subagent's record of a Read call that gave back the first two lines
        self.record([("Read", {"file_path": "a"}, "1\tx\n2\ty\n")])
        # When: its next call is read
        made = call.read(self.event("ls"))
        # Then: the call before reads those lines
        self.assertEqual(made.before, [call.Call("read", [], (), ((f"{self.base}/a", (1, 2)),))])

    def test_a_call_whose_record_is_not_found_has_nothing_known_before_it(self):
        # Given: no record of the subagent where Claude Code keeps it
        # When: its call is read
        # Then: what came before is not known, told apart from nothing before
        self.assertIsNone(call.read(self.event("ls")).before)

    def test_a_call_read_alone_knows_nothing_before_it(self):
        # Given: a subagent's record of a call
        self.record([helpers.bash("ls")])
        # When: its next call is read alone
        # Then: what came before is not read
        self.assertIsNone(call.alone("Bash", {"command": "pwd"}, self.base).before)


class TestText(testing.FolderTest):
    """The text the file a call writes holds once it is written, for a call made in `base`."""

    def text(self, tool, given):
        return call.read({"cwd": self.base, "tool_name": tool, "tool_input": given}).text

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
        for tool, given in (
            ("Write", {"file_path": "a.md"}),
            ("Edit", {"file_path": "a.md", "old_string": "x"}),
            ("Edit", {"file_path": "a.md", "new_string": "x"}),
            ("Bash", {"command": "echo x > a.md"}),
            ("Read", {"file_path": "a.md"}),
        ):
            with self.subTest(tool=tool, given=given):
                # Given: a call whose input gives no text, or that writes by a command
                # When: it is read
                # Then: its text is not known
                self.assertIsNone(self.text(tool, given))


if __name__ == "__main__":
    unittest.main()
