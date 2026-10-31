"""The hooks' reading of a command's words and statements, as the shell takes them: quotes,
backslashes, comments, operators, redirects and heredocs."""

import unittest

from helpers import HERE, shell


def read(command: str) -> list[list[str]]:
    """The words of each statement of the command, each redirect and its target left out."""
    return [shell.without_redirects(w) for _, w, _ in shell.statements(command, HERE)]


# A commit taking its message from a heredoc, as rn's /rn:up skill keeps a session's folder.
KEEP = "git add .rn/s\ngit commit -F - <<'EOF'\nKeep the plan\nEOF\ngit push"


class TestWords(unittest.TestCase):
    def test_each_separator_ends_a_statement(self):
        for separator in (";", ";;", "&", "&&", "|", "||", "|&", "(", ")", "`", "\n"):
            with self.subTest(separator=separator):
                # Given: a command of two statements with the separator between them
                # When: it is read
                # Then: it gives each statement's words
                self.assertEqual(
                    read(f"git add a{separator}git push"), [["git", "add", "a"], ["git", "push"]]
                )

    def test_quoted_operators_are_words(self):
        # Given: a commit whose message is operator signs, quoted
        # When: it is read
        # Then: the signs are a word of the statement
        self.assertEqual(read("git commit -m '&&' \"<<\""), [["git", "commit", "-m", "&&", "<<"]])

    def test_a_quoted_sign_is_a_word_of_the_command(self):
        # Given: a command with `;` and `>` in quotes before a path
        # When: its statements are read
        # Then: it is one statement, the quoted signs its words
        found = [words for _, words, _ in shell.statements("echo ';' '>' a", HERE)]
        self.assertEqual(found, [["echo", ";", ">", "a"]])

    def test_a_quoted_heredoc_sign_begins_no_heredoc(self):
        # Given: a quoted `<<` with a word after it, and a push on the next line
        # When: it is read
        # Then: the next line is a statement, not a heredoc's text
        self.assertEqual(read('echo "<<" x\ngit push'), [["echo", "<<", "x"], ["git", "push"]])

    def test_a_hash_after_quotes_is_part_of_the_word(self):
        # Given: a word whose `#` comes right after a quoted part
        # When: it is read
        # Then: the `#` and what follows it are part of the word
        self.assertEqual(read("echo ''#x y"), [["echo", "#x", "y"]])

    def test_a_backslash_before_a_lines_end_joins_the_lines(self):
        # Given: a push split over two lines by a backslash
        # When: it is read
        # Then: it is one statement
        self.assertEqual(read("git \\\npush"), [["git", "push"]])

    def test_a_backslash_keeps_the_character_after_it(self):
        # Given: words holding a blank and a separator, each after a backslash, and a backslash
        # at the command's end
        # When: it is read
        # Then: each is part of the word, and the last backslash none
        self.assertEqual(read("echo a\\ b c\\;d e\\"), [["echo", "a b", "c;d", "e"]])

    def test_double_quotes_take_a_backslash_off_what_it_escapes_alone(self):
        # Given: a word in double quotes holding backslashes before characters they escape there,
        # before a line's end, and before one they do not
        # When: it is read
        # Then: each escape gives its character, the line's end is joined, and the other
        # backslash is kept
        self.assertEqual(read('echo "a\\"b\\\\c\\$d\\`e\\\nf\\g"'), [["echo", 'a"b\\c$d`ef\\g']])

    def test_single_quotes_keep_every_backslash(self):
        # Given: a word in single quotes holding backslashes before characters double quotes take
        # them off
        # When: it is read
        # Then: each backslash is kept
        self.assertEqual(read("echo '\\$\\\"'"), [["echo", '\\$\\"']])

    def test_a_file_descriptor_first_in_a_statement_is_no_word(self):
        # Given: a push whose errors are redirected before its first word
        # When: it is read
        # Then: the descriptor is no word of the push
        self.assertEqual(read("2>/dev/null git push"), [["git", "push"]])

    def test_an_empty_quoted_word_is_a_word(self):
        # Given: a commit whose message is empty quotes
        # When: it is read
        # Then: the empty word is part of the statement
        self.assertEqual(read("git commit -m ''"), [["git", "commit", "-m", ""]])

    def test_a_redirect_and_its_target_are_left_out(self):
        for redirect in ("<", ">", ">>", ">|", "<>", "&>", "&>>", "<<<", ">&", "<&"):
            with self.subTest(redirect=redirect):
                # Given: a push with a redirect
                # When: it is read
                # Then: the redirect and its target are no words of the push
                self.assertEqual(read(f"git push {redirect} x origin"), [["git", "push", "origin"]])

    def test_a_file_descriptor_before_a_redirect_is_no_word(self):
        # Given: a push whose errors are redirected to its output
        # When: it is read
        # Then: the descriptor is no word of the push
        self.assertEqual(read("git push 2>&1"), [["git", "push"]])

    def test_digits_not_right_before_a_redirect_are_words(self):
        commands = (
            "git push '2'>x",
            'git push "2">x',
            "git push \\2>x",
            "git push 2 >x",
            "git push a2>x",
        )
        for command in commands:
            with self.subTest(command=command):
                # Given: digits quoted, escaped, apart from the redirect, or after a letter
                # When: it is read
                # Then: they are a word
                self.assertEqual(len(read(command)[0]), 3)

    def test_a_redirect_at_a_statements_end_takes_no_word_of_the_next(self):
        # Given: a redirect with no target before a separator
        # When: it is read
        # Then: the next statement keeps its first word
        self.assertEqual(read("echo >; git push"), [["echo"], ["git", "push"]])

    def test_a_blank_command_has_no_statement(self):
        # Given: a command of blanks and separators alone
        # When: it is read
        # Then: it has no statement
        self.assertEqual(read(" \t;\n"), [])

    def test_a_line_s_end_after_an_operator_ends_the_statement(self):
        # Given: a statement ended by `;` and a line's end together, and one by `)` and a line's
        # end, then a statement on the next line
        # When: the statements are read
        # Then: each is read apart, and the next line's words begin the next
        for command in ("cat a;\ncat b", "(cat a)\ncat b"):
            with self.subTest(command=command):
                found = [words for _, words, _ in shell.statements(command, HERE)]
                self.assertEqual(found, [["cat", "a"], ["cat", "b"]])

    def test_spaces_before_a_word_are_skipped(self):
        # Given: a command with two spaces before a word, a separator and a comment, and a line
        # begun with a tab
        # When: the statements are read
        # Then: each statement holds its words alone, and the comment none
        found = shell.statements("cat  a  ;  cat b  # c\n\tcat d", HERE)
        self.assertEqual([w for _, w, _ in found], [["cat", "a"], ["cat", "b"], ["cat", "d"]])

    def test_operators_around_a_line_s_end_are_read_in_order(self):
        # Given: a line ending in `;`, the next beginning with `;`
        # When: the words are read
        # Then: the operators come in the order they were written
        self.assertEqual(shell.words("a;\n;b"), ["a", ";", "\n", ";", "b"])

    def test_a_line_s_end_in_quotes_is_part_of_the_word(self):
        # Given: a command with a word in quotes that holds a line's end
        # When: the words are read
        # Then: the quoted word is one word, the line's end in it
        self.assertEqual(shell.words("echo 'a\nb'"), ["echo", "a\nb"])

    def test_a_command_whose_quoting_does_not_close_is_read_word_by_word(self):
        # Given: statements joined by `&&`, the first with a quote that does not close
        # When: the statements are read
        # Then: each is read apart, word by word
        found = shell.statements("echo don't && cat a", HERE)
        self.assertEqual([w for _, w, _ in found], [["echo", "don't"], ["cat", "a"]])


class TestHeredocs(unittest.TestCase):
    def test_a_heredocs_text_is_left_out(self):
        # Given: the keep of rn's /rn:up skill, a commit taking its message from a heredoc
        # When: it is read
        # Then: the heredoc's text and end word are left out
        want = [["git", "add", ".rn/s"], ["git", "commit", "-F", "-"], ["git", "push"]]
        self.assertEqual(read(KEEP), want)

    def test_a_heredoc_ends_only_at_its_end_word_alone_on_a_line(self):
        for line in ("EOF x", " EOF", "say EOF", "\x07 EOF"):
            with self.subTest(line=line):
                # Given: a heredoc whose text holds its end word inside a line, indented, or after
                # another word, a plain one or one of a control character
                # When: it is read
                # Then: its text runs to the line of its end word alone
                command = f"cat <<EOF\n{line}\nEOF\ngit push"
                self.assertEqual(read(command), [["cat"], ["git", "push"]])

    def test_two_heredocs_on_a_line_are_left_out_in_turn(self):
        # Given: two heredocs begun on one line
        # When: it is read
        # Then: the text of both is left out
        command = "cat <<A <<B\ngit push\nA\ngit commit\nB\ngit add x"
        self.assertEqual(read(command), [["cat"], ["git", "add", "x"]])

    def test_each_line_after_a_heredoc_is_read(self):
        # Given: a heredoc, its end word on a line of its own, then two lines of commands
        # When: the statements are read
        # Then: the heredoc's statement and both lines after it are read
        found = shell.statements("cat <<EOF\nhi\nEOF\necho x\ncat b", HERE)
        self.assertEqual(
            [w for _, w, _ in found], [["cat", "<<", "EOF"], ["echo", "x"], ["cat", "b"]]
        )

    def test_a_heredoc_begun_with_a_dash_ends_at_its_end_word_after_tabs(self):
        # Given: a heredoc after another statement, begun with `<<-`, its text a line of a tab and
        # its end word after a tab, then a statement
        # When: the statements are read
        # Then: it ends there and the statement after it is read
        found = shell.statements("ls; cat <<-EOF\n\tx\n\tEOF\necho y", HERE)
        self.assertEqual([w for _, w, _ in found], [["ls"], ["cat", "<<-", "EOF"], ["echo", "y"]])

    def test_a_heredoc_begun_without_a_dash_runs_on_past_its_end_word_after_a_tab(self):
        # Given: a heredoc begun with `<<`, its end word after a tab, then a statement
        # When: the statements are read
        # Then: its text runs on, the statement in it
        found = shell.statements("ls; cat <<EOF\n\tEOF\necho y", HERE)
        self.assertEqual([w for _, w, _ in found], [["ls"], ["cat", "<<", "EOF"]])

    def test_a_heredoc_with_no_end_to_its_line_keeps_the_commands_words(self):
        # Given: a heredoc whose line has no end
        # When: the words are read
        # Then: the command's words are kept
        self.assertEqual(shell.words("cat <<EOF"), ["cat", "<<", "EOF"])

    def test_a_heredoc_with_no_end_word_leaves_its_text_out_to_the_end(self):
        # Given: a heredoc whose text has no end word
        # When: the words are read with the text left out
        # Then: the text is left out to the command's end
        self.assertEqual(shell.words("cat <<EOF\nhi > a"), ["cat", "<<", "EOF", "\n"])


if __name__ == "__main__":
    unittest.main()
