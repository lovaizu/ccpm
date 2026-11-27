"""Decides rounds' command line: its subcommands, what each takes and prints, and the exit code by
which whoever ran it reads its result."""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Sequence
from urllib.parse import unquote

import form
import practice
from fault import Answer, Wrong, answered
from place import RunPlace, of_folder

from rounds import course, files

USAGE = """\
usage: rounds next <run> <deliverable>
       rounds fix <run> <deliverable>   (the problem's words on stdin)
       rounds confirmed <run> <deliverable>
       rounds weighed <run> <folder>
"""
# What `next` prints for each role, by the stage of the entry it starts in.
_ROLE = {files.CONTENT: "generator", files.REFACTOR: "refactorer"}


def main(argv: Sequence[str], cwd: str, plugin_root: str, stdin: Callable[[], str] = str) -> Answer:
    """The exit code, stdout, and stderr of `rounds` with the arguments, from the folder `cwd`,
    with rn's folder at `plugin_root`, and what it's given on stdin read by `stdin`, which only
    `fix` reads.

    - `next <run> <deliverable>`: 0 printing what `course.next_of` gives for the deliverable, as
      one line, its words apart by a tab, each folder and file absolute: `generator`, for a Round
      of content, or `refactorer`, for a Round of refactoring, each a new one made by
      `files.started` where the course takes one, with its folder and the folder of the best
      practice it's made by, as `practice.kinds` finds the deliverable's kind or the kind that
      `practice.refactoring` gives; `evaluator` with its folder and the file `judges-by.json` there,
      written with what `practice.judged` gives of the kind's best practice; `fixer` with its
      folder and the kind's best practice; `weigh` with the result to weigh; `confirm` with the
      evaluator's result whose findings the user confirms; or `done`, also where the course takes
      a Round of refactoring of a kind that `practice.refactoring` refactors by none.
    - `fix <run> <deliverable>`, with the problem's words on stdin, as they were printed or said:
      0 printing the new Fix's folder, absolute, its problem in `problem.md`; 1 writing nothing
      where the words are empty, or where the deliverable's course is at neither its confirming nor
      its end, as a Fix mends only what its Rounds made.
    - `confirmed <run> <deliverable>`: marks the findings left confirmed by the user with no mend,
      as `files.confirm` does, and gives 0 printing what's next, as `next` prints it; 1 writing
      nothing where the course isn't at its confirming.
    - `weighed <run> <folder>`: marks the Round or Fix weighed, as `files.weigh` does, and gives
      0 printing what's next for its deliverable, as `next` prints it.

    `<run>` is the run's folder, as `place.of_folder` takes it. 1 with `rounds: <what's wrong>`
    where the input is Wrong, such as a result out of its schema, a deliverable that no step of
    the steering names, or a kind with no best practice, saying how to mend it; 2 with the usage
    where the arguments are other than these.
    """
    if not argv or argv[0] not in _SUBCOMMANDS or len(argv) != 3:
        return 2, "", USAGE
    given = [argv[2], stdin()] if argv[0] == "fix" else [argv[2]]
    subcommand = _SUBCOMMANDS[argv[0]]
    return answered("rounds", lambda: subcommand(of_folder(cwd, argv[1]), given, cwd, plugin_root))


def _next(run: RunPlace, given: list[str], cwd: str, plugin_root: str) -> Answer:
    return 0, _line(run, given[0], plugin_root), ""


def _line(run: RunPlace, deliverable: str, plugin_root: str) -> str:
    schemas = os.path.join(plugin_root, "domain", "schemas")
    steering = _steering(run, schemas)
    step, kind = _named(steering, deliverable)
    root = files.folder_of(run, step, deliverable)
    made = files.entries(root, schemas)
    found = _course(made, kind)
    if found.what == "new":
        stage = found.stage or files.CONTENT
        folder = files.started(root, stage, made)
        return f"{_ROLE[stage]}\t{folder}\t{_practice(run, plugin_root, kind, stage)}\n"
    if found.entry is None:
        return f"{found.what}\n"
    if found.what == "weigh":
        return f"weigh\t{_result(found.entry)}\n"
    if found.what == "confirm":
        return f"confirm\t{_result(found.entry)}\n"
    if found.what == "evaluator":
        return (
            f"evaluator\t{found.entry.folder}\t{_judges_by(run, plugin_root, kind, found.entry)}\n"
        )
    stage = found.entry.stage
    role = _ROLE.get(stage, found.what)
    return f"{role}\t{found.entry.folder}\t{_practice(run, plugin_root, kind, stage)}\n"


def _course(made: list[files.Entry], kind: str) -> course.Next:
    """What comes next for the deliverable, as `course.next_of` gives it, its end in place of a
    Round of refactoring where the kind takes none."""
    found = course.next_of(made)
    if found.what == "new" and found.stage == files.REFACTOR and not practice.refactoring(kind):
        return course.Next("done")
    return found


def _named(steering: dict, deliverable: str) -> tuple[int, str]:
    """The number of the step whose Rounds the deliverable takes now, and its kind there: the
    first step not done that names it, else the last that does, as a later step that adds to it
    starts its own Rounds."""
    named = [
        (number, step["status"], each["kind"])
        for number, step in enumerate(steering["state"]["steps"], 1)
        for each in step["deliverables"]
        if each["path"] == deliverable
    ]
    for number, status, kind in named:
        if status != "done":
            return number, kind
    if named:
        return named[-1][0], named[-1][2]
    raise Wrong(
        f"no step names the deliverable {deliverable!r}; give its path as its step names it"
    )


def _practice(run: RunPlace, plugin_root: str, kind: str, stage: str) -> str:
    """The folder of the best practice that a Round or Fix of the stage is made by."""
    by = (practice.refactoring(kind) or kind) if stage == files.REFACTOR else kind
    found = practice.kinds(plugin_root, run.worktree)
    if by not in found:
        raise Wrong(
            f"rn has no best practice of the kind {by!r}; give the deliverable a kind it has"
        )
    return found[by]


def _judges_by(run: RunPlace, plugin_root: str, kind: str, entry: files.Entry) -> str:
    """Writes what the evaluator judges by in its Round, and gives the file's path."""
    held = practice.judged(practice.read(_practice(run, plugin_root, kind, files.CONTENT)))
    path = os.path.join(entry.folder, "judges-by.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(held, f, indent=1, ensure_ascii=False)
        f.write("\n")
    return path


def _result(entry: files.Entry) -> str:
    role = next(each for each in ("fixer", "evaluator", "generator") if each in entry.results)
    return os.path.join(entry.folder, files.RESULTS[role][0])


def _steering(run: RunPlace, schemas: str) -> dict:
    schema = os.path.join(schemas, "steering.schema.json")
    return form.held(run.steering, schema, "the steering")


def _fix(run: RunPlace, given: list[str], cwd: str, plugin_root: str) -> Answer:
    deliverable, words = given
    if not words.strip():
        raise Wrong(
            "the problem's words are empty; give them on stdin as they were printed or said"
        )
    schemas = os.path.join(plugin_root, "domain", "schemas")
    steering = _steering(run, schemas)
    step, kind = _named(steering, deliverable)
    root = files.folder_of(run, step, deliverable)
    made = files.entries(root, schemas)
    if _course(made, kind).what not in ("confirm", "done"):
        raise Wrong(
            f"{deliverable}: its Rounds aren't over, or a Fix of it is under way; take its next"
            " step from rounds next first"
        )
    folder = files.started(root, files.FIX, made)
    with open(os.path.join(folder, "problem.md"), "w", encoding="utf-8") as f:
        f.write(words if words.endswith("\n") else words + "\n")
    return 0, f"{folder}\n", ""


def _confirmed(run: RunPlace, given: list[str], cwd: str, plugin_root: str) -> Answer:
    schemas = os.path.join(plugin_root, "domain", "schemas")
    step, kind = _named(_steering(run, schemas), given[0])
    found = _course(files.entries(files.folder_of(run, step, given[0]), schemas), kind)
    if found.what != "confirm" or found.entry is None:
        raise Wrong(
            f"{given[0]}: no findings wait on the user's confirming; take its next step from"
            " rounds next"
        )
    files.confirm(found.entry.folder)
    return 0, _line(run, given[0], plugin_root), ""


def _weighed(run: RunPlace, given: list[str], cwd: str, plugin_root: str) -> Answer:
    folder = os.path.normpath(os.path.join(cwd, given[0]))
    files.weigh(run, folder)
    return 0, _line(run, _deliverable_of(folder), plugin_root), ""


def _deliverable_of(folder: str) -> str:
    return unquote(os.path.basename(os.path.dirname(folder)))


# Each subcommand, by its name.
_SUBCOMMANDS: dict[str, Callable[[RunPlace, list[str], str, str], Answer]] = {
    "next": _next,
    "fix": _fix,
    "confirmed": _confirmed,
    "weighed": _weighed,
}
