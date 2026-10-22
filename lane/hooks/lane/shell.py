"""What a shell command reads and writes: the paths its words name, each taken from where the
command's cd has gone by then, as the shell takes it, and a heredoc's text left out, as it is input,
not paths."""

from __future__ import annotations

import os
import re
from collections.abc import Iterator
from typing import Optional

# Where one statement ends and the next begins.
SEPARATORS = {";", ";;", "|", "|&", "||", "&", "&&", "(", ")", "`", "\n"}
# A redirect that writes the path after it.
WRITES = {">", ">>", ">|", "<>", "&>", "&>>"}
# A heredoc's end word, a here-string or a file descriptor follows these, not a path.
NOT_PATHS = {"<<", "<<-", "<<<", ">&", "<&"}
# The redirects whose next word is a heredoc's end word, and whether each takes the tabs off the
# start of each line of its text.
HEREDOCS = {"<<": False, "<<-": True}
REDIRECTS = {*WRITES, *NOT_PATHS, "<"}
# Every operator, the longest first, so `&&` is not taken for two `&`.
OPERATORS = sorted({*SEPARATORS, *REDIRECTS}, key=len, reverse=True)
# One piece of a command as the shell reads it, tried in this order: blanks between words; a
# backslash before a line's end, which joins the two lines; a comment, which begins only where a
# word could; text in single or in double quotes, each closed by its quote; a quote not closed,
# with the rest of the command; a character after a backslash; an operator; and plain text. Every
# character begins one of them.
PIECE = re.compile(
    r"(?P<blank>[ \t]+)"
    r"|(?P<join>\\\n)"
    r"|(?P<comment>(?:^|(?<=[ \t\n;&|()<>`]))#[^\n]*)"
    r"|'(?P<single>[^']*)'"
    r'|"(?P<double>(?:\\.|[^"\\])*)"'
    r"|(?P<unclosed>['\"].*)"
    r"|\\(?P<escaped>.?)"
    r"|(?P<operator>" + "|".join(re.escape(o) for o in OPERATORS) + ")"
    r"|(?P<plain>[^ \t\n'\"\\;&|()<>`]+)",
    re.DOTALL,
)
# In double quotes a backslash escapes only these, and before a line's end joins the two lines.
DOUBLE_ESCAPED = re.compile(r'\\([$`"\\])|\\\n')
# turn's script and each step it is asked, whose next word is where the run is kept.
STEPS = {"start", "next", "given", "parts", "record"}
# Commands that write each path they name, and those that write the last.
WRITE_EACH = {"rm", "rmdir", "touch", "mkdir", "tee", "truncate"}
WRITE_LAST = {"cp", "mv", "ln", "install"}
# git's options that take the next word.
GIT_VALUED = {"-C", "-c"}
# The lines a command reads of a file, from the first to the last, 1 the file's first line: the last
# None for the file's end, and a first of 0 or below counted back from the end, -1 its last line and
# 0 the end after it.
Lines = tuple[int, Optional[int]]
WHOLE: Lines = (1, None)
# A count of lines head or tail takes, as `-n 5`, `-n5` or `-5`; for tail, `+5` from the fifth on.
COUNT = re.compile(r"-?n?(?P<on>\+)?(?P<count>[0-9]+)")
# What head and tail take where no option is given: ten lines.
UNCOUNTED = [("-n", "10")]
# sed's script printing the lines from one number to another, as `10,20p`, `5,$p` or `3p`.
SED_LINES = re.compile(r"(?P<first>[0-9]+)(?:,(?P<last>[0-9]+|\$))?p")


class Operator(str):
    """A word the shell takes as an operator, such as `;` or `>`, not one quoted to look like it."""


def sign(word: str, kinds: set[str]) -> bool:
    """Whether the word is an operator of these kinds."""
    return isinstance(word, Operator) and word in kinds


def heredocs_end(command: str, pos: int, ends: list[tuple[str, bool]]) -> int:
    """Where the command goes on after the heredocs whose text begins at pos, one after another,
    each ended by a line holding its end word alone, after tabs where they are taken off; the end
    of the command where a heredoc's end word never comes."""
    for end, tabs in ends:
        line = re.compile(("^\t*" if tabs else "^") + re.escape(end) + "$", re.MULTILINE)
        found = line.search(command, pos)
        pos = found.end() if found else len(command)
    return pos


def words(command: str) -> list[str]:
    """The command's words and operators in order, the operators as Operator: quotes and
    backslashes taken off each word, and comments and each heredoc's text left out. A quoted `&&`
    or `<<` is a word, and digits right before a redirect, a file descriptor, are no word. A
    command whose quote does not close, which the shell does not run, is read word by word."""
    found: list[str] = []
    # The word being read, None before it begins; whether any of it was quoted; and the end words
    # of the heredocs begun on this line.
    word: str | None = None
    quoted = False
    ends: list[tuple[str, bool]] = []
    # Each round reads what is left of the command to its end, unless it breaks off at the line
    # after which heredocs' text begins; then what follows that text is left for the next round.
    left: str | None = command
    while left is not None:
        reading, left = left, None
        for piece in PIECE.finditer(reading):
            # Each alternative of PIECE is a named group, so the piece has its kind. A kind is
            # told by membership rather than `==`, since an order comparison such as `>=` would
            # tell it from the kinds that come there too, and a mutant making it one would pass
            # every test.
            kind = str(piece.lastgroup)
            text = piece.group(kind)
            if kind in ("unclosed",):
                return [Operator(w) if w in OPERATORS else w for w in command.split()]
            if kind in ("single", "double", "escaped", "plain"):
                if kind in ("double",):
                    text = DOUBLE_ESCAPED.sub(lambda m: m.group(1) or "", text)
                word = (word or "") + text
                quoted = quoted or kind != "plain"
                continue
            if kind in ("join", "comment"):
                continue
            # Only a redirect's text begins with `<` or `>`.
            if text[0] in "<>" and word is not None and word.isdigit() and not quoted:
                word = None
            if word is not None:
                if found and sign(found[-1], set(HEREDOCS)):
                    ends.append((word, HEREDOCS[found[-1]]))
                found.append(word)
            word, quoted = None, False
            if kind in ("operator",):
                found.append(Operator(text))
            if text == "\n" and ends:
                left = reading[heredocs_end(reading, piece.end(), ends) :]
                ends = []
                break
    if word is not None:
        found.append(word)
    return found


def without_redirects(said: list[str]) -> list[str]:
    """The words of a statement, each redirect and its target left out."""
    pairs = zip([""] + said, said)
    return [w for before, w in pairs if not sign(w, REDIRECTS) and not sign(before, REDIRECTS)]


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
        if said[0] == "git":
            yield git_statement(here, said)


def git_statement(here: str | None, said: list[str]) -> tuple[str | None, list[str]]:
    """The folder a git statement run from here acts in, each `-C` moving it, and its words after
    git's options, the git command first."""
    rest = said[1:]
    while rest and rest[0].startswith("-"):
        if rest[0] == "-C" and rest[1:]:
            here = path(here, rest[1])
        rest = rest[2:] if rest[0] in GIT_VALUED else rest[1:]
    return here, rest


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


def paths(here: str, words: list[str]) -> list[str]:
    """The path each word names from the folder, those the words do not settle left out."""
    return [p for p in (path(here, w) for w in words) if p]


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
        found += [path(here, w) for before, w in zip([""] + said, said) if sign(before, WRITES)]
        # A redirect's target is not an argument of the command.
        plain = without_redirects(said)
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


def reads(command: str, cwd: str) -> list[tuple[str, Lines | None]]:
    """Each file the command prints what it reads of, by cat, head, tail, sed or grep, with the
    lines it reads of each, None where the command does not tell them, such as those grep finds; a
    file the words do not settle left out."""
    found = []
    for here, said, _ in statements(command, cwd):
        plain = without_redirects(said)
        if plain and plain[0] in READERS:
            lines, files = READERS[plain[0]](plain[1:])
            found += [(p, lines) for p in (path(here, f) for f in files) if p]
    return found


def split(args: list[str], valued: set[str]) -> tuple[list[tuple[str, str]], list[str]]:
    """A command's options, each with the word it takes, "" for none, and its operands: an option
    is a word begun with `-`, `-` alone among them as it names no file but the input, and every
    word after `--` is an operand."""
    options: list[tuple[str, str]] = []
    operands: list[str] = []
    rest = iter(args)
    for word in rest:
        if word in ("--",):
            operands += rest
        elif word.startswith("-"):
            options.append((word, next(rest, "") if word in valued else ""))
        else:
            operands.append(word)
    return options, operands


def counted(options: list[tuple[str, str]]) -> re.Match[str] | None:
    """The count of lines the last of head's or tail's options gives; None where it gives none,
    such as a count of bytes."""
    option, value = options[-1]
    return COUNT.fullmatch(value if option in ("-n",) else option)


def cat_lines(args: list[str]) -> tuple[Lines, list[str]]:
    """The lines cat prints of the files its arguments name, and the files: each whole."""
    return WHOLE, split(args, set())[1]


def head_lines(args: list[str]) -> tuple[Lines | None, list[str]]:
    """The lines head prints, the first, ten where no count is given, and the files."""
    options, operands = split(args, {"-n", "-c"})
    found = counted(options or UNCOUNTED)
    return ((1, int(found["count"])) if found else None), operands


def tail_lines(args: list[str]) -> tuple[Lines | None, list[str]]:
    """The lines tail prints, the last, ten where no count is given, or with `+` those from a line
    on, and the files."""
    options, operands = split(args, {"-n", "-c"})
    found = counted(options or UNCOUNTED)
    if not found:
        return None, operands
    count = int(found["count"])
    return ((count, None) if found["on"] else (-count, None)), operands


def sed_lines(args: list[str]) -> tuple[Lines | None, list[str]]:
    """The lines sed prints, every line but with -n, then those its script prints by number, and
    the files; its script is what -e gives, one line each, or else its first operand."""
    options, operands = split(args, {"-e", "-f"})
    scripts = [value for option, value in options if option in ("-e",)]
    if not scripts:
        scripts, operands = operands[:1], operands[1:]
    if ("-n", "") not in options:
        return WHOLE, operands
    found = SED_LINES.fullmatch("\n".join(scripts))
    if not found:
        return None, operands
    last = found["last"] or found["first"]
    return (int(found["first"]), None if last in ("$",) else int(last)), operands


def grep_lines(args: list[str]) -> tuple[Lines | None, list[str]]:
    """The lines grep prints, those its pattern finds, which it does not tell, and the files; its
    pattern is given by -e or -f, or is its first operand."""
    options, operands = split(args, {"-e", "-f", "-m", "-A", "-B", "-C"})
    given = any(option in ("-e", "-f") for option, _ in options)
    return None, operands if given else operands[1:]


# The commands that print what they read of the files they name, each with how it reads them.
READERS = {
    "cat": cat_lines,
    "head": head_lines,
    "tail": tail_lines,
    "sed": sed_lines,
    "grep": grep_lines,
}
