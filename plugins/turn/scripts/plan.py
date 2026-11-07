"""What the planner runs on a run's folder, as `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan.py
<command> <run>`: `start` begins the run from its Call; `hand` hands the design to Pin again, with
the shortfalls of the last round; `ready` puts the work into its rounds; `next` ends a work whose
rounds met every question and begins the next; each prints what the planner gives and ends with,
giving 0, or why it cannot, giving 1. `check` says whether the Run holds and where the run is,
giving 0, each fault, giving 1, or why it could not check, giving 2. And what a person or CI runs
on a best practice, as `... plan.py form|markdown|example <best practice json>...`: its faults
and its Markdown and the copy of its example left behind, and each file in its folder that none of
them holds; its Markdown written beside it; and the copy of its example written from the work its
source names, with each file that none of them holds removed; each failing where it names any. It
hands each to runs.py, phases.py and practices.py in core/domain/."""

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
import tree

USAGE = (
    "usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan.py start|hand|ready|next|check <run>\n"
    "       python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan.py form|markdown|example"
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
    try:
        handed = tree.load(design)
    except tree.Unreadable as why:
        said = "; ".join(str(why).splitlines())
        raise files.Unreadable(f"the design tree {design} cannot be read: {said}") from None
    short = phases.shortfalls(run, phases.last(work))
    runs.hand(run)
    request = runs.request(design, "").rstrip("\n")
    if short:
        request += (
            "\nThe work made from this design falls short; each point names the decisions that"
            " serve its question:"
        )
        request += "".join(
            f"\n- {said} ({', '.join(phases.serving(handed, question))})"
            for question, said in short
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


def copied(path: str, data: dict) -> tuple[dict[str, bytes], list[str]]:
    """The files of the best practice's example copied from its source, or else why they cannot be
    made."""
    if "example" not in data:
        return {}, [f"its source {data['source']} has no example to be copied to"]
    try:
        return practices.copies(path, data), []
    except FileNotFoundError as why:
        return {}, [f"{why.filename}, which its example copies, is not there"]


def behind(path: str, data: dict) -> list[str]:
    """Each file of the best practice's example that is not as its source makes it, or why it
    cannot be made; none where it names no source."""
    if "source" not in data:
        return []
    made, found = copied(path, data)
    for copy, content in made.items():
        try:
            with open(copy, "rb") as f:
                same = f.read() == content
        except FileNotFoundError:
            same = False
        if not same:
            found.append(f"{copy} is not a copy of its source; run plan.py example")
    return found


def strays(path: str, data: dict) -> list[str]:
    """Each file in the best practice's folder that neither it, its template nor its example holds,
    in words; none where its source cannot be copied, which behind names."""
    try:
        found = practices.leftovers(path, data)
    except FileNotFoundError:
        return []
    fix = "run plan.py example" if "source" in data else "remove it"
    return [f"{file} is neither the template's nor the example's; {fix}" for file in found]


def form(path: str) -> list[str]:
    """Each fault of the best practice's form, its Markdown and the copy of its example left
    behind it, and each file in its folder that none of them holds."""
    try:
        data = files.load(path, "best-practice")
    except files.Unreadable as why:
        return [str(why)]
    late = behind(path, data) + strays(path, data)
    found = practices.missing(path, data)
    if found:
        return found + late
    found = practices.faults(data, practices.template(path, data)) + practices.unheld(path, data)
    target = os.path.splitext(path)[0] + ".md"
    try:
        with open(target, encoding="utf-8") as f:
            if f.read() != practices.markdown(practices.kind_of(path), data):
                found.append(f"{target} is not as its JSON makes it; run plan.py markdown")
    except FileNotFoundError:
        found.append(f"{target} is missing; run plan.py markdown")
    return found + late


def markdown(path: str) -> list[str]:
    """Writes the best practice's Markdown beside it, where it can be read."""
    try:
        data = files.load(path, "best-practice")
    except files.Unreadable as why:
        return [str(why)]
    with open(os.path.splitext(path)[0] + ".md", "w", encoding="utf-8") as f:
        f.write(practices.markdown(practices.kind_of(path), data))
    return []


def example(path: str) -> list[str]:
    """Writes the best practice's example, and each figure it shows, as a copy of its source, and
    removes each file in its folder that neither it, its template nor its example holds."""
    try:
        data = files.load(path, "best-practice")
    except files.Unreadable as why:
        return [str(why)]
    if "source" not in data:
        return ["it names no source to copy its example from"]
    made, found = copied(path, data)
    for copy, content in made.items():
        os.makedirs(os.path.dirname(copy), exist_ok=True)
        with open(copy, "wb") as f:
            f.write(content)
    # Only once the copy is made, as which files it holds is known only then.
    for file in practices.leftovers(path, data) if made else []:
        os.remove(file)
    return found


PRACTICES: dict[str, Callable[[str], list[str]]] = {
    "form": form,
    "markdown": markdown,
    "example": example,
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
