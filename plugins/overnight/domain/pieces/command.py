"""pieces.py's command line, and the lines it prints of how each piece stands."""

from __future__ import annotations

# The exit code, standard output, and standard error of a command.
Answer = tuple[int, str, str]

USAGE = """\
usage: pieces.py report
"""


def main(argv: list[str], cwd: str) -> Answer:
    """The exit code, stdout, and stderr of `pieces.py` with the arguments, from the folder `cwd`.

    Takes: `report`, from the repository's root, the folder that the session works in.
    Gives: 0 with a table of each piece's number, state, branch, waits, and last words, and a line
    of how many of the pieces the usage limit, a wait for an answer, or the session closing
    stopped, as the README's walkthrough shows; 0 with `No pieces yet` where no piece is recorded.
    Changes: nothing.
    Refuses: 2 with the usage where the arguments aren't `report`, and 2 with the file and what's
    wrong where a record leaves its layout.
    """
    raise NotImplementedError("pieces.command.main")
