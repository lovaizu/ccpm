"""The cases of command.py's contract: a command that a lane takes, put as the role runs it, and a
command run matched against it whole."""

import os

from helpers import command, testing

ROOT = "/plugins/changelog"


class TestExpanded(testing.FolderTest):
    def test_the_plugin_folder_is_put_in_for_its_variable(self):
        self.assertEqual(
            command.expanded("python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check.py", ROOT, {}),
            ["python3 /plugins/changelog/scripts/check.py"],
        )

    def test_a_value_of_plain_characters_is_put_in_as_it_is(self):
        self.assertEqual(
            command.expanded("check {file}", ROOT, {"file": ["notes/a-1.json"]}),
            ["check notes/a-1.json"],
        )

    def test_a_value_of_other_characters_is_put_in_single_quotes(self):
        self.assertEqual(
            command.expanded("check {file}", ROOT, {"file": ["my notes; rm x"]}),
            ["check 'my notes; rm x'"],
        )

    def test_a_value_of_several_texts_gives_a_command_for_each(self):
        self.assertEqual(
            command.expanded("check {file}", ROOT, {"file": ["a", "b"]}),
            ["check a", "check b"],
        )

    def test_two_values_give_a_command_for_each_pair(self):
        self.assertEqual(
            command.expanded("c {a} {b}", ROOT, {"a": ["1", "2"], "b": ["x"]}),
            ["c 1 x", "c 2 x"],
        )

    def test_a_value_given_as_null_names_no_command(self):
        self.assertEqual(command.expanded("check {file}", ROOT, {"file": None}), [])

    def test_a_value_not_given_is_refused(self):
        with self.assertRaisesRegex(command.Unvalued, r"^file$"):
            command.expanded("check {file}", ROOT, {})

    def test_braces_naming_no_value_are_the_commands_own(self):
        self.assertEqual(
            command.expanded("find . -exec ls {} + ${HOME}", ROOT, {}),
            ["find . -exec ls {} + ${HOME}"],
        )


class TestMatches(testing.FolderTest):
    def test_a_command_run_as_written_matches(self):
        self.assertTrue(command.matches("git log --oneline", "git log --oneline"))

    def test_blanks_at_the_ends_of_the_command_run_are_passed_over(self):
        self.assertTrue(command.matches("  git log --oneline\n", "git log --oneline"))

    def test_a_command_in_other_words_does_not_match(self):
        self.assertFalse(command.matches("git log --oneline -5", "git log --oneline"))

    def test_a_dependency_folder_holding_its_manifest_matches(self):
        self.write_json("checker/.claude-plugin/plugin.json", {"name": "checker"})
        folder = os.path.join(self.base, "checker")
        self.assertTrue(
            command.matches(
                f"python3 {folder}/scripts/check.py x",
                "python3 ${dependency:checker}/scripts/check.py x",
            )
        )

    def test_a_folder_of_another_plugin_does_not_match_a_dependency(self):
        self.write_json("other/.claude-plugin/plugin.json", {"name": "other"})
        folder = os.path.join(self.base, "other")
        self.assertFalse(command.matches(f"run {folder}/x", "run ${dependency:checker}/x"))

    def test_a_folder_holding_no_manifest_does_not_match_a_dependency(self):
        self.assertFalse(command.matches(f"run {self.base}/x", "run ${dependency:checker}/x"))

    def test_a_relative_folder_does_not_match_a_dependency(self):
        self.assertFalse(command.matches("run checker/x", "run ${dependency:checker}/x"))


class TestDependencies(testing.FolderTest):
    def test_each_dependency_a_command_names_is_found(self):
        self.assertEqual(
            command.dependencies("a ${dependency:checker}/x ${dependency:lint}/y"),
            ["checker", "lint"],
        )

    def test_each_value_a_command_names_is_found(self):
        self.assertEqual(command.values("c {a} ${HOME} {b-1}"), ["a", "b-1"])
