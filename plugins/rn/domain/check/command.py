"""Decides check.py's command line: what it takes, what it prints, and the exit code by which the
role that runs it reads its result."""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from typing import Any

from fault import Answer, CantRun, Wrong
from rounds.files import ROLES

from check import form, result

USAGE = """\
usage: check.py <role> <cut>
"""


def main(argv: Sequence[str], cwd: str, plugin_root: str) -> Answer:
    """The exit code, stdout, and stderr of `check.py` with the arguments, from the folder `cwd`,
    with rn's folder at `plugin_root`.

    `<role> <cut>`, the role's Cut by its path from `cwd`: 0 printing nothing where the Cut holds
    its schema and `check.result.faults` finds no fault in the role's result beside it, with the
    run's worktree that the Cut's paths give and `cwd`; 1 with each
    fault a line, or, where the role wrote no result, the path where it writes one. 1 with
    `check.py: <what's wrong>` where the role's result is Wrong, as one that can't be read as JSON,
    saying how to mend it. 2 with `check.py: <what it couldn't check and why>` where it CantRun: a
    role of neither, a Cut that can't be read as JSON or leaves its schema, or a schema that can't
    be read, as the role reads 2 as a check that couldn't check; 2 with the usage where the
    arguments are other than a role and a Cut.
    """
    if len(argv) != 2:
        return 2, "", USAGE
    try:
        found = _faults(argv[0], argv[1], cwd, plugin_root)
    except Wrong as wrong:
        return 1, "", f"check.py: {wrong}\n"
    except CantRun as couldnt:
        return 2, "", f"check.py: {couldnt}\n"
    return (1 if found else 0), "".join(f"{each}\n" for each in found), ""


def _faults(role: str, cut_path: str, cwd: str, plugin_root: str) -> list[str]:
    """Each fault of the role's result against its Cut, or the path where it writes one."""
    if role not in ROLES:
        raise CantRun(
            f"couldn't check a result of {role!r}, as it checks only the generator's and the"
            " evaluator's"
        )
    unchecked = f"couldn't check the {role}'s result, as its Cut {cut_path}"
    try:
        cut = _read(os.path.join(cwd, cut_path))
    except (OSError, ValueError) as error:
        raise CantRun(f"{unchecked} can't be read as JSON: {error}") from None
    schema = os.path.join(plugin_root, "domain", "schemas", f"{role}-cut.schema.json")
    found = form.faults(cut, schema)
    if found:
        raise CantRun(f"{unchecked} leaves the form of a {role}'s Cut at {found[0]}")
    written = os.path.join(cut["round"], f"{role}.json")
    if not os.path.isfile(os.path.join(cwd, written)):
        return [f"{written}: no result is written there; write it before you end"]
    try:
        given = _read(os.path.join(cwd, written))
    except (OSError, ValueError) as error:
        raise Wrong(f"{written}: can't be read as JSON: {error}") from None
    return result.faults(role, cut, given, os.path.join(cwd, cut["worktree"]), cwd)


def _read(path: str) -> Any:
    """The JSON of the file."""
    with open(path, encoding="utf-8") as file:
        return json.load(file)
