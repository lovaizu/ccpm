"""The steering, the map to the user's purpose kept current: its form, the plan in the form of rn's
plan checklist's F-1 under the front matter and above Next and Open, which rn's scripts write, read
and held at every keep, as rn's scripts read their data from it and the user reads the same file at
each sign-off; written back in that form's layout; and changed only as a move changes it, each
action done ticked, each task done taken out and each part turn made put back."""

from __future__ import annotations

import itertools
import re
from typing import NamedTuple

import stop
import template

# The steering's front matter keys, in the order rn writes them; those of the languages go into
# every CCS, and a CCS names the stage it was made in under the stage's key too.
RN = "rn"
PR = "pr"
STAGE = "stage"
SIGNOFF = "signoff"
LANGUAGES = ("artifact-language", "conversation-language")
KEYS = (RN, PR, STAGE, SIGNOFF, *LANGUAGES)
# The stages, in their order, three of them named as the work made at them: the plan, the finished
# work and the learnings.
PLAN = "plan"
DESIGN = "design"
BUILD = "build"
DELIVERABLE = "deliverable"
LEARNINGS = "learnings"
FINISHED = "finished"
STAGES = (PLAN, DESIGN, BUILD, DELIVERABLE, LEARNINGS, FINISHED)
# The sign-offs, each at the stage of its name, with the stage the user's approval there moves the
# session to; `none` where no sign-off waits, and as the pull request before `start` opened it.
APPROVED = {PLAN: DESIGN, DESIGN: BUILD, DELIVERABLE: LEARNINGS}
SIGNOFFS = tuple(APPROVED)
NONE = "none"
VALUES = {STAGE: STAGES, SIGNOFF: (NONE, *SIGNOFFS)}
# The stages `state --stage` moves the session to, each from the one it moves from, as the others
# move at the sign-offs: build from the design stage where it made no document, so the design
# sign-off has nothing to show.
MOVES = {BUILD: DESIGN, DELIVERABLE: BUILD, FINISHED: LEARNINGS}
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
# What a task's line ends with: the goal or the criteria it serves, by their IDs, as a list in
# words.
SERVED = re.compile(r".* Serves (?P<ids>(?:G1|AC[0-9]+)(?:(?:,? and |, )(?:G1|AC[0-9]+))*)\.")
ID = re.compile(r"G1|AC[0-9]+")
COMPLETION = re.compile(r"  Completion criterion: \S.*")
COMPLETION_FORM = (
    "`  Completion criterion: <what its result must do for what it serves, and the check that"
    " shows it>`"
)
# The one command that runs the check a task's completion criterion names, where it is one, on a
# line of its own under it.
TEST = re.compile(r"  Test: `(?P<command>[^`]+)`")
TEST_FORM = "`  Test: `<the command>``"
# Each action opens a line of its own under its task's completion criterion, ticked or not and
# numbered, and runs on in lines indented under it, in one of two forms: the orchestrator's, with
# the user, or turn's, making one work of a kind at a path, which turn's call is made on.
ACTION = re.compile(r"  - \[(?P<tick>[ x])\] (?P<number>[0-9]+)\. \S.*")
BY_THE_ORCHESTRATOR = re.compile(
    r"  - \[[ x]\] [0-9]+\. (?P<what>\S.*)\. The orchestrator, with the user\."
)
BY_TURN = re.compile(
    r"  - \[[ x]\] [0-9]+\. (?P<what>\S.*, `(?P<path>[^`]+)` as an? (?P<kind>[a-z0-9-]+) work)"
    r"\. turn\."
)
ACTION_FORMS = (
    "in one of the forms of rn's plan checklist's F-1, `  - [ ] {0}. <what is found out or"
    " settled>. The orchestrator, with the user.` or `  - [ ] {0}. <what is made, from which works"
    " before it>, `<its path>` as a <kind> work. turn.`"
)


OPENED = re.compile(r"- (?P<id>\S.*)")
OPEN_FORM = "each point open as `- <what is open>`"
NOTHING_OPEN = "None."
# An action done, as `state --done` takes it: its task's ID and its number.
DONE = re.compile(r"(T[0-9]+)\.([0-9]+)")
# Where the tick stands on an action's line.
TICK = 5
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


class Action(NamedTuple):
    """An action of a task, in one of its forms: its number, whether it is ticked, what is done in
    it, and the path and the kind of the work turn makes in it, None for each where it is the
    orchestrator's."""

    number: str
    ticked: bool
    what: str
    path: str | None
    kind: str | None


class Task(NamedTuple):
    """A task of the steering: its ID, the number of its line, its line with those it runs on to as
    one, the IDs it serves, None where its line names none, whether it has its completion
    criterion, each line giving the command that checks its result with its number, as the command
    it gives, None where it is out of that form, and each line opening an action under it with its
    number, as the action it is, None where it is out of an action's form."""

    id: str
    n: int
    text: str
    serves: list[str] | None
    completion: bool
    tests: list[tuple[int, str, str | None]]
    actions: list[tuple[int, str, Action | None]]


def said(lines: list[tuple[int, str]]) -> str:
    """The first of the lines and those it runs on to, until a blank line, as one line, without the
    indent of each."""
    return " ".join(itertools.takewhile(bool, (line.strip() for _, line in lines)))


def task_of(item: Item) -> Task:
    """The task the item of the tasks is."""
    n = item.lines[0][0]
    first = list(itertools.takewhile(lambda line: line[1].strip(), item.lines))
    text = said(first)
    served = SERVED.fullmatch(text)
    rest = item.lines[len(first) :]
    return Task(
        item.id,
        n,
        text,
        None if served is None else ID.findall(served["ids"]),
        any(COMPLETION.fullmatch(said) for _, said in rest),
        [(k, line, command_in(line)) for k, line in rest if line.startswith("  Test:")],
        actions_of(rest),
    )


def command_in(line: str) -> str | None:
    """The command the line gives as the one that checks a task's result, None where it is out of
    that form."""
    found = TEST.fullmatch(line)
    return found["command"] if found else None


def actions_of(lines: list[tuple[int, str]]) -> list[tuple[int, str, Action | None]]:
    """Each action of the lines under a task's line, by the number of its first line and that line,
    with the action it is, its lines read as one, None where it is in neither form."""
    found: list[tuple[int, str, list[str]]] = []
    for n, line in lines:
        if line.startswith("  - "):
            found.append((n, line, [line]))
        elif found and line.startswith("    ") and found[-1][2][-1].strip():
            found[-1][2].append(line.strip())
        elif found:
            found[-1][2].append("")
    return [(n, line, action_in(" ".join(filter(None, words)))) for n, line, words in found]


def action_in(text: str) -> Action | None:
    """The action the text of its lines is, None where it is in neither form."""
    head = ACTION.fullmatch(text)
    turns = BY_TURN.fullmatch(text)
    done = turns or BY_THE_ORCHESTRATOR.fullmatch(text)
    if head is None or done is None:
        return None
    return Action(
        head["number"],
        is_ticked(head),
        done["what"],
        turns["path"] if turns else None,
        turns["kind"] if turns else None,
    )


def task_items(lines: list[str]) -> list[Item]:
    """Each item of the tasks of the lines, from a steering's title through its tasks, as far as
    they hold their form."""
    return items_of(sections(lines).get(TASKS, []), TASK, TASK_FORM)[0]


def tasks_of(lines: list[str]) -> list[Task]:
    """Each task of the lines, from a steering's title through its tasks, as far as they hold their
    form."""
    return [task_of(i) for i in task_items(lines)]


def is_ticked(head: re.Match[str]) -> bool:
    """Whether the action whose first line is read in its form is ticked."""
    return head["tick"] == "x"  # pragma: no mutate


def all_ticked(task: Task) -> bool:
    """Whether every action of the task is ticked."""
    return all(action is not None and action.ticked for _, _, action in task.actions)


def out_of_form(text: str) -> str:
    """The point the steering's text is out of its form by, at its line, what was expected and what
    was found: the front matter, Next and Open as rn's scripts write them, and the plan between them
    as rn's plan checklist's F-1 gives it; "" where it holds."""
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
    n, pr = found[PR]
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
    for k, (n, line, command) in enumerate(task.tests):
        if command is None:
            return (
                f"line {n}: expected the one command that runs {task.id}'s check as {TEST_FORM},"
                f" found `{line}`"
            )
        if k:
            return (
                f"line {n}: expected the one command that runs {task.id}'s check once, found"
                f" `{line}`"
            )
    if not task.actions:
        return f"line {task.n}: expected the actions of {task.id}, found none"
    for number, (n, line, action) in enumerate(task.actions, 1):
        if action is None or action.number != str(number):
            return (
                f"line {n}: expected action {number} of {task.id} {ACTION_FORMS.format(number)},"
                f" found `{line}`"
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
            f"rn: the steering would be out of its form: {point};"
            " nothing is kept: give what this move writes again so it holds, or have turn make the"
            " part it puts back again"
        )


def opened(points: list[str]) -> list[str]:
    """The lines under Open for the points open: each an item, or `None.` where none is."""
    return [f"- {point}" for point in points] or [NOTHING_OPEN]


def told_done(plan: list[str], done: list[str]) -> str:
    """The line telling the user what the actions done are and what comes next: the action after
    the last of them, or, where it was its task's last, the task weighed; "" where none is done."""
    if not done:
        return ""
    actions = {
        f"{task.id}.{action.number}": (task.id, action)
        for task in tasks_of(plan)
        for _, _, action in task.actions
        if action is not None
    }
    task_id, last = actions[done[-1]]
    after = [
        a for key, (t, a) in actions.items() if t == task_id and int(a.number) > int(last.number)
    ]
    following = (
        f"{task_id}.{after[0].number}, {lowered(after[0].what)}"
        if after
        else f"what {task_id} brought is weighed against the plan"
    )
    said = "; ".join(f"{one}, {lowered(actions[one][1].what)}" for one in done)
    return f"Done: {said}. Next: {following}."


def lowered(text: str) -> str:
    """The text with its first letter in lower case, as it goes on a sentence."""
    return text[:1].lower() + text[1:]


def tick(line: str, on: bool) -> str:
    """The action's line with its tick set or not."""
    return f"{line[:TICK]}{'x' if on else ' '}{line[TICK + 1 :]}"


def ticked(plan: list[str], done: list[str]) -> list[str]:
    """The plan's lines with each action done ticked, and each task of them whose actions are then
    all ticked gone, as the steering holds only what is left; stops where the steering holds no
    such action."""
    lines = list(plan)
    actions = {
        f"{task.id}.{action.number}": n
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
        (task.id, action.number)
        for task in tasks_of(plan)
        for _, _, action in task.actions
        if action is not None and action.ticked
    }
    lines = list(part)
    for task in tasks_of(lines):
        for n, _, action in task.actions:
            if action is not None:
                lines[n - 1] = tick(lines[n - 1], (task.id, action.number) in was)
    return lines


def decided(lines: list[str], goal: bool = True) -> dict[str, str]:
    """What the steering says under the goal, where asked, and under each acceptance criterion, by
    its ID, in the order of the steering, each as one line; read from a steering that holds its
    form."""
    parts = sections(lines)
    found: dict[str, str] = {}
    above = parts[""]
    start = next((k for k, (_, line) in enumerate(above) if GOAL.fullmatch(line)), None)
    if goal and start is not None:
        found["G1"] = said(above[start:]).partition(": ")[2]
    criteria = items_of(parts.get(CRITERIA, []), CRITERION, CRITERION_FORM)[0]
    found.update((i.id, said(i.lines).partition(": ")[2]) for i in criteria)
    return found
