"""What the planner runs on a run's folder, as `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan.py
<command> <run>`: `start` begins the run from its Call; `hand` hands the design to Pin again, with
the shortfalls of the last round; `ready` puts the work into its rounds; `next` ends a work whose
rounds met every question and begins the next; each prints what the planner gives and ends with,
giving 0, or why it cannot, giving 1. `check` says whether the Run holds and where the run is,
giving 0, each fault, giving 1, or why it could not check, giving 2. And what a person or CI runs
on a best practice, as `... plan.py form|markdown|sources <best practice json>...`: its faults and
its Markdown left behind, its Markdown written beside it, and each ground whose page is not the one
meant, each failing where it names any. It hands each to runs.py, phases.py and practices.py in
core/domain/."""

from __future__ import annotations

import os
import sys
from typing import Callable

# No module before it on the path has the name of Turn's.
sys.path.insert(
    0,  # pragma: no mutate
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core", "domain"),
)

import files
import phases
import practices
import runs

USAGE = (
    "usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan.py start|hand|ready|next|check <run>\n"
    "       python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan.py form|markdown|sources"
    " <best practice json>..."
)
HANDED = "Give `handed`, and end with this Request as it is"


def start(run: str) -> str:
    """Begins the run, and says the Request."""
    request = runs.start(run)
    design = os.path.join(runs.load(run)["works"][0]["folder"], runs.DESIGN)
    return f"{run} is begun, and its design handed over at {design}. {HANDED}:\n{request}"


def hand(run: str) -> str:
    """Hands the design of the work the run is at to Pin again, and says the Request, each
    shortfall of the last round with the decisions that serve its question."""
    work = runs.current(runs.load(run))
    design = os.path.join(work["folder"], runs.DESIGN)
    tree = files.read(design)
    short = phases.shortfalls(run, phases.last(work))
    runs.hand(run)
    request = runs.request(design, "").rstrip("\n")
    if short:
        request += (
            "\nThe work made from this design falls short; each point names the decisions that"
            " serve its question:"
        )
        request += "".join(
            f"\n- {said} ({', '.join(phases.serving(tree, question))})" for question, said in short
        )
    return (
        f"the design of {work['kind']} is handed to Pin again. {HANDED}, with on its last lines"
        f" any change the request names, as given:\n{request}"
    )


def ready(run: str) -> str:
    """Puts the work into its rounds, and says the generator's run values."""
    line = runs.ready(run)
    work = runs.current(runs.load(run))
    return (
        f"the work of {work['kind']} is in its rounds. Give `ready`, and end with this line, for up"
        f" to start the generator with:\n{line}"
    )


def advance(run: str) -> str:
    """Ends the work whose rounds met every question, and says the Request of the next, or the
    Message that hands the run's work back."""
    work = runs.current(runs.load(run))
    if phases.where(run) not in ("finished",):
        raise files.Unreadable(
            f"the rounds of {work['kind']} have not met every question of both phases"
        )
    request = runs.advance(run)
    if not request:
        return (
            f"the run is done. Give `done`, and end with this Message as it is:\n{runs.done(work)}"
        )
    design = os.path.join(runs.current(runs.load(run))["folder"], runs.DESIGN)
    return (
        f"the work of {work['kind']} is done, and the next handed over at {design}. {HANDED}:\n"
        f"{request}"
    )


MOVES: dict[str, Callable[[str], str]] = {
    "start": start,
    "hand": hand,
    "ready": ready,
    "next": advance,
}


def where(run: str, data: dict) -> str:
    """Where the run is, and what the planner runs next."""
    work = runs.current(data)
    change = f"To hand Pin a change, run plan.py hand {run}."
    # What is said of a work done or with Pin, by where it is.
    said = {
        runs.DONE: (
            "The run is done. Give `done`, and end with this Message as it is:\n"
            f"{runs.done(work)}\n{change}"
        ),
        runs.PIN: (
            f"The design of {work['kind']} is with Pin, at"
            f" {os.path.join(work['folder'], runs.DESIGN)}.\nOnce Pin hands it back confirmed,"
            f" write into the work's paths, commands and files in {run}/run.json what the design"
            f" gives, then run plan.py ready {run}. To go on with it after the run stopped, or to"
            f" hand Pin a change, run plan.py hand {run}."
        ),
    }
    if work["at"] in said:
        return said[work["at"]]
    # What is said of a work in its rounds, by where its rounds stand.
    rounds = {
        "short": f"Its last round fell short: run plan.py hand {run}.",
        "finished": f"Its rounds have met every question: run plan.py next {run}.",
    }
    going = f"To go on with them, run plan.py ready {run}. {change}"
    return f"The work of {work['kind']} is in its rounds.\n" + rounds.get(phases.where(run), going)


def check(run: str) -> int:
    """Prints whether the run's Run holds and where the run is, and gives 0, 1 or 2."""
    if not os.path.exists(os.path.join(run, runs.RUN)):
        form = os.path.join(files.FORMS, runs.CALL)
        print(
            f"plan.py: {run} holds no Run yet. Settle the kind, write {run}/{runs.CALL} in the form"
            f" of {form}, then run plan.py start {run}."
        )
        return 0
    try:
        data = runs.load(run)
        found = [
            fault
            for w in data["works"]
            if w["at"] in (runs.ROUNDS, runs.DONE)
            for fault in runs.work_faults(w)
        ]
        said = "" if found else where(run, data)
    except files.Unreadable as why:
        print(f"plan.py: could not check {run}: {why}", file=sys.stderr)
        return 2
    if found:
        print(f"plan.py: {run} does not hold:")
        for fault in found:
            print(f"- {fault}")
        return 1
    print(f"plan.py: {run} holds. {said}")
    return 0


def form(path: str) -> list[str]:
    """Each fault of the best practice's form, and its Markdown left behind it."""
    try:
        data = files.load(path, "best-practice")
    except files.Unreadable as why:
        return [str(why)]
    found = practices.missing(path, data)
    if found:
        return found
    found = practices.faults(data, practices.template(path, data))
    target = os.path.splitext(path)[0] + ".md"
    kind = os.path.splitext(os.path.basename(path))[0]
    try:
        with open(target, encoding="utf-8") as f:
            if f.read() != practices.markdown(kind, data):
                found.append(f"{target} is not as its JSON makes it; run plan.py markdown")
    except FileNotFoundError:
        found.append(f"{target} is missing; run plan.py markdown")
    return found


def markdown(path: str) -> list[str]:
    """Writes the best practice's Markdown beside it, where it can be read."""
    try:
        data = files.load(path, "best-practice")
    except files.Unreadable as why:
        return [str(why)]
    with open(os.path.splitext(path)[0] + ".md", "w", encoding="utf-8") as f:
        kind = os.path.splitext(os.path.basename(path))[0]
        f.write(practices.markdown(kind, data))
    return []


def sources(path: str) -> list[str]:
    """Each ground of the best practice whose page is not the one meant, where it can be read."""
    try:
        return practices.sources(files.load(path, "best-practice"))
    except files.Unreadable as why:
        return [str(why)]


PRACTICES: dict[str, Callable[[str], list[str]]] = {
    "form": form,
    "markdown": markdown,
    "sources": sources,
}


def main(argv: list[str]) -> int:
    """Runs the command on what it is given, as the module says; or prints the usage and gives 2."""
    if argv[1:] and argv[0] in PRACTICES:
        failed = False
        for path in argv[1:]:
            for fault in PRACTICES[argv[0]](path):
                print(f"plan.py: {path}: {fault}", file=sys.stderr)
                failed = True
        return 1 if failed else 0
    if len(argv) != 2 or argv[0] not in (*MOVES, "check"):
        print(USAGE, file=sys.stderr)
        return 2
    command, run = argv
    # check, the one command that moves nothing.
    if command not in MOVES:
        return check(run)
    try:
        said = MOVES[command](run)
    except files.Unreadable as why:
        print(f"plan.py: {run} cannot {command}: {why}", file=sys.stderr)
        return 1
    print(f"plan.py: {said}")
    return 0


# Run as the command, and not when the tests import it under the name plan.
if __name__ == "__main__":  # pragma: no mutate
    sys.exit(main(sys.argv[1:]))
