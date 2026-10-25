"""The hooks' reading of what a shell command reads: each file it prints of what it reads, by the
commands the steps tell and the AI writes, with the lines it reads of it."""

import os
import unittest

from helpers import HERE, shell

# The lines from the first to the end.
WHOLE = (1, None)


def reads(command):
    """Each file the command reads, by its name in HERE, with the lines it reads."""
    return [(os.path.relpath(p, HERE), lines) for p, lines in shell.reads(command, HERE)]


class TestCat(unittest.TestCase):
    def test_cat_reads_each_file_it_names_whole(self):
        # Given: cat of two files, an option before them
        # When: what it reads is read
        # Then: each file is read whole
        self.assertEqual(reads("cat -n a b"), [("a", WHOLE), ("b", WHOLE)])

    def test_a_dash_alone_names_no_file(self):
        # Given: cat of its input, named by `-`, and of a file
        # When: what it reads is read
        # Then: the file alone is read
        self.assertEqual(reads("cat - a"), [("a", WHOLE)])

    def test_cat_of_nothing_reads_no_file(self):
        # Given: cat reading what is piped into it
        # When: what the command reads is read
        # Then: the file before the pipe is read, cat itself reads no file
        self.assertEqual(reads("grep x a | cat"), [("a", None)])


class TestHeadAndTail(unittest.TestCase):
    def test_head_reads_the_lines_its_count_gives_from_the_first(self):
        # Given: head with no count, its count given in each form the AI writes, and given after
        # another option
        # When: what it reads is read
        # Then: it reads the first ten lines, or as many as its count gives
        for command, lines in (
            ("head a", (1, 10)),
            ("head -n 5 a", (1, 5)),
            ("head -n5 a", (1, 5)),
            ("head -5 a", (1, 5)),
            ("head -q -n 5 a", (1, 5)),
        ):
            with self.subTest(command=command):
                self.assertEqual(reads(command), [("a", lines)])

    def test_tail_reads_the_lines_its_count_gives_from_the_end_or_from_a_line_on(self):
        # Given: tail with no count, its count in each form the AI writes, and `+` for a line on
        # When: what it reads is read
        # Then: it reads the last ten lines, as many as its count gives, or from the line to the end
        for command, lines in (
            ("tail a", (-10, None)),
            ("tail -n 5 a", (-5, None)),
            ("tail -5 a", (-5, None)),
            ("tail -n +7 a", (7, None)),
        ):
            with self.subTest(command=command):
                self.assertEqual(reads(command), [("a", lines)])

    def test_a_count_not_of_lines_does_not_tell_the_lines(self):
        # Given: head and tail counting bytes, and a count that is no number
        # When: what each reads is read
        # Then: the file is read, its lines not told
        for command in ("head -c 100 a", "head -n x a", "tail -c 100 a"):
            with self.subTest(command=command):
                self.assertEqual(reads(command), [("a", None)])


class TestSed(unittest.TestCase):
    def test_sed_printing_lines_reads_them(self):
        # Given: sed -n printing a span of lines, a span to the end, one line, its script given
        # by -e, and with another option before -n
        # When: what it reads is read
        # Then: it reads those lines
        for command, lines in (
            ("sed -n '60,70p' a", (60, 70)),
            ("sed -n '5,$p' a", (5, None)),
            ("sed -n 3p a", (3, 3)),
            ("sed -n -e '1,9p' a", (1, 9)),
            ("sed -E -n 2,4p a", (2, 4)),
        ):
            with self.subTest(command=command):
                self.assertEqual(reads(command), [("a", lines)])

    def test_sed_printing_every_line_reads_the_file_whole(self):
        # Given: sed without -n, which prints every line it reads
        # When: what it reads is read
        # Then: the file is read whole
        self.assertEqual(reads("sed 's/x/y/' a"), [("a", WHOLE)])

    def test_sed_n_with_another_script_does_not_tell_the_lines(self):
        # Given: sed -n printing the lines that match, and printing by two scripts
        # When: what each reads is read
        # Then: the file is read, its lines not told
        for command in ("sed -n '/x/p' a", "sed -n -e 1,5p -e 7p a"):
            with self.subTest(command=command):
                self.assertEqual(reads(command), [("a", None)])


class TestGrep(unittest.TestCase):
    def test_grep_reads_each_file_after_its_pattern_its_lines_not_told(self):
        # Given: grep with options, its pattern and two files
        # When: what it reads is read
        # Then: each file is read, the pattern none, its lines not told
        self.assertEqual(reads("grep -n -A 2 x a b"), [("a", None), ("b", None)])

    def test_grep_given_its_pattern_by_e_reads_every_word_after(self):
        # Given: grep given its pattern by -e
        # When: what it reads is read
        # Then: every word after its options is a file it reads
        self.assertEqual(reads("grep -e x a"), [("a", None)])


class TestStatements(unittest.TestCase):
    def test_each_statement_reads_from_where_it_runs(self):
        # Given: reads joined by `&&`, the second after a cd, and an echo between them
        # When: what the command reads is read
        # Then: each file is read from the folder its statement runs in, echo reading none
        self.assertEqual(
            reads("cat a && echo --- && cd d && head -n 2 b"),
            [("a", WHOLE), ("d/b", (1, 2))],
        )

    def test_a_word_after_double_dash_is_a_file(self):
        # Given: cat given `--`, after which a word beginning with `-` is a file
        # When: what it reads is read
        # Then: that word is a file it reads
        self.assertEqual(reads("cat -- -a"), [("-a", WHOLE)])

    def test_a_redirect_s_target_is_no_file_read(self):
        # Given: cat with its errors and its output redirected
        # When: what it reads is read
        # Then: the file named alone is read
        self.assertEqual(reads("cat a 2>/dev/null > b"), [("a", WHOLE)])

    def test_a_file_the_words_do_not_settle_is_left_out(self):
        # Given: cat of a file named by a variable, and of one after a cd the words do not settle
        # When: what each reads is read
        # Then: neither is taken
        for command in ('cat "$f"', 'cd "$d" && cat a'):
            with self.subTest(command=command):
                self.assertEqual(reads(command), [])

    def test_other_commands_read_no_file(self):
        # Given: commands that print no file they read, and a statement of a redirect alone
        # When: what each reads is read
        # Then: none is taken
        for command in ("awk 1 a", "wc -l a", "> a"):
            with self.subTest(command=command):
                self.assertEqual(reads(command), [])


if __name__ == "__main__":
    unittest.main()
