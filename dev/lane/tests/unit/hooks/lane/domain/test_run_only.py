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


# A command holding the run's value `file` as one part.
CHECK = "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check.py {file}"


def given(command: str, texts: list, take: str = CHECK) -> bool:
    """Whether run_only taking the command holding `{file}` lets the command through, the run
    given the texts as `file`."""
    return run_only.allows(command, [take], ROOT, "/w", {"file": texts})


class TestValue(unittest.TestCase):
    """A command holding a value given for the run as one part."""

    def test_the_command_with_the_runs_own_value_goes_through(self):
        for command, texts in (
            (f"python3 {ROOT}/scripts/check.py notes.json", ["notes.json"]),
            (f"python3 {ROOT}/scripts/check.py b.json", ["a.json", "b.json"]),
            (
                f"  python3 {ROOT}/scripts/check.py docs/v-1.2_x@y+z=w:%,.json\n",
                ["docs/v-1.2_x@y+z=w:%,.json"],
            ),
        ):
            with self.subTest(command=command):
                # Given: run_only on check.py `{file}`, the run given the file, or two
                # When: the subagent runs it with one of them, with blanks around it
                # Then: it goes through
                self.assertTrue(given(command, texts))

    def test_any_other_value_or_words_are_stopped(self):
        for command in (
            f"python3 {ROOT}/scripts/check.py other.json",
            f"python3 {ROOT}/scripts/check.py notes.json other.json",
            f"python3 {ROOT}/scripts/check.py notes.json; git commit",
            f"python3 {ROOT}/scripts/check.py {{file}}",
            CHECK,
            f"python3 {ROOT}/scripts/check.py",
        ):
            with self.subTest(command=command):
                # Given: run_only on check.py `{file}`, the run given notes.json
                # When: the subagent runs it with another file, one more, another command after,
                # the name of the value, as the step writes it, or with none
                # Then: it is stopped
                self.assertFalse(given(command, ["notes.json"]))

    def test_a_value_is_one_word_however_it_reads(self):
        for text, through, stopped in (
            ("my notes.json", "'my notes.json'", ["my notes.json", '"my notes.json"']),
            ("a.json; git commit", "'a.json; git commit'", ["a.json; git commit"]),
            ("$(git commit)", "'$(git commit)'", ["$(git commit)", '"$(git commit)"']),
            ("it's.json", "'it'\"'\"'s.json'", ["it's.json", "'it's.json'"]),
            ("a\nb", "'a\nb'", ["a\nb"]),
            ("${CLAUDE_PLUGIN_ROOT}", "'${CLAUDE_PLUGIN_ROOT}'", [f"'{ROOT}'", ROOT]),
            ("${dependency:checker}", "'${dependency:checker}'", ["'/any'", "/any"]),
            ("{other}", "'{other}'", ["x.json", "'x.json'"]),
        ):
            for command, through_ in [(through, True), *((t, False) for t in stopped)]:
                with self.subTest(text=text, command=command):
                    # Given: the run given a file whose name holds a blank, a shell's
                    # separator, a substitution, a quote, a line break, or what lane reads as the
                    # plugin's folder, a dependency's folder or a value
                    # When: the subagent runs check.py on it
                    # Then: only the name as one word, in single quotes, goes through, as it
                    # stands, so no value adds words to the command or stands for another
                    command = f"python3 {ROOT}/scripts/check.py {command}"
                    self.assertEqual(given(command, [text]), through_)

    def test_values_in_one_command_are_each_held_to_their_own(self):
        take = "diff {old} {new}"
        values = {"old": ["a.md"], "new": ["b.md"]}
        for command, through in (("diff a.md b.md", True), ("diff b.md a.md", False)):
            with self.subTest(command=command):
                # Given: a command holding two values, the run given each its own
                # When: the subagent runs it with them in order, or swapped
                # Then: only the first goes through
                found = run_only.allows(command, [take], ROOT, "/w", values)
                self.assertEqual(found, through)

    def test_a_value_the_run_gives_no_text_of_stands_as_written(self):
        # Given: check.py `{file}`, the run giving texts of another name alone
        # When: the subagent runs it as written, and the commands are shown
        # Then: it goes through only as written, and is shown so
        command = f"python3 {ROOT}/scripts/check.py {{file}}"
        self.assertTrue(run_only.allows(command, [CHECK], ROOT, "/w", {"other": ["a"]}))
        self.assertEqual(run_only.put([CHECK], ROOT, {"other": ["a"]}), [command])

    def test_braces_not_naming_a_value_are_the_commands_own(self):
        for take in ("find . -exec ls {} +", "awk '{print $1}' x", "echo ${HOME}", "echo {a,b}"):
            with self.subTest(take=take):
                # Given: a command with braces holding nothing, a blank, a $ before them, or a
                # comma
                # When: the subagent runs it as written
                # Then: it goes through, as no value lies in it
                self.assertEqual(run_only.values_in(take), [])
                self.assertTrue(run_only.allows(take, [take], ROOT, "/w", {}))

    def test_the_commands_are_shown_with_each_value_put_in_as_one_word(self):
        # Given: check.py `{file}`, given two files, one with a blank, beside a dependency's
        # command
        takes = [CHECK, "python3 ${dependency:checker}/c.py {file}"]
        # When: the commands are shown as the subagent may run them
        found = run_only.put(takes, ROOT, {"file": ["a.json", "my b.json"]})
        # Then: each holds the plugin's folder and each value in its place, the dependency as
        # written
        self.assertEqual(
            found,
            [
                f"python3 {ROOT}/scripts/check.py a.json",
                f"python3 {ROOT}/scripts/check.py 'my b.json'",
                "python3 ${dependency:checker}/c.py a.json",
                "python3 ${dependency:checker}/c.py 'my b.json'",
            ],
        )


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
