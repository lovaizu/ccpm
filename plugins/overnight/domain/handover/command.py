"""handover.py's command line: what the AI hands on, and the lines it prints of the piece handed
over or of what to add."""

from __future__ import annotations

# The exit code, standard output, and standard error of a command.
Answer = tuple[int, str, str]

USAGE = """\
usage: handover.py <tools>, with the prompt on standard input
"""


def main(argv: list[str], stdin: str, cwd: str) -> Answer:
    """The exit code, stdout, and stderr of `handover.py` with the arguments and standard input,
    from the folder `cwd`.

    Takes: as its one argument, each tool as the user wrote them, such as `Read, Edit,
    Bash(pytest:*)`; the prompt on standard input; from the repository's root, the folder that
    the session works in.
    Gives: 0 with the piece's number, folder, branch, and tools, and how to see how it goes, as
    the README's walkthrough shows.
    Changes: what `hand.hand_over` changes.
    Refuses: 2 with what to add where the prompt is empty or no tool is named; 2 with git's words
    where git can't make the worktree; 2 with the system's words where the runner can't start.
    """
    raise NotImplementedError("handover.command.main")
