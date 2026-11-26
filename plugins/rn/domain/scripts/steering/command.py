"""Decides steering's command line: its subcommands, what each takes and prints, and the exit code
by which whoever ran it reads its result."""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Sequence
from typing import Any

import form
from fault import Answer, CantRun, Wrong, answered
from host import Host, checked
from place import RunPlace, of_folder

from steering import due, record

USAGE = """\
usage: steering commit <run>
       steering step <run> <number> open|trying|done
       steering deliverable <run> <path> open|done
       steering due <run>
"""


def main(argv: Sequence[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    """The exit code, stdout, and stderr of `steering` with the arguments, from the folder `cwd`,
    with rn's folder at `plugin_root`, and git reached through `host`.

    - `commit <run>`: takes the pruner's result, `<run>/pruner.json` in the form of
      domain/schemas/pruner.schema.json, into the steering as `record.taken_in` makes it, writes
      and commits the steering alone as `rn: <the result's message>`, removes the result, which no
      commit holds, and gives 0 printing the commit's hash, then what's due, as `due` prints it.
    - `step <run> <number> <status>`: marks the step as `record.step_marked` does, commits the
      steering alone as `rn: <its words>: <status>`, and gives 0 printing what's due.
    - `deliverable <run> <path> <status>`: marks the deliverable as `record.deliverable_marked`
      does, commits the steering alone as `rn: <path>: <status>`, and gives 0 printing what's due.
    - `due <run>`: gives 0 printing each line that `due.due` gives, a line each.

    `<run>` is the run's folder, as `place.of_folder` takes it. 1 with `steering: <what's wrong>`,
    changing nothing, where the input is Wrong: a result or a steering that's missing, isn't JSON,
    or leaves its schema, naming each place, or a mark that `record` refuses. 2 with what stopped
    it where it CantRun, such as git refusing the commit, with what git said; 2 with the usage where
    the arguments are other than these.
    """
    if not argv or argv[0] not in _SUBCOMMANDS or len(argv) != _SUBCOMMANDS[argv[0]][1]:
        return 2, "", USAGE
    subcommand = _SUBCOMMANDS[argv[0]][0]
    schemas = os.path.join(plugin_root, "domain", "schemas")
    return answered(
        "steering", lambda: subcommand(of_folder(cwd, argv[1]), list(argv[2:]), schemas, host)
    )


def _commit(run: RunPlace, given: list[str], schemas: str, host: Host) -> Answer:
    result = _read(run.pruner, os.path.join(schemas, "pruner.schema.json"), "the pruner's result")
    before = (
        _read(run.steering, os.path.join(schemas, "steering.schema.json"), "the steering")
        if os.path.isfile(run.steering)
        else None
    )
    steering = record.taken_in(before, result)
    hash_ = _committed(run, steering, result["message"], host)
    os.remove(run.pruner)
    return 0, f"{hash_}\n" + _lines(due.due(steering)), ""


def _step(run: RunPlace, given: list[str], schemas: str, host: Host) -> Answer:
    if not given[0].isdigit():
        raise Wrong(f"{given[0]!r} isn't a step's number; give its number from 1")
    steering, words = record.step_marked(_steering(run, schemas), int(given[0]), given[1])
    _committed(run, steering, f"{words}: {given[1]}", host)
    return 0, _lines(due.due(steering)), ""


def _deliverable(run: RunPlace, given: list[str], schemas: str, host: Host) -> Answer:
    steering = record.deliverable_marked(_steering(run, schemas), given[0], given[1])
    _committed(run, steering, f"{given[0]}: {given[1]}", host)
    return 0, _lines(due.due(steering)), ""


def _due(run: RunPlace, given: list[str], schemas: str, host: Host) -> Answer:
    return 0, _lines(due.due(_steering(run, schemas))), ""


def _steering(run: RunPlace, schemas: str) -> dict[str, Any]:
    return _read(run.steering, os.path.join(schemas, "steering.schema.json"), "the steering")


def _read(path: str, schema: str, what: str) -> dict[str, Any]:
    try:
        with open(path, encoding="utf-8") as f:
            value = json.load(f)
    except FileNotFoundError:
        raise Wrong(f"{path}: no {what} lies there") from None
    except json.JSONDecodeError as error:
        raise Wrong(f"{path}: {what} isn't JSON: {error}") from None
    found = form.faults(value, schema)
    if found:
        raise Wrong(
            f"{path}: {what} leaves its schema, {os.path.basename(schema)}: " + "; ".join(found)
        )
    return value


def _committed(run: RunPlace, steering: dict[str, Any], message: str, host: Host) -> str:
    with open(run.steering, "w", encoding="utf-8") as f:
        json.dump(steering, f, indent=2, ensure_ascii=False)
        f.write("\n")
    path = os.path.relpath(run.steering, run.worktree)
    checked(host, ["git", "add", "--", path], run.worktree, CantRun, "git can't stage the steering")
    checked(
        host,
        ["git", "commit", "-q", "-m", f"rn: {message}", "--", path],
        run.worktree,
        CantRun,
        "git can't commit the steering",
    )
    return checked(
        host, ["git", "rev-parse", "HEAD"], run.worktree, CantRun, "git can't name the commit"
    ).out.strip()


def _lines(lines: list[str]) -> str:
    return "".join(f"{each}\n" for each in lines)


# Each subcommand, by its name, with the number of arguments it takes, its name among them.
_SUBCOMMANDS: dict[str, tuple[Callable[[RunPlace, list[str], str, Host], Answer], int]] = {
    "commit": (_commit, 2),
    "step": (_step, 4),
    "deliverable": (_deliverable, 4),
    "due": (_due, 2),
}
