"""rn's command line, the subcommands rn's orchestrator runs for each move a machine can judge, so
that what must come out the same does on every run and a rule holds at the moment of the move: each
reads its arguments, checks each where it comes in, and calls the module of the part that makes
the move. Run from the top of the user's repository as
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/rn.py" <subcommand> ...`, with Python 3.9 or later and the
standard library alone; it prints JSON, or the proposal as text for the orchestrator to show, and on
a stop exits 1 with what went wrong and what to do."""

from __future__ import annotations

import argparse
import datetime
import os
import sys
from collections.abc import Callable
from typing import Any, NoReturn

import ccs
import conversations
import history
import learnings
import proposal
import repo
import session
import steering
import stop

# The plugin's own folder, which holds rn's checklists and its manifest.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_session(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """The session the checked-out branch is in, with its stage and the sign-off waiting, as
    session.where gives them."""
    return session.where()


def run_start(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Starts a session named by the slug, as session.start does; stops where a value is not given
    in its form."""
    slug = stop.named(args.slug, "slug")
    title = stop.given(args.title, "title")
    languages = {
        key: stop.given(getattr(args, key.replace("-", "_")), key) for key in steering.LANGUAGES
    }
    message = stop.given(args.message, "message")
    return session.start(slug, title, languages, message, root, today)


def run_state(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Keeps the move where the session stands, as session.state does; stops where the message is
    empty."""
    message = stop.given(args.message, "message")
    given = (args.next, args.open, args.done, args.put, args.stage, message)
    return session.state(*given, args.goes_on)


def run_decide(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Writes a decision of the work, as ccs.decide does; stops where the work is none rn makes, a
    value is empty, or the title holds `: `."""
    work = session.worked(args.work)
    title = stop.given(args.title, "title")
    if ": " in title:
        raise stop.Stop(
            f"rn: the title {title!r} holds `: `, which parts a decision's title from what it says;"
            " give the title without it"
        )
    says = stop.given(args.says, "decision")
    message = stop.given(args.message, "message")
    return ccs.decide(work, title, says, message)


def run_checklists(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """The paths of the kind's checklists; stops where the kind is not a name or has none."""
    return ccs.checklists(stop.named(args.kind, "kind"), root)


def run_ccs(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Writes the work's CCS, as ccs.handed does; stops, writing nothing, where the
    work is none rn makes, a text or a path given is empty, a choice gives no why, or a path is
    given of a part rn cuts."""
    work = session.worked(args.work)
    paths = [stop.given(p, "path of the work") for p in args.path]
    receiver = None if args.receiver is None else stop.given(args.receiver, "receiver")
    use = None if args.use is None else stop.given(args.use, "use")
    chosen = [ccs.choice(c) for c in args.chose]
    if work in session.PARTS and paths:
        raise stop.Stop(
            f"rn: the work {work} is a part rn cuts from the session's record; give no path of it"
        )
    return ccs.handed(work, paths, receiver, use, args.has, chosen, root)


def run_check(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Checks the part the orchestrator writes for the call of the number as `state --put` holds it,
    keeping nothing, as session.held_part says; gives the number where it holds. Stops where it does
    not, the branch holds no session, or the part cannot be taken."""
    session.held_part(session.current(), args.number)
    return {"held": args.number}


def run_decisions(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Each decision of the work and the checklists of its kind, as ccs.decisions gives them; stops
    where the work is none rn makes."""
    return ccs.decisions(session.worked(args.work), root)


def run_proposal(args: argparse.Namespace, root: str, today: datetime.date) -> str:
    """The proposal at the sign-off, the steering set waiting at it, as proposal.shown does."""
    return proposal.shown(args.signoff)


def run_answer(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Keeps the user's answer to the sign-off waiting, as proposal.answered does; stops where the
    message is empty."""
    message = stop.given(args.message, "message")
    return proposal.answered(args.answer, args.open, message)


def run_learnings(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Every learning of the session by ID, as learnings.listed gives them. Stops where the branch
    holds no session."""
    return {"learnings": learnings.listed(session.current())}


def run_history(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """The session's history on its branch, where the orchestrator looks for the learnings once the
    finished work is approved: each feedback with its answer, each work made again and each
    decision an answer replaced, each with its commit, as history.history gives them. Stops where
    the branch holds no session, or git fails."""
    return history.history(session.current())


def run_search(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Each part the user or the orchestrator said or did that holds the words, in the
    orchestrator's conversations of the session, with its conversation and time, as
    conversations.search gives them, for the orchestrator to check a cause of a learning it doubts.
    Stops where the words are empty, the branch holds no session, or Claude Code keeps no
    conversation of it here, as when the session ran on another machine."""
    words = stop.given(args.words, "text to search for")
    session.current()
    return {"found": conversations.search(words)}


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
    state.add_argument("--goes-on", action="store_true")
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
    hand.add_argument("--chose", action="append", default=[])
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
    sub.add_parser("history").set_defaults(run=run_history)
    search = sub.add_parser("search")
    search.set_defaults(run=run_search)
    search.add_argument("words")
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
