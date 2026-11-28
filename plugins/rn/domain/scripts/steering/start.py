"""Decides what starting a task's next role makes and gives: a Round or Fix to work in, as
the steering's entry names it, new for a role that starts its own, and the same where a stop left
it with no result; and what the role is given there."""

from __future__ import annotations

import json
import os
from typing import Any

import practice
from fault import Wrong
from place import WorkPlace

from steering import rounds
from steering.record import Steering

# The stage of the Round or Fix that each role starts, as its folder's name begins.
_STAGE = {"generator": rounds.CONTENT, "refactorer": rounds.REFACTOR, "fixer": rounds.FIX}
# The result the orchestrator weighs, by the role that gave it, the evaluator's findings first.
_WEIGHED = ("evaluator", "refactorer", "generator")


def started(
    work: WorkPlace, steering: Steering, path: str, words: str, plugin_root: str
) -> tuple[Steering, str]:
    """The steering with the task's next role started, and the line that gives the role.

    Takes: the work, its steering, the task's path as the steering names it, the problem's
    words for a Fix, and rn's folder.
    Gives: the steering as it is, and for a weighing, `weigh\\t<result>`, the evaluator's result
    of its entry where it holds one, else the refactorer's or the generator's point; for its
    evaluator, `evaluator\\t<folder>\\t<judges-by>`, `judges-by.json` written in its entry with
    what `practice.judged` gives; for each other role, the steering with its entry, and
    `<role>\\t<folder>\\t<best practice>`, the folder made one past the deliverable's last
    entry, or its entry where a stop left the role there with no result, a Fix's with `problem.md`
    holding the words, and the best practice of its kind, or of its refactoring's.
    Changes: makes the folder, and writes judges-by.json or problem.md in it.
    Refuses: Wrong where no task has the path, where its evaluator has no Round to
    judge, where a Fix's words are empty, or where rn has no best practice of the kind.
    """
    each = _task(steering, path)
    root = rounds.folder_of(work, path)
    role = each.get("next", "generator")
    if role == "weigh":
        return steering, f"weigh\t{_weighed(os.path.join(root, each['entry']))}\n"
    if role == "evaluator":
        if "entry" not in each:
            raise Wrong(f"{path} has no Round to judge; start its generator first")
        folder = os.path.join(root, each["entry"])
        return steering, f"evaluator\t{folder}\t{_judges_by(work, plugin_root, each, folder)}\n"
    by = each["refactor"] if role == "refactorer" else each["kind"]
    found = _practice(work, plugin_root, by)
    if role == "fixer" and not words.strip():
        raise Wrong("the problem's words are empty; give them on stdin as they were said")
    folder = _entry(root, role, each, os.path.join(plugin_root, "domain", "schemas"))
    if role == "fixer":
        with open(os.path.join(folder, "problem.md"), "w", encoding="utf-8") as f:
            f.write(words if words.endswith("\n") else words + "\n")
    marked = json.loads(json.dumps(steering))
    _task(marked, path)["entry"] = os.path.basename(folder)
    return marked, f"{role}\t{folder}\t{found}\n"


def _task(steering: Steering, path: str) -> dict[str, Any]:
    for each in steering["tasks"]:
        if each["path"] == path:
            return each
    raise Wrong(f"no task has the path {path!r}; give it as `steering due` names it")


def _weighed(folder: str) -> str:
    for role in _WEIGHED:
        result = os.path.join(folder, rounds.RESULTS[role][0])
        if os.path.isfile(result):
            return result
    raise Wrong(f"{folder} holds no result to weigh")


def _entry(root: str, role: str, each: dict[str, Any], schemas: str) -> str:
    """The folder the role works in: its entry, where a stop left the role there with no result,
    as rn's hook moves the task on once one is there, else one past the last, made."""
    stage = _STAGE[role]
    entry = each.get("entry", "")
    if entry.startswith(f"{stage}-"):
        return os.path.join(root, entry)
    made = rounds.entries(root, schemas)
    folder = os.path.join(root, f"{stage}-{made[-1].number + 1 if made else 1}")
    os.makedirs(folder, exist_ok=True)
    return folder


def _practice(work: WorkPlace, plugin_root: str, kind: str | None) -> str:
    found = practice.kinds(plugin_root)
    if kind not in found:
        raise Wrong(
            f"rn has no best practice of the kind {kind!r}; give the deliverable a kind it has"
        )
    return found[kind]


def _judges_by(work: WorkPlace, plugin_root: str, each: dict[str, Any], folder: str) -> str:
    held = practice.judged(practice.read(_practice(work, plugin_root, each["kind"])))
    path = os.path.join(folder, "judges-by.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(held, f, indent=1, ensure_ascii=False)
        f.write("\n")
    return path
