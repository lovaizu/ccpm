"""The session the checked-out branch is in and its record, the folder `.rn/<yyyymmdd>-<slug>/`: the
session started with its pull request, the steering as the last keep left it, written with its
Markdown, each move written, and committed and pushed as its step ends, each call as the files of
one number, the works rn makes, each part the orchestrator writes cut and put back, each task taken
out once turn has returned it, and the stage moved at a stage's end."""

from __future__ import annotations

import datetime
import functools
import json
import os
import re
from collections.abc import Callable
from typing import Any, NamedTuple

import call
import learnings
import repo
import steering
import stop

# The folder in the user's repository holding every session's record and the user's checklists, and
# a session's folder in it, by the date it began and its slug.
RECORD = ".rn"
SESSION_NAME = re.compile(r"[0-9]{8}-[a-z0-9-]+")
# The session's steering, the Markdown the user reads of it, and the folder of its calls, in the
# session's folder.
STEERING = "steering.json"
MARKDOWN = "steering.md"
CALLS = "calls"
# Each decision an answer replaced, a JSON object a line, in the session's folder: one step's commit
# keeps every move of it, so a decision replaced within a step shows in no version of its CCS.
REPLACED = "replaced.jsonl"
# The works rn makes: the plan and the learnings, both written by the orchestrator; and, made by
# turn, the finished work; the result of each task, `t<n>` for task T<n>, made by one call to turn,
# such as a research result, a document or a part of the finished work; and a checklist of a kind.
TASK_WORK = re.compile(r"t(?P<task>[0-9]+)")
CHECKLIST_WORK = re.compile(r"checklist-[a-z0-9-]+")
WORKS = (
    f"{steering.PLAN}, {steering.LEARNINGS}, {steering.DELIVERABLE}, t<n> for task T<n>, or"
    " checklist-<kind>"
)
# The works the ux and the architecture stage each make for their sign-off: each task's result and
# each checklist.
DOCUMENTED = re.compile(rf"{TASK_WORK.pattern}|{CHECKLIST_WORK.pattern}")
# The works whose call makes a part the orchestrator writes, cut into a file of its own, each with
# what its file is named: the plan's the plan as JSON in the steering's form, the learnings' the
# session's learnings.
PART = {steering.PLAN: "plan.json", steering.LEARNINGS: learnings.FILE}
PARTS = tuple(PART)
# A file of a call, by its number and what it is: the CCS, turn's result for a call to turn, or the
# part the orchestrator writes for a call on a part.
CCS = "ccs.json"
RESULT = "result.json"
CALL = re.compile(rf"([0-9]{{4}})-({'|'.join(map(re.escape, (CCS, RESULT, *PART.values())))})")
# The keys of the CCS entries rn reads back: the work's name, each decision of the work as
# `<title>: <what it says>`, and each choice made for it that no answer of the user's gave, as
# `<what was chosen>: <why>`; the stage it was made in is under the key of the stage.
WORK = "work"
STAGE = "stage"
DECISION = "decision"
CHOSEN = "chosen"
# The step of /rn:up each move whose next step is always the same leads to, as Next, by the number
# orchestrator.md and the files of its stages give it: a session started, and a stage moved at its
# end.
STARTED = "Step 8 of /rn:up on plan: hear the purpose and what shows it done"
STAGED = {
    steering.ARCHITECTURE: (
        "Step 10 of /rn:up on plan: hear which documents of how the work is built and checked it"
        " needs"
    ),
    steering.BUILD: "Step 11 of /rn:up on plan: make the tasks that build the finished work",
    steering.DELIVERABLE: (
        "Step 11 of /rn:up on deliverable: have the finished work used for each acceptance"
        " criterion"
    ),
    steering.FINISHED: "Nothing is left: the pull request waits for the user's merge",
}
# A task done, as `state --done` takes it.
DONE = re.compile(r"T[0-9]+")


def worked(work: str) -> str:
    """The work, when it names one rn makes; stops otherwise."""
    named = (TASK_WORK, CHECKLIST_WORK)
    if work not in PARTS + (steering.DELIVERABLE,) and not any(n.fullmatch(work) for n in named):
        raise stop.Stop(f"rn: the work {work!r} is none rn makes; give {WORKS}, such as t1")
    return work


def task_of(work: str) -> str:
    """The ID of the task whose result the work is, "" where the work is no task's."""
    named = TASK_WORK.fullmatch(work)
    return f"T{named['task']}" if named else ""


def task_in(steered: dict[str, Any], work: str) -> dict[str, Any]:
    """The task of the plan whose result the work is; stops where the plan holds no such task."""
    found = steering.task_of(steered["plan"], task_of(work))
    if found is None:
        raise stop.Stop(
            f"rn: the plan holds no task {task_of(work)}, whose result the work {work} is; give"
            " the work of a task the plan holds as t<n>, such as t1, or write the plan again with"
            " it, keep it, then run this again"
        )
    return found


def replaced_path(folder: str) -> str:
    """The path of the session's record of the decisions an answer replaced."""
    return os.path.join(folder, REPLACED)


def steering_path(folder: str) -> str:
    """The path of the session's steering."""
    return os.path.join(folder, STEERING)


def markdown_path(folder: str) -> str:
    """The path of the Markdown the user reads of the session's steering."""
    return os.path.join(folder, MARKDOWN)


def call_path(folder: str, number: str, what: str) -> str:
    """The path of a file of the session's call of the number: its CCS, its result or its part."""
    return os.path.join(folder, CALLS, f"{number}-{what}")


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
        and steering.stage_of(repo.at("HEAD", steering_path(f))) != steering.FINISHED
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


def where() -> dict[str, str | None]:
    """The session the checked-out branch is in, with its stage and the sign-off waiting, as its
    steering's last commit holds them; None for each where there is none. Stops where rn is not at
    the top of a repository, git cannot tell the branch's changes, or the branch changed more than
    one session not finished."""
    found = session()
    if found is None:
        return {"session": None, "stage": None, "signoff": None}
    text = repo.at("HEAD", steering_path(found))
    return {
        "session": found,
        "stage": steering.stage_of(text),
        "signoff": steering.signoff_of(text),
    }


def done_tasks(folder: str, plan: dict[str, Any], found: list[Call] | None = None) -> set[str]:
    """Each task done: one the plan no longer holds whose result turn returned for its latest
    call, of the calls given or, where none are, the session's."""
    left = {t["id"] for t in plan["tasks"]}
    last = {c.work: c for c in (calls(folder) if found is None else found)}
    return {task_of(w) for w, c in last.items() if task_of(w) and c.closed} - left


def kept_steering(folder: str) -> dict[str, Any]:
    """The steering as the last keep left it in git's index, as each keep, committing or not,
    writes it there; stops where the working tree's differs from it, with how to restore it, or
    where it is out of its form, as only a commit made by hand leaves it."""
    path = steering_path(folder)
    last = repo.staged(path)
    if (repo.read_text(path) if os.path.isfile(path) else None) != last:
        raise stop.Stop(
            f"rn: {path} differs from what the last keep left, and rn's scripts alone write it;"
            f" restore it with `git checkout -- {path}`, then run this again"
        )
    data = steering.read(last)
    point = (
        "$: expected the steering as JSON, found none"
        if data is None
        else steering.out_of_form(data, done_of(folder, data))
    )
    if point:
        raise stop.Stop(
            f"rn: {path} as the last keep left it is out of its form: {point}; rn keeps none so,"
            f" so restore the last one rn kept with `git checkout <commit> -- {path}`, the commit"
            f" found with `git log -- {path}`, then run this again, which keeps it"
        )
    return data


def done_of(folder: str, data: Any) -> set[str]:
    """The tasks done beside the steering's plan, none where it holds no plan of tasks that can be
    read, as its form is then named without them."""
    try:
        ids = {t["id"] for t in data["plan"]["tasks"]}
    except (TypeError, KeyError):
        return set()
    return done_tasks(folder, {"tasks": [{"id": i} for i in ids]})


def write(folder: str, steered: dict[str, Any]) -> None:
    """Writes the steering, once it holds its form, and the Markdown the user reads of it, into the
    working tree and git's index, where kept_steering reads what the last keep left. Stops, writing
    nothing, where it is out of its form; and where git fails."""
    steering.held_form(steered, done_tasks(folder, steered["plan"]))
    path, markdown = steering_path(folder), markdown_path(folder)
    repo.write_text(path, steering.text(steered))
    repo.write_text(markdown, steering.markdown(steered))
    repo.git(["add", "--", path, markdown], repo.AS_GIT_SAYS)


def written(folder: str, steered: dict[str, Any], message: str) -> None:
    """Keeps a move its step goes on after, such as one kept before a point is asked: the steering
    written, and the message held for the commit the step ends with, as going on from a stop needs
    the files, not the push, and a push at each answer holds the run it answers. Stops, writing
    nothing, where the steering is out of its form; and where git fails."""
    write(folder, steered)
    repo.hold(message)


def keep(folder: str, steered: dict[str, Any], message: str) -> str:
    """Keeps the move a step ends with: the steering written, and every change of the step
    committed with the message, then the message of each move written since the last commit, in
    the order written, then pushed; gives the commit. Stops, writing nothing, where the steering is
    out of its form; and where git fails."""
    write(folder, steered)
    if repo.changed():
        repo.git(["add", "-A"], repo.AS_GIT_SAYS)
        said = "\n\n".join([message, *repo.held()])
        repo.git(["commit", "-q", "-F", "-"], repo.AS_GIT_SAYS, said)
    repo.let_go()
    repo.push()
    return repo.git(["rev-parse", "HEAD"], repo.AS_GIT_SAYS).strip()


class Call(NamedTuple):
    """A call: its number, the work it is on and the stage it was made in, as its CCS names them,
    its CCS, and whether it takes no more decisions: turn returned its result, or, on the plan or
    the learnings, its part is cut, as the orchestrator writes it at once from the CCS as it
    stands."""

    number: str
    work: str
    stage: str
    ccs: dict[str, list[dict[str, str]]]
    closed: bool


def calls(folder: str, commit: str | None = None) -> list[Call]:
    """Each call of the session, in the order made, as the working tree holds them, or the commit
    given; stops where a CCS is no JSON object, saying how to restore it."""
    place = os.path.join(folder, CALLS)
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
        work, stage = (next(iter(call.entries(ccs, key)), "") for key in (WORK, STAGE))
        closing = (RESULT, PART.get(work))
        found.append(Call(number, work, stage, ccs, any(c in files[number] for c in closing)))
    return found


def latest(found: list[Call], work: str) -> Call | None:
    """The work's latest call; None where it has none."""
    return next((c for c in reversed(found) if c.work == work), None)


def decisions_of(made: Call) -> list[str]:
    """Each decision of the call, in the order kept."""
    return call.entries(made.ccs, DECISION)


def choices_of(made: Call | None) -> list[str]:
    """Each choice made in the user's place the call keeps, in the order kept; none where there is
    no call."""
    return [] if made is None else call.entries(made.ccs, CHOSEN)


def next_number(found: list[Call]) -> str:
    """The number of a new call, the one after the last."""
    return f"{int(found[-1].number) + 1 if found else 1:04d}"


# A task's ID as a change to the steering shows it, added or removed, with the task's number.
CHANGED_TASK = re.compile(r'^[+-]\s*"id": "T([0-9]+)"', re.MULTILINE)


def numbered_on(
    folder: str, plan: dict[str, Any], found: list[Call], part: dict[str, Any], number: str
) -> None:
    """Returns when each task of the part is one the plan holds, one done, put back so its result
    is made again on its own calls, or numbered above every task any version of the steering held
    on the branch since it left the default branch, so an ID never names two tasks; stops
    otherwise, keeping nothing."""
    changes = repo.git(
        ["log", "-p", "--format=", f"{repo.base()}..HEAD", "--", steering_path(folder)],
        repo.AS_GIT_SAYS,
    )
    most = max((int(n) for n in CHANGED_TASK.findall(changes)), default=0)
    left = [t["id"] for t in plan["tasks"]]
    done = done_tasks(folder, plan, found)
    stray = [
        t["id"]
        for t in part["tasks"]
        if t["id"] not in left and t["id"] not in done and int(t["id"][1:]) <= most
    ]
    if stray:
        raise stop.Stop(
            f"rn: the part of the call {number} holds {stop.joined(stray)}, neither a task the"
            " steering holds, nor one done, nor numbered above every task it has held, and an ID"
            " names one task alone; nothing is kept: write the part again, each new task numbered"
            f" from T{most + 1}, then run this again"
        )


def dropped(folder: str, found: list[Call], task_id: str, number: str) -> None:
    """Returns when the plan written for the call of the number may leave the task out: turn has
    returned the result of the task's latest call, or the task has no call, as a task no longer
    needed was never made; stops otherwise, keeping nothing, as a task leaves the plan only once
    the result made for it is back."""
    last = latest(found, task_id.lower())
    if last is not None and not last.closed:
        raise stop.Stop(
            f"rn: the part of the call {number} leaves out {task_id}, and turn has not returned"
            f" its result: {call_path(folder, last.number, RESULT)} is not there; keep {task_id}"
            f" in the part until turn returns the call `rn.py ccs {task_id.lower()}` prints, then"
            " run this again; nothing is kept"
        )


def part_of(folder: str, number: str) -> tuple[Call, Any]:
    """The call of the number and the part the orchestrator writes for it, the plan as JSON, the
    learnings as their lines; stops where the session holds no such call, the call makes no part,
    its part is not cut, or the plan's is no JSON."""
    found = next((c for c in calls(folder) if c.number == number), None)
    if found is None:
        raise stop.Stop(
            f"rn: {os.path.join(folder, CALLS)} holds no call {number}; give the number of a call"
            " on plan or learnings, such as 0001"
        )
    if found.work not in PARTS:
        raise stop.Stop(
            f"rn: the call {number} is on {found.work}, which makes no part rn puts back; give a"
            " call on plan or learnings"
        )
    path = call_path(folder, number, PART[found.work])
    if not os.path.isfile(path):
        raise stop.Stop(
            f"rn: {path}, the part the call {number} makes, is not there; cut it with"
            f" `rn.py ccs {found.work}`, write it, then run this again"
        )
    text = repo.read_text(path)
    if found.work == steering.LEARNINGS:  # pragma: no mutate
        return found, learnings.trimmed(text.splitlines())
    part = steering.read(text)
    if part is None:
        raise stop.Stop(
            f"rn: {path} is no JSON; write the plan there as JSON in the steering's form, as rn.py"
            f" cut it, then run this again"
        )
    return found, part


def moved(status: dict[str, Any], stage: str, plan: dict[str, Any], folder: str) -> dict[str, Any]:
    """The status with the stage moved to the one given; stops where the session is not at the
    stage it moves from; from the ux or the architecture stage, where a call made in it is on a work
    its sign-off shows, a document or a checklist made, which goes to that sign-off; and to the
    deliverable stage, where a task is left."""
    was = steering.MOVES[stage]
    if status["stage"] != was:
        raise stop.Stop(
            f"rn: the session is at the {status['stage']} stage, and moves to {stage} from the"
            f" {was} stage alone; the other stages move at the sign-offs, with `rn.py answer`"
        )
    if was in steering.SIGNOFFS:
        made = [c.work for c in calls(folder) if c.stage == was and DOCUMENTED.fullmatch(c.work)]
        if made:
            raise stop.Stop(
                f"rn: the {was} stage made {stop.joined(list(dict.fromkeys(made)))}, which go to"
                f" the {was} sign-off; show it with `rn.py proposal {was}`, and the user's"
                f" approval there moves the session to {stage}"
            )
    left = [t["id"] for t in plan["tasks"]]
    if stage == steering.DELIVERABLE and left:
        raise stop.Stop(
            f"rn: {stop.joined(left)} is still in the plan, and the finished work is checked once"
            " no task is; take each out with --done T<n> once turn has returned it, then run this"
            " again"
        )
    return {**status, "stage": stage}


def cut(work: str, steered: dict[str, Any]) -> str:
    """The part a call on the plan or the learnings makes, as it is cut for the orchestrator to
    write: the plan as JSON in the steering's form, the learnings none, as they are written
    once."""
    if work == steering.PLAN:  # pragma: no mutate
        return steering.text(steered["plan"])
    return ""


def put_part(
    folder: str, steered: dict[str, Any], number: str | None
) -> tuple[dict[str, Any], list[str]]:
    """The steering and the session's learnings once the part of the call of the number is put
    back, as put says; the steering as it is and none where no number is given."""
    if number is None:
        return steered, []
    return put(folder, steered, *part_of(folder, number))


def put(
    folder: str, steered: dict[str, Any], made: Call, part: Any
) -> tuple[dict[str, Any], list[str]]:
    """The steering and the session's learnings with the part written for the call put back: the
    plan's as the steering's plan, none of the learnings; the learnings' as the session's learnings.
    Stops, the point at the part's own place, where the plan's is out of its form, a task of it is
    numbered as one held before, or it takes out a task turn has not returned."""
    if made.work == steering.LEARNINGS:  # pragma: no mutate
        return steered, part
    found = calls(folder)
    point = steering.part_out(part, done_tasks(folder, steered["plan"], found))
    if point:
        raise stop.Stop(
            f"rn: {call_path(folder, made.number, PART[made.work])} would be out of its form:"
            f" {point}; change it so it holds, then run this again"
        )
    numbered_on(folder, steered["plan"], found, part, made.number)
    kept_ids = {t["id"] for t in part["tasks"]}
    for task in steered["plan"]["tasks"]:
        if task["id"] not in kept_ids:
            dropped(folder, found, task["id"], made.number)
    return {**steered, "plan": part}, []


def held_part(folder: str, number: str) -> str | None:
    """The Markdown of the plan the orchestrator wrote for the call of the number, as the steering
    would show it once `state --put` puts it back, for the orchestrator to check as the user reads
    it; None for the learnings'. Holds the part to what `state` holds it to at the keep: the plan's
    in its form, each new task numbered above those held, each task it takes out returned, and the
    learnings' in theirs; keeps nothing. Stops otherwise, the point at the part's own place, as its
    writer reads it; and where the steering differs from what the last keep left, or the part
    cannot be taken."""
    steered = kept_steering(folder)
    made, part = part_of(folder, number)
    put_steering, learnt = put(folder, steered, made, part)
    if made.work == steering.PLAN:  # pragma: no mutate
        return steering.markdown(put_steering)
    point = learnings.out(learnt)
    if point:
        raise stop.Stop(
            f"rn: {call_path(folder, number, PART[made.work])} would be out of its form: {point};"
            " change it so it holds, then run this again"
        )
    return None


def state(
    given_next: str | None,
    opened: list[str],
    done: list[str],
    number: str | None,
    stage: str | None,
    message: str,
    goes_on: bool,
) -> dict[str, str]:
    """Keeps the move: the part of the call of the number put back, the plan's into the steering,
    the learnings' as the session's learnings; each task done taken out of the plan, once turn has
    returned its result; the stage moved where given; Next and Open replaced whole, Next as the
    stage moved leads where none is given; then, as the step ends, every change committed and
    pushed as keep says, giving the commit, and the line told where a task is done; or, where the
    step goes on after it, the move written as written says, giving the steering's path. Stops,
    keeping nothing, where a move the step goes on after puts a part back, takes a task out or
    moves the stage, each of which ends a step, Next is empty, the branch holds no session, the
    steering differs from what the last keep left, a part, a task or a stage cannot be taken, or
    the steering or the learnings would be out of their form; and where git fails."""
    if goes_on and (number or done or stage):
        raise stop.Stop(
            "rn: a move within a step puts no part back, takes no task out and moves no stage, as"
            " each ends the step; keep it without --goes-on"
        )
    folder = current()
    steered = kept_steering(folder)
    status = steered["status"]
    if given_next is not None:
        next_step = stop.given(given_next, "next step")
    elif stage is not None:
        next_step = STAGED[stage]
    else:
        next_step = status["next_step"]
    steered, learnt = put_part(folder, steered, number)
    found = calls(folder)
    for one in done:
        if not DONE.fullmatch(one) or steering.task_of(steered["plan"], one) is None:
            raise stop.Stop(
                f"rn: the plan holds no task {one}; give each task done as T<n>, of a task the"
                " plan holds, such as T1"
            )
        last = latest(found, one.lower())
        if last is None or not last.closed:
            raise stop.Stop(
                f"rn: turn has not returned {one}'s result, and a task leaves the plan only once"
                f" it has; have turn make it with the call `rn.py ccs {one.lower()}` prints, read"
                " it at each item's lines, then run this again; nothing is kept"
            )
    plan = steering.without(steered["plan"], done)
    tell = steering.told_done(steered["plan"], done)
    status = status if stage is None else moved(status, stage, plan, folder)
    status = {**status, "next_step": next_step, "open_questions": list(opened)}
    steered = {**steered, "plan": plan, "status": status}
    pr = str(steered["session"]["pr"])
    # The steering is held to its form before the learnings are written, so a stop leaves neither.
    steering.held_form(steered, done_tasks(folder, plan, found))
    if stage == steering.FINISHED:
        # The pull request is marked ready before the session is kept finished, so a gh that
        # fails leaves the session to go on from here.
        again = "run `rn.py state --stage finished` again"
        repo.gh(["pr", "ready", pr], again)
    if goes_on:
        written(folder, steered, message)
        return {"written": steering_path(folder)}
    if learnt:
        learnings.write(folder, learnt)
    commit = keep(folder, steered, message)
    return {"kept": commit, "tell": tell} if tell else {"kept": commit}


def started(slug: str, today: datetime.date, steered: dict[str, Any], message: str) -> str:
    """The session started on a branch of its own named by the slug, made from the remote's default
    branch as it is now, its folder named by the day and the slug, and the steering kept in it with
    the message; gives the folder. Stops, leaving the checked-out branch as it is, where the
    steering is out of its form, the folder is on the default branch already, or the branch is
    there; and where git fails."""
    repo.git(["fetch", "-q", "origin"], repo.AS_GIT_SAYS)
    branch = repo.default_branch()
    folder = os.path.join(RECORD, f"{today:%Y%m%d}-{slug}")
    if repo.git(["ls-tree", "--name-only", branch, "--", folder], repo.AS_GIT_SAYS):
        raise stop.Stop(f"rn: {folder} is on {branch} already; give another slug")
    steering.held_form(steered, ())
    repo.git(["checkout", "-q", "--no-track", "-b", slug, branch], "give another slug")
    keep(folder, steered, message)
    return folder


def opened_pr(folder: str, slug: str, steered: dict[str, Any], title: str) -> str:
    """The draft pull request of the session's branch opened into the default branch, with the
    title and a body linking the steering's Markdown, and its URL kept as the steering's pr; gives
    it. Stops where gh or git fails, saying to run `rn.py start` again."""
    again = "run `rn.py start` again with the same arguments on this branch"
    repository = repo.gh(["repo", "view", "--json", "url", "--jq", ".url"], again)
    link = f"[{MARKDOWN}]({repository}/blob/{slug}/{markdown_path(folder)})"
    into = repo.default_branch().partition("/")[2]
    asked = ["pr", "create", "--draft", "--base", into, "--head", slug, "--title", title]
    pr = repo.gh([*asked, "--body", link], again)
    keep(folder, {**steered, "session": {**steered["session"], "pr": pr}}, f"pr: {pr}")
    return pr


def version(root: str) -> str:
    """rn's version, as its manifest at root gives it; stops where it gives none."""
    path = os.path.join(root, ".claude-plugin", "plugin.json")
    try:
        with open(path, encoding="utf-8") as f:
            return str(json.load(f)["version"])
    except (OSError, ValueError, KeyError):
        raise stop.Stop(f"rn: {path} gives no version of rn; install rn again") from None


def start(
    slug: str,
    title: str,
    languages: dict[str, str],
    message: str,
    root: str,
    today: datetime.date,
) -> dict[str, str]:
    """Starts a session on a branch of its own named by the slug, made from the remote's default
    branch as it is now: its steering at the goal stage, with the version of rn installed at root,
    the title, the languages, Next and nothing open, kept with the message; then the draft pull
    request opened, its body linking the steering's Markdown, and its URL kept as the steering's
    pr. Run again on that branch where the pull request was not opened, it opens it. Gives the
    folder, the branch and the pull request. Stops, leaving the checked-out branch as it is, where
    rn is not at the top of a repository, the working tree has changes not committed, the folder or
    the branch is there already, or rn's version is not there; and where git or gh fails."""
    repo.at_top()
    paths = repo.changed()
    if paths:
        raise stop.Stop(
            f"rn: the working tree has changes not committed: {', '.join(paths)}; rn leaves them as"
            " they are, and starts from the default branch: commit or stash them, then run this"
            " again"
        )
    if repo.branch() == slug:
        folder = current()
        steered = kept_steering(folder)
        if steered["session"]["pr"] is not None:
            raise stop.Stop(
                f"rn: the session {folder} is started already, with its pull request"
                f" {steered['session']['pr']}; go on with it with /rn:up"
            )
    else:
        steered = steering.made(version(root), title, languages, STARTED)
        folder = started(slug, today, steered, message)
    pr = opened_pr(folder, slug, steered, title)
    return {"session": folder, "branch": slug, "pr": pr}
