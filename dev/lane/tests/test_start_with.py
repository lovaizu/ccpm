"""start_with: until the subagent has run the script the lane takes, any call that does not run it is
a drift, in the forms the steps tell and the AI writes; once it has run it, no call is."""

import unittest

import helpers
from helpers import NO_PLUGIN, start_with

# The script the lane takes, as a step names it, and its path as the AI writes it once Claude Code
# has put the plugin's folder in for `${CLAUDE_PLUGIN_ROOT}`.
TAKES = ["scripts/turn.py"]
SCRIPT = "/home/u/.claude/plugins/turn/scripts/turn.py"
# The script taken as turn's step 1 writes the command, with python3 and the plugin's folder as
# Claude Code puts it in.
WRITTEN = ['python3 "${CLAUDE_PLUGIN_ROOT}/scripts/turn.py" given']


def read(command, tool="Bash"):
    """A call of the tool with the command, as the guard reads it."""
    return helpers.call_of({"cwd": "/r", "tool_name": tool, "tool_input": {"command": command}})


def drifts(command, before=(), takes=TAKES, tool="Bash"):
    """Whether the call drifts, made after the Bash calls of the commands before it."""
    made = read(command, tool)._replace(before=[read(b) for b in before])
    return start_with.drifts(made, takes, NO_PLUGIN)


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
            "A=/scripts/turn.py 0",
        ):
            with self.subTest(command=command):
                # Given: no call made before
                # When: the subagent's first call runs something else, another command, the
                # script only read, a script of another name
                # or folder, or the script's path as an assignment's value, as the shell reads a
                # path whose folder is a name and `=` before the command it runs
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


class TestTakenAsTheStepWritesIt(unittest.TestCase):
    def test_the_script_run_as_the_step_writes_it_is_no_drift(self):
        for command in (
            f'python3 "{SCRIPT}" given /tmp/run',
            f"{SCRIPT} given /tmp/run",
            'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/turn.py" given /tmp/run',
        ):
            with self.subTest(command=command):
                # Given: a lane taking the script as the step writes the command
                # When: the first call runs it with the plugin's folder put in, by its path alone,
                # or as the step writes it
                # Then: it is no drift
                self.assertFalse(drifts(command, takes=WRITTEN))

    def test_anything_else_run_first_drifts(self):
        for command in (
            f"python3 {SCRIPT} next /tmp/run",
            "python3 /p/scripts/other.py given",
            "python3 given",
        ):
            with self.subTest(command=command):
                # Given: a lane taking the script as the step writes the command
                # When: the first call runs it with other words, another script, or python3 on
                # the words after the script
                # Then: it is a drift
                self.assertTrue(drifts(command, takes=WRITTEN))

    def test_a_script_run_by_sh_is_taken_by_its_path(self):
        # Given: a lane taking a script run by sh, as a step writes it
        takes = ['sh "${CLAUDE_PLUGIN_ROOT}/scripts/turn.py"']
        # When: the first call runs it by sh with the plugin's folder put in
        # Then: it is no drift
        self.assertFalse(drifts(f"sh {SCRIPT}", takes=takes))

    def test_a_take_naming_no_script_is_run_by_no_call(self):
        # Given: a lane taking python3 alone, naming no script
        # When: the first call runs python3 alone
        # Then: it is a drift, as no script taken has run
        self.assertTrue(drifts("python3", takes=["python3"]))

    def test_a_take_naming_no_script_leaves_the_others_taken(self):
        # Given: a lane taking python3 alone, then the script
        # When: the first call runs the script
        # Then: it is no drift
        self.assertFalse(drifts(f"python3 {SCRIPT}", takes=["python3", *TAKES]))


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
        self.assertFalse(start_with.drifts(made, TAKES, NO_PLUGIN))


if __name__ == "__main__":
    unittest.main()
