"""run_only: a command goes through only where it is, whole, one of the commands the lane names,
the plugin's folder put in for `${CLAUDE_PLUGIN_ROOT}` as Claude Code puts it in the step."""

import os
import unittest

import helpers
from helpers import run_only

ROOT = "/p/changelog"


def allows(command: str, takes: list) -> bool:
    """Whether run_only taking the commands lets the command through, run in /w."""
    return run_only.allows(command, takes, ROOT, "/w")


class TestAllows(unittest.TestCase):
    def test_a_command_named_goes_through(self):
        for command in ("git log --oneline", "git diff", "  git log --oneline\n"):
            with self.subTest(command=command):
                # Given: run_only naming git log --oneline and git diff
                # When: the subagent runs one of them, or one with blanks around it
                # Then: it goes through
                self.assertTrue(allows(command, ["git log --oneline", "git diff"]))

    def test_any_other_command_is_stopped(self):
        for command in (
            "git commit -m entries",
            "git log --oneline -5",
            "git log  --oneline",
            "cd /w && git log --oneline",
            "git log --oneline; git commit -m m",
            "git log",
            "",
        ):
            with self.subTest(command=command):
                # Given: run_only naming git log --oneline
                # When: the subagent runs another command, the command with more words, other
                # blanks between them, after another, before another, fewer words, or nothing
                # Then: it is stopped, as only the command named, whole, goes through
                self.assertFalse(allows(command, ["git log --oneline"]))

    def test_a_command_naming_the_plugins_folder_is_matched_as_the_subagent_reads_it(self):
        take = "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py writer done"
        for command, through in (
            (f"python3 {ROOT}/hooks/lane/result.py writer done", True),
            (take, False),
        ):
            with self.subTest(command=command):
                # Given: run_only naming a script by the plugin's folder
                # When: the subagent runs it by the folder Claude Code put in, or as written
                # Then: the folder put in goes through, as the subagent read it, and the other not
                self.assertEqual(allows(command, [take]), through)


# A command of the dependency checker's skill, as the proposal names it.
TAKE = "python3 ${dependency:checker}/scripts/check.py CHANGELOG.md"


class TestDependency(helpers.PluginTest):
    """A command a dependency's skill names, by the folder Claude Code installed it in."""

    def setUp(self) -> None:
        super().setUp()
        self.declare(["checker"])
        self.checker = self.dependency("checker", "checker")

    def declare(self, dependencies: object) -> None:
        """The plugin's manifest declaring the dependencies given."""
        manifest = {"name": "changelog", "version": "0.1.0", "dependencies": dependencies}
        self.write_json(self.manifest(), manifest)

    def dependency(self, folder: str, name: str) -> str:
        """A plugin of the name installed in the folder of the test's, as Claude Code installs
        it; gives its whole path."""
        self.write_json(os.path.join(folder, ".claude-plugin", "plugin.json"), {"name": name})
        return os.path.join(self.base, folder)

    def allows(self, command: str, takes: tuple = (TAKE,)) -> bool:
        """Whether run_only taking the commands lets the command through."""
        return run_only.allows(command, list(takes), self.plugin, self.base)

    def test_a_command_of_the_dependencys_folder_goes_through(self):
        for given in (["checker"], ["checker@other"], [{"name": "checker", "version": "^1"}]):
            with self.subTest(given=given):
                # Given: checker declared by name, in another marketplace, or with a version
                self.declare(["other", *given])
                # When: the subagent runs the command by the folder checker is installed in
                # Then: it goes through, whatever the folder
                command = f"python3 {self.checker}/scripts/check.py CHANGELOG.md"
                self.assertTrue(self.allows(command))
                self.assertTrue(self.allows(f"  {command}\n"))

    def test_a_command_of_another_folder_or_other_words_is_stopped(self):
        fake = os.path.join(self.base, "fake")
        os.makedirs(fake)
        other = self.dependency("other", "other")
        for command in (
            f"python3 {fake}/scripts/check.py CHANGELOG.md",
            f"python3 {other}/scripts/check.py CHANGELOG.md",
            "python3 checker/scripts/check.py CHANGELOG.md",
            f"python3 {self.checker}/scripts/check.py CHANGELOG.md --all",
            f"python3 {self.checker}/scripts/check.py",
            f"python3 {self.checker}/scripts/check.py CHANGELOG.md; git commit",
            TAKE,
        ):
            with self.subTest(command=command):
                # Given: run_only naming checker's command
                # When: the subagent runs it from a folder with no manifest, one of another
                # plugin, a folder not whole, with other words, or as the proposal writes it
                # Then: it is stopped
                self.assertFalse(self.allows(command))

    def test_a_dependency_the_manifest_does_not_declare_is_stopped(self):
        command = f"python3 {self.checker}/scripts/check.py CHANGELOG.md"
        for given in ([], ["other"], "checker", [1], None):
            with self.subTest(given=given):
                # Given: the plugin declaring no dependency, another, or dependencies in no list
                self.declare(given)
                # When: the subagent runs checker's command
                # Then: it is stopped, as only the plugin's own manifest declares a dependency
                self.assertFalse(self.allows(command))

    def test_a_manifest_that_cannot_be_read_declares_nothing(self):
        command = f"python3 {self.checker}/scripts/check.py CHANGELOG.md"
        for text in ("{", "[]"):
            with self.subTest(text=text):
                # Given: the plugin's manifest, or checker's, holding no JSON object
                manifests = (
                    self.manifest(),
                    os.path.join(self.checker, ".claude-plugin", "plugin.json"),
                )
                for manifest in manifests:
                    self.declare(["checker"])
                    self.dependency("checker", "checker")
                    self.write(manifest, text)
                    # When: the subagent runs checker's command
                    # Then: it is stopped
                    self.assertFalse(self.allows(command))

    def test_each_dependency_named_is_held_to_its_own_folder(self):
        # Given: a command naming checker's folder and other's, both declared
        self.declare(["checker", "other"])
        other = self.dependency("other", "other")
        take = "python3 ${dependency:checker}/a.py ${dependency:other}/b.txt"
        # When: the subagent runs it by each folder, or by them swapped
        # Then: the first goes through, and the second is stopped
        self.assertTrue(self.allows(f"python3 {self.checker}/a.py {other}/b.txt", (take,)))
        self.assertFalse(self.allows(f"python3 {other}/a.py {self.checker}/b.txt", (take,)))


if __name__ == "__main__":
    unittest.main()
