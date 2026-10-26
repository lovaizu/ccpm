"""What a work's CCS holds beside its decisions, so turn makes the work from the session's record
alone: the checklists of its kind, what its receiver has, the goal and the criteria it serves, the
finished work's files, and for the plan what each task done served, decided and made."""

from __future__ import annotations

import glob
import os
import shlex
from typing import Any, NamedTuple

import call
import repo
import session
import steering
import stop

# For each role turn reads from a CCS, the key of the CCS entries that hold it; the call to turn:up
# hands this table to turn.
ENTRIES = {
    "work": "path",
    "checklist": "checklist",
    "receiver": "audience",
    "use": "purpose",
    "has": "has",
}
# The key of the CCS entries each holding a goal or a criterion the work serves.
SERVES = "serves"
# The key of the CCS entry naming the kind of the work, whose checklists it is made with.
KIND = "kind"
# The kind of a checklist, which rn's checklist for checklists makes from rn's `usability.md`, what
# any reader needs, as well.
CHECKLIST = "checklist"
# The works rn makes the same way every time, each with its kind, its receiver and their use: the
# plan, the learnings and the finished work.
OWN = {
    steering.PLAN: (
        "plan",
        (
            "the user at the plan sign-off, approving what the finished work will do and why, and"
            " rn's orchestrator in any later conversation, carrying the work on without asking"
            " them again"
        ),
        "approving the goal and the acceptance criteria, then carrying each later work to them",
    ),
    steering.LEARNINGS: (
        "learnings",
        "the user deciding each learning once the finished work is approved",
        (
            "deciding where each learning goes: their checklists, an issue to rn's makers, both,"
            " or neither"
        ),
    ),
    steering.DELIVERABLE: (
        "deliverable",
        "the user at the deliverable sign-off",
        "checking that the finished work does each acceptance criterion",
    ),
}


class Made(NamedTuple):
    """How a work is made, as far as rn knows it before the orchestrator gives the rest: the kind,
    its receiver and their use, the paths it is, and what the receiver has; None, or none, for each
    rn does not know."""

    kind: str | None
    receiver: str | None
    use: str | None
    paths: list[str]
    has: list[str]


def made_as(work: str, steered: steering.Steering, folder: str, root: str) -> Made:
    """How rn makes the work every time: one of its own as OWN, `checklist-<kind>` and `issue-<n>`
    have it, what the receiver has the whole repository, rn's own folder for an issue to its makers;
    a task's work of the kind, at the path, its action names, the rest given or kept; the paths of
    the plan, the learnings and the finished work are found as their CCS is written, and the
    learnings' receiver has the records shown then."""
    if work in OWN:
        kind, receiver, use = OWN[work]
        return Made(kind, receiver, use, [], ["."])
    if session.CHECKLIST_WORK.fullmatch(work):
        made = work.partition("-")[2]
        a = "an" if made.startswith(tuple("aeiou")) else "a"
        return Made(
            CHECKLIST,
            f"whoever makes {a} {made} work in this repository and whoever judges it",
            f"making and judging each {made} work",
            [os.path.join(session.RECORD, "checklists", f"{made}.md")],
            ["."],
        )
    if session.ISSUE_WORK.fullmatch(work):
        return Made(
            "issue",
            "rn's makers, reading the issue on lovaizu/ccpm, who build rn for all its users",
            "deciding how rn changes so that every user's later work meets the need",
            [os.path.join(folder, f"{work}.md")],
            [root],
        )
    action = session.made_by(steered, work)
    return Made(action.kind, None, None, [action.path or ""], [])


def kept_as(last: session.Call | None) -> Made:
    """How the work was made in its latest call, as its CCS names it; none of it where it has
    none."""
    ccs = {} if last is None else last.ccs
    first = {name: next(iter(call.entries(ccs, key)), None) for name, key in ENTRIES.items()}
    return Made(
        next(iter(call.entries(ccs, KIND)), None),
        first["receiver"],
        first["use"],
        call.entries(ccs, ENTRIES["work"]),
        call.entries(ccs, ENTRIES["has"]),
    )


def rns_own(kind: str, root: str) -> list[str]:
    """rn's own checklist for the kind, in any folder of rn's checklists; none where rn has none."""
    return sorted(glob.glob(os.path.join(root, "checklists", "**", f"{kind}.md"), recursive=True))


def checklists(kind: str, root: str) -> list[str]:
    """The checklists for the kind: rn's own, then the user's addition; stops where neither is
    there."""
    found = rns_own(kind, root)
    added = os.path.join(session.RECORD, "checklists", f"{kind}.md")
    if os.path.isfile(added):
        found.append(added)
    if not found:
        raise stop.Stop(
            f"rn: there is no checklist for the kind {kind}, neither rn's nor {added}; make"
            f" {added} first, as a work of its own to rn's checklist for checklists"
        )
    return found


def has_path(path: str) -> str:
    """The path of what the receiver has with the work, when a file or folder is there; stops
    otherwise, as turn stops a call naming one that is not."""
    if not os.path.exists(path):
        raise stop.Stop(
            f"rn: what the receiver has, {path}, is not there; give the path of a file or folder"
            " they have with the work, from the top"
        )
    return path


def finished_work() -> list[str]:
    """Each file the branch changed since it left the default branch outside `.rn/`, in the order
    of their paths, which is the finished work; a file it removed is not, as it is not there to
    use. Stops where there is none."""
    paths = repo.git(
        [
            "diff",
            "--name-only",
            "--diff-filter=d",
            repo.base(),
            "HEAD",
            "--",
            f":(exclude){session.RECORD}",
        ],
        repo.AS_GIT_SAYS,
    ).splitlines()
    if not paths:
        raise stop.Stop(
            f"rn: the branch changed no file outside {session.RECORD}/ since it left"
            f" {repo.default_branch()}, so there is no finished work to name; have each task made"
            " and kept, or give the work's paths, then run this again"
        )
    return paths


def served(steered: steering.Steering, work: str) -> dict[str, str]:
    """The goal and each criterion the work serves, by ID, as the steering says each on one line:
    those its task's line names for a task's work; the goal and every criterion for the finished
    work, which is checked for each; none for any other, the plan making them, and the learnings
    and a checklist serving none of the user's work. Stops where the steering holds no task of a
    task's work."""
    said = steering.decided(steered.plan)
    if work == steering.DELIVERABLE:
        return said
    if not session.TASK_WORK.fullmatch(work):
        return {}
    session.made_by(steered, work)
    task = {t.id: t for t in steering.tasks_of(steered.plan)}[session.task_of(work)]
    return {key: text for key, text in said.items() if key in (task.serves or [])}


def test_of(steered: steering.Steering, work: str, number: str, root: str) -> str | None:
    """The command that checks the work, for the call of the number that makes it: for a part rn
    puts back, the plan or the learnings, rn.py's check of it as `state --put` holds it, run by rn
    where it is installed at root, as no task's command is for those; the one the completion
    criterion of the work's task names, where it is one, for the task's last action of turn's, which
    makes its result, the actions of turn's before it making the check and seeing it fail; None for
    any other work."""
    if work in session.PARTS:
        return f"python3 {shlex.quote(os.path.join(root, 'scripts', 'rn.py'))} check {number}"
    task = {t.id: t for t in steering.tasks_of(steered.plan)}.get(session.task_of(work))
    if task is None or not task.tests:
        return None
    # The form holds one command at most, and the work, of an action of turn's, one action at least.
    [(_, _, command)] = task.tests
    *_, last = [a.number for _, _, a in task.actions if a is not None and a.path is not None]
    return {f"{task.id.lower()}.{last}": command}.get(work)


def done_made(folder: str, found: list[session.Call], plan: list[str]) -> list[str]:
    """The CCS of the latest call of each work of a task the plan no longer holds, done, in the
    order those calls were made: what the task served and decided, and the files it made, which
    is what the plan is made again from; turn's results are left out, as what they hold beside the
    work, each item's Good, changes no task."""
    left = [task.id for task in steering.tasks_of(plan)]
    last = {c.work: c.number for c in found}
    return [
        session.call_path(folder, number, session.CCS)
        for work, number in sorted(last.items(), key=lambda item: item[1])
        if session.task_of(work) and session.task_of(work) not in left
    ]


def needed(value: Any, what: str, work: str) -> Any:
    """The value, when the work has it; stops where it has none, saying how to give it."""
    if not value:
        raise stop.Stop(
            f"rn: no {what} of the work {work} is given, and no call on it names one; give it with"
            f" --{what}"
        )
    return value


def cut(work: str, steered: steering.Steering) -> str:
    """The part a call on the plan or the learnings makes, as it is cut for turn: the plan from the
    title through the tasks, the learnings none, as those kept are not made again."""
    return {steering.PLAN: "\n".join(steered.plan) + "\n", steering.LEARNINGS: ""}[work]


def written(
    work: str,
    steered: steering.Steering,
    made: Made,
    serving: dict[str, str],
    checklists: list[str],
    decisions: list[str],
    root: str,
) -> dict[str, list[dict[str, str]]]:
    """The work's CCS, in four parts, the shape turn takes: focal_entities, what the work is about,
    the work by its name, the stage it is made in, its kind, its paths, its receiver and what they
    have with it; goal_orientation, what the work is for, its use and what it serves as text, as
    turn makes the work from the CCS and the files it names alone; retrieved_artifacts, the kind's
    checklists and rn's `usability.md` where the work is a checklist; and constraints, the bounds
    it is made in: its decisions, the languages, English for an issue to rn's makers, and rn's
    checklist for a fix, which turn's roles
    are given to read, as each file a CCS names is, for a work made again. turn finds each entry by
    its key, whichever part holds it."""
    usability = os.path.join(root, "checklists", "usability.md")
    # An issue is written in English, the language of rn's makers' repository, whatever the
    # language of the user's.
    english = {steering.LANGUAGES[0]: "English"} if session.ISSUE_WORK.fullmatch(work) else {}
    languages = {**steered.keys, **english}
    return {
        "focal_entities": [
            {session.WORK: work},
            {steering.STAGE: steered.keys[steering.STAGE]},
            {KIND: made.kind or ""},
        ]
        + [{ENTRIES["work"]: p} for p in made.paths]
        + [{ENTRIES["receiver"]: made.receiver or ""}]
        + [{ENTRIES["has"]: p} for p in made.has],
        "goal_orientation": [{ENTRIES["use"]: made.use or ""}]
        + [{SERVES: f"{key}: {text}"} for key, text in serving.items()],
        "retrieved_artifacts": [{ENTRIES["checklist"]: p} for p in checklists]
        + ([{"source": usability}] if session.CHECKLIST_WORK.fullmatch(work) else []),
        "constraints": [{session.DECISION: d} for d in decisions]
        + [{key: languages[key]} for key in steering.LANGUAGES]
        + [{"fix": os.path.join(root, "checklists", "fix.md")}],
    }


def told(work: str, steered: steering.Steering) -> str:
    """The line telling the user what turn makes, and that it is used in their place before it
    comes back, which they can stop."""
    if work in OWN:
        words = {
            steering.PLAN: "the plan",
            steering.LEARNINGS: "the learnings of the stretch just answered",
            steering.DELIVERABLE: "the use of the finished work for each acceptance criterion",
        }[work]
    elif session.CHECKLIST_WORK.fullmatch(work):
        words = f"your checklist for {work.partition('-')[2]}"
    elif session.ISSUE_WORK.fullmatch(work):
        words = f"the issue {work.partition('-')[2]} to rn's makers"
    else:
        words = f"{work.upper()}, {steering.lowered(session.made_by(steered, work).what)}"
    return (
        f"turn makes {words}, and an AI that did not make it uses it in your place before it comes"
        " back; say stop to stop it."
    )
