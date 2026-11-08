"""The cases of run_only's check, which stops a command that no lane of the role names."""

from helpers import lanes, run_only, testing

CONTEXT = lanes.Context(("git log --oneline", "python3 /p/c.py"), ())
GIVEN = {"commands": ["git log --oneline"]}


def bash(text):
    return lanes.Call("Bash", {"command": text}, "/work")


class TestCheck(testing.FolderTest):
    def test_a_command_of_this_lane_goes_on(self):
        self.assertIsNone(run_only.check(bash("git log --oneline"), GIVEN, CONTEXT))

    def test_a_command_that_another_lane_of_the_role_names_goes_on(self):
        self.assertIsNone(run_only.check(bash("python3 /p/c.py"), GIVEN, CONTEXT))

    def test_any_other_command_is_broken_with_the_commands_the_role_may_run(self):
        self.assertEqual(
            run_only.check(bash("git commit -m x"), GIVEN, CONTEXT),
            "The commands you may run: `git log --oneline` and `python3 /p/c.py`.",
        )

    def test_a_role_that_may_run_no_command_is_told_so(self):
        self.assertEqual(
            run_only.check(bash("ls"), {"commands": []}, lanes.Context((), ())),
            "You may run no command.",
        )

    def test_each_dependency_folder_is_told_what_it_stands_for(self):
        context = lanes.Context(("python3 ${dependency:checker}/c.py",), ())
        self.assertEqual(
            run_only.check(bash("ls"), GIVEN, context),
            "The commands you may run: `python3 ${dependency:checker}/c.py`.\n"
            "`${dependency:checker}` stands for the folder that holds the plugin checker.",
        )

    def test_a_call_of_another_tool_goes_on(self):
        call = lanes.Call("Read", {"file_path": "a"}, "/work")
        self.assertIsNone(run_only.check(call, GIVEN, CONTEXT))

    def test_a_bash_call_with_no_command_cannot_be_checked(self):
        call = lanes.Call("Bash", {}, "/work")
        with self.assertRaisesRegex(lanes.Unchecked, r"the Bash call gives no command"):
            run_only.check(call, GIVEN, CONTEXT)
