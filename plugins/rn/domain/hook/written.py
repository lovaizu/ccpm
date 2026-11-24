"""Decides whether a Bash command writes a run's design tree, as the hook keeps each write to it to
the pruner: a redirection or `tee` onto the tree, an in-place edit, a copy or a move onto it, a
command that sets it back, and an interpreter whose code names it, but where the hook can tell
that the command only reads it, and a run of rn's own scripts, which write it by design. Where the
hook can't tell that a command that names the tree only reads it, it takes the command as a
write, and says so."""

from __future__ import annotations

import os
import re
from collections.abc import Callable
from typing import NamedTuple

from hook.shell import Command, commands, program, start
from hook.write import TREE, is_tree


class Written(NamedTuple):
    """A write to a run's design tree: the tree as the command names it, or its file's name where
    only an interpreter's code names it; and whether the hook is sure of the write, False where it
    can't tell that the command only reads the tree."""

    tree: str
    sure: bool


def written(command: str, cwd: str, plugin_root: str) -> Written | None:
    """The write to a run's design tree that the Bash command makes, or None where it makes none.

    Takes: the command, as Claude Code gives a Bash call's; the folder it runs in, against which a
    path from the current folder is read; and rn's folder, whose `scripts/*.py` the command may
    run.
    Gives: None where the command doesn't hold `design-tree.json`; else, for the first simple
    command that writes a path that `hook.write.is_tree` takes as a run's tree, a Written that is
    sure, by a redirection that writes onto it; by `tee`, `mv`, `rm`, `unlink`, `truncate`,
    `shred`, or `touch` given it; by `cp`, `install`, `ln`, `rsync`, or `scp` given it last; by
    `sed`, `perl`, or `ruby` with an in-place option, `awk` with `-i inplace`, `sort -o`, or
    `dd of=` onto it. A Written that isn't sure where the hook can't tell that it only reads: a
    program other than those and the readers given it; git but for `show`, `diff`, `log`,
    `status`, `blame`, `ls-files`, `cat-file`, `grep`, `add`, and `rev-parse`; find with an
    action that runs or deletes; a writer fed by xargs; a write onto a path held in a variable, or
    onto `design-tree.json` once a command before changed the folder; an interpreter whose code
    names `design-tree.json` and may write, by a word that writes or a mode other than `r`; and a
    command the shell can't read. A shell's command by `-c` or a heredoc is judged as a command of
    its own. A run of a script in rn's `scripts` folder by Python passes, its redirections judged
    as any other's. None for each other command, such as one that only reads the tree.
    Changes: nothing.
    Refuses: nothing.
    """
    if TREE not in command:
        return None
    found = commands(command)
    if found is None:
        return Written(TREE, False)
    moved = False
    for each in found:
        verdict = _of(each, _Place(cwd, plugin_root, moved))
        if verdict is not None:
            return verdict
        moved = moved or _moves(each)
    return None


class _Place(NamedTuple):
    """What a simple command is read against: the folder the call runs in, rn's folder, and
    whether a command before it changed the folder."""

    cwd: str
    root: str
    moved: bool


# The programs that change the current folder.
_MOVES = ("cd", "pushd", "popd")
# The shells, whose command by -c or a heredoc is a command of its own.
_SHELLS = ("sh", "bash", "zsh", "dash")
# Python under its names, which runs rn's scripts.
_PYTHON = re.compile(r"python[0-9.]*(\.exe)?|py(\.exe)?")
# The interpreters, whose code by an option such as -c, a heredoc, or a here-string may name the
# tree: Python under its names, Node.js, Ruby, and Perl.
_INTERPRETER = re.compile(r"python[0-9.]*(\.exe)?|py(\.exe)?|node|ruby|perl")
_CODE_OPTIONS = ("-c", "-e", "-E")
# A word of code that writes, removes, or runs what may: `write`, as in write_text or
# writeFileSync, among them.
_WRITES = re.compile(
    r"write|dump|replace|rename|remove|unlink|truncate|rmtree|shutil|copy|move|system|"
    r"subprocess|popen|exec|eval|chmod|touch|mkdir|symlink|mode\s*="
)
# A string literal of code, whose words, such as a path's folders, are no code.
_LITERAL = re.compile(r"'[^'\n]*'|\"[^\"\n]*\"")
# A file's mode as a literal that writes, such as 'w', "a", 'r+', or 'xb'.
_MODE = re.compile(r"""['"][rbt]*[wax+][rwaxbt+]*['"]""")
# A call of open whose second argument is anything but the literal mode 'r', 'rb', or 'rt'.
_OPENED = re.compile(r"""open\((?:[^(),]|\([^()]*\))*,(?!\s*['"]r[bt]?['"]\s*[,)])""")
# The subcommands of git that only read a file they name, or stage it.
_GIT_READS = ("show", "diff", "log", "status", "blame", "ls-files", "cat-file", "grep", "add")
_GIT_READS += ("rev-parse",)
# git's options that take the next word as their value.
_GIT_VALUES = ("-C", "-c", "--git-dir", "--work-tree")
# find's actions that run a program or delete.
_FIND_ACTS = ("-exec", "-execdir", "-ok", "-okdir", "-delete", "-fprint", "-fprintf", "-fls")
# The readers, which only read and print what they're given.
_READERS = (
    "cat",
    "head",
    "tail",
    "less",
    "more",
    "grep",
    "egrep",
    "fgrep",
    "rg",
    "jq",
    "wc",
    "diff",
    "cmp",
    "file",
    "stat",
    "ls",
    "echo",
    "printf",
    "test",
    "[",
    "md5sum",
    "sha1sum",
    "sha256sum",
    "shasum",
)

# Whether a program writes a file of its words, from its words and which of them is the tree:
# True where it writes, False where it only reads, and None where the hook can't tell.
_Verdict = Callable[[list[str], Callable[[str], bool]], "bool | None"]


def _of(command: Command, place: _Place) -> Written | None:
    """The write to the tree that the simple command makes."""
    return _redirected(command, place) or _by_words(command, place)


def _by_words(command: Command, place: _Place) -> Written | None:
    """The write to the tree that the simple command's program makes, by its words or its code."""
    at = start(command.words)
    words = command.words[at:]
    if not words:
        return None
    name, args = program(words[0]), words[1:]
    if _runs_rn(name, args, place):
        return None
    if name in _SHELLS:
        return _inner(command, args, place)
    code = _code(name, args, command)
    if TREE in code:
        return None if _only_loads(code) else Written(TREE, False)
    return _by_args(name, args, "xargs" in command.words[:at], place)


def _by_args(name: str, args: list[str], fed: bool, place: _Place) -> Written | None:
    """The write to the tree that the program of the name makes on its arguments, fed them by
    xargs or not."""
    trees = [each for each in args if _sure(each, place) or _maybe(each, place)]
    if not trees:
        unseen = (fed and name not in _READERS) or _finds_and_acts(name, args)
        return Written(TREE, False) if unseen else None
    verdict = _VERDICTS.get(name, _unknown)(args, lambda word: word in trees)
    if verdict is False:
        return None
    named = trees[-1] if name in _COPIES else trees[0]
    # The path that an operand such as dd's `of=` gives.
    path = re.sub(r"^[a-z]+=", "", named)
    return Written(path, bool(verdict) and _sure(named, place))


def _redirected(command: Command, place: _Place) -> Written | None:
    """The write to the tree that a redirection of the command makes."""
    for operator, target in command.redirections:
        if ">" not in operator:
            continue
        if _sure(target, place):
            return Written(target, True)
        if _maybe(target, place):
            return Written(target, False)
    return None


def _moves(command: Command) -> bool:
    """Whether the simple command changes the current folder."""
    at = start(command.words)
    return at < len(command.words) and program(command.words[at]) in _MOVES


def _sure(word: str, place: _Place) -> bool:
    """Whether the word is a path of a run's design tree: absolute, or from the call's folder
    where no command before changed it."""
    absolute = word.startswith(("/", "\\")) or bool(re.match(r"[A-Za-z]:[\\/]", word))
    return (absolute or not place.moved) and is_tree(os.path.join(place.cwd, word))


def _maybe(word: str, place: _Place) -> bool:
    """Whether the word may be the tree, where the hook can't tell: a path held in a variable, or
    one that names the tree's file once the folder changed or by a pattern."""
    named = re.split(r"[\\/]", word)[-1] == TREE or is_tree(word)
    return "$" in word or (named and (place.moved or any(each in word for each in "*?[")))


def _runs_rn(name: str, args: list[str], place: _Place) -> bool:
    """Whether the command runs a script of rn's `scripts` folder by Python."""
    if not _PYTHON.fullmatch(name):
        return False
    script = next((each for each in args if not each.startswith("-")), None)
    if script is None or any(each in ("-c", "-m") for each in args[: args.index(script)]):
        return False
    folder = _parts(os.path.dirname(os.path.join(place.cwd, script)))
    return script.endswith(".py") and folder == [*_parts(place.root), "scripts"]


def _parts(path: str) -> list[str]:
    """The folders of a path, by `/` or `\\`, without empty ones or `.`."""
    return [each for each in re.split(r"[\\/]", os.path.normpath(path)) if each not in ("", ".")]


def _inner(command: Command, args: list[str], place: _Place) -> Written | None:
    """The write to the tree that a shell's command by -c, a heredoc, or a here-string makes, or
    that the shell makes running a script given the tree."""
    code = [args[i + 1] for i, each in enumerate(args[:-1]) if each == "-c"] + _stdin(command)
    for each in code:
        found = written(each, place.cwd, place.root)
        if found is not None:
            return found
    trees = [each for each in args if _sure(each, place) or _maybe(each, place)]
    return Written(trees[0], False) if trees and not code else None


def _code(name: str, args: list[str], command: Command) -> str:
    """The code that an interpreter runs from its words and its stdin, or none for another
    program."""
    if not _INTERPRETER.fullmatch(name):
        return ""
    given = [args[i + 1] for i, each in enumerate(args[:-1]) if each in _CODE_OPTIONS]
    return "\n".join(given + _stdin(command))


def _stdin(command: Command) -> list[str]:
    """The text that the command takes on stdin: each heredoc's body, and each here-string."""
    strings = [target for operator, target in command.redirections if operator == "<<<"]
    return command.heredocs + strings


def _only_loads(code: str) -> bool:
    """Whether code that names the tree can be told to only read it: no word that writes outside
    its string literals, no mode that writes, and no call of open with another mode."""
    words = _LITERAL.sub('""', code)
    return not (_WRITES.search(words) or _MODE.search(code) or _OPENED.search(code))


def _finds_and_acts(name: str, args: list[str]) -> bool:
    """Whether the command is find with an action that runs or deletes."""
    return name == "find" and any(each in _FIND_ACTS for each in args)


def _reads(args: list[str], tree: Callable[[str], bool]) -> bool | None:
    return False


def _writes(args: list[str], tree: Callable[[str], bool]) -> bool | None:
    return True


def _unknown(args: list[str], tree: Callable[[str], bool]) -> bool | None:
    return None


def _copies(args: list[str], tree: Callable[[str], bool]) -> bool | None:
    """A copy writes the tree where it's the last path given."""
    paths = [each for each in args if not each.startswith("-")]
    return tree(paths[-1])


def _in_place(args: list[str], tree: Callable[[str], bool]) -> bool | None:
    """sed, perl, or ruby writes its file with an in-place option, such as -i, -i.bak, -pi, or
    --in-place."""
    return any(re.match(r"-[A-Za-z]*i|--in-place", each) for each in args)


def _awk(args: list[str], tree: Callable[[str], bool]) -> bool | None:
    """awk writes its file with gawk's in-place extension."""
    pairs = zip(args, [*args[1:], ""])
    return any(
        pair == ("-i", "inplace") or pair[0] in ("-iinplace", "--include=inplace") for pair in pairs
    )


def _sort(args: list[str], tree: Callable[[str], bool]) -> bool | None:
    """sort writes the file given to -o or --output."""
    given = [b for a, b in zip(args, args[1:]) if a == "-o"]
    given += [each[2:] for each in args if each.startswith("-o") and len(each) > 2]
    given += [each.split("=", 1)[1] for each in args if each.startswith("--output=")]
    return any(tree(each) for each in given)


def _dd(args: list[str], tree: Callable[[str], bool]) -> bool | None:
    """dd writes the file given to of=."""
    return any(each.startswith("of=") and tree(each) for each in args)


def _git(args: list[str], tree: Callable[[str], bool]) -> bool | None:
    """git only reads, or stages, by the subcommands of _GIT_READS; the hook can't tell of
    another."""
    at = 0
    while at < len(args) and args[at].startswith("-"):
        at += 2 if args[at] in _GIT_VALUES else 1
    return False if at < len(args) and args[at] in _GIT_READS else None


def _find(args: list[str], tree: Callable[[str], bool]) -> bool | None:
    """find only lists, but where an action runs or deletes."""
    return None if _finds_and_acts("find", args) else False


_COPIES = ("cp", "install", "ln", "rsync", "scp")
_VERDICTS: dict[str, _Verdict] = {
    **dict.fromkeys(_READERS, _reads),
    **dict.fromkeys(("tee", "mv", "rm", "unlink", "truncate", "shred", "touch"), _writes),
    **dict.fromkeys(_COPIES, _copies),
    **dict.fromkeys(("sed", "perl", "ruby"), _in_place),
    "awk": _awk,
    "gawk": _awk,
    "sort": _sort,
    "dd": _dd,
    "git": _git,
    "find": _find,
}
