"""The proposal at a sign-off, made from what is pushed alone, so it says nothing turn's first user
did not read: what the sign-off shows of the steering and of each work, and what changed since the
proposal at the same sign-off before; with the answers the user gives it."""

from __future__ import annotations

import re

import ccs
import repo
import session
import steering
import stop

# Each sign-off, with the words naming where the work is.
WHERE = dict(
    zip(
        steering.SIGNOFFS,
        (
            "The plan is on the draft pull request",
            "The design is on the draft pull request",
            "The finished work is on the pull request",
        ),
    )
)
# The works whose decisions a sign-off shows, by the stage they were called in and their names: at
# the design's, each task's and checklist's called in the design stage; at the deliverable's, each
# task's called in the build stage.
WORKS_SHOWN = {
    steering.DESIGN: (
        steering.DESIGN,
        re.compile(rf"{session.TASK_WORK.pattern}|{session.CHECKLIST_WORK.pattern}"),
    ),
    steering.DELIVERABLE: (steering.BUILD, session.TASK_WORK),
}
# Each answer the user gives a sign-off, with the command they type for it, which the AI cannot
# call, and the line every proposal ends with, saying how to answer.
COMMANDS = {"approved": "/rn:ty", "feedback": "/rn:gm"}
ANSWER = (
    f"{COMMANDS['approved']} to approve, {COMMANDS['feedback']} <feedback> to ask for a change."
)
# The most decisions of a work a sign-off shows, and the most characters of each, as five short
# lines are what a glance at the proposal takes in; a work past them is not yet simple.
MOST = 5
LONGEST = 200


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
        raise stop.Stop(
            f"rn: the work {work} holds {len(found)} decisions, more than the {MOST} a sign-off"
            f" shows of a work; {again}"
        )
    for title, said in found.items():
        if len(said) > LONGEST:
            raise stop.Stop(
                f'rn: the decision "{title}" of the work {work} is {len(said)} characters long,'
                f" more than the {LONGEST} a line of a sign-off holds; {again}"
            )
    return found


def blob(pr: str) -> str:
    """Where the repository of the session's pull request shows the files of the checked-out
    branch; stops where the pull request was not opened."""
    found = steering.PULL.fullmatch(pr)
    if found is None:
        raise stop.Stop(
            f"rn: the steering's pr, {pr!r}, is no pull request's URL; run `rn.py start` again on"
            " the session's branch, so it opens the pull request, then run this again"
        )
    return f"{found.group(1)}/blob/{repo.branch()}"


# What a proposal shows, by the work each part is of, "" for the steering's own: the line naming the
# work, none for the steering's, and the part's lines by what each is of, an ID or a decision's
# title.
Shows = dict[str, tuple[str, dict[str, str]]]


def shown_works(made: list[session.Call], signoff: str) -> list[str]:
    """The works whose decisions the sign-off shows, in the order first called."""
    if signoff not in WORKS_SHOWN:
        return []
    stage, form = WORKS_SHOWN[signoff]
    found: list[str] = []
    for call in made:
        if call.stage == stage and form.fullmatch(call.work) and call.work not in found:
            found.append(call.work)
    return found


def shown_at(commit: str, signoff: str, folder: str) -> Shows:
    """What the proposal at the sign-off shows of the session as the commit holds it: at the plan's,
    the goal and each criterion by its ID, and at the deliverable's each criterion; then each work
    the sign-off shows by its name: at the design's, its paths as links, from its latest call, with
    its decisions; at the deliverable's, its decisions, where it has any. Stops where turn has not
    returned a work's latest call, a work's decisions are not simple, or the pull request was not
    opened."""
    steered = steering.parsed(repo.at(commit, session.steering_path(folder)) or "")
    found: Shows = {}
    if signoff != steering.DESIGN:
        goal = signoff == steering.PLAN  # pragma: no mutate
        lines = steering.decided(steered.plan, goal)
        found[""] = ("", {key: f"{key}: {said}" for key, said in lines.items()})
    made = session.calls(folder, commit)
    for work in shown_works(made, signoff):
        last = session.latest(made, work)
        if last is None or not last.result:
            number = "" if last is None else last.number
            raise stop.Stop(
                f"rn: turn has not returned the work {work}: {session.call_path(folder, number, session.RESULT)} is"
                f" not there; have turn:up make it with the call `rn.py ccs {work} ...` printed,"
                " keep it, then run this again"
            )
        said = simple(work, session.decisions_of(last))
        label = work.upper() if session.TASK_WORK.fullmatch(work) else work
        if signoff == steering.DESIGN:  # pragma: no mutate
            link = blob(steered.keys[steering.PR])
            paths = [
                e[ccs.ENTRIES["work"]]
                for e in last.ccs.get("focal_entities", [])
                if ccs.ENTRIES["work"] in e
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
        + ([f"({stop.joined(same)} as before)"] if same else [])
    )


def compared(then: Shows | None, now: Shows) -> list[str]:
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
    path = session.steering_path(folder)
    listed = repo.git(
        [
            "log",
            "--reverse",
            "--format=%H",
            f"-G^signoff: {signoff}$",
            f"{repo.base()}..HEAD",
            "--",
            path,
        ],
        repo.AS_GIT_SAYS,
    )
    return [
        c
        for c in listed.split()
        if steering.keys_of(repo.at(c, path) or "").get(steering.SIGNOFF) == signoff
    ]


def ready(signoff: str, folder: str, steered: steering.Steering) -> None:
    """Returns when the session has what the sign-off shows: at the plan's, the goal, a criterion
    and no task left; at the deliverable's, the finished work returned; stops otherwise. The
    design's works are checked as they are shown."""
    if signoff == steering.PLAN:  # pragma: no mutate
        said = steering.decided(steered.plan)
        if "G1" not in said or len(said) < 2 or steering.tasks_of(steered.plan):
            raise stop.Stop(
                "rn: the plan sign-off needs the goal G1, a criterion and no task in the steering;"
                " have turn make the plan through its tasks, tick each action done with"
                " `rn.py state --done`, then run this again"
            )
    if signoff == steering.DELIVERABLE:  # pragma: no mutate
        last = session.latest(session.calls(folder), steering.DELIVERABLE)
        if last is None or not last.result:
            raise stop.Stop(
                "rn: turn has not returned the finished work; have turn:up make it with the call"
                " `rn.py ccs deliverable ...` prints, keep it, then run this again"
            )
