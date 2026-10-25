"""The session the checked-out branch is in and its record, the folder `.rn/<yyyymmdd>-<slug>/`: the
steering as the last keep left it, each move kept, each call to turn as the files of one number,
the works rn has turn make, the stage moved at a stage's end, and the learnings kept."""

from __future__ import annotations

import functools
import json
import os
import re
from collections.abc import Callable
from typing import NamedTuple

import call
import repo
import steering
import stop

# The folder in the user's repository holding every session's record and the user's checklists, and
# a session's folder in it, by the date it began and its slug.
RECORD = ".rn"
SESSION_NAME = re.compile(r"[0-9]{8}-[a-z0-9-]+")
# The session's steering, its learnings, and the folder of its calls to turn, in the session's
# folder.
STEERING = "steering.md"
LEARNT = "learnings.md"
TURN = "turn"
# The works rn has turn make: the plan, the part of the steering from the title through the tasks,
# as a task of the plan stage makes the plan; its learnings; what task T<n> makes outside the
# steering; the finished work; and a checklist of a kind.
TASK_WORK = re.compile(r"t[0-9]+")
CHECKLIST_WORK = re.compile(r"checklist-[a-z0-9-]+")
WORKS = "plan, learnings, deliverable, t<n> for task T<n>, or checklist-<kind>"
# The works whose call makes a part, cut into a file of its own, each with what its file is named:
# the plan's a part of the steering, the learnings' those it adds to the session's.
PART = {steering.PLAN: STEERING, steering.LEARNINGS: LEARNT}
PARTS = tuple(PART)
# A file of a call to turn, by its number and what it is: the CCS, turn's result, or the part the
# call makes.
CCS = "ccs.json"
RESULT = "result.json"
CALL = re.compile(rf"([0-9]{{4}})-({'|'.join(map(re.escape, (CCS, RESULT, *PART.values())))})")
# The keys of the CCS entries rn reads back: the work's name, and each decision of the work as
# `<title>: <what it says>`; the stage it was made in is under the front matter's key of the stage.
WORK = "work"
DECISION = "decision"
# The heading a part of the learnings opens with, which rn cuts for turn and leaves out when it
# adds the learnings to the session's; and each learning, in the form of rn's learnings checklist.
LEARNINGS = "Learnings"
LEARNING = re.compile(r"- (?P<id>L[0-9]+): (?P<said>\S.*)")
LEARNING_FORM = (
    "a learning as `- L<n>: <what happened, with the words it rests on, and where it would make"
    " later work better>`"
)


def worked(work: str) -> str:
    """The work, when it names one rn has turn make; stops otherwise."""
    if work not in PARTS + (steering.DELIVERABLE,) and not (
        TASK_WORK.fullmatch(work) or CHECKLIST_WORK.fullmatch(work)
    ):
        raise stop.Stop(f"rn: the work {work!r} is none rn makes; give {WORKS}, such as t1")
    return work


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
    repo.at_top()
    paths = repo.git(["diff", "--name-only", repo.base(), "HEAD", "--", RECORD], repo.AS_GIT_SAYS)
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
        if os.path.isdir(f)
        and steering.keys_of(repo.at("HEAD", steering_path(f)) or "").get(steering.STAGE)
        != steering.FINISHED
    ]
    if len(going) > 1:
        raise stop.Stop(
            f"rn: this branch changed more than one session not finished: {', '.join(going)}; a"
            " branch holds one session, so check out the branch of the one to go on with"
        )
    return next(iter(going), None)


def current() -> str:
    """The session the checked-out branch is in; stops where there is none."""
    found = session()
    if found is None:
        raise stop.Stop(
            "rn: the checked-out branch holds no session; start one with `rn.py start <slug>`"
        )
    return found


def kept_steering(folder: str) -> steering.Steering:
    """The steering as the last keep left it; stops where the working tree's differs from it, with
    how to restore it, or where it is out of its form, as only a commit made by hand leaves it."""
    path = steering_path(folder)
    last = repo.at("HEAD", path)
    if (repo.read_text(path) if os.path.isfile(path) else None) != last:
        raise stop.Stop(
            f"rn: {path} differs from what the last keep left, and rn's scripts alone write it;"
            f" restore it with `git checkout HEAD -- {path}`, then run this again"
        )
    point = steering.out_of_form(last or "")
    if point:
        raise stop.Stop(
            f"rn: {path} as the last commit holds it is out of the form of rn's plan checklist's"
            f" F-1: {point}; rn keeps none so, so restore the last one rn kept from"
            f" `git log -p -- {path}`, commit it, then run this again"
        )
    return steering.parsed(last or "")


def keep(folder: str, steered: steering.Steering, message: str) -> str:
    """Keeps the move: the steering written, once it holds its form, and every change of the move
    committed with the message, then pushed; gives the commit. Stops, writing nothing, where the
    steering is out of its form; and where git fails."""
    text = steering.render(steered)
    steering.held_form(text)
    repo.write_text(steering_path(folder), text)
    if repo.changed():
        repo.git(["add", "-A"], repo.AS_GIT_SAYS)
        repo.git(["commit", "-q", "-F", "-"], repo.AS_GIT_SAYS, message)
    repo.push()
    return repo.git(["rev-parse", "HEAD"], repo.AS_GIT_SAYS).strip()


class Call(NamedTuple):
    """A call to turn: its number, the work it is on and the stage it was made in, as its CCS names
    them, its CCS, and whether turn returned its result."""

    number: str
    work: str
    stage: str
    ccs: dict[str, list[dict[str, str]]]
    result: bool


def calls(folder: str, commit: str | None = None) -> list[Call]:
    """Each call to turn of the session, in the order made, as the working tree holds them, or the
    commit given; stops where a CCS is no JSON object, saying how to restore it."""
    place = os.path.join(folder, TURN)
    read: Callable[[str], str | None] = repo.read_text
    if commit is None:
        names = os.listdir(place) if os.path.isdir(place) else []
    else:
        listed = repo.git(["ls-tree", "--name-only", commit, "--", f"{place}/"], repo.AS_GIT_SAYS)
        names = [os.path.basename(p) for p in listed.splitlines()]
        read = functools.partial(repo.at, commit)
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
            raise stop.Stop(
                f"rn: {path} is no CCS, a JSON object; restore it with `git checkout HEAD --"
                f" {path}`, as rn's scripts alone write it, then run this again"
            )
        work, stage = (next(iter(call.entries(ccs, key)), "") for key in (WORK, steering.STAGE))
        found.append(Call(number, work, stage, ccs, RESULT in files[number]))
    return found


def latest(found: list[Call], work: str) -> Call | None:
    """The work's latest call; None where it has none."""
    return next((c for c in reversed(found) if c.work == work), None)


def decisions_of(made: Call) -> list[str]:
    """Each decision of the call, in the order kept."""
    return call.entries(made.ccs, DECISION)


def next_number(found: list[Call]) -> str:
    """The number of a new call, the one after the last."""
    return f"{int(found[-1].number) + 1 if found else 1:04d}"


# A task's line as a change to the steering shows it, added or removed, with the task's number.
CHANGED_TASK = re.compile(r"^[+-]- T([0-9]+): ", re.MULTILINE)


def numbered_on(folder: str, plan: list[str], part: list[str], number: str) -> None:
    """Returns when each task of the part is one the plan holds, or numbered above every task any
    version of the steering held on the branch since it left the default branch, so an ID never
    names two tasks; stops otherwise, keeping nothing."""
    changes = repo.git(
        ["log", "-p", "--format=", f"{repo.base()}..HEAD", "--", steering_path(folder)],
        repo.AS_GIT_SAYS,
    )
    most = max((int(n) for n in CHANGED_TASK.findall(changes)), default=0)
    left = [task.id for task in steering.tasks_of(plan)]
    stray = [t.id for t in steering.tasks_of(part) if t.id not in left and int(t.id[1:]) <= most]
    if stray:
        raise stop.Stop(
            f"rn: the part of the call {number} holds {stop.joined(stray)}, neither a task the steering"
            " holds nor numbered above every task it has held, and an ID names one task alone;"
            " nothing is kept: have turn make the part again, each new task numbered from"
            f" T{most + 1}, then run this again"
        )


def learnings_of(folder: str) -> list[str]:
    """The lines of the session's learnings; none before any is made."""
    path = learnings_path(folder)
    return steering.trimmed(repo.read_text(path).splitlines()) if os.path.isfile(path) else []


def put_learnings(learnings: list[str], part: list[str]) -> list[str]:
    """The session's learnings with those of the part turn made after them, the part's own heading
    left out, each numbered on from those kept."""
    count = len([line for line in learnings if LEARNING.fullmatch(line)])
    lines = steering.trimmed(part[1:]) if part[:1] == [f"## {LEARNINGS}"] else part
    put = []
    for line in lines:
        learnt = LEARNING.fullmatch(line)
        if learnt:
            count += 1
            line = f"- L{count}: {learnt['said']}"
        put.append(line)
    return learnings + put


def write_learnings(folder: str, lines: list[str]) -> None:
    """Writes the session's learnings, once each is an item in the form of a learning, the lines
    indented under it its own; stops otherwise, writing nothing."""
    path = learnings_path(folder)
    point = steering.items_of(list(enumerate(lines, 1)), LEARNING, LEARNING_FORM)[1]
    if point:
        raise stop.Stop(
            f"rn: {path} would be out of its form: {point}; nothing is kept: have turn make the"
            " part it puts back again"
        )
    repo.write_text(path, "\n".join(lines) + "\n")


def part_of(folder: str, number: str) -> tuple[str, list[str]]:
    """The work of the call of the number and the part turn made for it; stops where the session
    holds no such call, the call makes no part, turn has not returned it, or its part is not
    there."""
    call = next((c for c in calls(folder) if c.number == number), None)
    if call is None:
        raise stop.Stop(
            f"rn: {os.path.join(folder, TURN)} holds no call {number}; give --put the number of a"
            " call on plan or learnings, such as 0001"
        )
    if call.work not in PARTS:
        raise stop.Stop(
            f"rn: the call {number} is on {call.work}, which makes no part rn puts back; give --put"
            " a call on plan or learnings"
        )
    if not call.result:
        raise stop.Stop(
            f"rn: turn has not returned the call {number}: {call_path(folder, number, RESULT)} is"
            " not there; wait for turn to return it, then run this again"
        )
    path = call_path(folder, number, PART[call.work])
    if not os.path.isfile(path):
        raise stop.Stop(
            f"rn: {path}, the part the call {number} makes, is not there; cut it again with"
            f" `rn.py ccs {call.work} ...`, have turn make it, then run this again"
        )
    return call.work, steering.trimmed(repo.read_text(path).splitlines())


def moved(keys: dict[str, str], stage: str, plan: list[str], folder: str) -> dict[str, str]:
    """The front matter's keys with the stage moved to the one given; stops where the session is
    not at the stage it moves from; to the build stage, where a call made in the design stage is on
    a work other than the plan, a document made, which goes to the design sign-off; and to the
    deliverable stage, where a task is left."""
    if keys[steering.STAGE] != steering.MOVES[stage]:
        raise stop.Stop(
            f"rn: the session is at the {keys[steering.STAGE]} stage, and moves to {stage} from the"
            f" {steering.MOVES[stage]} stage alone; the other stages move at the sign-offs, with"
            " `rn.py answer`"
        )
    if stage == steering.BUILD:  # pragma: no mutate
        designed = [c for c in calls(folder) if c.stage == steering.DESIGN]  # pragma: no mutate
        made = [c.work for c in designed if c.work != steering.PLAN]
        if made:
            raise stop.Stop(
                f"rn: the design stage made {stop.joined(list(dict.fromkeys(made)))}, which go to the"
                " design sign-off; show it with `rn.py proposal design`, and the user's approval"
                " there moves the session to build"
            )
    left = [task.id for task in steering.tasks_of(plan)]
    if stage == steering.DELIVERABLE and left:
        raise stop.Stop(
            f"rn: {stop.joined(left)} is still in the steering, and the finished work is checked once no"
            " task is; tick each action done with --done T<n>.<action>, then run this again"
        )
    return {**keys, steering.STAGE: stage}
