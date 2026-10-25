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
import records
import repo
import session
import steering
import stop
import stretch

# The plugin's own folder, which holds rn's checklists and its manifest.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_session(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """The session the checked-out branch is in, with its stage and the sign-off waiting, as its
    steering's last commit holds them; None for each where there is none. Stops where rn is not at
    the top of a repository, git cannot tell the branch's changes, or the branch changed more than
    one session not finished."""
    found = session.session()
    if found is None:
        return {"session": None, "stage": None, "signoff": None}
    keys = steering.keys_of(repo.at("HEAD", session.steering_path(found)) or "")
    signoff = keys.get("signoff")
    return {
        "session": found,
        "stage": keys.get(steering.STAGE),
        "signoff": None if signoff in (None, steering.NONE) else signoff,
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
    next_step = stop.given(args.next, "next step")
    message = stop.given(args.message, "message")
    repo.at_top()
    paths = repo.changed()
    if paths:
        raise stop.Stop(
            f"rn: the working tree has changes not committed: {', '.join(paths)}; rn leaves them as"
            " they are, and starts from the default branch: commit or stash them, then run this"
            " again"
        )
    if repo.git(["branch", "--show-current"], repo.AS_GIT_SAYS).strip() == slug:
        folder = session.current()
        steered = session.kept_steering(folder)
        if steered.keys["pr"] != steering.NONE:  # pragma: no mutate
            raise stop.Stop(
                f"rn: the session {folder} is started already, with its pull request"
                f" {steered.keys['pr']}; go on with it with /rn:up"
            )
    else:
        repo.git(["fetch", "-q", "origin"], repo.AS_GIT_SAYS)
        branch = repo.default_branch()
        folder = os.path.join(session.RECORD, f"{today:%Y%m%d}-{slug}")
        if repo.git(["ls-tree", "--name-only", branch, "--", folder], repo.AS_GIT_SAYS):
            raise stop.Stop(f"rn: {folder} is on {branch} already; give another slug")
        keys = {
            "rn": version(root),
            "pr": steering.NONE,
            steering.STAGE: steering.PLAN,
            "signoff": steering.NONE,
            **languages,
        }
        steered = steering.Steering(keys, [f"# {title}"], next_step, [steering.NOTHING_OPEN])
        steering.held_form(steering.render(steered))
        repo.git(["checkout", "-q", "--no-track", "-b", slug, branch], "give another slug")
        session.keep(folder, steered, message)
    repository = repo.gh(["repo", "view", "--json", "url", "--jq", ".url"])
    link = f"[{session.STEERING}]({repository}/blob/{slug}/{session.steering_path(folder)})"
    into = repo.default_branch().partition("/")[2]
    pr = repo.gh(
        [
            "pr",
            "create",
            "--draft",
            "--base",
            into,
            "--head",
            slug,
            "--title",
            title,
            "--body",
            link,
        ]
    )
    session.keep(folder, steered._replace(keys=dict(steered.keys, pr=pr)), f"pr: {pr}")
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
    next_step = stop.given(args.next, "next step")
    message = stop.given(args.message, "message")
    folder = session.current()
    steered = session.kept_steering(folder)
    work = None
    learnt: list[str] = []
    if args.put is not None:
        work, part = session.part_of(folder, args.put)
        if work == steering.PLAN:  # pragma: no mutate
            session.numbered_on(folder, steered.plan, part, args.put)
            steered = steered._replace(plan=steering.put_plan(steered.plan, part))
        else:
            learnt = session.put_learnings(session.learnings_of(folder), part)
    plan = steering.ticked(steered.plan, args.done)
    keys = (
        steered.keys
        if args.stage is None
        else session.moved(steered.keys, args.stage, plan, folder)
    )
    steered = steering.Steering(keys, plan, next_step, steering.opened(args.open))
    # The steering is held to its form before the learnings are written, so a stop leaves neither.
    steering.held_form(steering.render(steered))
    if learnt:
        session.write_learnings(folder, learnt)
    kept = session.keep(folder, steered, message)
    if work == steering.LEARNINGS_WORK:
        shutil.rmtree(stretch.learning(), ignore_errors=True)
    return {"kept": kept}


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
    call where turn has not returned it, else in a new one carrying that call's decisions. The work
    is each path given; for the plan, its part of the steering, cut into the call's part, with what
    each task done served and made as what the receiver has, after those given; for the learnings,
    a part of their heading alone, cut into the call's part, as those kept are not made again; for
    the finished work given none, every file it is. Stops where a name, a text or a path given is
    wrong, the branch holds no session, a change is not kept or pushed, the steering differs from
    what the last keep left, the steering holds no task of a task's work, or the finished work is
    not there."""
    work = session.worked(args.work)
    kind = stop.named(args.kind, "kind")
    receiver = stop.given(args.receiver, "receiver")
    use = stop.given(args.use, "use")
    paths = [stop.given(p, "path of the work") for p in args.path]
    if work in session.PARTS and paths:
        raise stop.Stop(
            f"rn: the work {work} is a part rn cuts for turn from the session's record; give no"
            " path of it"
        )
    if not paths and work not in session.PARTS + (steering.DELIVERABLE,):
        raise stop.Stop(
            f"rn: no path of the work {work} is given; give the path of each file or folder of it,"
            " from the top"
        )
    # The session is found first, which stops below the top of the repository, since each path
    # given is read from the top.
    folder = session.current()
    repo.pushed()
    has = [ccs.held(p) for p in args.has]
    steered = session.kept_steering(folder)
    serving = ccs.served(steered, work)
    found = session.calls(folder)
    last = session.latest(found, work)
    number = last.number if last is not None and not last.result else session.next_number(found)
    carried = [] if last is None else session.decisions_of(last)
    if work in session.PARTS:
        cut = (
            "\n".join(steered.plan) if work == steering.PLAN else f"## {session.LEARNINGS}"
        )  # pragma: no mutate
        part = session.call_path(folder, number, session.PART[work])
        repo.write_text(part, cut + "\n")
        paths = [part]
    if work == steering.PLAN:
        has += ccs.done_made(folder, found, steered.plan)
    # A CCS holds its entries in four parts, the shape turn takes: focal_entities, what the work is
    # about, the work by its name, the stage it is made in, its paths, its receiver and what they
    # have with it; goal_orientation, what the work is for, its use and what it serves as text, as
    # turn makes the work from the CCS and the files it names alone; retrieved_artifacts, the
    # kind's checklists and rn's `usability.md` where the work is a checklist; and constraints, the
    # bounds it is made in: its decisions, the languages, and rn's checklist for a fix, which turn's
    # generator holds whenever it changes a work already there. turn finds each entry by its key,
    # whichever part holds it.
    usability = os.path.join(root, "checklists", "usability.md")
    written = {
        "focal_entities": [{session.WORK: work}, {steering.STAGE: steered.keys[steering.STAGE]}]
        + [{ccs.ENTRIES["work"]: p} for p in paths or ccs.finished_work()]
        + [{ccs.ENTRIES["receiver"]: receiver}]
        + [{ccs.ENTRIES["has"]: p} for p in has],
        "goal_orientation": [{ccs.ENTRIES["use"]: use}]
        + [{ccs.SERVES: f"{key}: {text}"} for key, text in serving.items()],
        "retrieved_artifacts": [{ccs.ENTRIES["checklist"]: p} for p in ccs.checklists(kind, root)]
        + ([{"source": usability}] if kind == ccs.CHECKLIST else []),
        "constraints": [{session.DECISION: d} for d in carried]
        + [{key: steered.keys[key]} for key in steering.LANGUAGES]
        + [{"fix": os.path.join(root, "checklists", "fix.md")}],
    }
    path = session.call_path(folder, number, session.CCS)
    repo.write_json(path, written)
    session.keep(folder, steered, f"Call {number} on {work}: handed to turn")
    # turn's call takes the table of keys under "kind", a field name of turn's own that is no kind
    # of work; and the command that checks the work under "test", null for none for now, as rn's
    # tasks name no such command yet, which they will give once rn is rebuilt.
    result = session.call_path(folder, number, session.RESULT)
    return {"ccs": path, "kind": ccs.ENTRIES, "result": result, "test": None}


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
    stage, waiting = steered.keys[steering.STAGE], steered.keys["signoff"]
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
    shown = proposal.proposed(signoff, folder)
    before = shown[:-1] if waiting == signoff else shown
    now = proposal.shown_at("HEAD", signoff, folder)
    then = proposal.shown_at(before[-1], signoff, folder) if before else None
    shown_text = "\n".join(
        [
            f"{signoff.capitalize()} sign-off",
            f"{proposal.SIGNOFFS[signoff]}: {steered.keys['pr']}",
            *proposal.compared(then, now),
            proposal.ANSWER,
        ]
    )
    if waiting == steering.NONE:
        waits = f"Wait at the {signoff} sign-off for the user's answer: {proposal.ANSWER}"
        session.keep(
            folder,
            steered._replace(keys=dict(steered.keys, signoff=signoff), next=waits),
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
    next_step = stop.given(args.next, "next step")
    message = stop.given(args.message, "message")
    folder = session.current()
    steered = session.kept_steering(folder)
    waiting = steered.keys["signoff"]
    if waiting == steering.NONE:
        raise stop.Stop(
            "rn: no sign-off waits for the user's answer; show the proposal with `rn.py proposal"
            " <plan|design|deliverable>` first, and keep the answer the user gives it"
        )
    command = proposal.COMMANDS[args.answer]
    shown = float(
        repo.git(
            ["log", "-1", "--format=%ct", proposal.proposed(waiting, folder)[-1]], repo.AS_GIT_SAYS
        )
    )
    if not conversations.typed(command, shown):
        raise stop.Stop(
            f"rn: the user has not typed {command} since the {waiting} sign-off was shown; the"
            " answer is theirs alone, so wait for them to type it, and keep it then"
        )
    keys = dict(steered.keys, signoff=steering.NONE)
    if args.answer == "approved":  # pragma: no mutate
        keys[steering.STAGE] = steering.APPROVED[waiting]
    answered = steered._replace(keys=keys, next=next_step, open=steering.opened(args.open))
    return {"kept": session.keep(folder, answered, message)}


def run_records(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Shows the stretch of the session the learnings are made from, once every change is pushed:
    its record, the history on the branch since the last call on the learnings turn returned and
    the session's files as they are now; then each conversation of the orchestrator, run at the top
    of the repository on the session's branch, from the time the stretch began, none where Claude
    Code keeps none here, as when the session ran on another machine. Each is written as text in the
    git folder, made afresh, where nothing is committed; gives their paths, the record first, what
    the receiver of the learnings' call has. Stops where the branch holds no session, or a change
    is not kept or pushed."""
    folder = session.current()
    repo.pushed()
    start = stretch.stretch(folder)
    began = float(repo.git(["log", "-1", "--format=%ct", start], repo.AS_GIT_SAYS))
    top = repo.git(["rev-parse", "--show-toplevel"], repo.AS_GIT_SAYS).strip()
    branch = repo.git(["branch", "--show-current"], repo.AS_GIT_SAYS).strip()
    place = stretch.learning()
    shutil.rmtree(place, ignore_errors=True)
    # Each text shown, by where it is written, with its text.
    shown = [(os.path.join("record", "history.txt"), stretch.history(folder, start))]
    shown += [(os.path.join("record", p), repo.read_text(p)) for p in stretch.session_files(folder)]
    for path in conversations.conversations(top, branch):
        name = os.path.basename(path)[: -len(".jsonl")] + ".txt"
        text = conversations.told(path, began)
        if text:
            shown.append((os.path.join("conversations", name), text))
    for name, text in shown:
        repo.write_text(os.path.join(place, name), records.wrapped(text))
    return [os.path.join(place, name) for name, _ in shown]


def run_learnings(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Every learning of the session, for the orchestrator to put to the user one per message once
    the finished work is approved: the session's, by ID, each as one line; and turn's, each as
    turn's result gives it, with the work, the call and the commit that kept it. Stops where the
    branch holds no session."""
    folder = session.current()
    said = steering.by_id(list(enumerate(session.learnings_of(folder))), "- ")
    return {"learnings": said, "turn": stretch.turns_learnings(folder)}


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
    for option in ("--title", *(f"--{key}" for key in steering.LANGUAGES), "--next", "--message"):
        start.add_argument(option, required=True)
    state = sub.add_parser("state")
    state.set_defaults(run=run_state)
    state.add_argument("--next", required=True)
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
    for option in ("--kind", "--receiver", "--use"):
        hand.add_argument(option, required=True)
    hand.add_argument("--has", action="append", default=[])
    shown_text = sub.add_parser("proposal")
    shown_text.set_defaults(run=run_proposal)
    shown_text.add_argument("signoff", choices=list(proposal.SIGNOFFS))
    answer = sub.add_parser("answer")
    answer.set_defaults(run=run_answer)
    answer.add_argument("answer", choices=proposal.ANSWERS)
    answer.add_argument("--next", required=True)
    answer.add_argument("--open", action="append", default=[])
    answer.add_argument("--message", required=True)
    lists = sub.add_parser("checklists")
    lists.set_defaults(run=run_checklists)
    lists.add_argument("kind")
    sub.add_parser("records").set_defaults(run=run_records)
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
