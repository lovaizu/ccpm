"""Decides record.py's command line: which command each call names, what it takes, what it prints,
and the exit code by which a role or the guard reads its result: 0 where it did what it names, 1
with what's wrong, and 2 with why it couldn't run, or with the usage."""

from __future__ import annotations

USAGE = """\
usage: record.py add <record> <of> <id> <gave>
       record.py check <role> <result> [<cut>]
"""


def main(argv: list[str], cwd: str, plugin_root: str) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of `record.py` with the arguments, from the folder `cwd`,
    with rn's folder at `plugin_root`:

    - `add <record> <of> <id> <gave>` adds the entry to the record; 1 where the ID is neither a
      step's number nor a practice's ID, or `gave` is empty.
    - `check <role> <result> [<cut>]` gives 0 where rn's check finds no fault in the role's end, 1
      with each fault, and 2 where it can't check.

    2 with the usage where the arguments are none of these."""
    raise NotImplementedError("command.main")
