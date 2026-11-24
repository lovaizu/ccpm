"""Decides whether a role's result holds what its Cut gave it: its form, each condition answered
once by its ID, each line it quotes standing in the deliverable, each file it names in its
deliverable or its own folder, and the document that the deliverable's kind makes holding its
kind's template."""

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
from check.form import schema

# The roles whose result check.py checks, each by the name of its result's schema in
# domain/schemas/, and the key of its Cut that names the folder of its result: a Round's for the
# generator and the evaluator, and a Fix's for the fixer.
FORMS = {
    "generator": ("generator-round", "round"),
    "evaluator": ("evaluator-round", "round"),
    "fixer": ("fixer-fix", "fix"),
}
# The folder of a role's result, in words, by the key of its Cut that names it.
_FOLDERS = {"round": "the Round's folder", "fix": "the Fix's folder"}


def folder(role: str, cut: Cut) -> str:
    """The folder of the role's result that its Cut names, from the folder that the conversation
    works in: the Cut's `round` for the generator and the evaluator, and its `fix` for the fixer.
    Raises Wrong for a role of none of FORMS."""
    return cut[_form(role)[1]]


def faults(role: str, cut: Cut, result: Result, worktree: str, cwd: str) -> list[str]:
    """Each fault of the role's result, in a line that says how to mend it.

    Takes: one of FORMS, `generator`, `evaluator`, or `fixer`, the role's Cut, its result, the
    run's worktree, from which the deliverable's paths are given, and the folder that the
    conversation works in, from which the Cut's own paths are given.
    Gives: each place where the result leaves its schema, as FORMS names it; for the generator,
    each `good` whose condition the Cut's deliverable doesn't hold, a `point` with no words where
    the result is `point`, and each file it names outside the deliverable's paths and the Round's
    folder; for the fixer, each file it names outside the deliverable's paths and the Fix's
    folder; for the evaluator, each condition of the Cut answered in neither `good` nor `more`, or
    in both, or twice, and each ID the Cut doesn't hold; for both, each line of a `good` that no
    file of the deliverable holds as it stands; and, for the generator, where the Cut names its
    kind's `template`, each fault that `template.check.faults` finds in the Cut's language in the
    deliverable's path where that is a Markdown file, the document that the kind makes, as
    `<file>:<line>: <what>`, `<file>` from the worktree's top, and in no more path or file found
    in a folder. None where the result holds each.
    Changes: nothing.
    Refuses: Wrong where the role is none of FORMS.
    """
    found = form_faults(result, schema(_form(role)[0]))
    if found:
        # The checks below read the result in its form.
        return found
    files = _files(cut["deliverable"], worktree)
    if role == "generator":
        found += _generator(cut, result)
    if role == "evaluator":
        found += _evaluator(cut, result)
    if role != "evaluator":
        found += _outside(role, cut, result, worktree, cwd)
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


def _form(role: str) -> tuple[str, str]:
    """The role's result's schema and its Cut's key of its folder, refused as Wrong for a role of
    none of FORMS."""
    if role not in FORMS:
        raise Wrong(f"check.py checks the result of {', '.join(FORMS)}, not {role!r}")
    return FORMS[role]


def _generator(cut: Cut, result: Result) -> list[str]:
    """The faults that only a generator's result can have."""
    held = [each["id"] for each in cut["deliverable"]["necessary_conditions"]]
    found = [
        f"{each['condition']}: isn't a condition of the deliverable; name one of {', '.join(held)}"
        for each in result.get("good", [])
        if each["condition"] not in held
    ]
    if result["result"] == "point" and "point" not in result:
        found.append("point: the result point gives no point; write the point in `point`")
    return found


def _outside(role: str, cut: Cut, result: Result, worktree: str, cwd: str) -> list[str]:
    """Each file that the maker's result names outside the deliverable's paths and its own
    folder, the Round's or the Fix's."""
    key = _form(role)[1]
    places = [os.path.join(worktree, each) for each in _paths(cut["deliverable"])]
    places.append(os.path.join(cwd, cut[key]))
    return [
        f"{each}: lies outside the deliverable's paths and {_FOLDERS[key]}; write only there"
        for each in result.get("files", [])
        if not any(_under(os.path.join(worktree, each), place) for place in places)
    ]


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
    """Each place where the deliverable's path, a Markdown file, leaves its kind's template in the
    Cut's language, where the Cut names one."""
    name = os.path.normpath(cut["deliverable"]["path"])
    if cut["template"] is None or not name.endswith(".md") or name not in files:
        return []
    template = _text(os.path.join(cwd, cut["template"]))
    return [
        f"{name}:{each.line}: {each.what}"
        for each in check.faults(template, files[name], cut["language"])
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
