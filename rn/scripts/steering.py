"""The steering, the map to the user's purpose kept current: its form, rn's plan checklist's F-1, read
and held at every keep, as rn's scripts read their data from it and the user reads the same file at
each sign-off; written back in that form's layout; and changed only as a move changes it, each
action done ticked, each task done taken out and each part turn made put back."""

from __future__ import annotations

import itertools
import re
from typing import NamedTuple

import stop
import template

# The stages that are named as the work made at them: the plan, the finished work and the
# learnings.
PLAN = "plan"
LEARNINGS_WORK = "learnings"
DELIVERABLE = "deliverable"
# The front matter's key of the stage, by which a CCS names the stage it was made in too.
STAGE = "stage"
# The steering's front matter keys, in the order rn writes them; those of the languages go into
# every CCS.
KEYS = ("rn", "pr", "stage", "signoff", "artifact-language", "conversation-language")
LANGUAGES = ("artifact-language", "conversation-language")
# The stages, in their order, and the sign-offs, each a stage of its name too; `none` where no
# sign-off waits, and as the pull request before `start` opened it.
DESIGN = "design"
BUILD = "build"
FINISHED = "finished"
STAGES = (PLAN, DESIGN, BUILD, DELIVERABLE, LEARNINGS_WORK, FINISHED)
NONE = "none"
VALUES = {"stage": STAGES, "signoff": (NONE, PLAN, DESIGN, DELIVERABLE)}
# The stage the user's approval at each sign-off moves the session to.
APPROVED = {PLAN: DESIGN, DESIGN: BUILD, DELIVERABLE: LEARNINGS_WORK}
# The stages `state --stage` moves the session to, each from the one it moves from, as the others
# move at the sign-offs: build from the design stage where it made no document, so the design
# sign-off has nothing to show.
MOVES = {BUILD: DESIGN, DELIVERABLE: BUILD, FINISHED: LEARNINGS_WORK}
# The steering's `##` headings, in their order: the criteria and the tasks once made, while some
# are, Next and Open always.
CRITERIA = "Acceptance criteria"
TASKS = "Tasks"
NEXT = "Next"
OPEN = "Open"
HEADINGS = (CRITERIA, TASKS, NEXT, OPEN)


# The forms of rn's plan checklist's F-1: the title, the goal on a line of its own under it, and
# each criterion, task and point open an item of its section's list, as each learning is of the
# learnings, the lines indented under an item its own; with each in words, as a stop names it.
TITLE = re.compile(r"# \S.*")
TITLE_FORM = "`# <the piece of work, in a few words>`"
GOAL = re.compile(r"G1: \S.*")
GOAL_FORM = "`G1: <the user's purpose, with why they want it>`"
CRITERION = re.compile(r"- (?P<id>AC[0-9]+): \S.*")
CRITERION_FORM = (
    "an acceptance criterion as `- AC<n>: <one thing the finished work must do for the goal>`"
)
TASK = re.compile(r"- (?P<id>T[0-9]+): \S.*")
TASK_FORM = "a task as `- T<n>: <the result it makes>. Serves <G1, or the criteria by ID>.`"
# What a task's line ends with: the goal or the criteria it serves, by their IDs, as a list in words.
SERVED = re.compile(r".* Serves (?P<ids>(?:G1|AC[0-9]+)(?:(?:,? and |, )(?:G1|AC[0-9]+))*)\.")
ID = re.compile(r"G1|AC[0-9]+")
COMPLETION = re.compile(r"  Completion criterion: \S.*")
COMPLETION_FORM = (
    "`  Completion criterion: <what its result must do for what it serves, and the check that"
    " shows it>`"
)
ACTION = re.compile(r"  - \[(?P<tick>[ x])\] (?P<number>[0-9]+)\. \S.*")


OPENED = re.compile(r"- (?P<id>\S.*)")
OPEN_FORM = "each point open as `- <what is open>`"
NOTHING_OPEN = "None."
# An action done, as `state --done` takes it: its task's ID and its number.
DONE = re.compile(r"(T[0-9]+)\.([0-9]+)")
# Where the tick stands on an action's line.
TICK = 5
# The parts of the steering a proposal shows, by the heading each is under, "" for the part above
# the first, with how each line holding an ID in it begins.
SHOWS = {"": "G1: ", CRITERIA: "- "}


# A pull request's URL, after the repository's.
PULL = re.compile(r"(\S+)/pull/[0-9]+")


def keys_of(text: str) -> dict[str, str]:
    """The `key: value` lines of the front matter the text opens with, as lane reads them; none
    where it opens with no front matter, or holds one lane cannot read, as nothing it says can be
    told."""
    try:
        found = template.keys(text.splitlines()) or {}
    except ValueError:
        return {}
    return {key: value for key, (_, value) in found.items()}


def sections(lines: list[str]) -> dict[str, list[tuple[int, str]]]:
    """Each part of the steering's body under a `##` heading, by the heading's text, and the part
    above the first under "", each as its lines with their numbers, counted from 1."""
    start = template.body(lines)
    heads = {n: said for n, level, said in template.headings(lines, start) if level == 2}
    part = ""
    found: dict[str, list[tuple[int, str]]] = {part: []}
    for n, line in enumerate(lines[start:], start + 1):
        if n in heads:
            part = heads[n]
            found[part] = []
        else:
            found[part].append((n, line))
    return found


def trimmed(lines: list[str]) -> list[str]:
    """The lines without the blank ones they open and end with."""
    words = [k for k, line in enumerate(lines) if line.strip()]
    return lines[words[0] : words[-1] + 1] if words else []


class Item(NamedTuple):
    """An item of a list of the steering: its ID, and its lines with their numbers, its first and
    each indented or blank under it."""

    id: str
    lines: list[tuple[int, str]]


def items_of(
    part: list[tuple[int, str]], form: re.Pattern[str], words: str
) -> tuple[list[Item], str]:
    """Each item of the part, a list whose items each open with `- ` in the form given, its ID the
    form's `id`, and go on in lines indented under it; with the point the part is out of that form
    by, at its line, "" where it holds: a line neither, an item out of the form, or an ID again."""
    found: list[Item] = []
    for n, line in part:
        if line.startswith("- "):
            item = form.fullmatch(line)
            if item is None:
                return found, f"line {n}: expected {words}, found `{line}`"
            if item["id"] in [i.id for i in found]:
                return found, f"line {n}: expected each ID once, found {item['id']} again"
            found.append(Item(item["id"], [(n, line)]))
        elif found and (line.startswith("  ") or not line.strip()):
            found[-1].lines.append((n, line))
        elif line.strip():
            return (
                found,
                f"line {n}: expected {words}, or a line indented under one, found `{line}`",
            )
    return found, ""


class Task(NamedTuple):
    """A task of the steering: its ID, the number of its line, its line with those it runs on to as
    one, the IDs it serves, None where its line names none, whether it has its completion
    criterion, and each line opening an action under it with its number, as the action it is, None
    where it is out of an action's form."""

    id: str
    n: int
    text: str
    serves: list[str] | None
    completion: bool
    actions: list[tuple[int, str, re.Match[str] | None]]


def task_of(item: Item) -> Task:
    """The task the item of the tasks is."""
    n = item.lines[0][0]
    blank = next((k for k, (_, said) in enumerate(item.lines) if not said.strip()), len(item.lines))
    text = " ".join(said.strip() for _, said in item.lines[:blank])
    served = SERVED.fullmatch(text)
    rest = item.lines[blank:]
    return Task(
        item.id,
        n,
        text,
        None if served is None else ID.findall(served["ids"]),
        any(COMPLETION.fullmatch(said) for _, said in rest),
        [(k, said, ACTION.fullmatch(said)) for k, said in rest if said.startswith("  - ")],
    )


def task_items(lines: list[str]) -> list[Item]:
    """Each item of the tasks of the lines, from a steering's title through its tasks, as far as
    they hold their form."""
    return items_of(sections(lines).get(TASKS, []), TASK, TASK_FORM)[0]


def tasks_of(lines: list[str]) -> list[Task]:
    """Each task of the lines, from a steering's title through its tasks, as far as they hold their
    form."""
    return [task_of(i) for i in task_items(lines)]


def is_ticked(action: re.Match[str]) -> bool:
    """Whether the action, read in its form, is ticked."""
    return action["tick"] == "x"  # pragma: no mutate


def all_ticked(task: Task) -> bool:
    """Whether every action of the task is ticked."""
    return all(action is not None and is_ticked(action) for _, _, action in task.actions)


def out_of_form(text: str) -> str:
    """The point the steering's text is out of the form of rn's plan checklist's F-1 by, at its
    line, what was expected and what was found; "" where it holds."""
    lines = text.splitlines()
    try:
        found = template.keys(lines)
    except ValueError as unread:
        return str(unread)
    return keys_out(found) or body_out(lines)


def keys_out(found: dict[str, tuple[int, str]] | None) -> str:
    """The point the steering's front matter, as lane reads it, is out of its form by: each key of
    F-1 in order and no other, each with a value, the stage and the sign-off each one of theirs, and
    the pull request's URL, or none before `start` opened it; "" where it holds."""
    if found is None:
        return "line 1: expected the front matter opened by `---`, found none"
    if list(found) != list(KEYS):
        return (
            f"expected the front matter's keys {', '.join(KEYS)} in that order, found"
            f" {', '.join(found) or 'none'}"
        )
    for key, (n, value) in found.items():
        if not value:
            return f"line {n}: expected a value for {key}, found none"
    for key, taken in VALUES.items():
        n, value = found[key]
        if value not in taken:
            return f"line {n}: expected {key} to be {stop.joined(list(taken), 'or')}, found {value}"
    n, pr = found["pr"]
    if pr != NONE and not PULL.fullmatch(pr):
        return (
            f"line {n}: expected pr to be the pull request's URL, or none before it is opened,"
            f" found {pr}"
        )
    return ""


def body_out(lines: list[str]) -> str:
    """The point the steering's body is out of its form by: the title first, the goal under it,
    the headings of F-1 each once in order, Next and Open always, each list of IDs in its form,
    each task in its, Next some text, and Open `None.` or its points; "" where it holds."""
    start = template.body(lines)
    first = next(
        ((n, line) for n, line in enumerate(lines[start:], start + 1) if line.strip()), None
    )
    if first is None or not TITLE.fullmatch(first[1]):
        found = f"`{first[1]}`" if first else "none"
        return f"expected the title as {TITLE_FORM} first, found {found}"
    heads = template.headings(lines, first[0])
    order = [h for h in HEADINGS if h in [said for _, _, said in heads]]
    for (n, level, said), wanted in itertools.zip_longest(heads, order):
        if level != 2 or said != wanted:
            allowed = stop.joined([f"`## {h}`" for h in HEADINGS])
            return (
                f"line {n}: expected only the headings {allowed}, each once and in that order,"
                f" found `{lines[n - 1]}`"
            )
    parts = sections(lines)
    for heading in (NEXT, OPEN):
        if heading not in parts:
            return f"expected the heading `## {heading}`, found none"
    # The lines with words after the title, and the paragraph the first of them opens, which is the
    # goal's alone.
    goal = [(n, line) for n, line in parts[""] if line.strip()][1:]
    after = parts[""][parts[""].index(goal[0]) :] if goal else []
    paragraph = list(itertools.takewhile(lambda x: x[1].strip(), after))
    if goal and (not GOAL.fullmatch(goal[0][1]) or goal[len(paragraph) :]):
        return (
            f"line {goal[0][0]}: expected the goal as {GOAL_FORM}, one paragraph under the title,"
            f" found `{goal[0][1]}`"
        )
    criteria, point = listed(parts, CRITERIA, CRITERION, CRITERION_FORM)
    if point:
        return point
    held = {"G1"} if goal else set()
    held.update(i.id for i in criteria)
    tasks, point = listed(parts, TASKS, TASK, TASK_FORM)
    for task in map(task_of, tasks):
        point = point or task_out(task, held)
    if point:
        return point
    if not any(line.strip() for _, line in parts[NEXT]):
        return f"expected the step of /rn:up to take next under `## {NEXT}`, found none"
    return open_out(parts[OPEN])


def listed(
    parts: dict[str, list[tuple[int, str]]], heading: str, form: re.Pattern[str], words: str
) -> tuple[list[Item], str]:
    """The items of the list under the heading, none where the steering has no such heading yet,
    with the point they are out of their form by, at least one item among it; "" where they hold."""
    if heading not in parts:
        return [], ""
    items, point = items_of(parts[heading], form, words)
    if not point and not items:
        point = f"expected {words} under `## {heading}`, found none"
    return items, point


def task_out(task: Task, held: set[str]) -> str:
    """The point the task is out of its form by: its line ending with the goal or the criteria it
    serves, each of them the steering holds, its completion criterion, and its actions numbered
    from 1, some not ticked, as a task done leaves the steering; "" where it holds."""
    if task.serves is None:
        return (
            f"line {task.n}: expected {task.id} to end `Serves <G1, or the criteria by ID>.`, found"
            f" `{task.text}`"
        )
    stray = [i for i in task.serves if i not in held]
    if stray:
        return (
            f"line {task.n}: expected {task.id} to serve only the goal and the criteria the"
            f" steering holds, found {stray[0]}"
        )
    if not task.completion:
        return f"line {task.n}: expected {COMPLETION_FORM} under {task.id}, found none"
    if not task.actions:
        return f"line {task.n}: expected the actions of {task.id}, found none"
    for number, (n, line, action) in enumerate(task.actions, 1):
        if action is None or action["number"] != str(number):
            return (
                f"line {n}: expected action {number} of {task.id} as `  - [ ] {number}. <what is"
                f" done>. <who does it>`, found `{line}`"
            )
    if all_ticked(task):
        return (
            f"line {task.n}: expected only tasks with an action not ticked, as a task leaves the"
            f" steering once all its actions are, found {task.id} with every action ticked"
        )
    return ""


def open_out(part: list[tuple[int, str]]) -> str:
    """The point what is open is out of its form by: `None.` alone, or each point an item; "" where
    it holds."""
    if [line for _, line in part if line.strip()] == [NOTHING_OPEN]:
        return ""
    items, point = items_of(part, OPENED, OPEN_FORM)
    if not point and not items:
        point = f"expected `{NOTHING_OPEN}`, or {OPEN_FORM}, under `## {OPEN}`, found none"
    return point


class Steering(NamedTuple):
    """The steering's parts as rn writes them: the front matter's keys, the lines from the title
    through the tasks, Next, and the lines under Open."""

    keys: dict[str, str]
    plan: list[str]
    next: str
    open: list[str]


def parsed(text: str) -> Steering:
    """The parts of the steering's text, which holds its form."""
    lines = text.splitlines()
    start = template.body(lines)
    # Every heading after the title is a `##` one, as the form holds, and a title of the words of
    # Next or Open comes before that heading, which takes its place.
    heads = {said: n for n, _, said in template.headings(lines, start)}
    return Steering(
        keys_of(text),
        trimmed(lines[start : heads[NEXT] - 1]),
        "\n".join(trimmed(lines[heads[NEXT] : heads[OPEN] - 1])),
        trimmed(lines[heads[OPEN] :]),
    )


def render(steered: Steering) -> str:
    """The steering's text, its parts as F-1 lays them out, a blank line between each."""
    front = "".join(f"{key}: {value}\n" for key, value in steered.keys.items())
    parts = [
        "\n".join(steered.plan),
        f"## {NEXT}\n\n{steered.next}",
        f"## {OPEN}\n\n" + "\n".join(steered.open),
    ]
    return f"---\n{front}---\n\n" + "\n\n".join(parts) + "\n"


def held_form(text: str) -> None:
    """Returns when the steering's text holds its form; stops otherwise, keeping nothing."""
    point = out_of_form(text)
    if point:
        raise stop.Stop(
            f"rn: the steering would be out of the form of rn's plan checklist's F-1: {point};"
            " nothing is kept: give what this move writes again so it holds, or have turn make the"
            " part it puts back again"
        )


def opened(points: list[str]) -> list[str]:
    """The lines under Open for the points open: each an item, or `None.` where none is."""
    return [f"- {point}" for point in points] or [NOTHING_OPEN]


def tick(line: str, on: bool) -> str:
    """The action's line with its tick set or not."""
    return f"{line[:TICK]}{'x' if on else ' '}{line[TICK + 1 :]}"


def ticked(plan: list[str], done: list[str]) -> list[str]:
    """The plan's lines with each action done ticked, and each task of them whose actions are then
    all ticked gone, as the steering holds only what is left; stops where the steering holds no
    such action."""
    lines = list(plan)
    actions = {
        f"{task.id}.{action['number']}": n
        for task in tasks_of(lines)
        for n, _, action in task.actions
        if action is not None
    }
    for one in done:
        if not DONE.fullmatch(one) or one not in actions:
            raise stop.Stop(
                f"rn: the steering holds no action {one}; give each action done as T<n>.<action>,"
                " of a task and an action it holds, such as T1.2"
            )
        lines[actions[one] - 1] = tick(lines[actions[one] - 1], True)
    return pruned(lines, {one.partition(".")[0] for one in done})


def pruned(plan: list[str], ids: set[str]) -> list[str]:
    """The plan's lines without each task of the IDs whose actions are all ticked, its lines and the
    blank ones after it, and without the tasks' heading where no task is left."""
    items = task_items(plan)
    gone = [i for i in items if i.id in ids and all_ticked(task_of(i))]
    out = {n for i in gone for n, _ in i.lines}
    lines = trimmed([line for n, line in enumerate(plan, 1) if n not in out])
    if gone and not task_items(lines):
        # The tasks are the plan's last part, so with none left their heading is its last line.
        lines.pop()
    return trimmed(lines)


def put_plan(plan: list[str], part: list[str]) -> list[str]:
    """The part turn made, as the steering's plan: each action ticked as it was in the plan before,
    by its task's ID and its number, the rest not, as the ticks are rn's to write."""
    was = {
        (task.id, action["number"])
        for task in tasks_of(plan)
        for _, _, action in task.actions
        if action is not None and is_ticked(action)
    }
    lines = list(part)
    for task in tasks_of(lines):
        for n, _, action in task.actions:
            if action is not None:
                lines[n - 1] = tick(lines[n - 1], (task.id, action["number"]) in was)
    return lines


def item(lines: list[tuple[int, str]], at_: int) -> str:
    """The text of the line at the index and the lines it runs on to, until a blank line or the
    next item of a list, as one line."""
    words = [lines[at_][1]]
    for _, line in lines[at_ + 1 :]:
        if not line.strip() or line.startswith("- "):
            break
        words.append(line.strip())
    return " ".join(words)


def by_id(lines: list[tuple[int, str]], begins: str) -> dict[str, str]:
    """What the lines say under each ID, each line beginning as given opening one, by its ID, in
    their order, each as one line; read from lines that hold their form."""
    found: dict[str, str] = {}
    for k, (_, line) in enumerate(lines):
        if line.startswith(begins):
            key, _, rest = item(lines, k).removeprefix("- ").partition(": ")
            found[key] = rest
    return found


def decided(lines: list[str], shown: tuple[str, ...]) -> dict[str, str]:
    """What the steering says under each ID in the parts shown, such as the goal and each
    acceptance criterion, by its ID, in the order of the steering, each as one line; read from a
    steering that holds its form."""
    parts = sections(lines)
    found: dict[str, str] = {}
    for part in shown:
        found.update(by_id(parts.get(part, []), SHOWS[part]))
    return found
