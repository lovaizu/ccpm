"""scripts/throwaway.py, what a role runs a work's command by: in a throwaway copy of the folder it
is run in, a throwaway home as HOME holding each file given, both removed after, giving the
command's exit code; or its usage, giving 2."""

import contextlib
import io
import os
import runpy
import unittest
from unittest import mock

import helpers
from helpers import throwaway

USAGE = (
    "usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/throwaway.py [--file <path under ~>]..."
    " -- <command>\n"
)


class TestMain(helpers.testing.FolderTest):
    def setUp(self) -> None:
        super().setUp()
        self.repo = os.path.join(self.base, "repo")
        self.write(os.path.join(self.repo, "tidy.py"), "print('tidy')\n")
        self.seen = os.path.join(self.base, "seen")
        os.makedirs(self.seen)
        here = os.getcwd()
        os.chdir(self.repo)
        self.addCleanup(os.chdir, here)

    def ran(self, *argv: str) -> tuple[int, str]:
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = throwaway.main(list(argv))
        return code, err.getvalue()

    def said(self, name: str) -> str:
        return self.read(os.path.join(self.seen, name)).strip()

    def test_the_command_runs_in_a_copy_with_a_home_of_its_own_holding_each_file_given(self):
        # Given: a repository holding tidy.py
        # When: a command is run with two files given under the home
        command = (
            f"ls ~/Downloads > {self.seen}/ls; echo $HOME > {self.seen}/home;"
            f" pwd > {self.seen}/pwd; cat tidy.py > {self.seen}/tidy; touch made"
        )
        code = self.ran("--file", "Downloads/a.jpg", "--file", "Downloads/b", "--", command)
        # Then: it gives 0, saw the files under its own home, ran in a copy of the repository
        self.assertEqual(code, (0, ""))
        self.assertEqual(self.said("ls").split(), ["a.jpg", "b"])
        self.assertNotEqual(self.said("home"), os.environ.get("HOME"))
        self.assertEqual(self.said("tidy"), "print('tidy')")
        self.assertNotEqual(self.said("pwd"), self.repo)
        # And: the repository is as it was, and the home and the copy are gone
        self.assertEqual(os.listdir(self.repo), ["tidy.py"])
        self.assertFalse(os.path.exists(self.said("home")))
        self.assertFalse(os.path.exists(self.said("pwd")))

    def test_the_command_s_exit_code_is_given_and_both_are_removed_still(self):
        # Given: a command that fails
        # When: it is run
        code = self.ran("--", f"pwd > {self.seen}/pwd; exit 3")
        # Then: its code is given, and its folder is gone
        self.assertEqual(code, (3, ""))
        self.assertFalse(os.path.exists(self.said("pwd")))

    def test_a_call_it_does_not_take_gives_2_and_its_usage_running_nothing(self):
        probe = f"touch {self.seen}/ran"
        for argv in (
            (),
            ("--",),
            (probe,),
            ("--", probe, "x"),
            ("--file",),
            ("--file", "--", probe),
            ("--file", "a", "b", "--", probe),
            ("--files", "a", "--", probe),
            ("--fil", "a", "--", probe),
            ("--file", "a", "--file", "--", probe),
            ("--file", "/etc/x", "--", probe),
            ("--file", "../x", "--", probe),
            ("--file", "a/../..", "--", probe),
            ("--file", ".", "--", probe),
        ):
            with self.subTest(argv=argv):
                # Given: no command, a command not after --, two, a file not named, or a file
                # out of the home or the home itself
                # When: it is run
                # Then: it gives 2 with its usage, and runs nothing
                self.assertEqual(self.ran(*argv), (2, USAGE))
                self.assertFalse(os.path.exists(os.path.join(self.seen, "ran")))

    def test_a_file_whose_name_begins_with_dots_lies_under_the_home(self):
        # Given: a file named ..notes under the home
        # When: a command is run with it
        code = self.ran("--file", "..notes", "--", f"ls -A ~ > {self.seen}/ls")
        # Then: it is made there
        self.assertEqual((code, self.said("ls")), ((0, ""), "..notes"))

    def test_a_link_in_the_folder_is_copied_as_the_file_it_reaches(self):
        # Given: a link to a file outside the repository, and a link to nothing
        outside = os.path.join(self.base, "outside.md")
        self.write(outside, "kept\n")
        os.symlink(outside, os.path.join(self.repo, "notes.md"))
        os.symlink(os.path.join(self.base, "gone"), os.path.join(self.repo, "gone"))
        # When: a command writes through the first
        code = self.ran("--", f"echo more >> notes.md; cat notes.md > {self.seen}/notes")
        # Then: it wrote the copy alone, and the file outside is as it was
        self.assertEqual((code, self.said("notes")), ((0, ""), "kept\nmore"))
        self.assertEqual(self.read(outside), "kept\n")

    def test_the_script_takes_the_arguments_after_its_own_path(self):
        argv = ["throwaway.py", "--", "exit 0"]
        with mock.patch.object(throwaway.sys, "argv", argv), self.assertRaises(SystemExit) as end:
            runpy.run_path(throwaway.__file__, run_name="__main__")
        self.assertEqual(end.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
