"""The proposal at a sign-off, made from what is pushed alone, so it says nothing turn's first user
did not read: what the sign-off shows of the steering and of each work, and what changed since the
proposal at the same sign-off before; with the answers the user gives it."""

from __future__ import annotations

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
# The works a sign-off shows, by the stage they were called in and their names, and whether one
# with no decision is shown: at the design's, each task's and checklist's called in the design
# stage, each shown, as the user approves the documents themselves; at the deliverable's, each
# task's called in the build stage, shown only with a decision, as the finished work is what the
# user approves there.
WORKS_SHOWN = {
    steering.DESIGN: (steering.DESIGN, session.DESIGNED, True),
    steering.DELIVERABLE: (steering.BUILD, session.TASK_WORK, False),
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
    """What each of the work's decisions says, by its title, when a sign-off can show them, as the
    user judges what the work must be, not the names of the points; stops where they are
    more than it shows of a work, or one is longer than a line of it holds, as the work is then not
    yet simple."""
    again = (
        "the work is not yet simple: settle its points again more simply with the user, have turn"
        " make it again, then run this again"
    )
    found = {title: said for title, _, said in (d.partition(": ") for d in decisions)}
    if len(found) > MOST:
        raise stop.Stop(
            f"rn: the work {work} holds {len(found)} decisions, more than the {MOST} a sign-off"
            f" shows of a work; {again}"
        )
    for title, said in found.items():
        long = len(f"{title}: {said}")
        if long > LONGEST:
            raise stop.Stop(
                f'rn: the decision "{title}" of the work {work} is {long} characters long,'
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
    stage, form, _ = WORKS_SHOWN[signoff]
    found: list[str] = []
    for call in made:
        if call.stage == stage and form.fullmatch(call.work) and call.work not in found:
            found.append(call.work)
    return found


def shown_at(commit: str, signoff: str, folder: str) -> Shows:
    """What the proposal at the sign-off shows of the session as the commit holds it: at the plan's,
    the goal and each criterion by its ID, and at the deliverable's each criterion; then each work
    the sign-off shows by its kind and its paths as links, from its latest call, as the user knows a
    work by what it is and where, not by rn's name for it, with what its decisions say: at the
    design's each, at the deliverable's each with a decision. Stops where turn has not
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
        if last is None or not last.closed:
            number = "" if last is None else last.number
            raise stop.Stop(
                f"rn: turn has not returned the work {work}:"
                f" {session.call_path(folder, number, session.RESULT)} is not there; have turn:up"
                f" make it with the call `rn.py ccs {work} ...` printed, keep it, then run this"
                " again"
            )
        said = simple(work, session.decisions_of(last))
        if WORKS_SHOWN[signoff][2] or said:
            focal = last.ccs.get("focal_entities", [])
            kind = next((e[ccs.KIND] for e in focal if ccs.KIND in e), "")
            link = blob(steered.keys[steering.PR])
            paths = [e[ccs.ENTRIES["work"]] for e in focal if ccs.ENTRIES["work"] in e]
            found[work] = (f"{kind}: {', '.join(f'{link}/{p}' for p in paths)}", said)
    return found


def changes(before: dict[str, str] | None, now: dict[str, str]) -> list[str]:
    """The lines the proposal shows of the steering, each by its ID: each as it is, at the first
    proposal; then each changed or added, each removed, by its ID, and the rest named as before."""
    if before is None:
        return list(now.values())
    same = [key for key, line in now.items() if before.get(key) == line]
    return (
        [f"Changed: {line}" for key, line in now.items() if key not in same]
        + [f"Removed: {key}" for key in before if key not in now]
        + ([f"({stop.joined(same)} as before)"] if same else [])
    )


def decisions_changed(before: dict[str, str] | None, now: dict[str, str]) -> list[str]:
    """The lines the proposal shows of a work's decisions, each after a bullet: each as it says,
    marked where it changed or was added since the proposal before, then each gone, by what it said,
    as the user knows a decision by its words alone."""
    if before is None:
        before = now
    return [
        f"- {'' if before.get(title) == said else 'Changed: '}{said}" for title, said in now.items()
    ] + [f"- Removed: {said}" for title, said in before.items() if title not in now]


def compared(then: Shows | None, now: Shows) -> list[str]:
    """The lines the proposal shows: the steering's and each work's line with what changed of its
    part since the proposal shown before, none for the first; then each work shown before and no
    longer, by its line, shown as removed."""
    lines: list[str] = []
    for work, (line, said) in now.items():
        before = None if then is None else then.get(work, ("", {}))[1]
        lines += [line] + decisions_changed(before, said) if work else changes(before, said)
    gone = [shown for work, (shown, _) in (then or {}).items() if work not in now]
    return lines + [f"Removed: {shown}" for shown in gone]


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


def text(signoff: str, pr: str, then: Shows | None, now: Shows) -> str:
    """The proposal's text at the sign-off: its name, where the work is, with the pull request,
    what it shows and what changed since the proposal shown before, none for the first, and how to
    answer."""
    return "\n".join(
        [
            f"{signoff.capitalize()} sign-off",
            f"{WHERE[signoff]}: {pr}",
            *compared(then, now),
            ANSWER,
        ]
    )


def ready(signoff: str, folder: str, steered: steering.Steering) -> None:
    """Returns when the session has what the sign-off shows: at the plan's, the goal, a criterion
    and no task left; at the deliverable's, the finished work returned; stops otherwise. The
    design's works are checked as they are shown."""
    if signoff == steering.PLAN:  # pragma: no mutate
        said = steering.decided(steered.plan)
        if "G1" not in said or len(said) < 2 or steering.tasks_of(steered.plan):
            raise stop.Stop(
                "rn: the plan sign-off needs the goal G1, a criterion and no task in the steering;"
                " write the plan and carry out its tasks, tick each action done with"
                " `rn.py state --done`, then run this again"
            )
    if signoff == steering.DELIVERABLE:  # pragma: no mutate
        last = session.latest(session.calls(folder), steering.DELIVERABLE)
        if last is None or not last.closed:
            raise stop.Stop(
                "rn: turn has not returned the finished work; have turn:up make it with the call"
                " `rn.py ccs deliverable ...` prints, keep it, then run this again"
            )
