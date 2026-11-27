"""Decides steering's command line: its subcommands, what each takes and prints, and the exit code
by which whoever ran it reads its result."""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Sequence
from typing import Any

import form
import push
from fault import Answer, Wrong, answered
from host import Host
from place import RunPlace, of_folder

from steering import due, record, start

USAGE = """\
usage: steering step <run> <number> open|trying|done
       steering start <run> <path>   (a Fix's problem in words on stdin)
       steering inspected <run>
       steering due <run>
"""


def main(
    argv: Sequence[str], cwd: str, plugin_root: str, host: Host, stdin: Callable[[], str]
) -> Answer:
    """The exit code, stdout, and stderr of `steering` with the arguments, from the folder `cwd`,
    with rn's folder at `plugin_root`, git reached through `host`, and what it's given on stdin
    read by `stdin`, which only `start` of a Fix reads.

    - `step <run> <number> <status>`: marks the step as `record.step_marked` does, commits and
      pushes as `rn: <its words>: <status>`, and gives 0 printing what's due.
    - `start <run> <path>`: starts the deliverable's next role as `start.started` does, writing
      the steering where it changes, which rn's hook commits once the role ends, and gives 0
      printing the line that gives the role.
    - `inspected <run>`: marks the inspection passed as `record.inspected_marked` does, commits
      and pushes as `rn: the inspection passed`, and gives 0 printing what's due.
    - `due <run>`: gives 0 printing each line that `due.due` gives, a line each.

    `<run>` is the run's folder, as `place.of_folder` takes it. 1 with `steering: <what's wrong>`,
    changing nothing, where the input is Wrong: a result or a steering that's missing, isn't JSON,
    or leaves its schema, naming each place, or a mark that `record` refuses; 1 where something
    `push.kept` needs is Missing. 2 with what stopped it where it CantRun, such as git refusing the
    commit, with what git said; 2 with the usage where the arguments are other than these.
    """
    if not argv or argv[0] not in _SUBCOMMANDS or len(argv) != _SUBCOMMANDS[argv[0]][1]:
        return 2, "", USAGE
    if argv[0] == "start":
        return answered(
            "steering", lambda: _start(of_folder(cwd, argv[1]), argv[2], plugin_root, stdin)
        )
    subcommand = _SUBCOMMANDS[argv[0]][0]
    schemas = os.path.join(plugin_root, "domain", "schemas")
    return answered(
        "steering", lambda: subcommand(of_folder(cwd, argv[1]), list(argv[2:]), schemas, host)
    )


def _step(run: RunPlace, given: list[str], schemas: str, host: Host) -> Answer:
    if not given[0].isdigit():
        raise Wrong(f"{given[0]!r} isn't a step's number; give its number from 1")
    steering, words = record.step_marked(_steering(run, schemas), int(given[0]), given[1])
    _committed(run, steering, f"{words}: {given[1]}", host)
    return 0, _lines(due.due(steering)), ""


def _start(run: RunPlace, path: str, plugin_root: str, stdin: Callable[[], str]) -> Answer:
    schemas = os.path.join(plugin_root, "domain", "schemas")
    held = _steering(run, schemas)
    words = stdin() if _next(held, path) == "fixer" else ""
    marked, line = start.started(run, held, path, words, plugin_root)
    if marked != held:
        _written(run, marked)
    return 0, line, ""


def _next(steering: dict[str, Any], path: str) -> str:
    for step in steering["state"]["steps"]:
        for each in step["deliverables"]:
            if each["path"] == path and each["status"] == "open":
                return str(each.get("next", "generator"))
    return ""


def _inspected(run: RunPlace, given: list[str], schemas: str, host: Host) -> Answer:
    steering = record.inspected_marked(_steering(run, schemas))
    _committed(run, steering, "the inspection passed", host)
    return 0, _lines(due.due(steering)), ""


def _due(run: RunPlace, given: list[str], schemas: str, host: Host) -> Answer:
    return 0, _lines(due.due(_steering(run, schemas))), ""


def _steering(run: RunPlace, schemas: str) -> dict[str, Any]:
    return form.held(run.steering, os.path.join(schemas, "steering.schema.json"), "the steering")


def _committed(run: RunPlace, steering: dict[str, Any], message: str, host: Host) -> str:
    _written(run, steering)
    return push.kept(run, steering, f"rn: {message}", host)


def _written(run: RunPlace, steering: dict[str, Any]) -> None:
    with open(run.steering, "w", encoding="utf-8") as f:
        json.dump(steering, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _lines(lines: list[str]) -> str:
    return "".join(f"{each}\n" for each in lines)


# Each subcommand, by its name, with the number of arguments it takes, its name among them.
_SUBCOMMANDS: dict[str, tuple[Callable[[RunPlace, list[str], str, Host], Answer], int]] = {
    "step": (_step, 4),
    "start": (_due, 3),
    "inspected": (_inspected, 2),
    "due": (_due, 2),
}
