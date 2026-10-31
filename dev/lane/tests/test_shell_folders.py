"""Where a command's statements run, as the hooks read it: each cd moving the folder, git's
options before its command, and a folder inside another."""

import os
import unittest
from unittest import mock

from helpers import HERE, shell


def at(*names: str) -> list[str]:
    """The whole path of each name in the folder the commands run in."""
    return [os.path.join(HERE, n) for n in names]


def files_read(command: str) -> list[str]:
    """Each file the command reads, as its whole path."""
    return [p for p, _ in shell.reads(command, HERE)]


class TestCd(unittest.TestCase):
    def test_a_bare_cd_goes_home(self):
        # Given: a command going with a bare cd, then naming a file
        # When: the files it reads are read
        # Then: the file is taken from the home folder
        with mock.patch.dict(os.environ, {"HOME": "/home/u"}):
            self.assertEqual(files_read("cd && cat a"), ["/home/u/a"])

    def test_cd_back_leaves_the_folder_unsettled(self):
        # Given: a command going back with `cd -`, then naming a file
        # When: the files it reads are read
        # Then: the file is not taken, as the words do not settle where it is
        self.assertEqual(files_read("cd - && cat a"), [])

    def test_cd_to_a_folder_of_any_name_goes_there(self):
        # Given: a command going to a folder whose name starts with a sign, then naming a file
        # When: the files it reads are read
        # Then: the file is taken from that folder
        self.assertEqual(files_read("cd +old && cat a"), at("+old/a"))


class TestGit(unittest.TestCase):
    def test_a_git_statements_command_follows_gits_options(self):
        # Given: git statements with options before the git command: -C with its folder, -c with
        # its setting, options taking no word, and -C last with or without its folder
        # When: each one's command is read
        # Then: it is the words after the options, each with what it takes
        for command, found in (
            ("git -C x -C y commit -m z", ["commit", "-m", "z"]),
            ("git -c a=b log", ["log"]),
            ("git --no-pager log", ["log"]),
            ("git -C /x", []),
            ("git -C", []),
        ):
            with self.subTest(command=command):
                self.assertEqual(shell.git_command(shell.words(command)), found)


class TestInside(unittest.TestCase):
    def test_a_folder_is_inside_the_top_alone_or_in_it(self):
        # Given: the top, a folder in it, and others beside it, one whose name starts the same
        # When: each is asked whether it is inside the top
        # Then: the first two are
        for folder, found in (
            ("/r", True),
            ("/r/a", True),
            ("/rx", False),
            ("/s", False),
            ("/a", False),
        ):
            with self.subTest(folder=folder):
                self.assertEqual(shell.inside(shell.path(HERE, folder), HERE), found)

    def test_a_folder_the_words_do_not_settle_is_inside_no_top(self):
        # Given: a folder the words do not settle
        # When: it is asked whether it is inside the top
        # Then: it is not
        self.assertFalse(shell.inside(None, HERE))


if __name__ == "__main__":
    unittest.main()
