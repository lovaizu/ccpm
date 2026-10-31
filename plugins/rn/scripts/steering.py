"""The steering, the map to the user's purpose kept current: JSON held at every keep to its form,
forms/steering.json, and to what a form cannot hold, as rn's scripts read their data from it and a
fresh conversation goes on from it alone; the Markdown the user reads at each sign-off written from
it, the plan in the form of rn's plan checklist; and changed only as a move changes it, each task
done taken out and each plan the orchestrator wrote put in."""

from __future__ import annotations

import json
import os
import re
from collections.abc import Collection
from typing import Any

import schema
import stop

# The stages, in their order: the goal, settling why the user wants the work and what shows it
# done; the ux, what the user gets and how they use it; the architecture, how it is built and
# checked; then the build, the finished work used, the learnings and the session finished. Two are
# named as the work made at them: the finished work and the learnings.
GOAL = "goal"
UX = "ux"
ARCHITECTURE = "architecture"
BUILD = "build"
DELIVERABLE = "deliverable"
LEARNINGS = "learnings"
FINISHED = "finished"
STAGES = (GOAL, UX, ARCHITECTURE, BUILD, DELIVERABLE, LEARNINGS, FINISHED)
# The work the orchestrator writes the plan in, made again at every stage as the facts change it,
# so named apart from any stage.
PLAN = "plan"
# The sign-offs, each at the stage of its name, with the stage the user's approval there moves the
# session to.
APPROVED = {GOAL: UX, UX: ARCHITECTURE, ARCHITECTURE: BUILD, DELIVERABLE: LEARNINGS}
SIGNOFFS = tuple(APPROVED)
# The stages `state --stage` moves the session to, each from the one it moves from, as the others
# move at the sign-offs: the architecture from the ux stage, and the build from the architecture
# stage, where that stage made no document, so its sign-off has nothing to show.
MOVES = {ARCHITECTURE: UX, BUILD: ARCHITECTURE, DELIVERABLE: BUILD, FINISHED: LEARNINGS}
# The steering's form, beside rn's scripts in the plugin, which every keep holds the steering to.
FORM_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "forms", "steering.json"
)
with open(FORM_PATH, encoding="utf-8") as _f:
    FORM: dict[str, Any] = json.load(_f)
# The lists of the plan that hold IDs, each with the letters its IDs open with, numbered from 1.
LISTS = (("goals", "G"), ("acceptance_criteria", "AC"), ("tasks", "T"))
NUMBER = "[1-9][0-9]*"
# A pull request's URL, after the repository's.
PULL = re.compile(r"(\S+)/pull/[0-9]+")


def made(version: str, title: str, languages: dict[str, str], next_step: str) -> dict[str, Any]:
    """A steering at its start: made by the version of rn, of the title and in the languages, its
    pull request not yet opened, its plan empty, at the goal stage with no sign-off waiting, Next
    the step given and nothing open."""
    return {
        "session": {"rn": version, "pr": None, "title": title, "languages": languages},
        "plan": {"goals": [], "acceptance_criteria": [], "tasks": []},
        "status": {
            "stage": GOAL,
            "awaiting_signoff": False,
            "next_step": next_step,
            "open_questions": [],
        },
    }


def read(text: str | None) -> Any:
    """The steering the text holds as JSON, None where it is none or no JSON, as it is then not
    one rn wrote."""
    try:
        return json.loads(text or "")
    except ValueError:
        return None


def stage_of(text: str | None) -> str | None:
    """The stage the steering's text gives, None where it gives none that can be read."""
    data = read(text)
    try:
        return str(data["status"]["stage"])
    except (TypeError, KeyError):
        return None


def signoff_of(text: str | None) -> str | None:
    """The sign-off the steering's text sets waiting, that of its stage, None where none waits or
    none can be read."""
    data = read(text)
    try:
        return stage_of(text) if data["status"]["awaiting_signoff"] is True else None
    except (TypeError, KeyError):
        return None


def out_of_form(data: Any, done: Collection[str] = ()) -> str:
    """The point the steering is out of its form by, at its place, what was expected and what was
    found: forms/steering.json, each text some words, the plan as plan_out holds it, the tasks done
    being those of the IDs given, a sign-off waiting only at a stage of one, and the pull request's
    URL, or null before it is opened; "" where it holds."""
    found = schema.held(FORM, data)
    if found:
        return found.told()
    status, pr = data["status"], data["session"]["pr"]
    if status["awaiting_signoff"] and status["stage"] not in SIGNOFFS:
        return (
            f"$.status.awaiting_signoff: expected false at the {status['stage']} stage, which has"
            " no sign-off, found true"
        )
    if pr is not None and not PULL.fullmatch(pr):
        return (
            "$.session.pr: expected the pull request's URL, or null before it is opened, found"
            f" {pr}"
        )
    return worded_out(data, "$") or plan_out(data["plan"], done, "$.plan")


def part_out(part: Any, done: Collection[str] = ()) -> str:
    """The point the plan the orchestrator wrote is out of its form by, at its place in the part,
    as its writer reads it: the plan's form in forms/steering.json, each text some words, and what
    plan_out holds it to; "" where it holds."""
    found = schema.out(FORM["$defs"]["plan"], FORM, part, ())
    if found:
        return found.told()
    return worded_out(part, "$") or plan_out(part, done, "$")


def worded_out(value: Any, at: str) -> str:
    """The point the value at the place is out of its form by where a text in it is empty or
    blank; "" where every text in it holds words."""
    if isinstance(value, str) and not value.strip():
        return f"{at}: expected some words, found {json.dumps(value)}"
    inside: list[tuple[str, Any]] = []
    if isinstance(value, dict):
        inside = [(f"{at}.{key}", each) for key, each in value.items()]
    elif isinstance(value, list):
        inside = [(f"{at}[{k}]", each) for k, each in enumerate(value)]
    return next(filter(None, (worded_out(each, place) for place, each in inside)), "")


def plan_out(plan: dict[str, Any], done: Collection[str], at: str) -> str:
    """The point the plan, in its form, is out of what the form cannot hold by, at its place: each
    ID of its letters numbered from 1 and once; each ID named one the plan holds, a goal by a
    criterion, a criterion by a completion criterion, a task by a task, or a task done; no task
    building on itself through others; and each goal served by a criterion; "" where it holds."""
    for name, letters in LISTS:
        seen: list[str] = []
        for k, item in enumerate(plan[name]):
            if not re.fullmatch(letters + NUMBER, item["id"]):
                return f"{at}.{name}[{k}].id: expected {letters}<n>, n from 1, found {item['id']}"
            if item["id"] in seen:
                return f"{at}.{name}[{k}].id: expected each ID once, found {item['id']} again"
            seen.append(item["id"])
    goals = [g["id"] for g in plan["goals"]]
    criteria = [c["id"] for c in plan["acceptance_criteria"]]
    tasks = [t["id"] for t in plan["tasks"]]
    named: list[tuple[str, list[str], list[str], str]] = [
        (f"{at}.acceptance_criteria[{k}].contributes_to", c["contributes_to"], goals, "goals")
        for k, c in enumerate(plan["acceptance_criteria"])
    ]
    for k, task in enumerate(plan["tasks"]):
        named += [
            (
                f"{at}.tasks[{k}].completion_criteria[{n}].contributes_to",
                c["contributes_to"],
                criteria,
                "acceptance criteria",
            )
            for n, c in enumerate(task["completion_criteria"])
        ]
        named.append(
            (
                f"{at}.tasks[{k}].builds_on",
                task["builds_on"],
                [*tasks, *done],
                "tasks or tasks done",
            )
        )
    for place, ids, held, words in named:
        stray = [i for i in ids if i not in held]
        if stray:
            return f"{place}: expected only {words} the plan holds, found {stray[0]}"
    return cycle_out(plan["tasks"], at) or served_out(plan, at)


def cycle_out(tasks: list[dict[str, Any]], at: str) -> str:
    """The point the tasks are out of their form by where one builds on itself, at once or through
    others, at the first such task; "" where none does."""
    builds = {t["id"]: t["builds_on"] for t in tasks}
    for k, task in enumerate(tasks):
        reached, left = set(), list(builds[task["id"]])
        while left:
            one = left.pop()
            if one not in reached:
                reached.add(one)
                left += builds.get(one, [])
        if task["id"] in reached:
            return (
                f"{at}.tasks[{k}].builds_on: expected no task it builds on to build on it, found"
                f" {task['id']} building on itself"
            )
    return ""


def served_out(plan: dict[str, Any], at: str) -> str:
    """The point the plan is out of its form by where a goal is served by no criterion, at the
    first such goal; "" where each is."""
    served = {i for c in plan["acceptance_criteria"] for i in c["contributes_to"]}
    for k, goal in enumerate(plan["goals"]):
        if goal["id"] not in served:
            return (
                f"{at}.goals[{k}]: expected an acceptance criterion contributing to {goal['id']},"
                " found none"
            )
    return ""


def held_form(data: Any, done: Collection[str]) -> None:
    """Returns when the steering holds its form, the tasks done those of the IDs given; stops
    otherwise, keeping nothing."""
    point = out_of_form(data, done)
    if point:
        raise stop.Stop(
            f"rn: the steering would be out of its form: {point};"
            " nothing is kept: give what this move writes again so it holds, or write the part it"
            " puts back again"
        )


def text(data: dict[str, Any]) -> str:
    """The steering as rn writes it, one key or value to a line, so a change shows in git as the
    lines it changes and the user can read it on the pull request."""
    return json.dumps(data, ensure_ascii=False, indent=1) + "\n"


def clause(said: str) -> str:
    """The words without the full stop they may end with, to go on with more of the sentence."""
    return said.rstrip().removesuffix(".")


def indented(said: str, by: int) -> str:
    """The words with each line after the first indented by the spaces given, as under an item."""
    return said.replace("\n", "\n" + " " * by)


def listed(ids: list[str]) -> str:
    """The IDs in words, or none."""
    return stop.joined(ids) if ids else "none"


def markdown(data: dict[str, Any]) -> str:
    """The Markdown the user reads of the steering: the title, the plan in the form of rn's plan
    checklist, the goals and the criteria once made and the tasks while one is left, then where the
    session stands, its stage, the sign-off waiting, Next and what is open."""
    plan, status = data["plan"], data["status"]
    parts = [f"# {data['session']['title']}"]
    goals = [
        f"- {g['id']}: {indented(g['what'], 2)}\n\n  {indented(g['why'], 2)}" for g in plan["goals"]
    ]
    criteria = [
        f"- {c['id']}: {indented(clause(c['what']), 2)}. Serves {listed(c['contributes_to'])}."
        for c in plan["acceptance_criteria"]
    ]
    tasks = [
        f"- {t['id']}: {indented(clause(t['what']), 2)}. Builds on {listed(t['builds_on'])}.\n\n"
        + "\n".join(
            f"  - {indented(clause(c['what']), 4)}. Serves {listed(c['contributes_to'])}."
            for c in t["completion_criteria"]
        )
        for t in plan["tasks"]
    ]
    for heading, items in (("Goals", goals), ("Acceptance criteria", criteria), ("Tasks", tasks)):
        if items:
            parts.append(f"## {heading}\n\n" + "\n\n".join(items))
    waiting = f", the {status['stage']} sign-off waiting" if status["awaiting_signoff"] else ""
    opened = [f"- {indented(q, 2)}" for q in status["open_questions"]] or ["None."]
    parts.append(
        f"## Where it stands\n\nStage: {status['stage']}{waiting}.\n\n"
        f"Next: {status['next_step']}\n\nOpen:\n\n" + "\n".join(opened)
    )
    return "\n\n".join(parts) + "\n"


def decided(plan: dict[str, Any]) -> dict[str, str]:
    """What the plan says of each goal, with why, and of each acceptance criterion, by its ID, in
    the order of the plan."""
    found = {g["id"]: f"{clause(g['what'])}. {g['why']}" for g in plan["goals"]}
    found.update((c["id"], c["what"]) for c in plan["acceptance_criteria"])
    return found


def task_of(plan: dict[str, Any], task_id: str) -> dict[str, Any] | None:
    """The plan's task of the ID, None where it holds none."""
    return next((t for t in plan["tasks"] if t["id"] == task_id), None)


def without(plan: dict[str, Any], gone: Collection[str]) -> dict[str, Any]:
    """The plan without each task of the IDs, as the steering holds only what is left."""
    return {**plan, "tasks": [t for t in plan["tasks"] if t["id"] not in gone]}


def told_done(plan: dict[str, Any], done: list[str]) -> str:
    """The line telling the user what the tasks done are and what comes next: what the last of them
    brought weighed against the plan; "" where none is done."""
    if not done:
        return ""
    what = {t["id"]: t["what"] for t in plan["tasks"]}
    said = "; ".join(f"{one}, {lowered(clause(what[one]))}" for one in done)
    return f"Done: {said}. Next: what {done[-1]} brought is weighed against the plan."


def lowered(said: str) -> str:
    """The text with its first letter in lower case, as it goes on a sentence."""
    return said[:1].lower() + said[1:]
