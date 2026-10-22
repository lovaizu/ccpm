"""start_with: until the subagent has run the script the lane takes, any call that does not run it is
a drift, in the forms the steps tell and the AI writes; once it has run it, no call is."""

import unittest

from helpers import call, start_with

# The script the lane takes, as a step names it, and its path as the AI writes it once Claude Code
# has put the plugin's folder in for `${CLAUDE_PLUGIN_ROOT}`.
TAKES = ["scripts/turn.py"]
SCRIPT = "/home/u/.claude/plugins/turn/scripts/turn.py"


def read(command, tool="Bash"):
    """A call of the tool with the command, as the guard reads it."""
    return call.read({"cwd": "/r", "tool_name": tool, "tool_input": {"command": command}})


def drifts(command, before=(), takes=TAKES, tool="Bash"):
    """Whether the call drifts, made after the Bash calls of the commands before it."""
    made = read(command, tool)._replace(before=[read(b) for b in before])
    return start_with.drifts(made, takes)


class TestFirstCall(unittest.TestCase):
    def test_a_first_call_running_the_script_in_the_forms_the_ai_writes_is_no_drift(self):
        for command in (
            f'python3 "{SCRIPT}" given /tmp/run',
            f"{SCRIPT} given /tmp/run",
            f"sh {SCRIPT}",
            "python3 scripts/turn.py",
            f"cd /r && python3 {SCRIPT} start x",
            '"${CLAUDE_PLUGIN_ROOT}/scripts/turn.py" next',
        ):
            with self.subTest(command=command):
                # Given: no call made before
                # When: the subagent's first call runs the script, in a form the AI writes
                # Then: it is no drift
                self.assertFalse(drifts(command))

    def test_a_first_call_running_anything_else_drifts(self):
        for command in (
            "ls",
            "wc -l notes.txt",
            f"cat {SCRIPT}",
            "python3",
            "python3 /p/scripts/other.py",
            "python3 /p/myscripts/turn.py",
            "python3 /p/turn.py",
        ):
            with self.subTest(command=command):
                # Given: no call made before
                # When: the subagent's first call runs something else, a command sorting before
                # the script's name or after it, the script only read, or a script of another name
                # or folder
                # Then: it is a drift
                self.assertTrue(drifts(command))

    def test_a_first_call_of_another_tool_drifts(self):
        # Given: no call made before
        # When: the subagent's first call is of a tool that runs nothing, such as Read
        # Then: it is a drift
        self.assertTrue(drifts(SCRIPT, tool="Read"))

    def test_a_script_taken_with_its_words_is_run_only_with_them(self):
        # Given: a lane taking the script with the words its step runs it with
        takes = ["scripts/turn.py given"]
        # When: the first call runs it with those words, with others, or with none
        # Then: those words begin no drift; others, or none, do
        self.assertFalse(drifts(f"python3 {SCRIPT} given /tmp/run", takes=takes))
        self.assertTrue(drifts(f"python3 {SCRIPT} next /tmp/run", takes=takes))
        self.assertTrue(drifts(f"python3 {SCRIPT}", takes=takes))

    def test_a_script_taken_with_several_words_is_run_with_all_of_them_first(self):
        # Given: a lane taking the script with two words after it
        takes = ["scripts/turn.py next run"]
        # When: the first call runs it with those two words and more after them, or with the
        # first alone
        # Then: those two words begin no drift; the first alone does
        self.assertFalse(drifts(f"python3 {SCRIPT} next run x", takes=takes))
        self.assertTrue(drifts(f"python3 {SCRIPT} next", takes=takes))

    def test_any_of_the_scripts_taken_may_be_run_first(self):
        # Given: a lane taking two scripts
        takes = ["scripts/a.py", "scripts/turn.py"]
        # When: the first call runs the second
        # Then: it is no drift
        self.assertFalse(drifts(f"python3 {SCRIPT}", takes=takes))


class TestLaterCalls(unittest.TestCase):
    def test_once_the_script_has_run_any_call_goes_on(self):
        # Given: the script run before
        # When: the subagent makes any other call
        # Then: it is no drift
        self.assertFalse(drifts("ls", before=["pwd", f"python3 {SCRIPT}"]))

    def test_until_the_script_has_run_every_other_call_drifts(self):
        # Given: calls made before, none running the script, such as one stopped by this lane
        # When: the subagent makes another call that does not run it
        # Then: it is a drift still
        self.assertTrue(drifts("ls", before=["pwd"]))

    def test_with_no_record_found_every_call_goes_on(self):
        # Given: a call whose subagent's record is not found, so what it did before is not known
        made = read("ls")
        # When: start_with reads it
        # Then: it is no drift, as a stop then would hold even after the script is run
        self.assertFalse(start_with.drifts(made, TAKES))


if __name__ == "__main__":
    unittest.main()
