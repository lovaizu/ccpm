"""Decides steering's command line: its subcommands, what each takes and prints, and the exit code
by which whoever ran it reads its result."""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Sequence
from typing import Any

import form
import practice
import push
from fault import Answer, Wrong, answered
from host import Host
from place import WorkPlace, of_folder

from steering import due, record, start

USAGE = """\
usage: steering aim <work>   (the aim on stdin)
       steering step <work> <number> open|trying|done
       steering start <work> <path>   (a Fix's problem in words on stdin)
       steering inspected <work>
       steering due <work>
"""


def main(
    argv: Sequence[str], cwd: str, plugin_root: str, host: Host, stdin: Callable[[], str]
) -> Answer:
    """The exit code, stdout, and stderr of `steering` with the arguments, from the folder `cwd`,
    with rn's folder at `plugin_root`, git reached through `host`, and what it's given on stdin
    read by `stdin`, which `aim` and `start` of a Fix read.

    - `aim <work>`: takes the aim on stdin, in the form of `aim.schema.json`, each deliverable of a
      kind of `practice.kinds` that isn't a refactoring's, into the steering as `record.taken_in`
      makes it, the steering made where the work has none yet, commits it as `rn: <the aim's
      message>`, and gives 0 printing what's due.
    - `step <work> <number> <status>`: marks the step as `record.step_marked` does, commits it as
      `rn: <its words>: <status>`, and gives 0 printing what's due.
    - `start <work> <path>`: starts the deliverable's next role as `start.started` does, writing
      the steering where it changes, which rn's hook commits once the role ends, and gives 0
      printing the line that gives the role.
    - `inspected <work>`: marks the inspection passed as `record.inspected_marked` does, commits
      it as `rn: the inspection passed`, and gives 0 printing what's due.
    - `due <work>`: gives 0 printing each line that `due.due` gives, a line each.

    Each commit holds the steering alone, as a role at work may be writing its files, and is pushed
    at once; where git can't push it, `unpushed\t<what git said>` comes before what's due, and the
    next push carries the commit.

    `<work>` is the work's folder, as `place.of_folder` takes it. 1 with `steering: <what's wrong>`,
    changing nothing, where the input is Wrong: a result or a steering that's missing, isn't JSON,
    or leaves its schema, naming each place, an aim that isn't JSON or leaves its schema, names a
    kind that isn't one, or that `record` refuses, or a mark that `record` refuses; 1 where
    something `push.kept` needs is Missing. 2 with what stopped it where it CantRun, such as git
    refusing the commit, with what git said; 2 with the usage where the arguments are other than
    these.
    """
    if not argv or argv[0] not in _SUBCOMMANDS or len(argv) != _SUBCOMMANDS[argv[0]][1]:
        return 2, "", USAGE
    if argv[0] == "start":
        return answered(
            "steering", lambda: _start(of_folder(cwd, argv[1]), argv[2], plugin_root, stdin)
        )
    if argv[0] == "aim":
        return answered("steering", lambda: _aim(of_folder(cwd, argv[1]), plugin_root, stdin, host))
    subcommand = _SUBCOMMANDS[argv[0]][0]
    schemas = os.path.join(plugin_root, "domain", "schemas")
    return answered(
        "steering", lambda: subcommand(of_folder(cwd, argv[1]), list(argv[2:]), schemas, host)
    )


def _aim(work: WorkPlace, plugin_root: str, stdin: Callable[[], str], host: Host) -> Answer:
    schemas = os.path.join(plugin_root, "domain", "schemas")
    try:
        aim = json.loads(stdin())
    except json.JSONDecodeError as error:
        raise Wrong(f"the aim isn't JSON: {error}") from None
    found = form.faults(aim, os.path.join(schemas, "aim.schema.json"))
    if found:
        raise Wrong("the aim leaves its schema, aim.schema.json: " + "; ".join(found))
    _kinds_held(aim, practice.kinds(plugin_root, work.worktree))
    held = _steering(work, schemas) if os.path.isfile(work.steering) else None
    steering = record.taken_in(held, aim)
    unpushed = _committed(work, steering, aim["message"], host)
    return 0, unpushed + _lines(due.due(steering)), ""


def _kinds_held(aim: dict[str, Any], kinds: dict[str, str]) -> None:
    """Refuses a deliverable of a kind that rn has no best practice of, or of a refactoring's,
    as a refactoring follows a deliverable made by its own kind."""
    made = sorted(set(kinds) - {practice.refactoring(each) for each in kinds})
    for step in aim.get("steps", []):
        for each in step["deliverables"]:
            if each["kind"] not in made:
                raise Wrong(
                    f"{each['path']}: {each['kind']!r} isn't a kind to make; give one of"
                    f" {', '.join(made)}"
                )


def _step(work: WorkPlace, given: list[str], schemas: str, host: Host) -> Answer:
    if not given[0].isdigit():
        raise Wrong(f"{given[0]!r} isn't a step's number; give its number from 1")
    steering, words = record.step_marked(_steering(work, schemas), int(given[0]), given[1])
    unpushed = _committed(work, steering, f"{words}: {given[1]}", host)
    return 0, unpushed + _lines(due.due(steering)), ""


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


def _inspected(work: WorkPlace, given: list[str], schemas: str, host: Host) -> Answer:
    steering = record.inspected_marked(_steering(work, schemas))
    unpushed = _committed(work, steering, "the inspection passed", host)
    return 0, unpushed + _lines(due.due(steering)), ""


def _due(work: WorkPlace, given: list[str], schemas: str, host: Host) -> Answer:
    return 0, _lines(due.due(_steering(work, schemas))), ""


def _steering(work: WorkPlace, schemas: str) -> dict[str, Any]:
    return form.held(work.steering, os.path.join(schemas, "steering.schema.json"), "the steering")


def _committed(work: WorkPlace, steering: dict[str, Any], message: str, host: Host) -> str:
    """Writes the steering, commits it alone, as a role at work may be writing its files, and
    pushes it; gives the line `unpushed\\t<what git said>` where git couldn't push, else none."""
    _written(work, steering)
    why = push.kept(work, f"rn: {message}", [work.steering], host)
    return f"unpushed\t{' '.join(why.split())}\n" if why else ""


def _written(work: WorkPlace, steering: dict[str, Any]) -> None:
    with open(work.steering, "w", encoding="utf-8") as f:
        json.dump(steering, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _lines(lines: list[str]) -> str:
    return "".join(f"{each}\n" for each in lines)


# Each subcommand, by its name, with the number of arguments it takes, its name among them.
_SUBCOMMANDS: dict[str, tuple[Callable[[WorkPlace, list[str], str, Host], Answer], int]] = {
    "aim": (_due, 2),
    "step": (_step, 4),
    "start": (_due, 3),
    "inspected": (_inspected, 2),
    "due": (_due, 2),
}
