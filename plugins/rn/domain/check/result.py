"""Decides whether a role's result holds what its Cut gave it, beyond what a rule of Lane's holds:
its form, each condition answered once by its ID, each line it quotes standing in the deliverable,
and each Markdown file of the deliverable holding its kind's template."""

from __future__ import annotations

import os
from collections import Counter
from typing import Any

from fault import Wrong
from practice import conditions
from rounds.files import Result
from template import check
from tree.cut import Cut

from check.form import faults as form_faults

# The folder of rn's schemas, beside this package.
_SCHEMAS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "schemas")


def faults(role: str, cut: Cut, result: Result, worktree: str, cwd: str) -> list[str]:
    """Each fault of the role's result, in a line that says how to mend it.

    Takes: `generator` or `evaluator`, the role's Cut, its result, the run's worktree, from which
    the deliverable's paths are given, and the folder that the conversation works in, from which
    the Cut's own paths are given.
    Gives: each place where the result leaves `<role>-round.schema.json`; for the generator, each
    `good` whose condition the Cut's deliverable doesn't hold, a `point` with no words where the
    result is `point`, and each file it names outside the deliverable's paths and the Round's
    folder; for the evaluator, each condition of the Cut answered in neither `good` nor `more`, or
    in both, or twice, and each ID the Cut doesn't hold; for both, each line of a `good` that no
    file of the deliverable holds as it stands; and, for the generator, where the folder of the
    best practice that the Cut names holds a `template.md`, each fault that `template.check.faults`
    finds in each Markdown file among the deliverable's paths, as `<file>:<line>: <what>`, `<file>`
    from the worktree's top. None where the result holds each.
    Changes: nothing.
    Refuses: Wrong where the role is neither `generator` nor `evaluator`.
    """
    if role not in ("generator", "evaluator"):
        raise Wrong(f"check.py checks the result of generator or evaluator, not {role!r}")
    found = form_faults(result, os.path.join(_SCHEMAS, f"{role}-round.schema.json"))
    if found:
        # The checks below read the result in its form.
        return found
    files = _files(cut["deliverable"], worktree)
    if role == "generator":
        found += _generator(cut, result, worktree, cwd)
    else:
        found += _evaluator(cut, result)
    found += [
        f"{each['condition']}: quotes {line!r}, a line that no file of the deliverable holds as it"
        " stands; quote its lines word for word"
        for each in result.get("good", [])
        for line in each["lines"]
        if not any(line in text.splitlines() for text in files.values())
    ]
    if role == "generator":
        found += _template(cut, files, cwd)
    return found


def _generator(cut: Cut, result: Result, worktree: str, cwd: str) -> list[str]:
    """The faults that only a generator's result can have."""
    node = cut["deliverable"]
    held = [each["id"] for each in node["necessary_conditions"]]
    found = [
        f"{each['condition']}: isn't a condition of the deliverable; name one of {', '.join(held)}"
        for each in result.get("good", [])
        if each["condition"] not in held
    ]
    if result["result"] == "point" and "point" not in result:
        found.append("point: the result point gives no point; write the point in `point`")
    places = [os.path.join(worktree, each) for each in _paths(node)]
    places.append(os.path.join(cwd, cut["round"]))
    found += [
        f"{each}: lies outside the deliverable's paths and the Round's folder; write only there"
        for each in result.get("files", [])
        if not any(_under(os.path.join(worktree, each), place) for place in places)
    ]
    return found


def _evaluator(cut: Cut, result: Result) -> list[str]:
    """The faults that only an evaluator's result can have: each condition answered once."""
    ids = [each["id"] for each in conditions(cut["judges_by"])]
    answered = Counter(each["condition"] for each in result["good"] + result["more"])
    found = [
        f"{each}: answered in neither good nor more; answer it in one of them"
        for each in ids
        if each not in answered
    ]
    found += [
        f"{each}: answered {count} times; answer it once, in good or in more"
        for each, count in answered.items()
        if each in ids and count > 1
    ]
    found += [
        f"{each}: isn't a condition of the Cut; answer only {', '.join(ids)}"
        for each in answered
        if each not in ids
    ]
    return found


def _template(cut: Cut, files: dict[str, str], cwd: str) -> list[str]:
    """Each place where a Markdown file of the deliverable leaves its kind's template, where the
    best practice holds one."""
    form = os.path.join(cwd, cut["best_practice"], "template.md")
    if not os.path.isfile(form):
        return []
    with open(form, encoding="utf-8") as file:
        template = file.read()
    return [
        f"{name}:{each.line}: {each.what}"
        for name, text in files.items()
        if name.endswith(".md")
        for each in check.faults(template, text)
    ]


def _paths(node: dict[str, Any]) -> list[str]:
    """The deliverable's paths: its path and each of its more paths."""
    return [node["path"], *node.get("more_paths", [])]


def _files(node: dict[str, Any], worktree: str) -> dict[str, str]:
    """The text of each file of the deliverable, by its path from the worktree's top."""
    found: dict[str, str] = {}
    for each in _paths(node):
        top = os.path.join(worktree, each)
        if os.path.isfile(top):
            found[os.path.normpath(each)] = _text(top)
        for folder, _, names in sorted(os.walk(top)):
            for name in sorted(names):
                path = os.path.join(folder, name)
                found[os.path.relpath(path, worktree)] = _text(path)
    return found


def _text(path: str) -> str:
    """The file's text."""
    with open(path, encoding="utf-8", errors="replace") as file:
        return file.read()


def _under(path: str, place: str) -> bool:
    """Whether the path is the place or lies under it."""
    path, place = os.path.normpath(path), os.path.normpath(place)
    return path == place or path.startswith(place + os.sep)
