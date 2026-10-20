"""What a shell command reads and writes: the paths its words name, each taken from where the
command's cd has gone by then, as the shell takes it, and a heredoc's text left out, as it is input,
not paths."""

from __future__ import annotations

import os
import shlex
from collections import deque
from collections.abc import Iterator
from typing import cast

# Where one statement ends and the next begins.
SEPARATORS = {";", "|", "||", "&", "&&", "(", ")", "`", "\n"}
# A redirect that writes the path after it.
WRITES = {">", ">>", ">|", "&>", "&>>"}
# A heredoc's end word, a here-string or a file descriptor follows these, not a path.
NOT_PATHS = {"<<", "<<-", "<<<", ">&", "<&"}
# What each heredoc's operator takes off the start of each line of its text, before its end word.
HEREDOCS = {"<<": "", "<<-": "\t"}
REDIRECTS = {*WRITES, *NOT_PATHS, "<"}
SIGNS = "();<>|&`\n"
# Every operator the signs make, the longest first, so `&&` is not taken for two `&`.
OPERATORS = sorted({*SEPARATORS, *REDIRECTS}, key=len, reverse=True)
# turn's script and each step it is asked, whose next word is where the run is kept.
STEPS = {"start", "next", "given", "parts", "record"}
# Commands that write each path they name, and those that write the last.
WRITE_EACH = {"rm", "rmdir", "touch", "mkdir", "tee", "truncate"}
WRITE_LAST = {"cp", "mv", "ln", "install"}
# git's options that take the next word.
GIT_VALUED = {"-C", "-c"}


class Operator(str):
    """A word the shell takes as an operator, such as `;` or `>`, not one quoted to look like it."""


def sign(word: str, kinds: set[str]) -> bool:
    """Whether the word is an operator of these kinds."""
    return isinstance(word, Operator) and word in kinds


class Lexer(shlex.shlex):
    """shlex, telling of each word whether it is operators, before any quote is taken off, with a
    line's end always a word of its own, and taking `#` as a comment only where a word begins, as
    the shell does."""

    signs: bool
    # The end words of the heredocs begun on this line, each with what is taken off its lines.
    ends: list[tuple[str, str]]
    # shlex keeps here the characters it has read and put back, since Python 3.6, where
    # punctuation_chars came in; its type stubs leave it out.
    _pushback_chars: deque[str]

    def char(self) -> str:
        return self._pushback_chars.pop() if self._pushback_chars else self.instream.read(1)

    def read_token(self) -> str | None:
        c = self.char()
        while c and c in self.whitespace:
            c = self.char()
        if c == "#":
            while c and c != "\n":
                c = self.char()
        self.signs = bool(c) and c in self.punctuation_chars
        if c == "\n":
            for end, start in self.ends:
                self.text(end, start)
            self.ends = []
            return c
        self._pushback_chars.append(c)
        if not self.signs:
            return super().read_token()
        # Signs read are a word.
        word = cast(str, super().read_token())
        # shlex puts back the character after the signs, and `-` is no sign, as `cat -n` is one
        # word; right after `<<`, not `<<<`, it makes `<<-`.
        heredoc = word.endswith("<<") and not word.endswith("<<<")
        if heredoc and list(self._pushback_chars) == ["-"]:
            word += self._pushback_chars.pop()
        if "\n" in word:
            # What follows the line's end is read again, the next char first.
            self._pushback_chars.extend(reversed(word[word.index("\n") :]))
            word = word[: word.index("\n")]
        return word

    def text(self, end: str, start: str) -> None:
        """Reads past a heredoc's text, to its end word on a line of its own, the characters of
        `start` taken off the line's start first."""
        line = None
        while line != end:
            line, c = "", self.char()
            while c and c != "\n":
                line, c = line + c, self.char()
            line = line.lstrip(start)
            if not c:
                return


def words(command: str) -> list[str]:
    """The command's words, with `;`, `|`, `&&`, a line's end and the like apart from the paths
    they follow, and from each other, as shlex joins signs that come together, such as `);`; and
    each heredoc's text left out, from the line after `<<` to its end word."""
    lexer = Lexer(command, posix=True, punctuation_chars=SIGNS)
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    lexer.commenters = ""
    lexer.ends = []
    said: list[str] = []
    try:
        for word in iter(lexer.get_token, None):
            if not lexer.signs:
                if said and sign(said[-1], set(HEREDOCS)):
                    lexer.ends.append((word, HEREDOCS[said[-1]]))
                said.append(word)
                continue
            said += [Operator(o) for o in apart(word)]
    except ValueError:
        # Read word by word, as its quoting does not close.
        return [Operator(w) if w in OPERATORS else w for w in command.split()]
    return said


def apart(signs: str) -> list[str]:
    """Signs shlex joined, each operator apart, the longest first."""
    found = []
    while signs:
        operator = next(o for o in OPERATORS if signs.startswith(o))
        found.append(operator)
        signs = signs[len(operator) :]
    return found


def statements(command: str, cwd: str) -> Iterator[tuple[str | None, list[str], str]]:
    """Each statement of the command: the folder it runs in, where the last cd went, or None where
    the words do not settle it, such as `cd "$d"`; its words; and what ends it."""
    here: str | None = cwd
    statement: list[str] = []
    for word in words(command) + [Operator("\n")]:
        if not sign(word, SEPARATORS):
            statement.append(word)
            continue
        if statement[:1] == ["cd"]:
            # A bare cd goes home.
            target = (statement + ["~"])[1]
            here = None if target == "-" else path(here, target)
        elif statement:
            yield here, statement, word
        statement = []


def git(command: str, cwd: str) -> Iterator[tuple[str | None, list[str]]]:
    """Each git statement of the command: the folder it acts in, where the last cd went and each
    `-C` moved it, or None where the words do not settle it, such as `cd "$d"` into a folder of its
    own; and its words after git's options, the git command first."""
    for here, said, _ in statements(command, cwd):
        rest = said[1:] if said[0] == "git" else None
        while rest and rest[0].startswith("-"):
            if rest[0] == "-C" and rest[1:]:
                here = path(here, rest[1])
            rest = rest[2:] if rest[0] in GIT_VALUED else rest[1:]
        if rest is not None:
            yield here, rest


def inside(folder: str | None, top: str) -> bool:
    """Whether the folder is the top or in it; one the words do not settle is not."""
    return folder is not None and (folder == top or folder.startswith(top + os.sep))


def path(here: str | None, word: str) -> str | None:
    """The path a word names from the folder, or None where the words do not settle it."""
    # A path cannot hold a null character, and the shell does not pass one.
    if not word or "$" in word or "`" in word or "\0" in word:
        return None
    word = os.path.expanduser(word)
    if not os.path.isabs(word) and here is None:
        return None
    return os.path.realpath(os.path.join(here or "", word))


def named(command: str, cwd: str) -> list[str]:
    """Each path the command names, but where cd goes, a redirect's target and where the run is
    kept, which turn's script is asked of."""
    found = []
    for here, said, _ in statements(command, cwd):
        # Each word with the two before it.
        for second, first, word in zip(["", ""] + said, [""] + said, said):
            if sign(word, REDIRECTS) or sign(first, NOT_PATHS):
                continue
            if second.endswith("turn.py") and first in STEPS:
                continue
            found.append(path(here, word))
    return [p for p in found if p]


def written(command: str, cwd: str) -> list[str]:
    """Each path the command writes: by a redirect, by a command that writes the paths it names, or
    in place by sed."""
    found = []
    for here, said, _ in statements(command, cwd):
        # Each word with the one before it.
        pairs = list(zip([""] + said, said))
        found += [path(here, w) for before, w in pairs if sign(before, WRITES)]
        # A redirect's target is not an argument of the command.
        plain = [w for before, w in pairs if not sign(w, REDIRECTS) and not sign(before, REDIRECTS)]
        # An empty word, such as the backup suffix of `sed -i ''`, names no path.
        args = [w for w in plain[1:] if w and not w.startswith("-")]
        head = plain[0] if plain else ""
        if head in WRITE_EACH:
            found += [path(here, w) for w in args]
        elif head in WRITE_LAST:
            found += [path(here, w) for w in args[-1:]]
        elif head == "sed" and any(w.startswith(("-i", "--in-place")) for w in plain):
            found += [path(here, w) for w in args[1:]]
    return [p for p in found if p]


def printed(command: str, cwd: str) -> list[str]:
    """The files the command prints whole with cat, in a statement not piped or redirected."""
    found = []
    for here, said, end in statements(command, cwd):
        if said[0] == "cat" and end != "|" and not any(sign(w, REDIRECTS) for w in said):
            found += [path(here, w) for w in said[1:] if not w.startswith("-")]
    return [p for p in found if p]
