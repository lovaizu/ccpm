"""Property-based tests of the hooks' reading of a command: each behavior over a kind of command,
checked on many commands Hypothesis makes, new on every run, CI included."""

import os
import shlex
import string
import sys
import unittest

# Hypothesis is installed on the newest Python alone, so the type check on 3.9 finds it missing.
try:
    from hypothesis import given  # pyrefly: ignore[missing-import]
    from hypothesis import strategies as st  # pyrefly: ignore[missing-import]
except ImportError:
    raise unittest.SkipTest("Hypothesis runs on the newest Python alone") from None

HOOKS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "common", "hooks"
)
sys.path.insert(0, os.path.normpath(HOOKS))

import shell

sys.path.insert(0, os.path.join(os.path.normpath(HOOKS), "..", "..", "dev", "common"))

import testing

testing.load_hypothesis_profile()

WORDS = st.lists(st.text(min_size=1), min_size=1, max_size=5)
NAMES = st.text(string.ascii_letters + string.digits + "._/", min_size=1, max_size=12).filter(
    lambda n: n not in (".", "..") and not n.startswith("-")
)
SEPARATORS = st.sampled_from([";", "&&", "||", "|", "&", "\n"])


def said(words):
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
        found = [(words, end) for _, words, end in shell.statements(command, "/r")]
        self.assertEqual(found, [(["echo", *w], e) for w, e in zip(statements, ends + ["\n"])])

    @given(st.lists(st.text(st.characters(blacklist_characters="\n"))))
    def test_any_heredoc_text_is_left_out(self, lines):
        # Given: a heredoc of any lines, none of them its end word alone, and a statement after it
        # When: the statements are read
        # Then: the heredoc's statement and the one after it are read, the text none
        text = "".join(f"{line}\n" for line in lines if line != "EOF")
        command = f"cat <<'EOF'\n{text}EOF\necho x"
        found = [words for _, words, _ in shell.statements(command, "/r")]
        self.assertEqual(found, [["cat", "<<", "EOF"], ["echo", "x"]])


class TestPaths(unittest.TestCase):
    @given(st.text(max_size=200))
    def test_any_command_is_read_into_paths_whole(self, command):
        # Given: any command
        # When: the paths it names, writes and prints whole are read
        # Then: they are read without breaking, each path whole
        for paths in (shell.named, shell.written, shell.printed):
            self.assertTrue(all(os.path.isabs(p) for p in paths(command, "/r")))

    @given(st.lists(NAMES, min_size=1, max_size=5))
    def test_cat_reads_each_file_it_names(self, names):
        # Given: files of any plain names
        # When: a command prints them with cat
        # Then: each is taken as read whole
        found = shell.printed("cat " + " ".join(names), "/r")
        self.assertEqual(found, [os.path.realpath(os.path.join("/r", n)) for n in names])
