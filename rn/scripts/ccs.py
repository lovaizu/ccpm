"""What a work's CCS holds beside its decisions, so turn makes the work from the session's record
alone: the checklists of its kind, what its receiver has, the goal and the criteria it serves, the
finished work's files, and for the plan what each task done served, decided and made."""

from __future__ import annotations

import glob
import os

import repo
import session
import steering
import stop

# For each role turn reads from a CCS, the key of the CCS entries that hold it; the call to turn:up
# hands this table to turn.
ENTRIES = {
    "work": "deliverable",
    "checklist": "checklist",
    "receiver": "audience",
    "use": "purpose",
    "has": "has",
}
# The key of the CCS entries each holding a goal or a criterion the work serves.
SERVES = "serves"
# The kind of a checklist, which rn's checklist for checklists makes from rn's `usability.md`, what
# any reader needs, as well.
CHECKLIST = "checklist"


def own(kind: str, root: str) -> list[str]:
    """rn's own checklist for the kind, in any folder of rn's checklists; none where rn has none."""
    return sorted(glob.glob(os.path.join(root, "checklists", "**", f"{kind}.md"), recursive=True))


def checklists(kind: str, root: str) -> list[str]:
    """The checklists for the kind: rn's own, then the user's addition; stops where neither is
    there."""
    found = own(kind, root)
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
            f"rn: the branch changed no file outside {session.RECORD}/ since it left {repo.default_branch()}, so"
            " there is no finished work to name; have each task made and kept, or give the work's"
            " paths, then run this again"
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
    task = next(t for t in steering.tasks_of(steered.plan) if t.id == session.task_of(work))
    return {key: text for key, text in said.items() if key in (task.serves or [])}


def test_of(steered: steering.Steering, work: str) -> str | None:
    """The command that checks the work, for the call that makes it: the one the completion
    criterion of the work's task names, where it is one, for the task's last action of turn's, which
    makes its result, the actions of turn's before it making the check and seeing it fail; None for
    any other work."""
    task = next((t for t in steering.tasks_of(steered.plan) if t.id == session.task_of(work)), None)
    if task is None or not task.tests:
        return None
    last = [action.number for _, _, action in task.actions if action and action.path][-1]
    return task.tests[0][2] if f"{task.id.lower()}.{last}" == work else None


def done_made(folder: str, found: list[session.Call], plan: list[str]) -> list[str]:
    """The CCS of the latest call of each work of a task the plan no longer holds, done, in the
    order those calls were made: what the task served and decided, and the files it made, which
    is what the plan is made again from; turn's results are left out, as what they hold beside the
    work, each item's Good and turn's lessons, changes no task."""
    left = [task.id for task in steering.tasks_of(plan)]
    last = {c.work: c.number for c in found}
    return [
        session.call_path(folder, number, session.CCS)
        for work, number in sorted(last.items(), key=lambda item: item[1])
        if session.task_of(work) and session.task_of(work) not in left
    ]
