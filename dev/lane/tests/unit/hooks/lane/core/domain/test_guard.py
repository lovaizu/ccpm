"""The guard: of a tool call of a subagent with lanes laid, whether it goes through or which
sentences stop it, judged from the call's documented input alone; and, where it cannot judge, the
error that says why and who must fix it."""

import os
import unittest

import helpers
from helpers import guard

# What a subagent is told, after run_only's sentence, of the commands it may run.
MAY_RUN = "The commands you may run, each word for word: `git log --oneline`."
LAY_AGAIN = (
    "Ask the main conversation for the fix: the maker of changelog must lay its lanes again with"
    " `lay.py write`, so they match its steps. Go on with the rest of your work meanwhile."
)


class GuardTest(helpers.PluginTest):
    def setUp(self) -> None:
        super().setUp()
        self.lay()

    def check(self, event: dict, name: str = "writer", wrong: str = "") -> list:
        """What the guard says of the event, of the subagent of the name."""
        return guard.check(self.plugin, "changelog", name, event, wrong)


class TestRun(GuardTest):
    def test_a_command_its_lanes_name_goes_through(self):
        # Given: writer, whose step 2 runs only git log --oneline
        # When: it runs git log --oneline
        # Then: nothing is said, so the call goes on
        self.assertEqual(self.check(self.bash("git log --oneline")), [])

    def test_any_other_command_is_stopped_with_the_sentence_and_the_commands_it_may_run(self):
        for command in ("git commit -m entries", "git log --oneline -3", "ls"):
            with self.subTest(command=command):
                # Given: writer, whose step 2 runs only git log --oneline
                # When: it runs another command
                # Then: it is told the sentence, and on the next line the commands it may run
                self.assertEqual(
                    self.check(self.bash(command)), [guard.Said(f"{helpers.RUN}\n{MAY_RUN}")]
                )

    def test_the_commands_of_every_run_lane_go_through_and_are_told(self):
        # Given: writer running only git log --oneline on step 2 and only git diff on step 3
        self.lay(
            [
                helpers.STEPS[0],
                {"step": 3, "lanes": [{"lane": "run_only", "takes": ["git diff"]}]},
            ],
            helpers.WRITER.replace("--oneline`.\n", f"--oneline`. {helpers.RUN}\n").replace(
                "`CHANGELOG.md`.\n", "`CHANGELOG.md`. Run only `git diff`.\n"
            ),
        )
        # When: it runs git diff, and git commit
        # Then: git diff goes through, and git commit is told both sentences and both commands
        self.assertEqual(self.check(self.bash("git diff")), [])
        commands = "`git log --oneline`, `git diff`"
        told = (
            f"{helpers.RUN}\nRun only `git diff`.\n"
            f"The commands you may run, each word for word: {commands}."
        )
        self.assertEqual(self.check(self.bash("git commit")), [guard.Said(told)])

    def test_a_subagent_with_lanes_and_no_run_lane_runs_no_command(self):
        # Given: writer with write_only alone laid
        self.lay([helpers.STEPS[1]], helpers.LAID.replace(f" {helpers.RUN}", ""))
        # When: it runs a command
        # Then: it is told it may run none
        self.assertEqual(
            self.check(self.bash("git log --oneline")), [guard.Said("You may run no command.")]
        )


class TestWrite(GuardTest):
    def test_an_output_its_lanes_name_is_written(self):
        for tool in ("Write", "Edit"):
            with self.subTest(tool=tool):
                # Given: writer, whose step 3 writes only CHANGELOG.md
                # When: it writes CHANGELOG.md by its whole path
                # Then: the call goes on
                path = os.path.join(self.base, "CHANGELOG.md")
                self.assertEqual(self.check(self.written(path, tool)), [])

    def test_any_other_file_is_stopped_with_the_sentence(self):
        for tool in ("Write", "Edit", "NotebookEdit"):
            with self.subTest(tool=tool):
                # Given: writer, whose step 3 writes only CHANGELOG.md
                # When: it writes another file, a notebook among them
                # Then: it is told the sentence
                self.assertEqual(
                    self.check(self.written("notes.ipynb", tool)), [guard.Said(helpers.WRITE)]
                )

    def test_a_subagent_with_no_write_lane_writes_freely(self):
        # Given: writer with run_only alone laid
        self.lay([helpers.STEPS[0]], helpers.LAID.replace(f" {helpers.WRITE}", ""))
        # When: it writes a file
        # Then: the call goes on
        self.assertEqual(self.check(self.written("any.md")), [])


class TestOther(GuardTest):
    def test_a_tool_no_lane_watches_goes_through(self):
        for tool, given in (
            ("Read", {"file_path": "README.md"}),
            ("Grep", {"pattern": "x"}),
            ("Agent", {"prompt": "p", "subagent_type": "x"}),
        ):
            with self.subTest(tool=tool):
                # Given: writer with its lanes laid
                # When: it uses a tool that neither runs nor writes
                # Then: the call goes on
                self.assertEqual(self.check(self.event(tool, given)), [])

    def test_a_subagent_with_no_lanes_laid_is_not_checked(self):
        # Given: the README's lanes laid in writer alone
        # When: reviewer runs git commit
        # Then: nothing is said, as lane checks only subagents that have rules
        self.assertEqual(self.check(self.bash("git commit"), "reviewer"), [])


class TestCannot(GuardTest):
    def test_lanes_json_that_cannot_be_read_is_an_error_naming_the_fix(self):
        # Given: hooks/lanes.json removed
        os.remove(os.path.join(self.plugin, "hooks", "lanes.json"))
        # When: writer runs git log --oneline
        # Then: it is an error, telling what is wrong and who must fix it
        said = "lane cannot check the lanes of writer: hooks/lanes.json is not there. " + LAY_AGAIN
        self.assertEqual(self.check(self.bash("git log --oneline")), [guard.Said(said, True)])

    def test_a_step_no_longer_saying_its_sentence_is_an_error_of_its_lane(self):
        # Given: writer's step 2 no longer saying run_only's sentence
        self.write(self.agent_file, helpers.LAID.replace(f" {helpers.RUN}", ""))
        # When: writer runs git log --oneline
        # Then: it is an error of run_only on step 2, as what it holds no longer reads so
        said = (
            "lane cannot check run_only on step 2 of writer: step 2 no longer says:"
            f" {helpers.RUN} {LAY_AGAIN}"
        )
        self.assertEqual(self.check(self.bash("git log --oneline")), [guard.Said(said, True)])
        # And: a write, which run_only does not judge, goes on
        self.assertEqual(self.check(self.written("CHANGELOG.md")), [])

    def test_an_event_not_as_claude_code_hands_it_is_an_error_for_claude_code(self):
        for event, wrong in (
            (self.bash("ls"), "$.cwd: expected a folder"),
            (self.event("Bash", {"command": 1}), ""),
            (self.event("Write", {"content": "x"}), ""),
        ):
            with self.subTest(event=event, wrong=wrong):
                # Given: an event the hook found wrong, a Bash call of no text, or a Write of
                # no path
                # When: the guard is given it
                said = self.check(event, wrong=wrong)
                # Then: it is an error for Claude Code, telling what is wrong
                self.assertEqual(len(said), 1)
                self.assertTrue(said[0].error)
                self.assertIn(
                    "lane cannot check the lanes of writer: the hook was handed no event as"
                    " Claude Code hands it, ",
                    said[0].text,
                )
                self.assertIn(wrong or "expected a string", said[0].text)
                self.assertIn("`claude update`", said[0].text)


if __name__ == "__main__":
    unittest.main()
