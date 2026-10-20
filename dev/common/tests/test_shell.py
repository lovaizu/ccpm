"""The hooks' reading of a command: the paths it names, writes and prints whole, each word taken
as the shell takes it."""

import os
import sys
import unittest

HOOKS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "common", "hooks"
)
sys.path.insert(0, os.path.normpath(HOOKS))

import shell

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

    def test_a_here_string_s_text_begun_with_a_dash_is_no_path(self):
        # Given: a command with a here-string's text right after `<<<`, begun with `-`
        # When: the paths it names are read
        # Then: the paths alone are taken
        self.assertEqual(shell.named("cat a <<<-text b", HERE), at("cat", "a", "b"))

    def test_a_quoted_sign_is_a_word_of_the_command(self):
        # Given: a command with `;` and `>` in quotes before a path
        # When: its statements and the paths it writes are read
        # Then: it is one statement, the quoted signs its words, and it writes no path
        found = [words for _, words, _ in shell.statements("echo ';' '>' a", HERE)]
        self.assertEqual(found, [["echo", ";", ">", "a"]])
        self.assertEqual(shell.written("echo '>' a", HERE), [])

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
        self.assertEqual(shell.named("cat a 2> err b", HERE), at("cat", "a", "err", "b"))

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

    def test_a_quoted_path_is_named_as_the_shell_takes_it(self):
        # Given: a command naming a path in single or double quotes, with a space in it
        # When: the paths it names are read
        # Then: the path is taken whole, without its quotes
        for command in ("cat 'a b'", 'cat "a b"'):
            with self.subTest(command=command):
                self.assertEqual(shell.named(command, HERE), at("cat", "a b"))

    def test_a_word_the_shell_makes_from_a_variable_is_no_path(self):
        # Given: a command naming a path made from a variable
        # When: the paths it names are read
        # Then: that path is not taken, as the words do not settle it
        self.assertEqual(shell.named("cat $HOME/a", HERE), at("cat"))

    def test_the_words_after_where_the_run_is_kept_are_named(self):
        # Given: turn's script asked a step, with a word after where the run is kept
        # When: the paths it names are read
        # Then: that word is taken
        self.assertEqual(shell.named("turn.py next r.json x", HERE), at("turn.py", "next", "x"))

    def test_each_line_s_statement_is_named(self):
        # Given: a command of two lines, neither a heredoc
        # When: the paths it names are read
        # Then: the words of both lines are taken
        self.assertEqual(shell.named("cat a\ncat b", HERE), at("cat", "a", "cat", "b"))

    def test_a_comment_names_no_path(self):
        # Given: a command with a comment after its words, and a `#` inside a word, and one whose
        # comment, holding a tab, runs to the command's end
        # When: the paths it names are read
        # Then: the words before the comment are taken, the word with `#` among them
        self.assertEqual(shell.named("cat a#b # c d\ncat e", HERE), at("cat", "a#b", "cat", "e"))
        self.assertEqual(shell.named("cat a #\tc", HERE), at("cat", "a"))

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

    def test_a_heredoc_s_end_word_ends_it_only_at_a_line_s_start(self):
        # Given: heredocs whose text holds the end word after another word, a plain one or one of
        # a control character, and then a redirect
        # When: the paths each writes are read
        # Then: none is taken, as the text runs on to its end word on a line of its own
        for word in ("say", "\x07"):
            command = f"cat <<EOF\n{word} EOF\nx > notes/new.md\nEOF"
            with self.subTest(command=command):
                self.assertEqual(shell.written(command, HERE), [])


class TestHeredoc(unittest.TestCase):
    def test_a_heredoc_cut_short_leaves_its_text_out_to_the_end(self):
        # Given: a heredoc whose line has no end, and one whose text has no end word
        # When: the words are read with the text left out
        # Then: the command's words are kept and the text is left out to the command's end
        self.assertEqual(shell.words("cat <<EOF"), ["cat", "<<", "EOF"])
        said = shell.words("cat <<EOF\nhi > a")
        self.assertEqual(said, ["cat", "<<", "EOF", "\n"])

    def test_the_command_after_a_heredoc_s_end_word_is_read(self):
        # Given: a heredoc, its end word on a line of its own, then a command writing a file
        # When: the paths it writes are read
        # Then: that file is taken, as the text ends at the end word
        command = "cat <<EOF\nhi\nEOF\necho x > notes/new.md"
        self.assertEqual(shell.written(command, HERE), at("notes/new.md"))

    def test_each_line_after_a_heredoc_is_read(self):
        # Given: a heredoc, its end word on a line of its own, then two lines of commands
        # When: the statements are read
        # Then: the heredoc's statement and both lines after it are read
        found = shell.statements("cat <<EOF\nhi\nEOF\necho x\ncat b", HERE)
        self.assertEqual(
            [w for _, w, _ in found], [["cat", "<<", "EOF"], ["echo", "x"], ["cat", "b"]]
        )

    def test_a_heredoc_begun_with_a_dash_ends_at_its_end_word_after_tabs(self):
        # Given: heredocs after another statement, their text a line of a tab, begun with `<<-`
        # and with `<<`, each with its end word after a tab, then a statement
        # When: the statements are read
        # Then: the `<<-` one ends there and the statement after it is read; the `<<` one runs on
        found = shell.statements("ls; cat <<-EOF\n\tx\n\tEOF\necho y", HERE)
        self.assertEqual([w for _, w, _ in found], [["ls"], ["cat", "<<-", "EOF"], ["echo", "y"]])
        found = shell.statements("ls; cat <<EOF\n\tEOF\necho y", HERE)
        self.assertEqual([w for _, w, _ in found], [["ls"], ["cat", "<<", "EOF"]])

    def test_a_command_whose_quoting_does_not_close_is_read_word_by_word(self):
        # Given: statements joined by `&&`, the first with a quote that does not close
        # When: the statements are read
        # Then: each is read apart, word by word
        found = shell.statements("echo don't && cat a", HERE)
        self.assertEqual([w for _, w, _ in found], [["echo", "don't"], ["cat", "a"]])


def read(command):
    """The words of each statement of the command, each redirect and its target left out."""
    return [shell.without_redirects(w) for _, w, _ in shell.statements(command, HERE)]


# The command rn's /rn:up skill runs to keep a session's folder.
KEEP = "git add .rn/s\ngit commit -F - <<'EOF'\nKeep the plan\nEOF\ngit push"


class TestReading(unittest.TestCase):
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

    def test_a_quoted_heredoc_sign_begins_no_heredoc(self):
        # Given: a quoted `<<` with a word after it, and a push on the next line
        # When: it is read
        # Then: the next line is a statement, not a heredoc's text
        self.assertEqual(read('echo "<<" x\ngit push'), [["echo", "<<", "x"], ["git", "push"]])

    def test_a_heredocs_text_is_left_out(self):
        # Given: the keep of rn's /rn:up skill, a commit taking its message from a heredoc
        # When: it is read
        # Then: the heredoc's text and end word are left out
        want = [["git", "add", ".rn/s"], ["git", "commit", "-F", "-"], ["git", "push"]]
        self.assertEqual(read(KEEP), want)

    def test_a_heredoc_ends_only_at_its_end_word_alone_on_a_line(self):
        # Given: a heredoc whose text holds its end word inside a line, and indented
        # When: it is read
        # Then: its text runs to the line of its end word alone
        self.assertEqual(read("cat <<EOF\nEOF x\n EOF\nEOF\ngit push"), [["cat"], ["git", "push"]])

    def test_two_heredocs_on_a_line_are_left_out_in_turn(self):
        # Given: two heredocs begun on one line
        # When: it is read
        # Then: the text of both is left out
        command = "cat <<A <<B\ngit push\nA\ngit commit\nB\ngit add x"
        self.assertEqual(read(command), [["cat"], ["git", "add", "x"]])

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
        commands = ("git push '2'>x", 'git push "2">x', "git push \\2>x", "git push 2 >x")
        for command in commands + ("git push a2>x",):
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


class TestWrittenByReadWrite(unittest.TestCase):
    def test_a_read_and_write_redirect_writes_its_target(self):
        # Given: a command opening a file to read and write with `<>`
        # When: the paths it writes are read
        # Then: the file is taken, as `<>` makes it where it is not there
        self.assertEqual(shell.written("cat <> a", HERE), at("a"))


class TestSedInPlace(unittest.TestCase):
    def test_sed_in_place_writes_the_file_after_its_script(self):
        # Given: sed editing a file in place, its backup suffix given
        # When: the paths it writes are read
        # Then: the file is taken
        self.assertEqual(shell.written("sed -i '' 's/a/b/' f", HERE), at("f"))


class TestPrinted(unittest.TestCase):
    def test_cat_before_an_or_prints_its_file(self):
        # Given: cat of a file, followed by another command after `||`
        # When: the files it prints whole are read
        # Then: the file is taken, as only a pipe takes what cat prints
        self.assertEqual(shell.printed("cat a || echo x", HERE), at("a"))

    def test_cat_alone_or_before_another_statement_prints_its_file(self):
        # Given: cat of a file alone, and before another statement after `;`
        # When: the files each prints whole are read
        # Then: the file is taken
        for command in ("cat a", "cat a; ls"):
            with self.subTest(command=command):
                self.assertEqual(shell.printed(command, HERE), at("a"))

    def test_only_cat_prints_its_file(self):
        # Given: commands other than cat naming a file, whose names sort before and after cat
        # When: the files each prints whole are read
        # Then: none is taken
        for command in ("awk 1 a", "head a"):
            with self.subTest(command=command):
                self.assertEqual(shell.printed(command, HERE), [])


class TestGit(unittest.TestCase):
    def test_each_git_statement_acts_where_c_moves_it(self):
        # Given: git statements with options before the git command: -C with its folder, -c with
        # its setting, options taking no word, and -C last with or without its folder
        # When: where each acts is read
        # Then: -C alone moves it, from where it stood, and the git command follows the options
        for command, found in (
            ("git -C x -C y commit -m z", [(at("x/y")[0], ["commit", "-m", "z"])]),
            ("git -c a=b log", [(HERE, ["log"])]),
            ("git --no-pager log", [(HERE, ["log"])]),
            ("git -C /x", [("/x", [])]),
            ("git -C", [(HERE, [])]),
            ("ls && cd a && git status", [(at("a")[0], ["status"])]),
            ("cat x", []),
        ):
            with self.subTest(command=command):
                self.assertEqual(list(shell.git(command, HERE)), found)

    def test_a_folder_is_inside_the_top_alone_or_in_it(self):
        # Given: the top, a folder in it, one beside it whose name starts the same or sorts before or after,
        # and one the words do not settle
        # When: each is asked whether it is inside the top
        # Then: the first two are
        # Each folder as a cd or -C makes it, a path of its own.
        for folder, found in (
            ("/r", True),
            ("/r/a", True),
            ("/rx", False),
            ("/s", False),
            ("/a", False),
        ):
            with self.subTest(folder=folder):
                self.assertEqual(shell.inside(shell.path(HERE, folder), HERE), found)
        self.assertFalse(shell.inside(None, HERE))
