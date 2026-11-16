"""Decides record.py's command line: what each of its commands, add and check, takes, and what it
prints with the exit code by which a role reads its result and the guard passes an end."""

from __future__ import annotations

import os
from collections.abc import Sequence

from fault import Wrong

from record import check, form

USAGE = """\
usage: record.py add <record> <of> <step or practice> <what it left or gave>
       record.py check <role> <result> [<record>]
"""


def main(argv: Sequence[str], cwd: str, plugin_root: str) -> tuple[int, str, str]:
    """Runs one command of record.py.

    Takes: the command line after `record.py`, the folder it runs in, and rn's folder.
    Gives, as the exit code, standard output, and standard error:
    - `add <record> <of> <id> <gave>`: 0, once `form.add` adds the step `<id>` of the prompt `<of>`,
      such as `generator 3`, or the practice `<id>` of the best practice `<of>`, such as
      `code N6.2`, `<record>` read from the folder it runs in.
    - `check <role> <result> [<record>]`: 0, where `check.check` finds nothing lacking; 1, with
      each thing lacking, one to a line on standard error, said so that the role carries it out.
    - 1, with what's wrong, where an input is out of form, as fault.Wrong says; 2, with the usage.
      A file it can't read stops it with its trace, which the guard holds the end by as well.
      Standard output stays empty, as the guard runs check.
    Changes: what `form.add` and `check.check` change.
    Refuses: as Gives says, by its exit code.
    Carries: S1 `G->>R: records each step and practice as it takes it (Record)`, `GD->>R: checks its
    record, its result, and the deliverable`, and `R-->>GD`.
    """
    command, args = (argv[0], list(argv[1:])) if argv else ("", [])
    if (command, len(args)) not in (("add", 4), ("check", 2), ("check", 3)):
        return 2, "", USAGE
    try:
        if command == "add":
            return _add(args, cwd)
        found = check.check(plugin_root, cwd, args[0], args[1], args[2] if args[2:] else None)
    except Wrong as e:
        return 1, "", f"record.py {command}: {e}\n"
    if not found:
        return 0, "", ""
    lead = f"rn's check: the end of {args[0]} lacks what follows; carry it out, then end again."
    return 1, "", "\n".join([lead, *found]) + "\n"


def _add(args: list[str], cwd: str) -> tuple[int, str, str]:
    record, of, named, gave = args
    step, practice = (int(named), None) if named.isdigit() else (None, named)
    form.add(os.path.join(cwd, record), form.Entry(of, step, practice, gave))
    return 0, "", ""
