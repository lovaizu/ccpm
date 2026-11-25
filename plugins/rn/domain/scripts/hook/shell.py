"""Decides how a Bash command reads as the shell would split it: each simple command at any place
in a chain, a pipeline, a list, or a subshell, with its words, its redirections, and the body of
each heredoc it takes, and which of its words is the command word."""

from __future__ import annotations

import re
import shlex
from typing import NamedTuple

# The words before a command word that run it, as `sudo rm` or `xargs rm` run rm, and the shell's
# words that a command follows, as in `do rm`. Each option after them is skipped too.
LEADS = (
    "sudo",
    "env",
    "command",
    "exec",
    "nohup",
    "time",
    "nice",
    "xargs",
    "builtin",
    "do",
    "then",
    "else",
    "if",
    "elif",
    "while",
    "until",
    "!",
    "{",
)

# A shell variable set before the command word, as in `LC_ALL=C rm`.
ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")

# What ends one command and starts the next: `;`, `&`, `|`, and the brackets of a subshell, alone
# or together, as in `&&` or `$(`.
SEPARATOR = re.compile(r"[;&|()]+")
# A redirection's operator, such as `>`, `>>`, `&>`, `>|`, `<`, or `<<`: a token of these signs
# alone that holds `<` or `>`.
REDIRECTION = re.compile(r"[<>&|]*[<>][<>&|]*")
# The operators of a heredoc, whose body follows on the lines after the command.
HEREDOCS = ("<<", "<<-")
# A heredoc's start on a line, its delimiter quoted or not, and not a here-string's `<<<`.
_HEREDOC = re.compile(r"(?<!<)<<(-?)(?!<)\s*(['\"]?)([^\s'\"<>;&|()]+)\2")


class Command(NamedTuple):
    """One simple command: its words, without its redirections; each redirection, its operator
    and the word after it, such as (`>`, `out.txt`) or (`<<<`, a here-string's text); and the body
    of each heredoc it takes, in order."""

    words: list[str]
    redirections: list[tuple[str, str]]
    heredocs: list[str]


def commands(text: str) -> list[Command] | None:
    """Each simple command of the Bash command, in order; None where the shell couldn't read it
    either, such as one whose quote never closes. A new line and a backquote each start a command,
    as `;` does, but for a heredoc's body, which goes to the command whose heredoc it is."""
    lines, bodies = _without_bodies(text)
    lexer = shlex.shlex(
        lines.replace("\n", ";").replace("`", ";"), posix=True, punctuation_chars=True
    )
    lexer.whitespace_split = True
    try:
        tokens = list(lexer)
    except ValueError:
        return None
    found = [Command([], [], [])]
    operator = None
    for token in tokens:
        if operator is not None:
            found[-1].redirections.append((operator, token))
            if operator in HEREDOCS and bodies:
                found[-1].heredocs.append(bodies.pop(0))
            operator = None
        elif REDIRECTION.fullmatch(token):
            operator = token
        elif SEPARATOR.fullmatch(token):
            found.append(Command([], [], []))
        else:
            found[-1].words.append(token)
    return found


def start(words: list[str]) -> int:
    """The place of the command word among a command's words: the first that isn't a variable
    set, a word that runs the command, or an option of such a word; the count of the words where
    each is one of those."""
    at = 0
    while at < len(words) and _leads(words[at]):
        at += 1
    return at


def program(word: str) -> str:
    """The program's name of a command word, without its folder, as in `/bin/rm`."""
    return re.split(r"[\\/]", word)[-1]


def _leads(word: str) -> bool:
    """Whether the word comes before the command word: a variable set, a word that runs the
    command, or an option of such a word."""
    return bool(ASSIGNMENT.match(word)) or word in LEADS or word.startswith("-")


def _without_bodies(text: str) -> tuple[str, list[str]]:
    """The command's lines without each heredoc's body, and each body, in order. A body runs from
    the line after its heredoc's start to the line that holds its delimiter alone, tabs before it
    left out where the operator is `<<-`, or to the end."""
    lines = text.split("\n")
    kept: list[str] = []
    bodies: list[str] = []
    at = 0
    while at < len(lines):
        kept.append(lines[at])
        starts = _HEREDOC.findall(lines[at])
        at += 1
        for dash, _, delimiter in starts:
            body: list[str] = []
            while at < len(lines) and (lines[at].lstrip("\t") if dash else lines[at]) != delimiter:
                body.append(lines[at])
                at += 1
            at += 1
            bodies.append("\n".join(body))
    return "\n".join(kept), bodies
