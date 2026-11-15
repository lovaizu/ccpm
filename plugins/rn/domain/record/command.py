"""Decides record.py's command line: what each of its commands, add and check, takes, and what it
prints with the exit code by which a role reads its result and the guard passes an end."""

from __future__ import annotations

from collections.abc import Sequence


def main(argv: Sequence[str], cwd: str, plugin_root: str) -> tuple[int, str, str]:
    """Runs one command of record.py.

    Takes: the command line after `record.py`, the folder it runs in, and rn's folder.
    Gives, as the exit code, standard output, and standard error:
    - `add <record> <of> <id> <gave>`: 0, once `form.add` adds the step `<id>` of the prompt `<of>`,
      such as `generator 3`, or the practice `<id>` of the best practice `<of>`, such as
      `code N6.2`.
    - `check <role> <result> [<record>]`: 0, where `check.check` finds nothing lacking; 1, with
      each thing lacking, one to a line, said so that the role carries it out.
    - 1, with what's wrong, where an input is out of form, as fault.Wrong says; 2, with why, where
      it can't check, or with the usage.
    Changes: what `form.add` and `check.check` change.
    Refuses: as Gives says, by its exit code.
    Carries: S1 `G->>R: records each step and practice as it takes it (Record)`, `GD->>R: checks its
    record, its result, and the deliverable`, and `R-->>GD`.
    """
    raise NotImplementedError("record.command.main")
