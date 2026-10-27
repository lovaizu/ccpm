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

    def test_sed_in_place_given_its_script_before_its_option_writes_the_file_after_both(self):
        # Given: sed given its script first and -i after it
        # When: the paths it writes are read
        # Then: the file is taken
        self.assertEqual(shell.written("sed 's/a/b/' -i f", HERE), at("f"))

    def test_sed_in_place_given_its_scripts_by_e_writes_only_the_files_after_them(self):
        # Given: sed editing a file in place, its scripts given by -e, one holding `$`
        # When: the paths it writes, and the words not settled, are read
        # Then: the file alone is taken, and no script is taken for a word not settled
        command = "sed -i -e 's/a/b/' -e 's/x$/y/' f"
        self.assertEqual(shell.written(command, HERE), at("f"))
        self.assertEqual(shell.unsettled_written(command, HERE), [])

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


class TestUnsettled(unittest.TestCase):
    def test_a_word_naming_a_path_written_that_the_words_do_not_settle_is_given(self):
        for command, unsettled in (
            ('echo x > "$out"', ["$out"]),
            ('cp a "$dst"', ["$dst"]),
            ('touch "`date`.log"', ["`date`.log"]),
            ('cd "$d" && rm a', ["a"]),
        ):
            with self.subTest(command=command):
                # Given: a command writing a path made from a variable or a command's output, or
                # named from a folder a cd the words do not settle went to
                # When: the words it writes that the words do not settle are read
                # Then: each is given as it is written, and no path is taken
                self.assertEqual(shell.unsettled_written(command, HERE), unsettled)
                self.assertEqual(shell.written(command, HERE), [])

    def test_a_settled_path_or_an_empty_word_gives_no_word_unsettled(self):
        for command in ("echo x > /tmp/a", "cd d && rm a", "sed -i '' 's/$/x/' f", 'cat "$f"'):
            with self.subTest(command=command):
                # Given: commands writing settled paths, with an empty word or a `$` that names
                # no path, or writing nothing
                # When: the words it writes that the words do not settle are read
                # Then: there are none
                self.assertEqual(shell.unsettled_written(command, HERE), [])


if __name__ == "__main__":
    unittest.main()
