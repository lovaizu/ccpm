"""Decides whether a Bash command surely writes a run's design tree, as the hook keeps each write
to it to the pruner: a redirection or `tee` onto the tree, an in-place edit, a copy or a move onto
it, and git setting it back or removing it. Each other command passes, as a refused read stops the
run, which costs more than the rare write that the hook can't be sure of, and rn's scripts check
the tree's form before each commit. A run of rn's own scripts is among those that pass, as they
write the tree by design."""

from __future__ import annotations

import os
import re
from collections.abc import Callable
from typing import NamedTuple

from hook.shell import Command, commands, program, start
from hook.write import TREE, is_tree


def written(command: str, cwd: str) -> str | None:
    """The run's design tree that the Bash command surely writes, as the command names it, or None
    where it writes none that the hook is sure of.

    Takes: the command, as Claude Code gives a Bash call's; and the folder it runs in, against
    which a path from the current folder is read.
    Gives: for the first simple command that writes a path that `hook.write.is_tree` takes as a
    run's tree, absolute or from the call's folder before any command changed it, that path: by a
    redirection that writes onto it; by `tee`, `mv`, `rm`, `unlink`, `truncate`, `shred`, or
    `touch` given it; by `cp`, `install`, `ln`, `rsync`, or `scp` given it last; by `sed`,
    `perl`, or `ruby` with an in-place option, `awk` with `-i inplace`, `sort -o`, or `dd of=`
    onto it; by git's `checkout`, `restore`, `stash`, `rm`, or `mv` given it. A shell's command by
    `-c`, a heredoc, or a here-string is judged as a command of its own. None for each other
    command: one that doesn't hold `design-tree.json`, one that only reads the tree, a run of rn's
    scripts or of any other program the hook doesn't know, an interpreter's code, a path held in a
    variable or found by a pattern, find, xargs, and a command the shell can't read among them.
    Changes: nothing.
    Refuses: nothing.
    """
    if TREE not in command:
        return None
    moved = False
    for each in commands(command) or []:
        tree = _of(each, _Place(cwd, moved))
        if tree is not None:
            return tree
        moved = moved or _moves(each)
    return None


class _Place(NamedTuple):
    """What a simple command is read against: the folder the call runs in, and whether a command
    before it changed the folder."""

    cwd: str
    moved: bool


# The programs that change the current folder.
_MOVES = ("cd", "pushd", "popd")
# The shells, whose command by -c or a heredoc is a command of its own.
_SHELLS = ("sh", "bash", "zsh", "dash")
# The subcommands of git that write a file they name: set it back, stash it, or remove or move it.
_GIT_WRITES = ("checkout", "restore", "stash", "rm", "mv")
# git's options that take the next word as their value.
_GIT_VALUES = ("-C", "-c", "--git-dir", "--work-tree")

# Whether a program surely writes a file of its words, from its words and which of them is the
# tree.
_Verdict = Callable[[list[str], Callable[[str], bool]], bool]


def _of(command: Command, place: _Place) -> str | None:
    """The tree that the simple command surely writes."""
    return _redirected(command, place) or _by_words(command, place)


def _by_words(command: Command, place: _Place) -> str | None:
    """The tree that the simple command's program surely writes, by its words."""
    words = command.words[start(command.words) :]
    if not words:
        return None
    name, args = program(words[0]), words[1:]
    if name in _SHELLS:
        return _inner(command, args, place)
    trees = [each for each in args if _sure(each, place)]
    if not trees or name not in _VERDICTS or not _VERDICTS[name](args, trees.__contains__):
        return None
    named = trees[-1] if name in _COPIES else trees[0]
    # The path that an operand such as dd's `of=` gives.
    return re.sub(r"^[a-z]+=", "", named)


def _redirected(command: Command, place: _Place) -> str | None:
    """The tree that a redirection of the command writes onto."""
    return next(
        (
            target
            for operator, target in command.redirections
            if ">" in operator and _sure(target, place)
        ),
        None,
    )


def _moves(command: Command) -> bool:
    """Whether the simple command changes the current folder."""
    at = start(command.words)
    return at < len(command.words) and program(command.words[at]) in _MOVES


def _sure(word: str, place: _Place) -> bool:
    """Whether the word is a path of a run's design tree: absolute, or from the call's folder
    where no command before changed it."""
    absolute = word.startswith(("/", "\\")) or bool(re.match(r"[A-Za-z]:[\\/]", word))
    return (absolute or not place.moved) and is_tree(os.path.join(place.cwd, word))


def _inner(command: Command, args: list[str], place: _Place) -> str | None:
    """The tree that a shell's command by -c, a heredoc, or a here-string surely writes."""
    code = [args[i + 1] for i, each in enumerate(args[:-1]) if each == "-c"]
    code += command.heredocs + [
        target for operator, target in command.redirections if operator == "<<<"
    ]
    return next((found for found in (written(each, place.cwd) for each in code) if found), None)


def _writes(args: list[str], tree: Callable[[str], bool]) -> bool:
    return True


def _copies(args: list[str], tree: Callable[[str], bool]) -> bool:
    """A copy writes the tree where it's the last path given."""
    paths = [each for each in args if not each.startswith("-")]
    return tree(paths[-1])


def _in_place(args: list[str], tree: Callable[[str], bool]) -> bool:
    """sed, perl, or ruby writes its file with an in-place option, such as -i, -i.bak, -pi, or
    --in-place."""
    return any(re.match(r"-[A-Za-z]*i|--in-place", each) for each in args)


def _awk(args: list[str], tree: Callable[[str], bool]) -> bool:
    """awk writes its file with gawk's in-place extension."""
    pairs = zip(args, [*args[1:], ""])
    return any(
        pair == ("-i", "inplace") or pair[0] in ("-iinplace", "--include=inplace") for pair in pairs
    )


def _sort(args: list[str], tree: Callable[[str], bool]) -> bool:
    """sort writes the file given to -o or --output."""
    given = [b for a, b in zip(args, args[1:]) if a == "-o"]
    given += [each[2:] for each in args if each.startswith("-o") and len(each) > 2]
    given += [each.split("=", 1)[1] for each in args if each.startswith("--output=")]
    return any(tree(each) for each in given)


def _dd(args: list[str], tree: Callable[[str], bool]) -> bool:
    """dd writes the file given to of=."""
    return any(each.startswith("of=") and tree(each) for each in args)


def _git(args: list[str], tree: Callable[[str], bool]) -> bool:
    """git writes the file it names by the subcommands of _GIT_WRITES."""
    at = 0
    while at < len(args) and args[at].startswith("-"):
        at += 2 if args[at] in _GIT_VALUES else 1
    return at < len(args) and args[at] in _GIT_WRITES


_COPIES = ("cp", "install", "ln", "rsync", "scp")
_VERDICTS: dict[str, _Verdict] = {
    **dict.fromkeys(("tee", "mv", "rm", "unlink", "truncate", "shred", "touch"), _writes),
    **dict.fromkeys(_COPIES, _copies),
    **dict.fromkeys(("sed", "perl", "ruby"), _in_place),
    "awk": _awk,
    "gawk": _awk,
    "sort": _sort,
    "dd": _dd,
    "git": _git,
}
