"""rn's command line, the subcommands rn's orchestrator runs for each move a machine can judge, so
that what must come out the same does on every run and a rule holds at the moment of the move. Run
from the top of the user's repository as `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/rn.py"
<subcommand> ...`, with Python 3.9 or later and the standard library alone; it prints JSON, or the
proposal as text for the orchestrator to show, and on a stop exits 1 with what went wrong and what
to do."""

from __future__ import annotations

import argparse
import datetime
import json
import os
import shutil
import sys
from collections.abc import Callable
from typing import Any, NoReturn

import ccs
import conversations
import proposal
import repo
import session
import steering
import stop
import stretch

# The plugin's own folder, which holds rn's checklists and its manifest.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The step of /rn:up each move whose next step is always the same leads to, as Next, by the number
# up's SKILL.md and the files of its stages give it: a session started, a sign-off approved, a
# sign-off sent back, a sign-off waiting, and a stage moved at its end.
STARTED = "Step 8 of /rn:up on plan: hear the purpose and what shows it done"
APPROVED_NEXT = {
    steering.PLAN: "Step 9 of /rn:up on plan: hear which documents the purpose needs",
    steering.DESIGN: "Step 10 of /rn:up on plan: make the tasks that build the finished work",
    steering.DELIVERABLE: "Step 11 of /rn:up: put each learning to the user",
}
FEEDBACK = "Step 6 of /rn:up on {}: find the point behind the feedback"
WAITING = "Step 5 of /rn:up on {}: wait for the user's answer, " + proposal.ANSWER
STAGED = {
    steering.BUILD: APPROVED_NEXT[steering.DESIGN],
    steering.DELIVERABLE: (
        "Step 10 of /rn:up on deliverable: have the finished work used for each acceptance"
        " criterion"
    ),
    steering.FINISHED: "Nothing is left: the pull request waits for the user's merge",
}


def run_session(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """The session the checked-out branch is in, with its stage and the sign-off waiting, as its
    steering's last commit holds them; None for each where there is none. Stops where rn is not at
    the top of a repository, git cannot tell the branch's changes, or the branch changed more than
    one session not finished."""
    found = session.session()
    if found is None:
        return {"session": None, steering.STAGE: None, steering.SIGNOFF: None}
    keys = steering.keys_of(repo.at("HEAD", session.steering_path(found)) or "")
    signoff = keys.get(steering.SIGNOFF)
    return {
        "session": found,
        steering.STAGE: keys.get(steering.STAGE),
        steering.SIGNOFF: None if signoff in (None, steering.NONE) else signoff,
    }


def version(root: str) -> str:
    """rn's version, as its manifest gives it; stops where it gives none."""
    path = os.path.join(root, ".claude-plugin", "plugin.json")
    try:
        with open(path, encoding="utf-8") as f:
            return str(json.load(f)["version"])
    except (OSError, ValueError, KeyError):
        raise stop.Stop(f"rn: {path} gives no version of rn; install rn again") from None


def run_start(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Starts a session on a branch of its own named by the slug, made from the remote's default
    branch as it is now: its steering at the plan stage, with rn's version, the languages, the
    title, Next and nothing open, kept with the message; then the draft pull request opened, its
    body linking the steering, and its URL kept as the steering's pr. Run again on that branch where
    the pull request was not opened, it opens it. Gives the folder, the branch and the pull request.
    Stops, leaving the checked-out branch as it is, where a value is not given in its form, rn is
    not at the top of a repository, the working tree has changes not committed, the folder or the
    branch is there already, or rn's version is not there; and where git or gh fails."""
    slug = stop.named(args.slug, "slug")
    title = stop.given(args.title, "title")
    languages = {
        key: stop.given(getattr(args, key.replace("-", "_")), key) for key in steering.LANGUAGES
    }
    message = stop.given(args.message, "message")
    repo.at_top()
    paths = repo.changed()
    if paths:
        raise stop.Stop(
            f"rn: the working tree has changes not committed: {', '.join(paths)}; rn leaves them as"
            " they are, and starts from the default branch: commit or stash them, then run this"
            " again"
        )
    if repo.branch() == slug:
        folder = session.current()
        steered = session.kept_steering(folder)
        if steered.keys[steering.PR] != steering.NONE:  # pragma: no mutate
            raise stop.Stop(
                f"rn: the session {folder} is started already, with its pull request"
                f" {steered.keys[steering.PR]}; go on with it with /rn:up"
            )
    else:
        keys = {
            steering.RN: version(root),
            steering.PR: steering.NONE,
            steering.STAGE: steering.PLAN,
            steering.SIGNOFF: steering.NONE,
            **languages,
        }
        steered = steering.Steering(keys, [f"# {title}"], STARTED, [steering.NOTHING_OPEN])
        folder = session.started(slug, today, steered, message)
    pr = session.opened_pr(folder, slug, steered, title)
    return {"session": folder, "branch": slug, "pr": pr}


def run_state(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Keeps the move: the part of the call `--put` names put back, the plan's into the steering,
    the learnings' added to the session's learnings; each action done ticked, and each task removed
    once all its actions are; the stage moved where given; Next and Open replaced whole; then
    every change committed with the message and pushed; gives the commit. The records shown for the
    learnings are removed once their part is put back. Stops, keeping nothing, where a value is
    empty, the branch holds no session, the steering differs from what the last keep left, a part,
    an ID, an action or a stage cannot be taken, or the steering or the learnings would be out of
    their form; and where git fails."""
    message = stop.given(args.message, "message")
    folder = session.current()
    steered = session.kept_steering(folder)
    if args.next is not None:
        next_step = stop.given(args.next, "next step")
    elif args.stage is not None:
        next_step = STAGED[args.stage]
    else:
        next_step = steered.next
    work, steered, learnt = session.put_part(folder, steered, args.put)
    done = {one.partition(".")[0] for one in args.done}
    plan = steering.pruned(steering.ticked(steered.plan, args.done), done)
    tell = steering.told_done(steered.plan, args.done)
    keys = (
        steered.keys
        if args.stage is None
        else session.moved(steered.keys, args.stage, plan, folder)
    )
    steered = steering.Steering(keys, plan, next_step, steering.opened(args.open))
    # The steering is held to its form before the learnings are written, so a stop leaves neither.
    steering.held_form(steering.render(steered))
    if args.stage == steering.FINISHED:
        # The pull request is marked ready before the session is kept finished, so a gh that
        # fails leaves the session to go on from here.
        again = "run `rn.py state --stage finished` again"
        repo.gh(["pr", "ready", steered.keys[steering.PR]], again)
    if learnt:
        session.write_learnings(folder, learnt)
    commit = session.keep(folder, steered, message)
    if work == steering.LEARNINGS:
        shutil.rmtree(stretch.records_folder(), ignore_errors=True)
    return {"kept": commit, "tell": tell} if tell else {"kept": commit}


def run_decide(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Keeps a decision of the work, `<title>: <what it says>`, in the constraints of its latest
    call where turn has not returned it, else of a new call carrying that call's decisions, one of
    the same title replaced where it stands; kept with the message and pushed. Gives the call's
    number and the commit. Stops where a value is empty or wrong, the branch holds no session, the
    steering differs from what the last keep left, or a CCS is no JSON object; and where git
    fails."""
    work = session.worked(args.work)
    title = stop.given(args.title, "title")
    if ": " in title:
        raise stop.Stop(
            f"rn: the title {title!r} holds `: `, which parts a decision's title from what it says;"
            " give the title without it"
        )
    says = stop.given(args.says, "decision")
    message = stop.given(args.message, "message")
    folder = session.current()
    steered = session.kept_steering(folder)
    if session.task_of(work):
        session.made_by(steered, work)
    found = session.calls(folder)
    last = session.latest(found, work)
    if last is not None and not last.result:
        number, written = last.number, last.ccs
    else:
        number = session.next_number(found)
        carried = [] if last is None else session.decisions_of(last)
        written = {
            "focal_entities": [
                {session.WORK: work},
                {steering.STAGE: steered.keys[steering.STAGE]},
            ],
            "constraints": [{session.DECISION: d} for d in carried],
        }
    constraints = written.setdefault("constraints", [])
    decision = {session.DECISION: f"{title}: {says}"}
    same = next(
        (
            k
            for k, e in enumerate(constraints)
            if e.get(session.DECISION, "").startswith(f"{title}: ")
        ),
        None,
    )
    if same is None:
        constraints.append(decision)
    else:
        constraints[same] = decision
    repo.write_json(session.call_path(folder, number, session.CCS), written)
    return {"call": number, "kept": session.keep(folder, steered, message)}


def run_checklists(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """The paths of the kind's checklists; stops where the kind is not a name or has none."""
    return ccs.checklists(stop.named(args.kind, "kind"), root)


def run_ccs(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Writes the work's CCS into the session, keeps it, and gives the call that hands it to
    turn:up, once every change is pushed, so the work is made from decisions a fresh conversation
    also has, and a conversation cut while turn runs goes on from the call: in the work's latest
    call where turn has not returned it, else in a new one carrying that call's decisions. What is
    given makes the work; what is not, rn's own way of making it, or what the work's latest call
    named, as ccs.made_as and ccs.kept_as say: for the plan, its part of the steering, cut into the
    call's part, with what each task done served and made after what the receiver has; for the
    learnings, an empty part, as those kept are not made again, the receiver having the records of
    the stretch, shown afresh; for the finished work given none, every file it is. Stops, writing
    nothing, where a name, a text or a path given is wrong, the branch holds no session, a change
    is not kept or pushed, the steering differs from what the last keep left, the steering holds
    no action of turn's of a task's work, the receiver, their use or what they have is neither
    given nor kept, the kind has no checklist, or the finished work is not there."""
    work = session.worked(args.work)
    paths = [stop.given(p, "path of the work") for p in args.path]
    receiver = None if args.receiver is None else stop.given(args.receiver, "receiver")
    use = None if args.use is None else stop.given(args.use, "use")
    if work in session.PARTS and paths:
        raise stop.Stop(
            f"rn: the work {work} is a part rn cuts for turn from the session's record; give no"
            " path of it"
        )
    # The session is found first, which stops below the top of the repository, since each path
    # given is read from the top.
    folder = session.current()
    repo.pushed()
    has = [ccs.has_path(p) for p in args.has]
    steered = session.kept_steering(folder)
    serving = ccs.served(steered, work)
    found = session.calls(folder)
    last = session.latest(found, work)
    number = last.number if last is not None and not last.result else session.next_number(found)
    made, kept = ccs.made_as(work, steered, folder, root), ccs.kept_as(last)
    receiver = ccs.needed(receiver or made.receiver or kept.receiver, "receiver", work)
    use = ccs.needed(use or made.use or kept.use, "use", work)
    has = ccs.needed(has or made.has or kept.has, "has", work)
    kind = made.kind or ""
    checklists = ccs.checklists(kind, root)
    part = session.call_path(folder, number, session.PART[work]) if work in session.PARTS else ""
    paths = ([part] if part else paths) or made.paths or ccs.finished_work()
    if work == steering.PLAN:
        has += ccs.done_made(folder, found, steered.plan)
    # Every check is made above, so a stop leaves nothing written.
    if work == steering.LEARNINGS:
        has = stretch.show(folder)
    if part:
        repo.write_text(part, ccs.cut(work, steered))
    written = ccs.written(
        work,
        steered,
        ccs.Made(kind, receiver, use, paths, has),
        serving,
        checklists,
        [] if last is None else session.decisions_of(last),
        root,
    )
    path = session.call_path(folder, number, session.CCS)
    repo.write_json(path, written)
    session.keep(folder, steered, f"Call {number} on {work}: handed to turn")
    # turn's call takes the table of keys under "kind", a field name of turn's own that is no kind
    # of work; and the command that checks the work under "test", null where there is none.
    result = session.call_path(folder, number, session.RESULT)
    handed = {
        "ccs": path,
        "kind": ccs.ENTRIES,
        "result": result,
        "test": ccs.test_of(steered, work, number, root),
    }
    return f"{repo.dumped(handed)}\n{ccs.told(work, steered)}"


def run_check(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Checks the part turn makes for the call of the number as `state --put` holds it, keeping
    nothing, as session.held_part says; gives the number where it holds. Stops where it does not,
    the branch holds no session, or the part cannot be taken."""
    session.held_part(session.current(), args.number)
    return {"held": args.number}


def run_decisions(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Each decision of the work, as its latest call keeps it, with that call's number; none, and
    no call, where it has none. Stops where the work is none rn makes, or the branch holds no
    session."""
    work = session.worked(args.work)
    last = session.latest(session.calls(session.current()), work)
    return {
        "work": work,
        "call": None if last is None else last.number,
        "decisions": [] if last is None else session.decisions_of(last),
    }


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
    folder = session.current()
    repo.pushed()
    steered = session.kept_steering(folder)
    stage, waiting = steered.keys[steering.STAGE], steered.keys[steering.SIGNOFF]
    if stage != signoff:
        raise stop.Stop(
            f"rn: the session is at the {stage} stage, and the {signoff} sign-off comes at the"
            f" {signoff} stage; take the steps of /rn:up that reach it first"
        )
    if waiting not in (steering.NONE, signoff):
        raise stop.Stop(
            f"rn: the {waiting} sign-off waits for the user's answer; keep it with `rn.py answer`"
            " first"
        )
    proposal.ready(signoff, folder, steered)
    proposals = proposal.proposed(signoff, folder)
    before = proposals[:-1] if waiting == signoff else proposals
    now = proposal.shown_at("HEAD", signoff, folder)
    then = proposal.shown_at(before[-1], signoff, folder) if before else None
    shown_text = proposal.text(signoff, steered.keys[steering.PR], then, now)
    if waiting == steering.NONE:
        waits = WAITING.format(signoff)
        session.keep(
            folder,
            steered._replace(keys={**steered.keys, steering.SIGNOFF: signoff}, next=waits),
            shown_text,
        )
    return shown_text


def run_answer(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Keeps the user's answer to the sign-off waiting: on approval the stage moved on, plan to
    design, design to build, deliverable to learnings; on either no sign-off waiting, and Next and
    Open replaced whole; kept with the message and pushed; gives the commit. Stops where a value is
    empty, the branch holds no session, the steering differs from what the last keep left, no
    sign-off waits, or the user has not typed the answer's command since the sign-off was shown, as
    an approval counts only from the user's own action; and where git fails."""
    message = stop.given(args.message, "message")
    folder = session.current()
    steered = session.kept_steering(folder)
    waiting = steered.keys[steering.SIGNOFF]
    if waiting == steering.NONE:
        raise stop.Stop(
            "rn: no sign-off waits for the user's answer; show the proposal with `rn.py proposal"
            " <plan|design|deliverable>` first, and keep the answer the user gives it"
        )
    command = proposal.COMMANDS[args.answer]
    shown_at = float(
        repo.git(
            ["log", "-1", "--format=%ct", proposal.proposed(waiting, folder)[-1]], repo.AS_GIT_SAYS
        )
    )
    if not conversations.typed(command, shown_at):
        raise stop.Stop(
            f"rn: the user has not typed {command} since the {waiting} sign-off was shown; the"
            " answer is theirs alone, so wait for them to type it, and keep it then"
        )
    keys = {**steered.keys, steering.SIGNOFF: steering.NONE}
    next_step = FEEDBACK.format(waiting)
    if args.answer == "approved":  # pragma: no mutate
        keys[steering.STAGE] = steering.APPROVED[waiting]
        next_step = APPROVED_NEXT[waiting]
    # The points open stay, as the answer settles none of them, each one given added after them.
    still = [line[2:] for line in steered.open if line.startswith("- ")]
    answered = steered._replace(keys=keys, next=next_step, open=steering.opened(still + args.open))
    return {"kept": session.keep(folder, answered, message)}


def run_learnings(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Every learning of the session, for the orchestrator to put to the user one per message once
    the finished work is approved, by ID, each as one line. Stops where the branch holds no
    session."""
    folder = session.current()
    listed = steering.items_of(
        list(enumerate(session.learnings_of(folder))), session.LEARNING, session.LEARNING_FORM
    )[0]
    said = {i.id: steering.said(i.lines).partition(": ")[2] for i in listed}
    return {"learnings": said}


class Parser(argparse.ArgumentParser):
    """argparse, stopping as rn stops rather than exiting with its own code."""

    def error(self, message: str) -> NoReturn:
        # The usage on one line, as argparse breaks a long one where a terminal would.
        usage = " ".join(self.format_usage().split()[1:])
        raise stop.Stop(f"rn: {message}; give it as {usage}")


def parser() -> Parser:
    """The subcommands, each with what it takes and the function that runs it."""
    top = Parser(prog="rn.py")
    sub = top.add_subparsers(dest="subcommand", required=True)
    sub.add_parser("session").set_defaults(run=run_session)
    start = sub.add_parser("start")
    start.set_defaults(run=run_start)
    start.add_argument("slug")
    for option in ("--title", *(f"--{key}" for key in steering.LANGUAGES), "--message"):
        start.add_argument(option, required=True)
    state = sub.add_parser("state")
    state.set_defaults(run=run_state)
    state.add_argument("--next")
    state.add_argument("--open", action="append", default=[])
    state.add_argument("--done", action="append", default=[])
    state.add_argument("--put")
    state.add_argument("--stage", choices=list(steering.MOVES))
    state.add_argument("--message", required=True)
    decide = sub.add_parser("decide")
    decide.set_defaults(run=run_decide)
    decide.add_argument("work")
    for option in ("--title", "--says", "--message"):
        decide.add_argument(option, required=True)
    hand = sub.add_parser("ccs")
    hand.set_defaults(run=run_ccs)
    hand.add_argument("work")
    hand.add_argument("path", nargs="*")
    hand.add_argument("--receiver")
    hand.add_argument("--use")
    hand.add_argument("--has", action="append", default=[])
    check = sub.add_parser("check")
    check.set_defaults(run=run_check)
    check.add_argument("number")
    shown_text = sub.add_parser("proposal")
    shown_text.set_defaults(run=run_proposal)
    shown_text.add_argument("signoff", choices=steering.SIGNOFFS)
    answer = sub.add_parser("answer")
    answer.set_defaults(run=run_answer)
    answer.add_argument("answer", choices=list(proposal.COMMANDS))
    answer.add_argument("--open", action="append", default=[])
    answer.add_argument("--message", required=True)
    lists = sub.add_parser("checklists")
    lists.set_defaults(run=run_checklists)
    lists.add_argument("kind")
    decisions = sub.add_parser("decisions")
    decisions.set_defaults(run=run_decisions)
    decisions.add_argument("work")
    sub.add_parser("learnings").set_defaults(run=run_learnings)
    return top


def main(argv: list[str], root: str, today: datetime.date) -> int:
    """Runs the subcommand and prints what it gives, JSON or the proposal's text; 1 on a stop."""
    try:
        args = parser().parse_args(argv)
        run: Callable[..., Any] = args.run
        out = run(args, root, today)
    except stop.Stop as why:
        print(why)
        return 1
    print(out if isinstance(out, str) else repo.dumped(out))
    return 0


# Run as the command, and not when the tests import it under the name rn.
if __name__ == "__main__":  # pragma: no mutate
    sys.exit(main(sys.argv[1:], ROOT, datetime.date.today()))
