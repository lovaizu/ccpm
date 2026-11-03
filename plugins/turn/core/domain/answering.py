"""The answers of a run of a step: the questions it was given, told by the name of its answers
file in the run's folder, as Turn's architecture names them; and the faults of its answers, each
question it was given answered once, and each line of a good lying in the work, so whoever reads
the answers finds the lines that meet each question there."""

from __future__ import annotations

import os
import re
from typing import Any

import designs
import files

# Each answers file of a run, by its name in the run's folder: the step's runs write one each.
NAME = re.compile(
    r"(?:(?P<step>self-check|verification|proofreading)/(?P<one>[^/]+)\.json|refactor-check\.json)"
)
NAMES = (
    "self-check/<part>.json, verification/<group>.json, refactor-check.json or"
    " proofreading/<group>.json"
)
# A line of the work, as `<path>:<line>` or `<path>:<from>-<to>`.
LINE = re.compile(r"(?P<path>.+):(?P<first>\d+)(?:-(?P<last>\d+))?")


def reached(tree: dict[str, Any], decisions: list[str]) -> list[str]:
    """The questions the decisions serve, each through the decisions it serves too, in the tree's
    order."""
    serves = {d["id"]: d["contributes_to"] for d in tree["decisions"]}
    seen: set[str] = set()
    todo = list(decisions)
    while todo:
        at = todo.pop()
        if at not in seen:
            seen.add(at)
            todo += serves.get(at, [])
    return [q["id"] for q in tree["questions"] if q["id"] in seen]


def grouped(run: str, key: str, group: str) -> list[str]:
    """The questions of the group under the key of the run's run.json."""
    path = os.path.join(run, "run.json")
    for g in files.load(path, "run").get(key, []):
        if g["id"] == group:
            return g["questions"]
    raise files.Unreadable(f"{path} has no group {group} under {key}")


def assigned(run: str, name: str) -> list[str]:
    """The questions the run of a step was given, told by its answers file's name in the run's
    folder: a part's, those its decisions serve; a group's, its group's; refactorer's, every
    question of the refactoring standard. Refuses, by files.Unreadable, a name of no answers file
    and a part or group the run has not."""
    found = NAME.fullmatch(name)
    if not found:
        raise files.Unreadable(f"{name} is no answers file of a run: {NAMES}")
    step, one = found["step"], found["one"]
    if step == "verification":
        return grouped(run, "groups", one)
    if step == "proofreading":
        return grouped(run, "refactoring_groups", one)
    if step == "self-check":
        path = os.path.join(run, "work.json")
        for part in files.load(path, "work")["parts"]:
            if part["id"] == one:
                tree = files.load(os.path.join(run, "design-tree.json"), "design-tree")
                return reached(tree, part["decisions"])
        raise files.Unreadable(f"{path} has no part {one}")
    refactoring = files.load(os.path.join(run, "run.json"), "run")["refactoring"]
    standard = files.load(os.path.join(run, "refactoring-standard.json"), "standard")
    return [f"{refactoring}/{q['id']}" for q in standard["benefits"]]


def line_fault(line: str, paths: list[str]) -> str:
    """How the line fails to lie in the work, or "" where it does: its form, its order, a file
    the work's paths do not hold or that is not there, and the file's length."""
    found = LINE.fullmatch(line)
    if not found:
        return f"{line} is not as <path>:<line> or <path>:<from>-<to>"
    path, first = found["path"], int(found["first"])
    last = int(found["last"] or first)
    if first < 1:
        return f"{line} begins before the file's first line"
    if last < first:
        return f"{line} ends before it begins"
    if not designs.under(path, paths):
        return f"{line} lies in none of the work's paths"
    try:
        with open(path, encoding="utf-8") as f:
            count = len(f.read().splitlines())
    except FileNotFoundError:
        return f"{line} names a file that is not there"
    if last > count:
        return f"{line} runs past {path}'s {count} lines"
    return ""


def faults(answers: dict[str, Any], given: list[str], paths: list[str], content: bool) -> list[str]:
    """Each fault of the answers: content where the run may give none; a question answered more
    than once, or not given; each line of a good that does not lie in the work; then each question
    given with no answer."""
    found = [] if content or not answers.get("content") else ["content is proofreader's alone"]
    lists = answers["good"] + answers["more"] + answers.get("content", [])
    named = [a["question"] for a in lists]
    for q in dict.fromkeys(named):
        # q is taken from named, so it counts once or more there.
        if named.count(q) > 1:  # pragma: no mutate
            found.append(f"{q} is answered more than once")
        if q not in given:
            found.append(f"{q} was not given to this run")
    for a in answers["good"]:
        for line in a["lines"]:
            fault = line_fault(line, paths)
            if fault:
                found.append(f"{a['question']}: {fault}")
    found += [f"{q} has no answer" for q in given if q not in named]
    return found


def check(run: str, path: str) -> list[str]:
    """Each fault of the answers at the path, a file of the run's folder: against the questions
    its run was given and the work's paths; content allowed in proofreader's alone. Refuses, by
    files.Unreadable, a file it cannot read."""
    name = os.path.relpath(path, run).replace(os.sep, "/")
    given = assigned(run, name)
    answers = files.load(path, "answers")
    paths = files.load(os.path.join(run, "work.json"), "work")["paths"]
    return faults(answers, given, paths, name.startswith("proofreading/"))
