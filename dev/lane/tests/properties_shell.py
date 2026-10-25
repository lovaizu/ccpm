"""Property-based tests of the hooks' reading of a command, and of a tool call read as one action:
each behavior over a kind of command, checked on many commands Hypothesis makes, new on every run,
CI included."""

import os
import shlex
import string
import unittest

import helpers
from helpers import HERE, NO_PLUGIN, shell, start_with, testing

hypothesis = testing.hypothesis()
assume = hypothesis.assume
given = hypothesis.given
st = hypothesis.strategies

WORDS = st.lists(st.text(min_size=1), min_size=1, max_size=5)
NAMES = st.text(string.ascii_letters + string.digits + "._/", min_size=1, max_size=12).filter(
    lambda n: n not in (".", "..") and not n.startswith("-")
)
# A variable's name, as an assignment before a command sets it.
VARIABLES = st.from_regex(r"[A-Za-z_][A-Za-z0-9_]*", fullmatch=True)
SEPARATORS = st.sampled_from([";", "&&", "||", "|", "&", "\n"])


def said(words: list[str]) -> str:
    """The words as a command, each quoted as a shell quotes it."""
    return " ".join(shlex.quote(w) for w in words)


class TestWords(unittest.TestCase):
    @given(WORDS)
    def test_any_quoted_words_are_read_as_they_are(self, words):
        # Given: a command whose words are any text, each quoted as a shell quotes it
        # When: its words are read
        # Then: each is one word, as it was written
        self.assertEqual(shell.words("echo " + said(words)), ["echo", *words])

    @given(st.lists(WORDS, min_size=1, max_size=4), st.data())
    def test_statements_joined_by_any_separator_are_read_apart(self, statements, data):
        # Given: statements of any quoted words, each after the first joined by a separator
        # When: the statements are read
        # Then: each comes back with its words, ended by the separator after it
        command = said(["echo", *statements[0]])
        ends = []
        for words in statements[1:]:
            ends.append(data.draw(SEPARATORS))
            command += f" {ends[-1]} " + said(["echo", *words])
        found = [(words, end) for _, words, end in shell.statements(command, HERE)]
        self.assertEqual(found, [(["echo", *w], e) for w, e in zip(statements, ends + ["\n"])])

    @given(st.lists(st.text(st.characters(blacklist_characters="\n"))))
    def test_any_heredoc_text_is_left_out(self, lines):
        # Given: a heredoc of any lines, none of them its end word alone, and a statement after it
        # When: the statements are read
        # Then: the heredoc's statement and the one after it are read, the text none
        text = "".join(f"{line}\n" for line in lines if line != "EOF")
        command = f"cat <<'EOF'\n{text}EOF\necho x"
        found = [words for _, words, _ in shell.statements(command, HERE)]
        self.assertEqual(found, [["cat", "<<", "EOF"], ["echo", "x"]])


class TestPaths(unittest.TestCase):
    @given(st.text(max_size=200))
    def test_any_command_is_read_into_paths_whole(self, command):
        # Given: any command
        # When: the paths it writes are read
        # Then: they are read without breaking, each path whole
        self.assertTrue(all(os.path.isabs(p) for p in shell.written(command, HERE)))

    @given(st.lists(NAMES, min_size=1, max_size=5))
    def test_cat_reads_each_file_it_names(self, names):
        # Given: files of any plain names
        # When: a command prints them with cat
        # Then: each is taken as read whole
        found = shell.reads("cat " + " ".join(names), HERE)
        whole = [(os.path.realpath(os.path.join(HERE, n)), shell.WHOLE) for n in names]
        self.assertEqual(found, whole)


class TestReads(unittest.TestCase):
    @given(st.text(max_size=200))
    def test_any_command_is_read_into_files_whole_with_their_lines(self, command):
        # Given: any command
        # When: what it reads is read
        # Then: it is read without breaking, each file's path whole, its lines two ends or none told
        for file, lines in shell.reads(command, HERE):
            self.assertTrue(os.path.isabs(file) and (lines is None or len(lines) == 2))

    @given(st.integers(1, 10**6), st.integers(0, 10**6), NAMES)
    def test_sed_printing_any_span_reads_those_lines(self, first, more, name):
        # Given: sed -n printing the lines of any span, from any line on, of a file of any name
        # When: what it reads is read
        # Then: it reads those lines of the file
        found = shell.reads(f"sed -n '{first},{first + more}p' {name}", HERE)
        self.assertEqual(
            found, [(os.path.realpath(os.path.join(HERE, name)), (first, first + more))]
        )


class TestRuns(unittest.TestCase):
    @given(st.lists(WORDS, min_size=1, max_size=4), st.data())
    def test_commands_of_any_quoted_words_joined_by_any_separator_are_each_run(self, runs, data):
        # Given: commands of any words, each quoted as a shell quotes it, the first word no cd,
        # git, env or assignment, which are read apart, joined by any separator
        assume(all(words[0] not in ("cd", "git", "env") for words in runs))
        assume(not any(shell.ASSIGNMENT.fullmatch(words[0]) for words in runs))
        command = " ".join(f"{said(words)} {data.draw(SEPARATORS)}" for words in runs)
        # When: the call is read
        # Then: it runs each command with its words as they were written
        found = helpers.acted("Bash", {"command": command})
        self.assertEqual((found.action, found.what), ("run", runs))

    @given(WORDS, st.text(min_size=1))
    def test_git_run_in_any_folder_runs_its_command(self, words, folder):
        # Given: git run with -C in any folder, its command and arguments any words, the command
        # beginning with no `-`, which git takes as its own option
        assume(not words[0].startswith("-"))
        # When: the call is read
        # Then: it runs git's command with its arguments
        command = f"git -C {shlex.quote(folder)} {said(words)}"
        self.assertEqual(
            helpers.acted("Bash", {"command": command}).what,
            [["git", *words]],
        )

    @given(st.lists(st.tuples(VARIABLES, st.text()), max_size=3), st.booleans(), WORDS)
    def test_a_command_after_any_assignments_and_env_runs_itself(self, assigned, env, words):
        # Given: a command of any words, its first no env and no assignment, after assignments of
        # any names and values, each value quoted as a shell quotes it, with env before them or
        # not, the command then beginning with no `-`, which env takes as its own option
        assume(words[0] != "env" and not shell.ASSIGNMENT.fullmatch(words[0]))
        assume(not (env and words[0].startswith("-")))
        before = ["env"] * env + [f"{name}={shlex.quote(value)}" for name, value in assigned]
        # When: the call is read
        # Then: it runs the command with its words, as they were written
        command = " ".join([*before, said(words)])
        self.assertEqual(
            helpers.acted("Bash", {"command": command}).what,
            [words],
        )


class TestStartWith(unittest.TestCase):
    @given(st.text(min_size=1), st.sampled_from(["python3 ", "sh ", ""]), WORDS)
    def test_the_script_run_first_from_any_folder_is_no_drift(self, folder, interpreter, words):
        # Given: a subagent that has made no call, and the script taken run from any folder,
        # quoted as a shell quotes it, by python3, by sh or by its path, with any words after it;
        # by its path, not a path like an assignment, as a folder `A=` makes it, which lane reads
        # as one, quoted or not, as no step names such a script
        path = os.path.join(folder, "scripts", "turn.py")
        script = shlex.quote(path)
        assume(interpreter or not shell.ASSIGNMENT.fullmatch(path))
        command = f"{interpreter}{script} {said(words)}"
        made = helpers.acted("Bash", {"command": command})
        # When: start_with reads it as the subagent's first call
        # Then: it is no drift
        self.assertFalse(
            start_with.drifts(made._replace(before=[]), ["scripts/turn.py"], NO_PLUGIN)
        )


if __name__ == "__main__":
    unittest.main()
