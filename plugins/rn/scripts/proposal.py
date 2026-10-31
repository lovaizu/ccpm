"""The proposal at a sign-off, made from what is pushed alone, so it says nothing turn's first user
did not read: what the sign-off shows of the steering and of each work, and what changed since the
proposal at the same sign-off before; the sign-off set waiting with it, and the answers the user
gives it kept."""

from __future__ import annotations

import json
from typing import Any

import ccs
import conversations
import repo
import session
import steering
import stop

# Each sign-off, with its name as the user reads it and the words naming where the work is.
HEADS = {
    steering.GOAL: ("Goal", "The goal is on the draft pull request"),
    steering.UX: ("UX", "The UX is on the draft pull request"),
    steering.ARCHITECTURE: ("Architecture", "The architecture is on the draft pull request"),
    steering.DELIVERABLE: ("Deliverable", "The finished work is on the pull request"),
}
# The sign-offs that show the documents of their own stage, and the works whose choices each
# sign-off shows, by the stage they were called in and their names: at the ux's and the
# architecture's, each task's and checklist's called in that stage, as the user approves the
# documents themselves; at the deliverable's, each task's called in the build stage or in the
# deliverable stage, where the use of the finished work brings a fix, shown in the finished work,
# as the finished work is what the user approves there.
DOCUMENTS = (steering.UX, steering.ARCHITECTURE)
WORKS_SHOWN = {
    **{signoff: ((signoff,), session.DOCUMENTED) for signoff in DOCUMENTS},
    steering.DELIVERABLE: ((steering.BUILD, steering.DELIVERABLE), session.TASK_WORK),
}
# Each answer the user gives a sign-off, with the command they type for it, which the AI cannot
# call, and the line every proposal ends with, saying how to answer.
COMMANDS = {"approved": "/rn:ty", "feedback": "/rn:gm"}
ANSWER = (
    f"{COMMANDS['approved']} to approve, {COMMANDS['feedback']} <feedback> to ask for a change."
)
# The step of /rn:up each answer and each sign-off set waiting leads to, as Next, by the number
# orchestrator.md and the files of its stages give it: a sign-off approved, a sign-off sent back,
# and a sign-off waiting.
APPROVED_NEXT = {
    steering.GOAL: (
        "Step 9 of /rn:up on plan: hear which documents of what the user gets and how they use it"
        " the work needs"
    ),
    steering.UX: session.STAGED[steering.ARCHITECTURE],
    steering.ARCHITECTURE: session.STAGED[steering.BUILD],
    steering.DELIVERABLE: (
        "Step 12 of /rn:up: find where the work fell short, then put each learning to the user"
    ),
}
FEEDBACK = "Step 6 of /rn:up on {}: find the point behind the feedback"
WAITING = "Step 5 of /rn:up on {}: wait for the user's answer, " + ANSWER


def blob(pr: str | None) -> str:
    """Where the repository of the session's pull request shows the files of the checked-out
    branch; stops where the pull request was not opened."""
    found = None if pr is None else steering.PULL.fullmatch(pr)
    if found is None:
        raise stop.Stop(
            "rn: the steering names no pull request, as it was not opened; run `rn.py start` again"
            " on the session's branch, so it opens the pull request, then run this again"
        )
    return f"{found.group(1)}/blob/{repo.branch()}"


# What a proposal shows, by the work each part is of, "" for the steering's own: the line naming the
# work, none for the steering's, and the part's lines by what each is of, an ID or what was
# chosen.
Shows = dict[str, tuple[str, dict[str, str]]]


def shown_works(made: list[session.Call], signoff: str) -> list[str]:
    """The works whose choices the ux's, the architecture's or the deliverable's sign-off shows, in
    the order first called."""
    stages, form = WORKS_SHOWN[signoff]
    found: list[str] = []
    for call in made:
        if call.stage in stages and form.fullmatch(call.work) and call.work not in found:
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


def shown_line(last: session.Call, pr: str | None) -> str:
    """The line naming a work as the user knows it, by its kind and its paths as links, not by rn's
    name for it."""
    focal = last.ccs.get("focal_entities", [])
    kind = next((e[ccs.KIND] for e in focal if ccs.KIND in e), "")
    link = blob(pr)
    paths = [e[ccs.ENTRIES["work"]] for e in focal if ccs.ENTRIES["work"] in e]
    return f"{kind}: {', '.join(f'{link}/{p}' for p in paths)}"


def shown_at(commit: str, signoff: str, folder: str) -> Shows:
    """What the proposal at the sign-off shows of the session as the commit holds it: at the goal's,
    the goal and each criterion by its ID; at the ux's and the architecture's, each work the
    sign-off shows by its line, from its latest call, with each choice made in the user's place; at
    the deliverable's, the finished work by its line, with each choice made in building it and in
    using it. Nothing of the user's own answers, which the work holds and the AI that used it in
    their place has checked. Stops where turn has not returned a work's latest call, its result is
    no JSON object, or the pull request was not opened."""
    steered = steering.read(repo.at(commit, session.steering_path(folder)))
    if signoff == steering.GOAL:  # pragma: no mutate
        said = steering.decided(steered["plan"])
        return {"": ("", {k: f"{k}: {line}" for k, line in said.items()})}
    made = session.calls(folder, commit)
    pr = steered["session"]["pr"]
    lasts = [returned(made, work, folder) for work in shown_works(made, signoff)]
    if signoff in DOCUMENTS:
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
    its history shows: a commit whose change adds or removes the line that sets a sign-off waiting,
    holding it waiting at that sign-off."""
    path = session.steering_path(folder)
    listed = repo.git(
        ["log", "--reverse", "--format=%H", f"-G{WAITS}", f"{repo.base()}..HEAD", "--", path],
        repo.AS_GIT_SAYS,
    )
    return [c for c in listed.split() if steering.signoff_of(repo.at(c, path)) == signoff]


# The line of the steering that sets the sign-off of its stage waiting, as rn writes it.
WAITS = '"awaiting_signoff": true'


def text(signoff: str, pr: str | None, then: Shows | None, now: Shows) -> str:
    """The proposal's text at the sign-off: its name, where the work is, with the pull request,
    what it shows and what changed since the proposal shown before, none for the first, and how to
    answer."""
    return "\n".join(
        [
            f"{HEADS[signoff][0]} sign-off",
            f"{HEADS[signoff][1]}: {pr}",
            *compared(then, now),
            ANSWER,
        ]
    )


def ready(signoff: str, folder: str, steered: dict[str, Any]) -> None:
    """Returns when the session has what the sign-off shows: no task left at any, as a sign-off
    shows the stage's works made; at the goal's, a goal and a criterion; at the deliverable's, the
    finished work returned; stops otherwise. The ux's and the architecture's works are checked as
    they are shown."""
    plan = steered["plan"]
    left = [t["id"] for t in plan["tasks"]]
    if left:
        raise stop.Stop(
            f"rn: {stop.joined(left)} is still in the plan, and a sign-off comes once no task is;"
            " carry out each task and take it out with `rn.py state --done T<n>` once turn has"
            " returned it, then run this again"
        )
    # Each criterion serves a goal and each goal is served, so a plan with a goal has a criterion.
    if signoff == steering.GOAL and not plan["goals"]:
        raise stop.Stop(
            "rn: the goal sign-off needs a goal and a criterion in the plan; write the plan, then"
            " run this again"
        )
    if signoff == steering.DELIVERABLE:  # pragma: no mutate
        last = session.latest(session.calls(folder), steering.DELIVERABLE)
        if last is None or not last.closed:
            raise stop.Stop(
                "rn: turn has not returned the finished work; have turn:up make it with the call"
                " `rn.py ccs deliverable ...` prints, keep it, then run this again"
            )


def shown(signoff: str) -> str:
    """The proposal at the sign-off, made from what is pushed alone: the pull request's link, then
    the goal and the acceptance criteria at the goal sign-off, each work made in the ux or the
    architecture stage with its links and each choice made in it unasked at that stage's, and the
    finished work with its links and each choice made unasked in building and using it at the
    deliverable's, as shown_at says, with what changed since the last proposal at the same sign-off;
    the steering set waiting at the sign-off, Next saying so, and kept with the proposal as its
    message. The same proposal again, keeping nothing, where it waits at that sign-off already, as
    a sign-off waiting is always that of the stage. Stops where the branch holds no session, a
    change is not kept or pushed, the steering differs from what the last keep left, the session is
    at another stage, the session lacks what the sign-off shows, a result of turn's is no JSON
    object, or the pull request was not opened."""
    folder = session.current()
    repo.pushed()
    steered = session.kept_steering(folder)
    status = steered["status"]
    stage, waiting = status["stage"], status["awaiting_signoff"]
    if stage != signoff:
        raise stop.Stop(
            f"rn: the session is at the {stage} stage, and the {signoff} sign-off comes at the"
            f" {signoff} stage; take the steps of /rn:up that reach it first"
        )
    ready(signoff, folder, steered)
    proposals = proposed(signoff, folder)
    before = proposals[:-1] if waiting else proposals
    now = shown_at("HEAD", signoff, folder)
    then = shown_at(before[-1], signoff, folder) if before else None
    shown_text = text(signoff, steered["session"]["pr"], then, now)
    if not waiting:
        set_waiting = {**status, "awaiting_signoff": True, "next_step": WAITING.format(signoff)}
        session.keep(folder, {**steered, "status": set_waiting}, shown_text)
    return shown_text


def answered(answer: str, opened: list[str], message: str) -> dict[str, str]:
    """Keeps the user's answer to the sign-off waiting, approved or feedback: on approval the stage
    moved on, goal to ux, ux to architecture, architecture to build, deliverable to learnings; on
    either no sign-off waiting, Next replaced, and each point opened added after those open; kept
    with the message and pushed; gives the commit. Stops where the branch holds no session, the
    steering differs from what the last keep left, no sign-off waits, the user has not typed the
    answer's command since the sign-off was shown, as an approval counts only from the user's own
    action, or no record of the conversation is kept to tell it by; and where git fails."""
    folder = session.current()
    steered = session.kept_steering(folder)
    status = steered["status"]
    waiting = status["stage"]
    if not status["awaiting_signoff"]:
        raise stop.Stop(
            "rn: no sign-off waits for the user's answer; show the proposal with `rn.py proposal"
            f" <{'|'.join(steering.SIGNOFFS)}>` first, and keep the answer the user gives it"
        )
    command = COMMANDS[answer]
    shown_since = float(
        repo.git(["log", "-1", "--format=%ct", proposed(waiting, folder)[-1]], repo.AS_GIT_SAYS)
    )
    if not conversations.typed(command, shown_since):
        raise stop.Stop(
            f"rn: the user has not typed {command} since the {waiting} sign-off was shown; the"
            " answer is theirs alone, so wait for them to type it, and keep it then"
        )
    stage, next_step = waiting, FEEDBACK.format(waiting)
    if answer == "approved":  # pragma: no mutate
        stage, next_step = steering.APPROVED[waiting], APPROVED_NEXT[waiting]
    # The points open stay, as the answer settles none of them, each one given added after them.
    answered_status = {
        "stage": stage,
        "awaiting_signoff": False,
        "next_step": next_step,
        "open_questions": [*status["open_questions"], *opened],
    }
    return {"kept": session.keep(folder, {**steered, "status": answered_status}, message)}
