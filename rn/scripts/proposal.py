"""The proposal at a sign-off, made from what is pushed alone, so it says nothing turn's first user
did not read: what the sign-off shows of the steering and of each work, and what changed since the
proposal at the same sign-off before; with the answers the user gives it."""

from __future__ import annotations

import json

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
# The works whose choices a sign-off shows, by the stage they were called in and their names: at the
# design's, each task's and checklist's called in the design stage, as the user approves the
# documents themselves; at the deliverable's, each task's called in the build stage, shown in the
# finished work, as the finished work is what the user approves there.
WORKS_SHOWN = {
    steering.DESIGN: (steering.DESIGN, session.DESIGNED),
    steering.DELIVERABLE: (steering.BUILD, session.TASK_WORK),
}
# Each answer the user gives a sign-off, with the command they type for it, which the AI cannot
# call, and the line every proposal ends with, saying how to answer.
COMMANDS = {"approved": "/rn:ty", "feedback": "/rn:gm"}
ANSWER = (
    f"{COMMANDS['approved']} to approve, {COMMANDS['feedback']} <feedback> to ask for a change."
)


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
# work, none for the steering's, and the part's lines by what each is of, an ID or what was
# chosen.
Shows = dict[str, tuple[str, dict[str, str]]]


def shown_works(made: list[session.Call], signoff: str) -> list[str]:
    """The works whose choices the design's or the deliverable's sign-off shows, in the order first
    called."""
    stage, form = WORKS_SHOWN[signoff]
    found: list[str] = []
    for call in made:
        if call.stage == stage and form.fullmatch(call.work) and call.work not in found:
            found.append(call.work)
    return found


def returned(made: list[session.Call], work: str, folder: str) -> session.Call:
    """The work's latest call; stops where turn has not returned it."""
    last = session.latest(made, work)
    if last is None or not last.closed:
        number = "" if last is None else last.number
        raise stop.Stop(
            f"rn: turn has not returned the work {work}:"
            f" {session.call_path(folder, number, session.RESULT)} is not there; have turn:up"
            f" make it with the call `rn.py ccs {work} ...` printed, keep it, then run this"
            " again"
        )
    return last


def chosen(last: session.Call, folder: str, commit: str) -> dict[str, str]:
    """Each choice made in the user's place that the call's work rests on, by what was chosen, as
    the line showing it with why: the orchestrator's, as its CCS keeps them, then those turn's
    maker named in its result. Stops where the result is no JSON object."""
    path = session.call_path(folder, last.number, session.RESULT)
    try:
        result = json.loads(repo.at(commit, path) or "")
    except ValueError:
        result = None
    if not isinstance(result, dict):
        raise stop.Stop(
            f"rn: {path} is no result of turn's, a JSON object; have turn:up make the work"
            f" {last.work} again with the call `rn.py ccs {last.work}` prints, keep it, then run"
            " this again"
        )
    found = {c.partition(": ")[0]: c for c in session.choices_of(last)}
    for made in result.get("chosen", []):
        found[made["chosen"]] = f"{made['chosen']}: {made['why']}"
    return found


def shown_line(last: session.Call, pr: str) -> str:
    """The line naming a work as the user knows it, by its kind and its paths as links, not by rn's
    name for it."""
    focal = last.ccs.get("focal_entities", [])
    kind = next((e[ccs.KIND] for e in focal if ccs.KIND in e), "")
    link = blob(pr)
    paths = [e[ccs.ENTRIES["work"]] for e in focal if ccs.ENTRIES["work"] in e]
    return f"{kind}: {', '.join(f'{link}/{p}' for p in paths)}"


def shown_at(commit: str, signoff: str, folder: str) -> Shows:
    """What the proposal at the sign-off shows of the session as the commit holds it: at the plan's,
    the goal and each criterion by its ID; at the design's, each work the sign-off shows by its
    line, from its latest call, with each choice made in the user's place; at the deliverable's,
    the finished work by its line, with each choice made in building it and in using it. Nothing of
    the user's own answers, which the work holds and the AI that used it in their place has checked.
    Stops where turn has not returned a work's latest call, its result is no JSON object, or the
    pull request was not opened."""
    steered = steering.parsed(repo.at(commit, session.steering_path(folder)) or "")
    if signoff == steering.PLAN:  # pragma: no mutate
        return {"": ("", {k: f"{k}: {said}" for k, said in steering.decided(steered.plan).items()})}
    made = session.calls(folder, commit)
    pr = steered.keys[steering.PR]
    lasts = [returned(made, work, folder) for work in shown_works(made, signoff)]
    if signoff == steering.DESIGN:  # pragma: no mutate
        return {last.work: (shown_line(last, pr), chosen(last, folder, commit)) for last in lasts}
    built = {k: v for last in lasts for k, v in chosen(last, folder, commit).items()}
    used = returned(made, steering.DELIVERABLE, folder)
    return {used.work: (shown_line(used, pr), {**built, **chosen(used, folder, commit)})}


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


def choices_changed(before: dict[str, str] | None, now: dict[str, str]) -> list[str]:
    """The lines the proposal shows of a work's choices, each after a bullet: each as it says,
    marked where it changed or was added since the proposal before, then each gone, by what it said,
    as the user knows a choice by its words alone."""
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
        lines += [line] + choices_changed(before, said) if work else changes(before, said)
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
