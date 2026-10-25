"""The paths a command writes, as the hooks read them: by a redirect, by a command that writes the
paths it names or the last, and in place by sed."""

import os
import unittest

from helpers import HERE, shell


def at(*names: str) -> list[str]:
    """The whole path of each name in the folder the commands run in."""
    return [os.path.join(HERE, n) for n in names]


class TestWritten(unittest.TestCase):
    def test_a_redirect_s_target_is_not_the_command_s_argument(self):
        # Given: commands that write the paths they name, or the last, with a redirect after them
        # When: the paths each writes are read
        # Then: the redirect's target and the command's own are taken, each once
        self.assertEqual(shell.written("rm a > log", HERE), at("log", "a"))
        self.assertEqual(shell.written("cp a b > log", HERE), at("log", "b"))

    def test_a_redirect_writes_a_file_whose_name_begins_with_a_dash(self):
        # Given: a redirect right before a file whose name begins with `-`
        # When: the paths it writes are read
        # Then: the file is taken
        self.assertEqual(shell.written("echo a >-b", HERE), at("-b"))

    def test_cp_or_mv_of_several_sources_writes_the_last_path(self):
        # Given: cp and mv of several files into a folder
        # When: the paths each writes are read
        # Then: the last path alone is taken, as the sources are read
        for command in ("cp a b dir/", "mv a b dir/"):
            with self.subTest(command=command):
                self.assertEqual(shell.written(command, HERE), at("dir"))

    def test_only_sed_in_place_writes_the_files_it_names(self):
        # Given: commands other than sed given `-i`, and sed without it
        # When: the paths each writes are read
        # Then: none is taken, as each prints what it reads
        for command in ("grep -i x a b", "sort -i a b", "sed 's/a/b/' a b"):
            with self.subTest(command=command):
                self.assertEqual(shell.written(command, HERE), [])

    def test_a_read_and_write_redirect_writes_its_target(self):
        # Given: a command opening a file to read and write with `<>`
        # When: the paths it writes are read
        # Then: the file is taken, as `<>` makes it where it is not there
        self.assertEqual(shell.written("cat <> a", HERE), at("a"))

    def test_sed_in_place_writes_the_file_after_its_script(self):
        # Given: sed editing a file in place, its backup suffix given
        # When: the paths it writes are read
        # Then: the file is taken
        self.assertEqual(shell.written("sed -i '' 's/a/b/' f", HERE), at("f"))

    def test_a_heredoc_s_line_holds_a_word_of_any_character(self):
        # Given: a heredoc whose line holds a word of a control character before a redirect
        # When: the paths it writes are read
        # Then: the redirect's target is taken, as the line runs to its end
        command = "cat <<EOF \x07 > notes/new.md\nhi\nEOF"
        self.assertEqual(shell.written(command, HERE), at("notes/new.md"))

    def test_a_heredoc_s_line_holds_words_after_blanks_of_either_kind(self):
        for blank in (" ", "\t"):
            with self.subTest(blank=blank):
                # Given: a heredoc whose line holds a redirect after a blank
                command = f"cat <<EOF{blank}> notes/new.md\nhi\nEOF"
                # When: the paths it writes are read
                # Then: the redirect's target is taken, as the heredoc's text begins on the next
                # line
                self.assertEqual(shell.written(command, HERE), at("notes/new.md"))

    def test_a_quoted_redirect_writes_no_path(self):
        # Given: a command with `>` in quotes before a path
        # When: the paths it writes are read
        # Then: none is taken
        self.assertEqual(shell.written("echo '>' a", HERE), [])


if __name__ == "__main__":
    unittest.main()
