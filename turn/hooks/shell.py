"""What a shell command reads and writes: the paths its words name, each taken from where the
command's cd has gone by then, as the shell takes it, and a heredoc's text left out, as it is input,
not paths."""

from __future__ import annotations

import os
import shlex
from collections.abc import Iterator

# Where one statement ends and the next begins.
SEPARATORS = {";", "|", "||", "&", "&&", "(", ")", "`", "\n"}
# A redirect that writes the path after it.
WRITES = {">", ">>", ">|", "&>", "&>>"}
# A heredoc's end word, a here-string or a file descriptor follows these, not a path.
NOT_PATHS = {"<<", "<<-", "<<<", ">&", "<&"}
REDIRECTS = WRITES | NOT_PATHS | {"<"}
SIGNS = "();<>|&`\n"
# Every operator the signs make, the longest first, so `&&` is not taken for two `&`.
OPERATORS = sorted(SEPARATORS | REDIRECTS, key=len, reverse=True)
# turn's script and each step it is asked, whose next word is where the run is kept.
STEPS = {"start", "next", "given", "parts", "record"}
# Commands that write each path they name, and those that write the last.
WRITE_EACH = {"rm", "rmdir", "touch", "mkdir", "tee", "truncate"}
WRITE_LAST = {"cp", "mv", "ln", "install"}


def words(command: str) -> list[str]:
    """The command's words, with `;`, `|`, `&&`, a line's end and the like apart from the paths
    they follow, and from each other, as shlex joins signs that come together, such as `);`."""
    lexer = shlex.shlex(command, posix=True, punctuation_chars=SIGNS)
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    try:
        said = list(lexer)
    except ValueError:
        return command.split()
    return [w for word in said for w in (apart(word) if set(word) <= set(SIGNS) else [word])]


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
    said = text_left_out(words(command))
    here: str | None = cwd
    statement: list[str] = []
    for word in said + ["\n"]:
        if word not in SEPARATORS:
            statement.append(word)
            continue
        if statement[:1] == ["cd"]:
            target = statement[1] if len(statement) > 1 else "~"
            here = None if target == "-" else path(here, target)
        elif statement:
            yield here, statement, word
        statement = []


def text_left_out(said: list[str]) -> list[str]:
    """The words with each heredoc's text left out, from the line after `<<` to its end word."""
    kept: list[str] = []
    rest = iter(said)
    for word in rest:
        kept.append(word)
        if word not in ("<<", "<<-"):
            continue
        end = next(rest, None)
        # The rest of the line is the command's, such as a redirect; the text runs from the next
        # line to its end word on a line of its own.
        line = []
        for word in rest:
            line.append(word)
            if word == "\n":
                break
        kept += [end] + line if end else line
        last = "\n"
        for word in rest:
            if word == end and last == "\n":
                break
            last = word
    return kept


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
        for i, word in enumerate(said):
            if word in REDIRECTS or (i and said[i - 1] in NOT_PATHS):
                continue
            if i > 1 and said[i - 2].endswith("turn.py") and said[i - 1] in STEPS:
                continue
            found.append(path(here, word))
    return [p for p in found if p]


def written(command: str, cwd: str) -> list[str]:
    """Each path the command writes: by a redirect, by a command that writes the paths it names, or
    in place by sed."""
    found = []
    for here, said, _ in statements(command, cwd):
        found += [path(here, w) for i, w in enumerate(said[1:]) if said[i] in WRITES]
        plain = [w for i, w in enumerate(said) if w not in REDIRECTS and not redirected(said, i)]
        # An empty word is no path, such as the suffix macOS's `sed -i ''` takes.
        args = [w for w in plain[1:] if w and not w.startswith("-")]
        head = plain[0] if plain else ""
        if head in WRITE_EACH:
            found += [path(here, w) for w in args]
        elif head in WRITE_LAST:
            found += [path(here, w) for w in args[-1:]]
        elif head == "sed" and any(w.startswith(("-i", "--in-place")) for w in plain):
            found += [path(here, w) for w in args[1:]]
    return [p for p in found if p]


def redirected(said: list[str], i: int) -> bool:
    """Whether the word at i is a redirect's target, not an argument of the command."""
    return bool(i) and said[i - 1] in REDIRECTS


def printed(command: str, cwd: str) -> list[str]:
    """The files the command prints whole with cat, in a statement not piped or redirected."""
    found = []
    for here, said, end in statements(command, cwd):
        if said[0] == "cat" and end != "|" and not REDIRECTS & set(said):
            found += [path(here, w) for w in said[1:] if not w.startswith("-")]
    return [p for p in found if p]
