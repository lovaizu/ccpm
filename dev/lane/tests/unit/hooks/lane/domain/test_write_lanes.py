"""The cases of write_step, edit_only, run_step, and hold: a file made or a command run as a step's
trace, a file once made changed only with Edit, and a command put to the person."""

from typing import ClassVar

from helpers import edit_only, hold, lanes, run_step, testing, write_step

CONTEXT = lanes.Context((), ())


def call(tool, cwd="/p", **given):
    return lanes.Call(tool, given, cwd)


class TestWriteStep(testing.FolderTest):
    GIVEN: ClassVar[dict] = {"output": ["/p/notes"]}

    def test_a_write_of_the_output_is_its_trace(self):
        self.assertTrue(write_step.traced(call("Write", file_path="notes/a.md"), self.GIVEN))

    def test_an_edit_of_the_output_is_its_trace(self):
        self.assertTrue(write_step.traced(call("Edit", file_path="/p/notes/a.md"), self.GIVEN))

    def test_a_write_of_another_file_is_no_trace(self):
        self.assertFalse(write_step.traced(call("Write", file_path="/p/b.md"), self.GIVEN))

    def test_a_command_is_no_trace(self):
        self.assertFalse(write_step.traced(call("Bash", command="ls"), self.GIVEN))

    def test_a_write_of_the_output_kept_makes_the_step_done(self):
        self.assertIsNone(write_step.done(self.GIVEN, [call("Write", file_path="/p/notes/a.md")]))

    def test_no_write_of_the_output_leaves_it_to_make(self):
        self.assertEqual(write_step.done(self.GIVEN, []), "`/p/notes` isn't made yet.")


class TestEditOnly(testing.FolderTest):
    def given(self):
        self.write("tree.json", "{}")
        return {"output": [f"{self.base}/tree.json"]}

    def test_a_write_that_makes_the_output_goes_on(self):
        given = {"output": [f"{self.base}/new.json"]}
        self.assertIsNone(
            edit_only.check(call("Write", file_path=f"{self.base}/new.json"), given, CONTEXT)
        )

    def test_a_write_of_the_output_once_there_is_broken(self):
        self.assertEqual(
            edit_only.check(
                call("Write", file_path=f"{self.base}/tree.json"), self.given(), CONTEXT
            ),
            f"`{self.base}/tree.json` is there, so change it with Edit.",
        )

    def test_an_edit_of_the_output_goes_on(self):
        self.assertIsNone(
            edit_only.check(call("Edit", file_path=f"{self.base}/tree.json"), self.given(), CONTEXT)
        )

    def test_a_notebook_edit_of_the_output_is_broken(self):
        given = {"output": [f"{self.base}/n.ipynb"]}
        self.assertEqual(
            edit_only.check(
                call("NotebookEdit", notebook_path=f"{self.base}/n.ipynb"), given, CONTEXT
            ),
            f"`{self.base}/n.ipynb` changes only with Edit.",
        )

    def test_a_write_of_another_file_goes_on(self):
        self.write("other.json", "{}")
        call_ = call("Write", file_path=f"{self.base}/other.json")
        self.assertIsNone(edit_only.check(call_, self.given(), CONTEXT))


class TestRunStep(testing.FolderTest):
    GIVEN: ClassVar[dict] = {"commands": ["python3 /p/c.py commit", "python3 /p/c.py deliver"]}

    def test_a_run_of_one_of_its_commands_is_its_trace(self):
        self.assertTrue(
            run_step.traced(call("Bash", command="python3 /p/c.py deliver"), self.GIVEN)
        )

    def test_another_command_is_no_trace(self):
        self.assertFalse(run_step.traced(call("Bash", command="ls"), self.GIVEN))

    def test_a_read_is_no_trace(self):
        self.assertFalse(run_step.traced(call("Read", file_path="/p/a"), self.GIVEN))

    def test_a_run_of_one_of_its_commands_kept_makes_the_step_done(self):
        self.assertIsNone(
            run_step.done(self.GIVEN, [call("Bash", command="python3 /p/c.py commit")])
        )

    def test_no_run_of_its_commands_leaves_the_step_to_do(self):
        self.assertEqual(
            run_step.done(self.GIVEN, []),
            "`python3 /p/c.py commit` or `python3 /p/c.py deliver` hasn't run yet.",
        )

    def test_a_step_whose_commands_are_all_given_null_is_done(self):
        self.assertIsNone(run_step.done({"commands": []}, []))


class TestHold(testing.FolderTest):
    GIVEN: ClassVar[dict] = {"commands": ["git push"]}

    def test_a_command_it_holds_goes_to_the_person(self):
        self.assertTrue(hold.held(call("Bash", command="git push"), self.GIVEN))

    def test_any_other_command_goes_on(self):
        self.assertFalse(hold.held(call("Bash", command="git status"), self.GIVEN))

    def test_a_call_of_another_tool_goes_on(self):
        self.assertFalse(hold.held(call("Read", file_path="/p/a"), self.GIVEN))
