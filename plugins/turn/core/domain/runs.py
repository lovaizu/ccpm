"""A run of Turn as its Run, run.json in the run's folder, holds it: the works it makes in order,
each with the kind whose best practice makes it, the best practice of how it reads, the folder of
its design file, its Standards and its rounds, the paths it lies at, what its user runs and the
files that needs, and where it is: waiting, with Pin, in its rounds, or done. A run makes one work,
or first the best practice of a kind new to Turn, made by `meta`, and then the work. The planner
writes the Call, call.json, and this module begins each work from it: the work's Standards and its
hand-over to Pin, a design file in the form of Pin's design tree, which keeps word for word what a
calling AI settled."""

from __future__ import annotations

import json
import os
from typing import Any

import files
import practices

# Turn's own best practices, and the repository's, which a run takes over Turn's of the same kind.
OWN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "best-practices")
REPOSITORY = os.path.join(".turn", "best-practices")
# The kind of the work that makes a best practice, by the best practice of a best practice.
META = "meta"
# The files of a work's folder.
CALL = "call.json"
RUN = "run.json"
DESIGN = "design-tree.json"
STANDARD = "standard.json"
READING = "reading-standard.json"
VERIFICATION = "verification"
GENERATOR = "generator.json"
# Where a work is, in the order it goes, and where it is before it is done.
WAITS, PIN, ROUNDS, DONE = "waits", "pin", "rounds", "done"
UNDONE = (WAITS, PIN, ROUNDS)


def practice_of(kind: str) -> str | None:
    """The path of the kind's best practice: the repository's, else Turn's own; None where neither
    has one."""
    for folder in (REPOSITORY, OWN):
        path = os.path.join(folder, f"{kind}.json")
        if os.path.isfile(path):
            return path
    return None


def read_practice(path: str) -> dict[str, Any]:
    """The best practice at the path; refuses, by files.Unreadable, one that is missing, is no JSON,
    or is out of its form, the JSON Schema of a best practice or the faults its form shows."""
    data = files.load(path, "best-practice")
    found = practices.faults(data)
    if found:
        raise files.Unreadable(f"the best practice {path} is out of its form: {'; '.join(found)}")
    return data


def load(run: str) -> dict[str, Any]:
    """The Run of the run's folder, held to its form."""
    return files.load(os.path.join(run, RUN), "run")


def save(run: str, data: dict[str, Any]) -> None:
    """Writes the Run into the run's folder."""
    files.save(os.path.join(run, RUN), data)


def current(data: dict[str, Any]) -> dict[str, Any]:
    """The work the run is at: the first not done, else the last."""
    return next((w for w in data["works"] if w["at"] in UNDONE), data["works"][-1])


def questions(kind: str, data: dict[str, Any]) -> list[dict[str, str]]:
    """The best practice's questions as a design tree asks them, each named with the kind, as
    `readme/Q1`."""
    return [{"id": f"{kind}/{q['id']}", "what": q["what"]} for q in data["benefits"]]


def given_faults(call: dict[str, Any]) -> list[str]:
    """Each way the points a calling AI settled cannot be handed over as given: a kind other than
    the Call's, and a decision not decided, or not marked settled by the maker AI, which Pin keeps
    as given only so."""
    given = call.get("given", {})
    found = []
    if "kind" in given and given["kind"] != call["kind"]:
        found.append(f"the kind is {call['kind']}, but the calling AI gave {given['kind']}")
    for d in given.get("decisions", []):
        if d.get("decided") is None or d.get("settled_by") != "maker":
            found.append(
                f"the calling AI's decision {d.get('id')} is not decided with settled_by maker,"
                " as Calling Turn asks"
            )
    return found


def works_of(run: str, call: dict[str, Any]) -> list[dict[str, Any]]:
    """The works of a new run, each waiting: the work the Call asks for, by the kind's best
    practice, after its best practice where the kind has none."""
    kind = call["kind"]
    work = {
        "kind": kind,
        "practice": practice_of(kind) or os.path.join(REPOSITORY, f"{kind}.json"),
        "reading": call["reading"],
        "folder": run,
        "paths": list(call.get("given", {}).get("work", [])),
        "commands": [],
        "files": [],
        "at": WAITS,
    }
    if practice_of(kind) is not None:
        return [work]
    made = {
        **work,
        "kind": META,
        "practice": os.path.join(OWN, f"{META}.json"),
        "reading": "refactor-doc",
        "folder": os.path.join(run, "best-practice"),
        "paths": [work["practice"]],
    }
    return [made, work]


def begin(run: str, data: dict[str, Any], work: dict[str, Any]) -> str:
    """Begins the work: writes its Standards and its hand-over to Pin into its folder, and puts it
    with Pin; gives the Request that hands it over, the design file's path as one JSON object on its
    first line and then what Pin is to pin down. Refuses, by files.Unreadable, a best practice that
    cannot be read or is out of its form."""
    call = files.load(os.path.join(run, CALL), "call")
    practice = read_practice(work["practice"])
    reading = read_practice(os.path.join(OWN, f"{work['reading']}.json"))
    given = call.get("given", {})
    # The work before the last is the best practice of the kind new to Turn.
    if work is not data["works"][-1]:
        goal = {"what": call["kind_goal"], "grounds": []}
        decisions: list[dict[str, Any]] = []
        words = (
            f"The best practice of the kind {call['kind']}, which Turn has none of, to make this"
            f" request by: {call['request']}"
        )
    else:
        goal = given.get("goal", {"what": call["goal"], "grounds": []})
        decisions = given.get("decisions", [])
        words = call["request"]
    design = os.path.join(work["folder"], DESIGN)
    tree = {"goal": goal, "questions": questions(work["kind"], practice), "decisions": decisions}
    files.save(design, tree)
    files.save(os.path.join(work["folder"], STANDARD), practices.standard(practice))
    files.save(os.path.join(work["folder"], READING), practices.standard(reading))
    work["at"] = PIN
    save(run, data)
    return request(design, words)


def request(design: str, words: str) -> str:
    """The Request to Pin: the design file's path as one JSON object on the first line, then the
    words."""
    return f"{json.dumps({'design': design}, ensure_ascii=False)}\n{words}"


def start(run: str) -> str:
    """Begins a new run from the Call in its folder: its Run, and its first work handed to Pin;
    gives the Request. Refuses, by files.Unreadable, a run begun before, a Call out of its form,
    points that cannot be handed over as given, a kind new to Turn with no purpose for its best
    practice, and a best practice that cannot be read."""
    if os.path.exists(os.path.join(run, RUN)):
        raise files.Unreadable(f"{run} has begun already: run plan.py check on it")
    call = files.load(os.path.join(run, CALL), "call")
    found = given_faults(call)
    if found:
        raise files.Unreadable("; ".join(found))
    if practice_of(call["kind"]) is None and "kind_goal" not in call:
        raise files.Unreadable(
            f"Turn has no best practice of {call['kind']}: write into {CALL} its kind_goal, who"
            " uses such a work and for what"
        )
    works = works_of(run, call)
    data = {"works": works}
    return begin(run, data, works[0])


def generator_values(run: str, work: dict[str, Any]) -> str:
    """The run values the generator is started with, as one JSON line."""
    values = {
        "run": run,
        "work": work["paths"],
        "answers": os.path.join(work["folder"], VERIFICATION, GENERATOR),
    }
    return json.dumps(values, ensure_ascii=False)


def work_faults(work: dict[str, Any]) -> list[str]:
    """Each way the work cannot go to its rounds: no path, or a path of a folder, as the evaluator
    reads each file of the work to its end."""
    if not work["paths"]:
        return [f"the work of {work['kind']} has no paths: write them into its paths"]
    return [
        f"the path {p} is a folder: name each file of the work"
        for p in work["paths"]
        if p.endswith("/") or os.path.isdir(p)
    ]


def ready(run: str) -> str:
    """Puts the work that is with Pin into its rounds, its paths read out of the design, and gives
    the generator's run values; one in its rounds stays there. Refuses, by files.Unreadable, a work
    done, and paths that cannot be made."""
    data = load(run)
    work = current(data)
    if work["at"] not in UNDONE:
        raise files.Unreadable("the work is done: hand a change to Pin before its rounds")
    found = work_faults(work)
    if found:
        raise files.Unreadable("; ".join(found))
    work["at"] = ROUNDS
    save(run, data)
    return generator_values(run, work)


def hand(run: str) -> dict[str, Any]:
    """Puts the work the run is at with Pin again, and gives it."""
    data = load(run)
    work = current(data)
    work["at"] = PIN
    save(run, data)
    return work


def advance(run: str) -> str:
    """Marks the work in its rounds done, and begins the next: gives its Request, or "" where the
    run is done. Before the next begins, the best practice the work made is held to its form and its
    Markdown written beside it. Refuses, by files.Unreadable, a work not in its rounds and a best
    practice made out of its form."""
    data = load(run)
    work = current(data)
    if work["at"] != ROUNDS:
        raise files.Unreadable(f"the work of {work['kind']} is not in its rounds, but {work['at']}")
    at = data["works"].index(work)
    # The work after it, a run having no more than two; None where it is the last.
    following = next(iter(data["works"][at + 1 :]), None)
    if following is not None:
        path = following["practice"]
        made = read_practice(path)
        with open(os.path.splitext(path)[0] + ".md", "w", encoding="utf-8") as f:
            f.write(practices.markdown(following["kind"], made))
    work["at"] = DONE
    save(run, data)
    return "" if following is None else begin(run, data, following)


def done(work: dict[str, Any]) -> str:
    """The Message that hands the work back."""
    return (
        f"Done: {', '.join(work['paths'])} written, and not committed. It meets every question of"
        f" {work['kind']} and of {work['reading']}."
        f" {os.path.join(work['folder'], VERIFICATION)}/ shows the lines that meet each question."
    )
