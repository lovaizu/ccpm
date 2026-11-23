"""Decides whether a Bash command deletes, as a maker that runs `rm` on a variable path stops the
run on a permission prompt: a command word `rm`, `rmdir`, or `unlink`, or `find` with `-delete` or
with `-exec` of one of those, at any place in a chain, a pipeline, a list, or a subshell."""

from __future__ import annotations

import re
import shlex

# The programs that delete what they're given.
DELETERS = ("rm", "rmdir", "unlink")

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

# find's actions that run a program on each file found.
FIND_RUNS = ("-exec", "-execdir", "-ok", "-okdir")

# A shell variable set before the command word, as in `LC_ALL=C rm`.
ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")

# What ends one command and starts the next: `;`, `&`, `|`, and the brackets of a subshell, alone
# or together, as in `&&` or `$(`.
SEPARATOR = re.compile(r"[;&|()]+")


def deletes(command: str) -> bool:
    """Whether the command deletes. A command that the shell couldn't read either, such as one
    whose quote never closes, deletes nothing."""
    # A new line and a backquote each start a command, as `;` does.
    lexer = shlex.shlex(
        command.replace("\n", ";").replace("`", ";"), posix=True, punctuation_chars=True
    )
    lexer.whitespace_split = True
    try:
        tokens = list(lexer)
    except ValueError:
        return False
    return any(_runs_delete(each) for each in _commands(tokens))


def _commands(tokens: list[str]) -> list[list[str]]:
    """The words of each command among the tokens, without its redirections."""
    commands: list[list[str]] = [[]]
    skip = False
    for token in tokens:
        if SEPARATOR.fullmatch(token):
            commands.append([])
        elif "<" in token or ">" in token:
            skip = True
        elif skip:
            skip = False
        else:
            commands[-1].append(token)
    return commands


def _runs_delete(words: list[str]) -> bool:
    """Whether the command of the words deletes."""
    at = 0
    while at < len(words) and _leads(words[at]):
        at += 1
    if at == len(words):
        return False
    name = _program(words[at])
    if name in DELETERS:
        return True
    rest = words[at + 1 :]
    if name != "find":
        return False
    runs = [rest[i + 1] for i, word in enumerate(rest[:-1]) if word in FIND_RUNS]
    return "-delete" in rest or any(_program(each) in DELETERS for each in runs)


def _leads(word: str) -> bool:
    """Whether the word comes before the command word: a variable set, a word that runs the
    command, or an option of such a word."""
    return bool(ASSIGNMENT.match(word)) or word in LEADS or word.startswith("-")


def _program(word: str) -> str:
    """The program's name of a command word, without its folder, as in `/bin/rm`."""
    return re.split(r"[\\/]", word)[-1]
