"""Decides steering's command line: its subcommands, what each takes and prints, and the exit code
by which whoever ran it reads its result."""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Sequence
from typing import Any

import form
from fault import Answer, Wrong, answered
from place import WorkPlace, of_folder

from steering import due, record, start

USAGE = """\
usage: steering aim <work>   (the aim on stdin)
       steering step <work> <number> open|trying|done
       steering start <work> <path>   (a Fix's problem in words on stdin)
       steering inspected <work>
       steering due <work>
"""


def main(argv: Sequence[str], cwd: str, plugin_root: str, stdin: Callable[[], str]) -> Answer:
    """The exit code, stdout, and stderr of `steering` with the arguments, from the folder `cwd`,
    with rn's folder at `plugin_root`, and what it's given on stdin read by `stdin`, which `aim`
    and `start` of a Fix read. Each writes the steering alone, as the orchestrator commits and
    pushes the work at each end of a purpose.

    - `aim <work>`: takes the aim on stdin, in the form of `aim.schema.json`, into the steering
      as `record.taken_in` makes it, the steering made where the work has none yet, and gives 0
      printing what's due.
    - `step <work> <number> <status>`: marks the step as `record.step_marked` does, and gives 0
      printing what's due.
    - `start <work> <path>`: starts the deliverable's next role as `start.started` does, writing
      the steering where it changes, and gives 0 printing the line that gives the role.
    - `inspected <work>`: marks the inspection passed as `record.inspected_marked` does, and gives
      0 printing what's due.
    - `due <work>`: gives 0 printing each line that `due.due` gives, a line each.

    `<work>` is the work's folder, as `place.of_folder` takes it. 1 with `steering: <what's wrong>`,
    changing nothing, where the input is Wrong: a result or a steering that's missing, isn't JSON,
    or leaves its schema, naming each place, an aim that isn't JSON or leaves its schema, or an aim
    or a mark that `record` refuses; 2 with the usage where the arguments are other than these.
    """
    if not argv or argv[0] not in _SUBCOMMANDS or len(argv) != _SUBCOMMANDS[argv[0]][1]:
        return 2, "", USAGE
    if argv[0] == "start":
        return answered(
            "steering", lambda: _start(of_folder(cwd, argv[1]), argv[2], plugin_root, stdin)
        )
    if argv[0] == "aim":
        return answered("steering", lambda: _aim(of_folder(cwd, argv[1]), plugin_root, stdin))
    subcommand = _SUBCOMMANDS[argv[0]][0]
    schemas = os.path.join(plugin_root, "domain", "schemas")
    return answered(
        "steering", lambda: subcommand(of_folder(cwd, argv[1]), list(argv[2:]), schemas)
    )


def _aim(work: WorkPlace, plugin_root: str, stdin: Callable[[], str]) -> Answer:
    schemas = os.path.join(plugin_root, "domain", "schemas")
    try:
        aim = json.loads(stdin())
    except json.JSONDecodeError as error:
        raise Wrong(f"the aim isn't JSON: {error}") from None
    found = form.faults(aim, os.path.join(schemas, "aim.schema.json"))
    if found:
        raise Wrong("the aim leaves its schema, aim.schema.json: " + "; ".join(found))
    held = _steering(work, schemas) if os.path.isfile(work.steering) else None
    steering = record.taken_in(held, aim)
    _written(work, steering)
    return 0, _lines(due.due(steering)), ""


def _step(work: WorkPlace, given: list[str], schemas: str) -> Answer:
    if not given[0].isdigit():
        raise Wrong(f"{given[0]!r} isn't a step's number; give its number from 1")
    steering = record.step_marked(_steering(work, schemas), int(given[0]), given[1])
    _written(work, steering)
    return 0, _lines(due.due(steering)), ""


def _start(work: WorkPlace, path: str, plugin_root: str, stdin: Callable[[], str]) -> Answer:
    schemas = os.path.join(plugin_root, "domain", "schemas")
    held = _steering(work, schemas)
    words = stdin() if _next(held, path) == "fixer" else ""
    marked, line = start.started(work, held, path, words, plugin_root)
    if marked != held:
        _written(work, marked)
    return 0, line, ""


def _next(steering: dict[str, Any], path: str) -> str:
    for step in steering["state"]["steps"]:
        for each in step["deliverables"]:
            if each["path"] == path and each["status"] == "open":
                return str(each.get("next", "generator"))
    return ""


def _inspected(work: WorkPlace, given: list[str], schemas: str) -> Answer:
    steering = record.inspected_marked(_steering(work, schemas))
    _written(work, steering)
    return 0, _lines(due.due(steering)), ""


def _due(work: WorkPlace, given: list[str], schemas: str) -> Answer:
    return 0, _lines(due.due(_steering(work, schemas))), ""


def _steering(work: WorkPlace, schemas: str) -> dict[str, Any]:
    return form.held(work.steering, os.path.join(schemas, "steering.schema.json"), "the steering")


def _written(work: WorkPlace, steering: dict[str, Any]) -> None:
    with open(work.steering, "w", encoding="utf-8") as f:
        json.dump(steering, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _lines(lines: list[str]) -> str:
    return "".join(f"{each}\n" for each in lines)


# Each subcommand, by its name, with the number of arguments it takes, its name among them.
_SUBCOMMANDS: dict[str, tuple[Callable[[WorkPlace, list[str], str], Answer], int]] = {
    "aim": (_due, 2),
    "step": (_step, 4),
    "start": (_due, 3),
    "inspected": (_inspected, 2),
    "due": (_due, 2),
}
