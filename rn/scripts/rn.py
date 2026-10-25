"""What rn's orchestrator runs for what must come out the same on every run, so that a rule a machine
can judge holds at the moment of the move: the session found and started with its draft pull
request, the steering rewritten and every change kept on the session's branch, each decision kept in
the call to turn it settles, the CCS each work is made from, a kind's checklists, the proposal at a
sign-off made from what is pushed alone, the user's answer to it kept, and the records and the
learnings the session's learnings are made from.

The orchestrator is the AI that runs rn's commands `/rn:up`, `/rn:ty` and `/rn:gm` with the user. A
session is one piece of work from `/rn:up` to the merge, on a branch of its own; its record is the
folder `.rn/<yyyymmdd>-<slug>/` on that branch, the slug a short name for the piece of work, holding
the steering `steering.md`, the plan and where the session stands, holding only what is left to do;
the learnings `learnings.md`, once some are made; and `turn/`, each call to turn as the files of one
number, four digits from 0001 in the order made: the CCS `<nnnn>-ccs.json`, turn's result
`<nnnn>-result.json` once it returned, and the part the call makes, for a call on the plan
`<nnnn>-steering.md`, the part of the steering, and for one on the learnings `<nnnn>-learnings.md`,
the learnings it adds. A CCS is the shape ACC gives an AI's state: a JSON object of parts, each a
list of entries, each entry a kind and its value as text. A work, such as the plan, a task's result
or the finished work, is made by turn, a plugin rn depends on, from such a CCS, which names the work
and the stage it was made in; a work's latest call is the highest number naming it. A kind, such as
readme or code, has rn's own checklist, and may have the user's addition `.rn/checklists/<kind>.md`.
At a sign-off, plan, design or deliverable, the orchestrator shows the user a proposal and waits for
`/rn:ty` or `/rn:gm`, whose answer it keeps.

The steering and the learnings are written by these scripts alone, the steering in the form of rn's
plan checklist's F-1: every keep refuses a steering that differs from what the last keep left, and
one the move would leave out of that form. Keeping a move is a commit of every change on the
session's branch and a push of it, so a fresh conversation, or another machine, goes on from it; a
work is handed to turn only once everything is pushed.

Run from the top of the user's repository as `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/rn.py"
<subcommand> ...`, with Python 3.9 or later and the standard library alone. It prints JSON, or the
proposal as text for the orchestrator to show, and on a stop exits 1 with what went wrong and what
to do.
"""

from __future__ import annotations

import argparse
import datetime
import functools
import glob
import itertools
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from collections.abc import Callable
from typing import Any, NamedTuple, NoReturn

# turn's reader of Claude Code's records, and lane's of a Markdown file's front matter and headings,
# each taken through a link.
import records
import template

# The plugin's own folder, which holds rn's checklists and its manifest.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The folder in the user's repository holding every session's record and the user's checklists.
RECORD = ".rn"
# A slug or a kind is a name that goes into a path, so it holds nothing that leads out of the folder
# it is meant for.
NAME = re.compile(r"[a-z0-9-]+")
SESSION_NAME = re.compile(r"[0-9]{8}-[a-z0-9-]+")
# The session's steering, its learnings, and the folder of its calls to turn, in the session's
# folder.
STEERING = "steering.md"
LEARNT = "learnings.md"
TURN = "turn"
# A file of a call to turn, by its number and what it is: the CCS, turn's result, or the part the
# call makes.
CALL = re.compile(r"([0-9]{4})-(ccs\.json|result\.json|steering\.md|learnings\.md)")
CCS = "ccs.json"
RESULT = "result.json"
# The works rn has turn make: the plan, the part of the steering from the title through the tasks,
# as a task of the plan stage makes the plan; its learnings; what task T<n> makes outside the
# steering; the finished work; and a checklist of a kind.
PLAN = "plan"
LEARNINGS_WORK = "learnings"
DELIVERABLE = "deliverable"
TASK_WORK = re.compile(r"t[0-9]+")
CHECKLIST_WORK = re.compile(r"checklist-[a-z0-9-]+")
WORKS = "plan, learnings, deliverable, t<n> for task T<n>, or checklist-<kind>"
# The works whose call makes a part, cut into a file of its own, each with what its file is named:
# the plan's a part of the steering, the learnings' those it adds to the session's.
PART = {PLAN: "steering.md", LEARNINGS_WORK: "learnings.md"}
PARTS = tuple(PART)
# For each role turn reads from a CCS, the key of the CCS entries that hold it; the call to turn:up
# hands this table to turn.
ENTRIES = {
    "work": "deliverable",
    "checklist": "checklist",
    "receiver": "audience",
    "use": "purpose",
    "has": "has",
}
# The keys of the CCS entries rn reads back: the work's name and the stage it was made in, each
# decision of the work as `<title>: <what it says>`; and that of each goal and criterion it serves.
WORK = "work"
STAGE = "stage"
DECISION = "decision"
SERVES = "serves"
# The kind of a checklist, which rn's checklist for checklists makes from rn's `usability.md`, what
# any reader needs, as well.
CHECKLIST = "checklist"
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
# The heading a part of the learnings opens with, which rn cuts for turn and leaves out when it
# adds the learnings to the session's.
LEARNINGS = "Learnings"
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
LEARNING = re.compile(r"- (?P<id>L[0-9]+): \S.*")
LEARNING_FORM = (
    "a learning as `- L<n>: <what happened, with the words it rests on, and where it would make"
    " later work better>`"
)
NUMBERED = re.compile(r"- L[0-9]+: ")
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
# The sign-offs, each with the words naming where the work is.
SIGNOFFS = {
    PLAN: "The plan is on the draft pull request",
    DESIGN: "The design is on the draft pull request",
    DELIVERABLE: "The finished work is on the pull request",
}
# The works whose decisions a sign-off shows, by the stage they were called in and their names: at
# the design's, each task's and checklist's called in the design stage; at the deliverable's, each
# task's called in the build stage.
WORKS_SHOWN = {
    DESIGN: (DESIGN, re.compile(rf"{TASK_WORK.pattern}|{CHECKLIST_WORK.pattern}")),
    DELIVERABLE: (BUILD, TASK_WORK),
}
ANSWERS = ("approved", "feedback")
ANSWER = "/rn:ty to approve, /rn:gm <feedback> to ask for a change."
# The most decisions of a work a sign-off shows, and the most characters of each, as five short
# lines are what a glance at the proposal takes in; a work past them is not yet simple.
MOST = 5
LONGEST = 200
# A pull request's URL, after the repository's.
PULL = re.compile(r"(\S+)/pull/[0-9]+")
# The folder in the repository's git folder where the records the learnings are made from are shown,
# so nothing of it shows as a change to keep.
LEARNING_PLACE = "rn"
# Claude Code names the folder of a project's records by the project's path, each character that is
# not a letter or digit as `-`, counted as JavaScript counts, a character beyond the basic plane as
# two; a name longer than this is cut to it and a hash of the path put after, which rn does not make
# again, so it finds that folder by what goes before the hash.
NAME_LENGTH = 200
# What a stop whose git command failed says to do where only git's own words tell what is wrong.
AS_GIT_SAYS = "fix it as git says, then run this again"


class Stop(Exception):
    """What went wrong, and what to do about it."""


def named(value: str, what: str) -> str:
    """The value, when it is a name; stops otherwise."""
    if not NAME.fullmatch(value):
        raise Stop(
            f"rn: the {what} {value!r} is not lowercase letters, digits and hyphens alone;"
            f" give it as such, such as add-login"
        )
    return value


def worked(work: str) -> str:
    """The work, when it names one rn has turn make; stops otherwise."""
    if work not in PARTS + (DELIVERABLE,) and not (
        TASK_WORK.fullmatch(work) or CHECKLIST_WORK.fullmatch(work)
    ):
        raise Stop(f"rn: the work {work!r} is none rn makes; give {WORKS}, such as t1")
    return work


def given(value: str, what: str) -> str:
    """The value, when it holds some text; stops otherwise."""
    if not value.strip():
        raise Stop(f"rn: the {what} is empty; give it in words")
    return value


def ran(command: list[str], failed: str, fed: str | None = None) -> str:
    """What the command prints, with the text fed to its input; stops with what it said and the
    action given, or where it cannot be run, saying to install it."""
    try:
        done = subprocess.run(command, check=False, capture_output=True, text=True, input=fed)
    except OSError as why:
        raise Stop(
            f"rn: {command[0]} could not be run: {why.strerror}; install it, then run this again"
        ) from None
    if done.returncode:
        said = done.stderr.strip()
        raise Stop(f"rn: {' '.join(command)} failed{': ' + said if said else ''}; {failed}")
    return done.stdout


def git(args: list[str], failed: str, fed: str | None = None) -> str:
    """What git prints for the arguments, with the text fed to its input; stops with what git said
    and the action given."""
    return ran(["git"] + args, failed, fed)


def at_top() -> None:
    """Returns when rn runs at the top of a git repository; stops otherwise."""
    below = git(["rev-parse", "--show-prefix"], "run rn inside the user's repository").strip()
    if below:
        raise Stop(
            f"rn: this runs in {below} below the top of the repository; run it from the top,"
            ' after `cd "$(git rev-parse --show-toplevel)"`'
        )


def default_branch() -> str:
    """The remote's default branch, as git knows it, such as origin/main."""
    ref = git(
        ["symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
        "run `git remote set-head origin --auto` so git knows the default branch, then run this"
        " again",
    )
    return ref.strip()


def base() -> str:
    """The commit the checked-out branch left the default branch at."""
    branch = default_branch()
    return git(
        ["merge-base", branch, "HEAD"],
        f"the checked-out branch shares no history with {branch}; fetch it whole with"
        " `git fetch --unshallow origin` where the clone is shallow, or check out the session's"
        " branch",
    ).strip()


# The files turn keeps beside a call's result while it runs, each named with the result's name and
# a dot, and removed once it returns: no part of the record, so neither kept nor a change to keep.
RUN_FILES = [
    ":(top,exclude,glob).rn/*/turn/*-result.json.*",
    ":(top,exclude,glob).rn/*/turn/*-result.json.*/**",
]


def changed() -> list[str]:
    """Each path of the working tree changed since the last commit, every file of a folder not
    yet added among them, turn's run files left out."""
    listed = git(["status", "--porcelain", "-uall", "--", ":/", *RUN_FILES], AS_GIT_SAYS)
    return [line[3:] for line in listed.splitlines()]


def at(commit: str, path: str) -> str | None:
    """The text of the file at the path as the commit holds it; None where it holds none."""
    if not git(["ls-tree", "--name-only", commit, "--", path], AS_GIT_SAYS):
        return None
    return git(["show", f"{commit}:{path}"], AS_GIT_SAYS)


def keys_of(text: str) -> dict[str, str]:
    """The `key: value` lines of the front matter the text opens with, as lane reads them; none
    where it opens with no front matter, or holds one lane cannot read, as nothing it says can be
    told."""
    try:
        found = template.keys(text.splitlines()) or {}
    except ValueError:
        return {}
    return {key: value for key, (_, value) in found.items()}


def steering_path(folder: str) -> str:
    """The path of the session's steering."""
    return os.path.join(folder, STEERING)


def learnings_path(folder: str) -> str:
    """The path of the session's learnings."""
    return os.path.join(folder, LEARNT)


def call_path(folder: str, number: str, what: str) -> str:
    """The path of a file of the session's call of the number: its CCS, its result or its part."""
    return os.path.join(folder, TURN, f"{number}-{what}")


def session() -> str | None:
    """The session the checked-out branch is in: the folder under `.rn/` the branch changed from
    the default branch whose steering, as the branch's last commit holds it, is not at the finished
    stage, so the move that finishes it is kept and every run after it finds none; None where there
    is none, and a stop where there are more than one."""
    at_top()
    paths = git(["diff", "--name-only", base(), "HEAD", "--", RECORD], AS_GIT_SAYS)
    folders = sorted(
        {
            os.path.join(RECORD, parts[1])
            for parts in (path.split("/") for path in paths.splitlines())
            if SESSION_NAME.fullmatch(parts[1])
        }
    )
    going = [
        f
        for f in folders
        if os.path.isdir(f) and keys_of(at("HEAD", steering_path(f)) or "").get(STAGE) != FINISHED
    ]
    if len(going) > 1:
        raise Stop(
            f"rn: this branch changed more than one session not finished: {', '.join(going)}; a"
            " branch holds one session, so check out the branch of the one to go on with"
        )
    return next(iter(going), None)


def current() -> str:
    """The session the checked-out branch is in; stops where there is none."""
    found = session()
    if found is None:
        raise Stop(
            "rn: the checked-out branch holds no session; start one with `rn.py start <slug>`"
        )
    return found


def read_text(path: str) -> str:
    """The text at the path."""
    with open(path, encoding="utf-8") as f:
        return f.read()


def write_text(path: str, text: str) -> None:
    """Writes the text at the path, making its folder where it is not there."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def write_json(path: str, data: Any) -> None:
    """Writes the data as JSON at the path, one key or value to a line, so the user can read it on
    the pull request."""
    write_text(path, json.dumps(data, ensure_ascii=False, indent=1) + "\n")


def dumped(data: Any) -> str:
    """The data as JSON on one line, with text beyond ASCII as it is, for the orchestrator to
    read."""
    return json.dumps(data, ensure_ascii=False)


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
            return f"line {n}: expected {key} to be {joined(list(taken), 'or')}, found {value}"
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
            allowed = joined([f"`## {h}`" for h in HEADINGS])
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


def render(steering: Steering) -> str:
    """The steering's text, its parts as F-1 lays them out, a blank line between each."""
    front = "".join(f"{key}: {value}\n" for key, value in steering.keys.items())
    parts = [
        "\n".join(steering.plan),
        f"## {NEXT}\n\n{steering.next}",
        f"## {OPEN}\n\n" + "\n".join(steering.open),
    ]
    return f"---\n{front}---\n\n" + "\n\n".join(parts) + "\n"


def held_form(text: str) -> None:
    """Returns when the steering's text holds its form; stops otherwise, keeping nothing."""
    point = out_of_form(text)
    if point:
        raise Stop(
            f"rn: the steering would be out of the form of rn's plan checklist's F-1: {point};"
            " nothing is kept: give what this move writes again so it holds, or have turn make the"
            " part it puts back again"
        )


def kept_steering(folder: str) -> Steering:
    """The steering as the last keep left it; stops where the working tree's differs from it, with
    how to restore it, or where it is out of its form, as only a commit made by hand leaves it."""
    path = steering_path(folder)
    last = at("HEAD", path)
    if (read_text(path) if os.path.isfile(path) else None) != last:
        raise Stop(
            f"rn: {path} differs from what the last keep left, and rn's scripts alone write it;"
            f" restore it with `git checkout HEAD -- {path}`, then run this again"
        )
    point = out_of_form(last or "")
    if point:
        raise Stop(
            f"rn: {path} as the last commit holds it is out of the form of rn's plan checklist's"
            f" F-1: {point}; rn keeps none so, so restore the last one rn kept from"
            f" `git log -p -- {path}`, commit it, then run this again"
        )
    return parsed(last or "")


def keep(folder: str, steering: Steering, message: str) -> str:
    """Keeps the move: the steering written, once it holds its form, and every change of the move
    committed with the message, then pushed; gives the commit. Stops, writing nothing, where the
    steering is out of its form; and where git fails."""
    text = render(steering)
    held_form(text)
    write_text(steering_path(folder), text)
    if changed():
        git(["add", "-A", "--", ":/", *RUN_FILES], AS_GIT_SAYS)
        git(["commit", "-q", "-F", "-"], AS_GIT_SAYS, message)
    push()
    return git(["rev-parse", "HEAD"], AS_GIT_SAYS).strip()


def push() -> None:
    """Pushes the checked-out branch to the remote's branch of its name, tracking it; stops with
    what git said and how to push once it is fixed."""
    git(
        ["push", "-q", "-u", "origin", "HEAD"],
        "fix it as git says, then push with `git push -u origin HEAD`",
    )


def pushed() -> None:
    """Returns when every change is committed and pushed, so what rn goes on from is what a fresh
    conversation would find; stops otherwise, saying how to keep or push it."""
    paths = changed()
    if paths:
        raise Stop(
            f"rn: the record has changes not kept, {', '.join(paths)}; rn goes on only from what is"
            " pushed, so keep the move with `rn.py state --next <n> --message <what it brought>`"
            " first, then run this again"
        )
    ahead = git(
        ["rev-list", "--count", "@{upstream}..HEAD"],
        "push the branch with `git push -u origin HEAD`, then run this again",
    ).strip()
    if int(ahead):
        raise Stop(
            f"rn: the branch has {ahead} commit(s) not pushed; push with `git push`, then run this"
            " again"
        )


class Call(NamedTuple):
    """A call to turn: its number, the work it is on and the stage it was made in, as its CCS names
    them, its CCS, and whether turn returned its result."""

    number: str
    work: str
    stage: str
    ccs: dict[str, list[dict[str, str]]]
    result: bool


def entry(ccs: dict[str, list[dict[str, str]]], key: str) -> str:
    """The first value of the key in the CCS; "" where none is."""
    return next((e[key] for part in ccs.values() for e in part if key in e), "")


def calls(folder: str, commit: str | None = None) -> list[Call]:
    """Each call to turn of the session, in the order made, as the working tree holds them, or the
    commit given; stops where a CCS is no JSON object, saying how to restore it."""
    place = os.path.join(folder, TURN)
    read: Callable[[str], str | None] = read_text
    if commit is None:
        names = os.listdir(place) if os.path.isdir(place) else []
    else:
        listed = git(["ls-tree", "--name-only", commit, "--", f"{place}/"], AS_GIT_SAYS)
        names = [os.path.basename(p) for p in listed.splitlines()]
        read = functools.partial(at, commit)
    # What files each number has.
    files: dict[str, set[str]] = {}
    for m in filter(None, map(CALL.fullmatch, names)):
        files.setdefault(m[1], set()).add(m[2])
    found = []
    for number in sorted(n for n, what in files.items() if CCS in what):
        path = call_path(folder, number, CCS)
        try:
            ccs = json.loads(read(path) or "")
        except ValueError:
            ccs = None
        if not isinstance(ccs, dict):
            raise Stop(
                f"rn: {path} is no CCS, a JSON object; restore it with `git checkout HEAD --"
                f" {path}`, as rn's scripts alone write it, then run this again"
            )
        found.append(
            Call(number, entry(ccs, WORK), entry(ccs, STAGE), ccs, RESULT in files[number])
        )
    return found


def latest(found: list[Call], work: str) -> Call | None:
    """The work's latest call; None where it has none."""
    return next((c for c in reversed(found) if c.work == work), None)


def decisions_of(call: Call) -> list[str]:
    """Each decision of the call, in the order kept."""
    return [e[DECISION] for e in call.ccs.get("constraints", []) if DECISION in e]


def next_number(found: list[Call]) -> str:
    """The number of a new call, the one after the last."""
    return f"{int(found[-1].number) + 1 if found else 1:04d}"


def run_session(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """The session the checked-out branch is in, with its stage and the sign-off waiting, as its
    steering's last commit holds them; None for each where there is none. Stops where rn is not at
    the top of a repository, git cannot tell the branch's changes, or the branch changed more than
    one session not finished."""
    found = session()
    if found is None:
        return {"session": None, "stage": None, "signoff": None}
    keys = keys_of(at("HEAD", steering_path(found)) or "")
    signoff = keys.get("signoff")
    return {
        "session": found,
        "stage": keys.get(STAGE),
        "signoff": None if signoff in (None, NONE) else signoff,
    }


def version(root: str) -> str:
    """rn's version, as its manifest gives it; stops where it gives none."""
    path = os.path.join(root, ".claude-plugin", "plugin.json")
    try:
        with open(path, encoding="utf-8") as f:
            return str(json.load(f)["version"])
    except (OSError, ValueError, KeyError):
        raise Stop(f"rn: {path} gives no version of rn; install rn again") from None


def gh(args: list[str]) -> str:
    """What GitHub's command prints for the arguments; stops with what it said, and how to go on
    once it is fixed."""
    return ran(
        ["gh"] + args,
        "fix it as gh says, such as with `gh auth login`, then run `rn.py start` again with the"
        " same arguments on this branch",
    ).strip()


def run_start(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Starts a session on a branch of its own named by the slug, made from the remote's default
    branch as it is now: its steering at the plan stage, with rn's version, the languages, the
    title, Next and nothing open, kept with the message; then the draft pull request opened, its
    body linking the steering, and its URL kept as the steering's pr. Run again on that branch where
    the pull request was not opened, it opens it. Gives the folder, the branch and the pull request.
    Stops, leaving the checked-out branch as it is, where a value is not given in its form, rn is
    not at the top of a repository, the working tree has changes not committed, the folder or the
    branch is there already, or rn's version is not there; and where git or gh fails."""
    slug = named(args.slug, "slug")
    title = given(args.title, "title")
    languages = {key: given(getattr(args, key.replace("-", "_")), key) for key in LANGUAGES}
    next_step = given(args.next, "next step")
    message = given(args.message, "message")
    at_top()
    paths = changed()
    if paths:
        raise Stop(
            f"rn: the working tree has changes not committed: {', '.join(paths)}; rn leaves them as"
            " they are, and starts from the default branch: commit or stash them, then run this"
            " again"
        )
    if git(["branch", "--show-current"], AS_GIT_SAYS).strip() == slug:
        folder = current()
        steering = kept_steering(folder)
        if steering.keys["pr"] != NONE:  # pragma: no mutate
            raise Stop(
                f"rn: the session {folder} is started already, with its pull request"
                f" {steering.keys['pr']}; go on with it with /rn:up"
            )
    else:
        git(["fetch", "-q", "origin"], AS_GIT_SAYS)
        branch = default_branch()
        folder = os.path.join(RECORD, f"{today:%Y%m%d}-{slug}")
        if git(["ls-tree", "--name-only", branch, "--", folder], AS_GIT_SAYS):
            raise Stop(f"rn: {folder} is on {branch} already; give another slug")
        keys = {"rn": version(root), "pr": NONE, STAGE: PLAN, "signoff": NONE, **languages}
        steering = Steering(keys, [f"# {title}"], next_step, [NOTHING_OPEN])
        held_form(render(steering))
        git(["checkout", "-q", "--no-track", "-b", slug, branch], "give another slug")
        keep(folder, steering, message)
    repository = gh(["repo", "view", "--json", "url", "--jq", ".url"])
    link = f"[{STEERING}]({repository}/blob/{slug}/{steering_path(folder)})"
    into = default_branch().partition("/")[2]
    pr = gh(
        [
            "pr",
            "create",
            "--draft",
            "--base",
            into,
            "--head",
            slug,
            "--title",
            title,
            "--body",
            link,
        ]
    )
    keep(folder, steering._replace(keys=dict(steering.keys, pr=pr)), f"pr: {pr}")
    return {"session": folder, "branch": slug, "pr": pr}


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
            raise Stop(
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


# A task's line as a change to the steering shows it, added or removed, with the task's number.
CHANGED_TASK = re.compile(r"^[+-]- T([0-9]+): ", re.MULTILINE)


def numbered_on(folder: str, plan: list[str], part: list[str], number: str) -> None:
    """Returns when each task of the part is one the plan holds, or numbered above every task any
    version of the steering held on the branch since it left the default branch, so an ID never
    names two tasks; stops otherwise, keeping nothing."""
    changes = git(
        ["log", "-p", "--format=", f"{base()}..HEAD", "--", steering_path(folder)], AS_GIT_SAYS
    )
    most = max((int(n) for n in CHANGED_TASK.findall(changes)), default=0)
    left = [task.id for task in tasks_of(plan)]
    stray = [t.id for t in tasks_of(part) if t.id not in left and int(t.id[1:]) <= most]
    if stray:
        raise Stop(
            f"rn: the part of the call {number} holds {joined(stray)}, neither a task the steering"
            " holds nor numbered above every task it has held, and an ID names one task alone;"
            " nothing is kept: have turn make the part again, each new task numbered from"
            f" T{most + 1}, then run this again"
        )


def learnings_of(folder: str) -> list[str]:
    """The lines of the session's learnings; none before any is made."""
    path = learnings_path(folder)
    return trimmed(read_text(path).splitlines()) if os.path.isfile(path) else []


def put_learnings(learnings: list[str], part: list[str]) -> list[str]:
    """The session's learnings with those of the part turn made after them, the part's own heading
    left out, each numbered on from those kept."""
    count = len([line for line in learnings if LEARNING.fullmatch(line)])
    lines = trimmed(part[1:]) if part[:1] == [f"## {LEARNINGS}"] else part
    put = []
    for line in lines:
        number = NUMBERED.match(line)
        if number:
            count += 1
            line = f"- L{count}: {line[number.end() :]}"
        put.append(line)
    return learnings + put


def write_learnings(folder: str, lines: list[str]) -> None:
    """Writes the session's learnings, once each is an item in the form of a learning, the lines
    indented under it its own; stops otherwise, writing nothing."""
    path = learnings_path(folder)
    point = items_of(list(enumerate(lines, 1)), LEARNING, LEARNING_FORM)[1]
    if point:
        raise Stop(
            f"rn: {path} would be out of its form: {point}; nothing is kept: have turn make the"
            " part it puts back again"
        )
    write_text(path, "\n".join(lines) + "\n")


def part_of(folder: str, number: str) -> tuple[str, list[str]]:
    """The work of the call of the number and the part turn made for it; stops where the session
    holds no such call, the call makes no part, turn has not returned it, or its part is not
    there."""
    call = next((c for c in calls(folder) if c.number == number), None)
    if call is None:
        raise Stop(
            f"rn: {os.path.join(folder, TURN)} holds no call {number}; give --put the number of a"
            " call on plan or learnings, such as 0001"
        )
    if call.work not in PARTS:
        raise Stop(
            f"rn: the call {number} is on {call.work}, which makes no part rn puts back; give --put"
            " a call on plan or learnings"
        )
    if not call.result:
        raise Stop(
            f"rn: turn has not returned the call {number}: {call_path(folder, number, RESULT)} is"
            " not there; wait for turn to return it, then run this again"
        )
    path = call_path(folder, number, PART[call.work])
    if not os.path.isfile(path):
        raise Stop(
            f"rn: {path}, the part the call {number} makes, is not there; cut it again with"
            f" `rn.py ccs {call.work} ...`, have turn make it, then run this again"
        )
    return call.work, trimmed(read_text(path).splitlines())


def moved(keys: dict[str, str], stage: str, plan: list[str], folder: str) -> dict[str, str]:
    """The front matter's keys with the stage moved to the one given; stops where the session is
    not at the stage it moves from; to the build stage, where a call made in the design stage is on
    a work other than the plan, a document made, which goes to the design sign-off; and to the
    deliverable stage, where a task is left."""
    if keys[STAGE] != MOVES[stage]:
        raise Stop(
            f"rn: the session is at the {keys[STAGE]} stage, and moves to {stage} from the"
            f" {MOVES[stage]} stage alone; the other stages move at the sign-offs, with"
            " `rn.py answer`"
        )
    if stage == BUILD:  # pragma: no mutate
        designed = [c for c in calls(folder) if c.stage == DESIGN]  # pragma: no mutate
        made = [c.work for c in designed if c.work != PLAN]
        if made:
            raise Stop(
                f"rn: the design stage made {joined(list(dict.fromkeys(made)))}, which go to the"
                " design sign-off; show it with `rn.py proposal design`, and the user's approval"
                " there moves the session to build"
            )
    left = [task.id for task in tasks_of(plan)]
    if stage == DELIVERABLE and left:
        raise Stop(
            f"rn: {joined(left)} is still in the steering, and the finished work is checked once no"
            " task is; tick each action done with --done T<n>.<action>, then run this again"
        )
    return dict(keys, stage=stage)


def run_state(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Keeps the move: the part of the call `--put` names put back, the plan's into the steering,
    the learnings' added to the session's learnings; each action done ticked, and each task removed
    once all its actions are; the stage moved where given; Next and Open replaced whole; then
    every change committed with the message and pushed; gives the commit. The records shown for the
    learnings are removed once their part is put back. Stops, keeping nothing, where a value is
    empty, the branch holds no session, the steering differs from what the last keep left, a part,
    an ID, an action or a stage cannot be taken, or the steering or the learnings would be out of
    their form; and where git fails."""
    next_step = given(args.next, "next step")
    message = given(args.message, "message")
    folder = current()
    steering = kept_steering(folder)
    work = None
    learnt: list[str] = []
    if args.put is not None:
        work, part = part_of(folder, args.put)
        if work == PLAN:  # pragma: no mutate
            numbered_on(folder, steering.plan, part, args.put)
            steering = steering._replace(plan=put_plan(steering.plan, part))
        else:
            learnt = put_learnings(learnings_of(folder), part)
    plan = ticked(steering.plan, args.done)
    keys = steering.keys if args.stage is None else moved(steering.keys, args.stage, plan, folder)
    steering = Steering(keys, plan, next_step, opened(args.open))
    # The steering is held to its form before the learnings are written, so a stop leaves neither.
    held_form(render(steering))
    if learnt:
        write_learnings(folder, learnt)
    kept = keep(folder, steering, message)
    if work == LEARNINGS_WORK:
        shutil.rmtree(learning(), ignore_errors=True)
    return {"kept": kept}


def run_decide(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Keeps a decision of the work, `<title>: <what it says>`, in the constraints of its latest
    call where turn has not returned it, else of a new call carrying that call's decisions, one of
    the same title replaced where it stands; kept with the message and pushed. Gives the call's
    number and the commit. Stops where a value is empty or wrong, the branch holds no session, the
    steering differs from what the last keep left, or a CCS is no JSON object; and where git
    fails."""
    work = worked(args.work)
    title = given(args.title, "title")
    if ": " in title:
        raise Stop(
            f"rn: the title {title!r} holds `: `, which parts a decision's title from what it says;"
            " give the title without it"
        )
    says = given(args.says, "decision")
    message = given(args.message, "message")
    folder = current()
    steering = kept_steering(folder)
    found = calls(folder)
    last = latest(found, work)
    if last is not None and not last.result:
        number, ccs = last.number, last.ccs
    else:
        number = next_number(found)
        carried = [] if last is None else decisions_of(last)
        ccs = {
            "focal_entities": [{WORK: work}, {STAGE: steering.keys[STAGE]}],
            "constraints": [{DECISION: d} for d in carried],
        }
    constraints = ccs.setdefault("constraints", [])
    decision = {DECISION: f"{title}: {says}"}
    same = next(
        (k for k, e in enumerate(constraints) if e.get(DECISION, "").startswith(f"{title}: ")), None
    )
    if same is None:
        constraints.append(decision)
    else:
        constraints[same] = decision
    write_json(call_path(folder, number, CCS), ccs)
    return {"call": number, "kept": keep(folder, steering, message)}


def own(kind: str, root: str) -> list[str]:
    """rn's own checklist for the kind, in any folder of rn's checklists; none where rn has none."""
    return sorted(glob.glob(os.path.join(root, "checklists", "**", f"{kind}.md"), recursive=True))


def checklists(kind: str, root: str) -> list[str]:
    """The checklists for the kind: rn's own, then the user's addition; stops where neither is
    there."""
    found = own(kind, root)
    added = os.path.join(RECORD, "checklists", f"{kind}.md")
    if os.path.isfile(added):
        found.append(added)
    if not found:
        raise Stop(
            f"rn: there is no checklist for the kind {kind}, neither rn's nor {added}; make"
            f" {added} first, as a work of its own to rn's checklist for checklists"
        )
    return found


def run_checklists(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """The paths of the kind's checklists; stops where the kind is not a name or has none."""
    return checklists(named(args.kind, "kind"), root)


def held(path: str) -> str:
    """The path of what the receiver has with the work, when a file or folder is there; stops
    otherwise, as turn stops a call naming one that is not."""
    if not os.path.exists(path):
        raise Stop(
            f"rn: what the receiver has, {path}, is not there; give the path of a file or folder"
            " they have with the work, from the top"
        )
    return path


def finished_work() -> list[str]:
    """Each file the branch changed since it left the default branch outside `.rn/`, in the order
    of their paths, which is the finished work; a file it removed is not, as it is not there to
    use. Stops where there is none."""
    paths = git(
        ["diff", "--name-only", "--diff-filter=d", base(), "HEAD", "--", f":(exclude){RECORD}"],
        AS_GIT_SAYS,
    ).splitlines()
    if not paths:
        raise Stop(
            f"rn: the branch changed no file outside {RECORD}/ since it left {default_branch()}, so"
            " there is no finished work to name; have each task made and kept, or give the work's"
            " paths, then run this again"
        )
    return paths


def served(steering: Steering, work: str) -> dict[str, str]:
    """The goal and each criterion the work serves, by ID, as the steering says each on one line:
    none for the plan, which makes them; those its task's line names for a task's work; the goal
    and every criterion for any other. Stops where the steering holds no task of a task's work."""
    said = decided(steering.plan, ("", CRITERIA))
    if work == PLAN:
        return {}
    if not TASK_WORK.fullmatch(work):
        return said
    task = next((t for t in tasks_of(steering.plan) if t.id == work.upper()), None)
    if task is None:
        raise Stop(
            f"rn: the steering holds no task {work.upper()}, which the work {work} is of; have turn"
            " make the tasks, keep them, then run this again"
        )
    return {key: text for key, text in said.items() if key in (task.serves or [])}


def done_made(folder: str, found: list[Call], plan: list[str]) -> list[str]:
    """For each call on a task's work whose task the plan no longer holds, done, in the order made,
    its CCS and its result where turn returned it, and the CCS of the work's latest call where turn
    has not, as it holds the decisions kept last: what the task served, decided and made, a research
    result made before a decision among them."""
    left = [task.id for task in tasks_of(plan)]
    last = {c.work: c.number for c in found}
    paths = []
    for call in found:
        if TASK_WORK.fullmatch(call.work) and call.work.upper() not in left:
            latest_call = call.number == last[call.work]  # pragma: no mutate
            if call.result or latest_call:
                paths.append(call_path(folder, call.number, CCS))
            paths += [call_path(folder, call.number, RESULT)] if call.result else []
    return paths


def run_ccs(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Writes the work's CCS into the session, keeps it, and gives the call that hands it to
    turn:up, once every change is pushed, so the work is made from decisions a fresh conversation
    also has, and a conversation cut while turn runs goes on from the call: in the work's latest
    call where turn has not returned it, else in a new one carrying that call's decisions. The work
    is each path given; for the plan, its part of the steering, cut into the call's part, with what
    each task done served and made as what the receiver has, after those given; for the learnings,
    a part of their heading alone, cut into the call's part, as those kept are not made again; for
    the finished work given none, every file it is. Stops where a name, a text or a path given is
    wrong, the branch holds no session, a change is not kept or pushed, the steering differs from
    what the last keep left, the steering holds no task of a task's work, or the finished work is
    not there."""
    work = worked(args.work)
    kind = named(args.kind, "kind")
    receiver = given(args.receiver, "receiver")
    use = given(args.use, "use")
    paths = [given(p, "path of the work") for p in args.path]
    if work in PARTS and paths:
        raise Stop(
            f"rn: the work {work} is a part rn cuts for turn from the session's record; give no"
            " path of it"
        )
    if not paths and work not in PARTS + (DELIVERABLE,):
        raise Stop(
            f"rn: no path of the work {work} is given; give the path of each file or folder of it,"
            " from the top"
        )
    # The session is found first, which stops below the top of the repository, since each path
    # given is read from the top.
    folder = current()
    pushed()
    has = [held(p) for p in args.has]
    steering = kept_steering(folder)
    serving = served(steering, work)
    found = calls(folder)
    last = latest(found, work)
    number = last.number if last is not None and not last.result else next_number(found)
    carried = [] if last is None else decisions_of(last)
    if work in PARTS:
        cut = "\n".join(steering.plan) if work == PLAN else f"## {LEARNINGS}"  # pragma: no mutate
        part = call_path(folder, number, PART[work])
        write_text(part, cut + "\n")
        paths = [part]
    if work == PLAN:
        has += done_made(folder, found, steering.plan)
    # A CCS holds its entries in four parts, the shape turn takes: focal_entities, what the work is
    # about, the work by its name, the stage it is made in, its paths, its receiver and what they
    # have with it; goal_orientation, what the work is for, its use and what it serves as text, as
    # turn makes the work from the CCS and the files it names alone; retrieved_artifacts, the
    # kind's checklists and rn's `usability.md` where the work is a checklist; and constraints, the
    # bounds it is made in: its decisions, the languages, and rn's checklist for a fix, which turn's
    # generator holds whenever it changes a work already there. turn finds each entry by its key,
    # whichever part holds it.
    usability = os.path.join(root, "checklists", "usability.md")
    ccs = {
        "focal_entities": [{WORK: work}, {STAGE: steering.keys[STAGE]}]
        + [{ENTRIES["work"]: p} for p in paths or finished_work()]
        + [{ENTRIES["receiver"]: receiver}]
        + [{ENTRIES["has"]: p} for p in has],
        "goal_orientation": [{ENTRIES["use"]: use}]
        + [{SERVES: f"{key}: {text}"} for key, text in serving.items()],
        "retrieved_artifacts": [{ENTRIES["checklist"]: p} for p in checklists(kind, root)]
        + ([{"source": usability}] if kind == CHECKLIST else []),
        "constraints": [{DECISION: d} for d in carried]
        + [{key: steering.keys[key]} for key in LANGUAGES]
        + [{"fix": os.path.join(root, "checklists", "fix.md")}],
    }
    path = call_path(folder, number, CCS)
    write_json(path, ccs)
    keep(folder, steering, f"Call {number} on {work}: handed to turn")
    # turn's call takes the table of keys under "kind", a field name of turn's own that is no kind
    # of work.
    return {"ccs": path, "kind": ENTRIES, "result": call_path(folder, number, RESULT)}


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


def joined(ids: list[str], last: str = "and") -> str:
    """The IDs in words, the last after the word given."""
    *rest, end = ids
    return f"{', '.join(rest)} {last} {end}" if rest else end


def simple(work: str, decisions: list[str]) -> dict[str, str]:
    """The work's decisions, by their titles, when a sign-off can show them; stops where they are
    more than it shows of a work, or one is longer than a line of it holds, as the work is then not
    yet simple."""
    again = (
        "the work is not yet simple: settle its points again more simply with the user, have turn"
        " make it again, then run this again"
    )
    found = {d.partition(": ")[0]: d for d in decisions}
    if len(found) > MOST:
        raise Stop(
            f"rn: the work {work} holds {len(found)} decisions, more than the {MOST} a sign-off"
            f" shows of a work; {again}"
        )
    for title, said in found.items():
        if len(said) > LONGEST:
            raise Stop(
                f'rn: the decision "{title}" of the work {work} is {len(said)} characters long,'
                f" more than the {LONGEST} a line of a sign-off holds; {again}"
            )
    return found


def blob(pr: str) -> str:
    """Where the repository of the session's pull request shows the files of the checked-out
    branch; stops where the pull request was not opened."""
    found = PULL.fullmatch(pr)
    if found is None:
        raise Stop(
            f"rn: the steering's pr, {pr!r}, is no pull request's URL; run `rn.py start` again on"
            " the session's branch, so it opens the pull request, then run this again"
        )
    branch = git(["branch", "--show-current"], AS_GIT_SAYS).strip()
    return f"{found.group(1)}/blob/{branch}"


# What a proposal shows, by the work each part is of, "" for the steering's own: the line naming the
# work, none for the steering's, and the part's lines by what each is of, an ID or a decision's
# title.
Shown = dict[str, tuple[str, dict[str, str]]]


def shown_works(made: list[Call], signoff: str) -> list[str]:
    """The works whose decisions the sign-off shows, in the order first called."""
    if signoff not in WORKS_SHOWN:
        return []
    stage, form = WORKS_SHOWN[signoff]
    found: list[str] = []
    for call in made:
        if call.stage == stage and form.fullmatch(call.work) and call.work not in found:
            found.append(call.work)
    return found


def shown_at(commit: str, signoff: str, folder: str) -> Shown:
    """What the proposal at the sign-off shows of the session as the commit holds it: at the plan's,
    the goal and each criterion by its ID, and at the deliverable's each criterion; then each work
    the sign-off shows by its name: at the design's, its paths as links, from its latest call, with
    its decisions; at the deliverable's, its decisions, where it has any. Stops where turn has not
    returned a work's latest call, a work's decisions are not simple, or the pull request was not
    opened."""
    steering = parsed(at(commit, steering_path(folder)) or "")
    found: Shown = {}
    if signoff != DESIGN:
        parts = ("", CRITERIA) if signoff == PLAN else (CRITERIA,)  # pragma: no mutate
        lines = decided(steering.plan, parts)
        found[""] = ("", {key: f"{key}: {said}" for key, said in lines.items()})
    made = calls(folder, commit)
    for work in shown_works(made, signoff):
        last = latest(made, work)
        if last is None or not last.result:
            number = "" if last is None else last.number
            raise Stop(
                f"rn: turn has not returned the work {work}: {call_path(folder, number, RESULT)} is"
                f" not there; have turn:up make it with the call `rn.py ccs {work} ...` printed,"
                " keep it, then run this again"
            )
        said = simple(work, decisions_of(last))
        label = work.upper() if TASK_WORK.fullmatch(work) else work
        if signoff == DESIGN:  # pragma: no mutate
            link = blob(steering.keys["pr"])
            paths = [
                e[ENTRIES["work"]]
                for e in last.ccs.get("focal_entities", [])
                if ENTRIES["work"] in e
            ]
            found[work] = (f"{label}: {', '.join(f'{link}/{p}' for p in paths)}", said)
        elif said:
            found[work] = (label, said)
    return found


def changes(before: dict[str, str] | None, now: dict[str, str], bullet: str) -> list[str]:
    """The lines the proposal shows of one part, each after the bullet: each as it is, at the first
    proposal; then each changed or added, each removed, by what it is of, and the rest named as
    before."""
    if before is None:
        return [f"{bullet}{line}" for line in now.values()]
    same = [key for key, line in now.items() if before.get(key) == line]
    return (
        [f"{bullet}Changed: {line}" for key, line in now.items() if key not in same]
        + [f"{bullet}Removed: {key}" for key in before if key not in now]
        + ([f"({joined(same)} as before)"] if same else [])
    )


def compared(then: Shown | None, now: Shown) -> list[str]:
    """The lines the proposal shows: each work's line and what changed of its part since the
    proposal shown before, none for the first, the steering's lines on their own and each decision
    after a bullet; then each work shown before and no longer, named as removed."""
    lines: list[str] = []
    for work, (line, said) in now.items():
        before = None if then is None else then.get(work, ("", {}))[1]
        lines += [line] if line else []
        lines += changes(before, said, "- " if work else "")
    return lines + [f"Removed: {work}" for work in then or {} if work not in now]


def proposed(signoff: str, folder: str) -> list[str]:
    """Each commit on the branch that set the steering waiting at the sign-off, oldest first, as
    its history shows: a commit whose change adds or removes the line, holding it."""
    path = steering_path(folder)
    listed = git(
        [
            "log",
            "--reverse",
            "--format=%H",
            f"-G^signoff: {signoff}$",
            f"{base()}..HEAD",
            "--",
            path,
        ],
        AS_GIT_SAYS,
    )
    return [c for c in listed.split() if keys_of(at(c, path) or "").get("signoff") == signoff]


def ready(signoff: str, folder: str, steering: Steering) -> None:
    """Returns when the session has what the sign-off shows: at the plan's, the goal, a criterion
    and no task left; at the deliverable's, the finished work returned; stops otherwise. The
    design's works are checked as they are shown."""
    if signoff == PLAN:  # pragma: no mutate
        said = decided(steering.plan, ("", CRITERIA))
        if "G1" not in said or len(said) < 2 or tasks_of(steering.plan):
            raise Stop(
                "rn: the plan sign-off needs the goal G1, a criterion and no task in the steering;"
                " have turn make the plan through its tasks, tick each action done with"
                " `rn.py state --done`, then run this again"
            )
    if signoff == DELIVERABLE:  # pragma: no mutate
        last = latest(calls(folder), DELIVERABLE)
        if last is None or not last.result:
            raise Stop(
                "rn: turn has not returned the finished work; have turn:up make it with the call"
                " `rn.py ccs deliverable ...` prints, keep it, then run this again"
            )


def run_proposal(args: argparse.Namespace, root: str, today: datetime.date) -> str:
    """The proposal at the sign-off, made from what is pushed alone: the pull request's link, then
    the goal and the acceptance criteria at the plan sign-off, each work made in the design stage
    with its links and its decisions at the design's, and the criteria and each task's decisions
    of the build stage at the deliverable's, with what changed since the last proposal at the same
    sign-off; the steering set waiting at the sign-off, Next saying so, and kept with the proposal
    as its message.
    The same proposal again, keeping nothing, where it waits at that sign-off already. Stops where
    the branch holds no session, a change is not kept or pushed, the steering differs from what the
    last keep left, the session is at another stage, another sign-off waits, the session lacks what
    the sign-off shows, a work's decisions are not simple, or the pull request was not opened."""
    signoff = args.signoff
    folder = current()
    pushed()
    steering = kept_steering(folder)
    stage, waiting = steering.keys[STAGE], steering.keys["signoff"]
    if stage != signoff:
        raise Stop(
            f"rn: the session is at the {stage} stage, and the {signoff} sign-off comes at the"
            f" {signoff} stage; take the steps of /rn:up that reach it first"
        )
    if waiting not in (NONE, signoff):
        raise Stop(
            f"rn: the {waiting} sign-off waits for the user's answer; keep it with `rn.py answer`"
            " first"
        )
    ready(signoff, folder, steering)
    shown = proposed(signoff, folder)
    before = shown[:-1] if waiting == signoff else shown
    now = shown_at("HEAD", signoff, folder)
    then = shown_at(before[-1], signoff, folder) if before else None
    proposal = "\n".join(
        [
            f"{signoff.capitalize()} sign-off",
            f"{SIGNOFFS[signoff]}: {steering.keys['pr']}",
            *compared(then, now),
            ANSWER,
        ]
    )
    if waiting == NONE:
        waits = f"Wait at the {signoff} sign-off for the user's answer: {ANSWER}"
        keep(
            folder,
            steering._replace(keys=dict(steering.keys, signoff=signoff), next=waits),
            proposal,
        )
    return proposal


# The command the user types for each answer, which the AI cannot call.
COMMANDS = {"approved": "/rn:ty", "feedback": "/rn:gm"}


def typed(command: str, start: float) -> bool:
    """Whether the user typed the command, at or after the time in seconds since 1970, in a
    conversation run at the top of the repository on the checked-out branch: an entry of the
    user's that is a command, as Claude Code keeps one typed, and names it; never an agent's
    message nor what a tool gave back, which are kept otherwise."""
    top = git(["rev-parse", "--show-toplevel"], AS_GIT_SAYS).strip()
    branch = git(["branch", "--show-current"], AS_GIT_SAYS).strip()
    name = f"<command-name>{command}</command-name>"
    for path in conversations(top, branch):
        for e in lines_of(path):
            content = e.get("message", {}).get("content")
            if (
                e.get("type") == "user"
                and isinstance(content, str)
                and content.startswith("<command-")
                and name in content
                and since(e, start)
            ):
                return True
    return False


def run_answer(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Keeps the user's answer to the sign-off waiting: on approval the stage moved on, plan to
    design, design to build, deliverable to learnings; on either no sign-off waiting, and Next and
    Open replaced whole; kept with the message and pushed; gives the commit. Stops where a value is
    empty, the branch holds no session, the steering differs from what the last keep left, no
    sign-off waits, or the user has not typed the answer's command since the sign-off was shown, as
    an approval counts only from the user's own action; and where git fails."""
    next_step = given(args.next, "next step")
    message = given(args.message, "message")
    folder = current()
    steering = kept_steering(folder)
    waiting = steering.keys["signoff"]
    if waiting == NONE:
        raise Stop(
            "rn: no sign-off waits for the user's answer; show the proposal with `rn.py proposal"
            " <plan|design|deliverable>` first, and keep the answer the user gives it"
        )
    command = COMMANDS[args.answer]
    shown = float(git(["log", "-1", "--format=%ct", proposed(waiting, folder)[-1]], AS_GIT_SAYS))
    if not typed(command, shown):
        raise Stop(
            f"rn: the user has not typed {command} since the {waiting} sign-off was shown; the"
            " answer is theirs alone, so wait for them to type it, and keep it then"
        )
    keys = dict(steering.keys, signoff=NONE)
    if args.answer == "approved":  # pragma: no mutate
        keys[STAGE] = APPROVED[waiting]
    answered = steering._replace(keys=keys, next=next_step, open=opened(args.open))
    return {"kept": keep(folder, answered, message)}


def learning() -> str:
    """The folder where the records the learnings are made from are shown, in the repository's git
    folder, as a whole path."""
    return os.path.join(
        git(["rev-parse", "--absolute-git-dir"], AS_GIT_SAYS).strip(), LEARNING_PLACE
    )


def project_folders(top: str) -> list[str]:
    """The folders where Claude Code keeps the records of conversations run at the path: the one
    named by it, or, where the name is longer than Claude Code keeps, each there named by its
    beginning and a hash."""
    name = "".join(
        c if c.isascii() and c.isalnum() else "-" * (len(c.encode("utf-16-le")) // 2) for c in top
    )
    kept = records.kept()
    if len(name) <= NAME_LENGTH:
        return [os.path.join(kept, name)]
    return sorted(
        glob.glob(os.path.join(glob.escape(kept), glob.escape(name[:NAME_LENGTH]) + "-*"))
    )


def lines_of(path: str) -> list[dict[str, Any]]:
    """Each entry of a record, as Claude Code keeps it, one JSON object to a line."""
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def begun(path: str) -> tuple[str, str]:
    """When the record began, its earliest entry's time, Claude Code writing each in one form; and
    its path, so records begun at once come in one order."""
    times = [e["timestamp"] for e in lines_of(path) if "timestamp" in e]
    return min(times, default=""), path


def conversations(top: str, branch: str) -> list[str]:
    """The record of each conversation run at the top of the repository that was on the branch at
    some entry, in the order they began."""
    found = [
        path
        for folder in project_folders(top)
        for path in glob.glob(os.path.join(glob.escape(folder), "*.jsonl"))
        if any(e.get("cwd") == top and e.get("gitBranch") == branch for e in lines_of(path))
    ]
    return sorted(found, key=begun)


def stretch(folder: str) -> str:
    """The commit the stretch the learnings are made from starts after: the one that kept the
    result of the last call on the learnings turn returned, or, where none is, the one the branch
    left the default branch at."""
    done = [c for c in calls(folder) if c.work == LEARNINGS_WORK and c.result]
    if not done:
        return base()
    result = call_path(folder, done[-1].number, RESULT)
    return git(["log", "-1", "--format=%H", "--", result], AS_GIT_SAYS).strip()


def history(folder: str, start: str) -> str:
    """The session's history on the branch since the start, each command before what it printed:
    each commit, oldest first, with its message, which holds each feedback, answer and proposal
    shown, and the files it changed, so a change to the work made outside turn shows, without their
    lines, as the record gives the session's files as they are now; then each change to the
    steering, under the commit that made it, which shows what each move rested on."""
    asked = [
        ["log", "--reverse", "--stat", f"{start}..HEAD"],
        ["log", "--reverse", "-p", "--format=%h", f"{start}..HEAD", "--", steering_path(folder)],
    ]
    return "".join(f"$ {shlex.join(['git', *a])}\n{git(a, AS_GIT_SAYS)}\n" for a in asked)


def session_files(folder: str) -> list[str]:
    """The session's files as they are now: the steering, the learnings, and each file of its calls
    to turn."""
    found = [steering_path(folder), learnings_path(folder)]
    found += sorted(glob.glob(os.path.join(glob.escape(folder), TURN, "*")))
    return [p for p in found if os.path.isfile(p)]


def since(entry_: dict[str, Any], start: float) -> bool:
    """Whether the entry was kept at or after the time, in seconds since 1970; not where it has no
    time."""
    kept = entry_.get("timestamp")
    # Python 3.9 reads no `Z` for UTC, which Claude Code writes.
    return (
        kept is not None
        and datetime.datetime.fromisoformat(kept.replace("Z", "+00:00")).timestamp() >= start
    )


def told(path: str, start: float) -> str:
    """A conversation of the orchestrator from the time, in seconds since 1970: the user's words,
    each skill's text, the orchestrator's words and each tool it called, one to a line; what each
    tool gave back is left out, as the record shows what was kept, and it is most of the
    conversation; "" where it holds none of them from the time."""
    said: list[str] = []
    for e in (e for e in records.entries(path) if since(e, start)):
        content = e.get("message", {}).get("content")
        if isinstance(content, str):
            said.append(f"[{e.get('type')}] {content}")
        for part in content if isinstance(content, list) else []:
            if part.get("type") in ("text", "tool_use"):
                said.append(records.said(part))
    return "".join(f"{line}\n" for line in said)


def run_records(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Shows the stretch of the session the learnings are made from, once every change is pushed:
    its record, the history on the branch since the last call on the learnings turn returned and
    the session's files as they are now; then each conversation of the orchestrator, run at the top
    of the repository on the session's branch, from the time the stretch began, none where Claude
    Code keeps none here, as when the session ran on another machine. Each is written as text in the
    git folder, made afresh, where nothing is committed; gives their paths, the record first, what
    the receiver of the learnings' call has. Stops where the branch holds no session, or a change
    is not kept or pushed."""
    folder = current()
    pushed()
    start = stretch(folder)
    began = float(git(["log", "-1", "--format=%ct", start], AS_GIT_SAYS))
    top = git(["rev-parse", "--show-toplevel"], AS_GIT_SAYS).strip()
    branch = git(["branch", "--show-current"], AS_GIT_SAYS).strip()
    place = learning()
    shutil.rmtree(place, ignore_errors=True)
    # Each text shown, by where it is written, with its text.
    shown = [(os.path.join("record", "history.txt"), history(folder, start))]
    shown += [(os.path.join("record", p), read_text(p)) for p in session_files(folder)]
    for path in conversations(top, branch):
        name = os.path.basename(path)[: -len(".jsonl")] + ".txt"
        text = told(path, began)
        if text:
            shown.append((os.path.join("conversations", name), text))
    for name, text in shown:
        write_text(os.path.join(place, name), records.wrapped(text))
    return [os.path.join(place, name) for name, _ in shown]


def turns_learnings(folder: str) -> list[dict[str, Any]]:
    """Each learning turn returned for a work of the session, from every version of every result
    committed on the branch since it left the default branch, as a work made again leaves the one
    before in the history alone; oldest first, each once, with the work, the call and the commit
    that first held it. A version that is no JSON object is passed over, as no result of turn's;
    turn's result names its learnings `lessons`."""
    works = {c.number: c.work for c in calls(folder)}
    listed = git(
        [
            "log",
            "--reverse",
            "--format=commit %H",
            "--name-only",
            "--diff-filter=AM",
            f"{base()}..HEAD",
            "--",
            os.path.join(folder, TURN, f"*-{RESULT}"),
        ],
        AS_GIT_SAYS,
    )
    found: list[dict[str, Any]] = []
    seen: list[dict[str, Any]] = []
    commit = ""
    for line in listed.splitlines():
        if line.startswith("commit "):
            commit = line[len("commit ") :]
        file = CALL.fullmatch(os.path.basename(line))
        if file is None:
            continue
        try:
            data = json.loads(git(["show", f"{commit}:{line}"], AS_GIT_SAYS))
        except ValueError:
            continue
        for learnt in data.get("lessons", []) if isinstance(data, dict) else []:
            if learnt not in seen:
                seen.append(learnt)
                found.append(dict(learnt, work=works.get(file[1], ""), call=file[1], commit=commit))
    return found


def run_learnings(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Every learning of the session, for the orchestrator to put to the user one per message once
    the finished work is approved: the session's, by ID, each as one line; and turn's, each as
    turn's result gives it, with the work, the call and the commit that kept it. Stops where the
    branch holds no session."""
    folder = current()
    said = by_id(list(enumerate(learnings_of(folder))), "- ")
    return {"learnings": said, "turn": turns_learnings(folder)}


class Parser(argparse.ArgumentParser):
    """argparse, stopping as rn stops rather than exiting with its own code."""

    def error(self, message: str) -> NoReturn:
        # The usage on one line, as argparse breaks a long one where a terminal would.
        usage = " ".join(self.format_usage().split()[1:])
        raise Stop(f"rn: {message}; give it as {usage}")


def parser() -> Parser:
    """The subcommands, each with what it takes and the function that runs it."""
    top = Parser(prog="rn.py")
    sub = top.add_subparsers(dest="subcommand", required=True)
    sub.add_parser("session").set_defaults(run=run_session)
    start = sub.add_parser("start")
    start.set_defaults(run=run_start)
    start.add_argument("slug")
    for option in ("--title", *(f"--{key}" for key in LANGUAGES), "--next", "--message"):
        start.add_argument(option, required=True)
    state = sub.add_parser("state")
    state.set_defaults(run=run_state)
    state.add_argument("--next", required=True)
    state.add_argument("--open", action="append", default=[])
    state.add_argument("--done", action="append", default=[])
    state.add_argument("--put")
    state.add_argument("--stage", choices=list(MOVES))
    state.add_argument("--message", required=True)
    decide = sub.add_parser("decide")
    decide.set_defaults(run=run_decide)
    decide.add_argument("work")
    for option in ("--title", "--says", "--message"):
        decide.add_argument(option, required=True)
    ccs = sub.add_parser("ccs")
    ccs.set_defaults(run=run_ccs)
    ccs.add_argument("work")
    ccs.add_argument("path", nargs="*")
    for option in ("--kind", "--receiver", "--use"):
        ccs.add_argument(option, required=True)
    ccs.add_argument("--has", action="append", default=[])
    proposal = sub.add_parser("proposal")
    proposal.set_defaults(run=run_proposal)
    proposal.add_argument("signoff", choices=list(SIGNOFFS))
    answer = sub.add_parser("answer")
    answer.set_defaults(run=run_answer)
    answer.add_argument("answer", choices=ANSWERS)
    answer.add_argument("--next", required=True)
    answer.add_argument("--open", action="append", default=[])
    answer.add_argument("--message", required=True)
    lists = sub.add_parser("checklists")
    lists.set_defaults(run=run_checklists)
    lists.add_argument("kind")
    sub.add_parser("records").set_defaults(run=run_records)
    sub.add_parser("learnings").set_defaults(run=run_learnings)
    return top


def main(argv: list[str], root: str, today: datetime.date) -> int:
    """Runs the subcommand and prints what it gives, JSON or the proposal's text; 1 on a stop."""
    try:
        args = parser().parse_args(argv)
        run: Callable[..., Any] = args.run
        out = run(args, root, today)
    except Stop as stop:
        print(stop)
        return 1
    print(out if isinstance(out, str) else dumped(out))
    return 0


# Run as the command, and not when the tests import it under the name rn.
if __name__ == "__main__":  # pragma: no mutate
    sys.exit(main(sys.argv[1:], ROOT, datetime.date.today()))
