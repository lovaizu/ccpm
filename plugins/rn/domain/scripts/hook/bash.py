"""Decides whether a Bash command deletes, as a maker that runs `rm` on a variable path stops the
run on a permission prompt: a command word `rm`, `rmdir`, or `unlink`, or `find` with `-delete` or
with `-exec` of one of those, at any place in a chain, a pipeline, a list, a subshell, or a
heredoc's body."""

from __future__ import annotations

from hook.shell import commands, program, start

# The programs that delete what they're given.
DELETERS = ("rm", "rmdir", "unlink")

# find's actions that run a program on each file found.
FIND_RUNS = ("-exec", "-execdir", "-ok", "-okdir")


def deletes(command: str) -> bool:
    """Whether the command deletes. A command that the shell couldn't read either, such as one
    whose quote never closes, deletes nothing."""
    found = commands(command)
    if found is None:
        return False
    return any(
        _runs_delete(each.words) or any(deletes(body) for body in each.heredocs) for each in found
    )


def _runs_delete(words: list[str]) -> bool:
    """Whether the command of the words deletes."""
    at = start(words)
    if at == len(words):
        return False
    name = program(words[at])
    if name in DELETERS:
        return True
    rest = words[at + 1 :]
    if name != "find":
        return False
    runs = [rest[i + 1] for i, word in enumerate(rest[:-1]) if word in FIND_RUNS]
    return "-delete" in rest or any(program(each) in DELETERS for each in runs)
