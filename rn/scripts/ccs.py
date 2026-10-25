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


def held(path: str) -> str:
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
    none for the plan, which makes them; those its task's line names for a task's work; the goal
    and every criterion for any other. Stops where the steering holds no task of a task's work."""
    said = steering.decided(steered.plan, ("", steering.CRITERIA))
    if work == steering.PLAN:
        return {}
    if not session.TASK_WORK.fullmatch(work):
        return said
    task = next((t for t in steering.tasks_of(steered.plan) if t.id == work.upper()), None)
    if task is None:
        raise stop.Stop(
            f"rn: the steering holds no task {work.upper()}, which the work {work} is of; have turn"
            " make the tasks, keep them, then run this again"
        )
    return {key: text for key, text in said.items() if key in (task.serves or [])}


def done_made(folder: str, found: list[session.Call], plan: list[str]) -> list[str]:
    """For each call on a task's work whose task the plan no longer holds, done, in the order made,
    its CCS and its result where turn returned it, and the CCS of the work's latest call where turn
    has not, as it holds the decisions kept last: what the task served, decided and made, a research
    result made before a decision among them."""
    left = [task.id for task in steering.tasks_of(plan)]
    last = {c.work: c.number for c in found}
    paths = []
    for call in found:
        if session.TASK_WORK.fullmatch(call.work) and call.work.upper() not in left:
            latest_call = call.number == last[call.work]  # pragma: no mutate
            if call.result or latest_call:
                paths.append(session.call_path(folder, call.number, session.CCS))
            paths += [session.call_path(folder, call.number, session.RESULT)] if call.result else []
    return paths
