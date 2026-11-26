"""Decides rounds' command line: its subcommands, what each takes and prints, and the exit code by
which whoever ran it reads its result."""

from __future__ import annotations

import os
from collections.abc import Callable, Sequence
from urllib.parse import unquote

import form
from fault import Answer, Wrong, answered
from place import RunPlace, of_folder

from rounds import course, files

USAGE = """\
usage: rounds next <run> <deliverable>
       rounds fix <run> <deliverable>   (the problem's words on stdin)
       rounds weighed <run> <folder>
"""
# What `next` prints for each role, by the stage of the entry it starts in.
_ROLE = {files.CONTENT: "generator", files.REFACTOR: "refactor"}


def main(argv: Sequence[str], cwd: str, plugin_root: str, stdin: Callable[[], str] = str) -> Answer:
    """The exit code, stdout, and stderr of `rounds` with the arguments, from the folder `cwd`,
    with rn's folder at `plugin_root`, and what it's given on stdin read by `stdin`, which only
    `fix` reads.

    - `next <run> <deliverable>`: 0 printing what `course.next_of` gives for the deliverable, as
      one line, its words apart by a tab, each folder and file absolute: `generator\\t<folder>`
      for a Round of content, `refactor\\t<folder>` for a Round of refactoring, a new one made by
      `files.started` where the course takes one, `evaluator\\t<folder>`, `fixer\\t<folder>`,
      `weigh\\t<the result to weigh>`, or `put-up`.
    - `fix <run> <deliverable>`, with the problem's words on stdin, as they were printed or said:
      0 printing the new Fix's folder, absolute, its problem in `problem.md`; 1 writing nothing
      where the words are empty, or where the deliverable's course isn't at its put-up, as a Fix
      mends only what its Rounds made.
    - `weighed <run> <folder>`: marks the Round or Fix weighed, as `files.weigh` does, and gives
      0 printing what's next for its deliverable, as `next` prints it.

    `<run>` is the run's folder, as `place.of_folder` takes it. 1 with `rounds: <what's wrong>`
    where the input is Wrong, such as a result out of its schema, saying how to mend it; 2 with
    the usage where the arguments are other than these.
    """
    if not argv or argv[0] not in _SUBCOMMANDS or len(argv) != 3:
        return 2, "", USAGE
    schemas = os.path.join(plugin_root, "domain", "schemas")
    given = [argv[2], stdin()] if argv[0] == "fix" else [argv[2]]
    subcommand = _SUBCOMMANDS[argv[0]]
    return answered("rounds", lambda: subcommand(of_folder(cwd, argv[1]), given, cwd, schemas))


def _next(run: RunPlace, given: list[str], cwd: str, schemas: str) -> Answer:
    return 0, _line(run, given[0], schemas), ""


def _line(run: RunPlace, deliverable: str, schemas: str) -> str:
    made = files.entries(run, deliverable, schemas)
    decisions = _decisions(run, schemas)
    found = course.next_of(made, decisions)
    if found.what == "new":
        stage = found.stage or files.CONTENT
        return f"{_ROLE[stage]}\t{files.started(run, deliverable, stage, decisions, made)}\n"
    if found.entry is None:
        return f"{found.what}\n"
    if found.what == "weigh":
        return f"weigh\t{_result(found.entry)}\n"
    role = _ROLE.get(found.entry.stage, found.what) if found.what == "generator" else found.what
    return f"{role}\t{found.entry.folder}\n"


def _result(entry: files.Entry) -> str:
    role = next(each for each in ("fixer", "evaluator", "generator") if each in entry.results)
    return os.path.join(entry.folder, files.RESULTS[role][0])


def _decisions(run: RunPlace, schemas: str) -> int:
    schema = os.path.join(schemas, "steering.schema.json")
    return len(form.held(run.steering, schema, "the steering")["ost"]["decisions"])


def _fix(run: RunPlace, given: list[str], cwd: str, schemas: str) -> Answer:
    deliverable, words = given
    if not words.strip():
        raise Wrong(
            "the problem's words are empty; give them on stdin as they were printed or said"
        )
    made = files.entries(run, deliverable, schemas)
    decisions = _decisions(run, schemas)
    if course.next_of(made, decisions).what != "put-up":
        raise Wrong(
            f"{deliverable}: its Rounds aren't over, or a Fix of it is under way; take its next"
            " step from rounds next first"
        )
    folder = files.started(run, deliverable, files.FIX, decisions, made)
    with open(os.path.join(folder, "problem.md"), "w", encoding="utf-8") as f:
        f.write(words if words.endswith("\n") else words + "\n")
    return 0, f"{folder}\n", ""


def _weighed(run: RunPlace, given: list[str], cwd: str, schemas: str) -> Answer:
    folder = os.path.normpath(os.path.join(cwd, given[0]))
    files.weigh(run, folder)
    deliverable = _deliverable_of(run, folder)
    return 0, _line(run, deliverable, schemas), ""


def _deliverable_of(run: RunPlace, folder: str) -> str:
    return unquote(os.path.basename(os.path.dirname(folder)))


# Each subcommand, by its name.
_SUBCOMMANDS: dict[str, Callable[[RunPlace, list[str], str, str], Answer]] = {
    "next": _next,
    "fix": _fix,
    "weighed": _weighed,
}
