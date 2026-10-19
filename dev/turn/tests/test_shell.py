"""The hooks' reading of a command: the paths it names, writes and prints whole, each word taken
as the shell takes it."""

import os
import unittest

from helpers import shell

# The folder each command runs in.
HERE = "/r"


def at(*names):
    return [os.path.join(HERE, n) for n in names]


class TestNamed(unittest.TestCase):
    def test_what_follows_a_here_string_or_a_file_descriptor_is_no_path(self):
        # Given: a command with a here-string's text, or a file descriptor after `>&` or `<&`,
        # before and after the paths it names
        # When: the paths it names are read
        # Then: the paths alone are taken
        for command in ("cat a <<< text b", "cat a 2>&1 b", "cat a 0<&3 b"):
            with self.subTest(command=command):
                self.assertNotIn(os.path.join(HERE, "text"), shell.named(command, HERE))
                self.assertNotIn(os.path.join(HERE, "1"), shell.named(command, HERE))
                self.assertNotIn(os.path.join(HERE, "3"), shell.named(command, HERE))
                self.assertIn(os.path.join(HERE, "b"), shell.named(command, HERE))

    def test_a_word_the_shell_makes_by_running_a_command_is_no_path(self):
        # Given: a command naming a path made by a backquoted command, read word by word as its
        # quoting does not close
        # When: the paths it names are read
        # Then: that path is not taken, as the words do not settle it
        self.assertEqual(shell.named("cat `pwd`/a 'x", HERE), at("cat", "'x"))

    def test_a_path_after_a_redirect_is_still_named(self):
        # Given: a command naming a path after a redirect to a file
        # When: the paths it names are read
        # Then: each word but the redirect is taken, the path after it too
        self.assertEqual(shell.named("cat a 2> err b", HERE), at("cat", "a", "2", "err", "b"))

    def test_only_where_the_run_is_kept_is_left_out_of_turns_script(self):
        # Given: turn's script asked a step, said by its path alone or after python3 and a flag;
        # a step's name not after turn's script; and turn's script asked something not a step
        # When: the paths each names are read
        # Then: the word after the step alone is left out, as the script is asked of it
        self.assertEqual(shell.named("turn.py given r.json", HERE), at("turn.py", "given"))
        self.assertEqual(
            shell.named("python3 -I turn.py next r.json", HERE),
            at("python3", "-I", "turn.py", "next"),
        )
        self.assertEqual(shell.named("cat parts r.json", HERE), at("cat", "parts", "r.json"))
        self.assertEqual(shell.named("given turn.py", HERE), at("given", "turn.py"))
        self.assertEqual(
            shell.named("python3 turn.py other r.json", HERE),
            at("python3", "turn.py", "other", "r.json"),
        )


class TestCd(unittest.TestCase):
    def test_a_bare_cd_goes_home(self):
        # Given: a command going with a bare cd, then naming a file
        # When: the paths it names are read
        # Then: the file is taken from the home folder
        home = os.path.realpath(os.path.expanduser("~"))
        self.assertEqual(
            shell.named("cd && cat a", HERE), [os.path.join(home, w) for w in ("cat", "a")]
        )

    def test_cd_back_leaves_the_folder_unsettled(self):
        # Given: a command going back with `cd -`, then naming a file
        # When: the paths it names are read
        # Then: the file is not taken, as the words do not settle where it is
        self.assertEqual(shell.named("cd - && cat a", HERE), [])

    def test_cd_to_a_folder_of_any_name_goes_there(self):
        # Given: a command going to a folder whose name starts with a sign, then naming a file
        # When: the paths it names are read
        # Then: the file is taken from that folder
        self.assertEqual(shell.named("cd +old && cat a", HERE), at("+old/cat", "+old/a"))


class TestWritten(unittest.TestCase):
    def test_a_redirect_s_target_is_not_the_command_s_argument(self):
        # Given: commands that write the paths they name, or the last, with a redirect after them
        # When: the paths each writes are read
        # Then: the redirect's target and the command's own are taken, each once
        self.assertEqual(shell.written("rm a > log", HERE), at("log", "a"))
        self.assertEqual(shell.written("cp a b > log", HERE), at("log", "b"))

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

    def test_a_heredoc_s_line_holds_a_word_of_any_character(self):
        # Given: a heredoc whose line holds a word of a control character before a redirect
        # When: the paths it writes are read
        # Then: the redirect's target is taken, as the line runs to its end
        command = "cat <<EOF \x07 > notes/new.md\nhi\nEOF"
        self.assertEqual(shell.written(command, HERE), at("notes/new.md"))

    def test_a_heredoc_s_end_word_ends_it_only_at_a_line_s_start(self):
        # Given: heredocs whose text holds the end word after another word, a plain one or one of
        # a control character, and then a redirect
        # When: the paths each writes are read
        # Then: none is taken, as the text runs on to its end word on a line of its own
        for word in ("say", "\x07"):
            command = f"cat <<EOF\n{word} EOF\nx > notes/new.md\nEOF"
            with self.subTest(command=command):
                self.assertEqual(shell.written(command, HERE), [])


class TestPrinted(unittest.TestCase):
    def test_cat_before_an_or_prints_its_file(self):
        # Given: cat of a file, followed by another command after `||`
        # When: the files it prints whole are read
        # Then: the file is taken, as only a pipe takes what cat prints
        self.assertEqual(shell.printed("cat a || echo x", HERE), at("a"))
