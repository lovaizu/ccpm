"""What the generator and the evaluator run on a run's folder, as `python3
${CLAUDE_PLUGIN_ROOT}/scripts/rounds.py round <run>`: the next round of the work the run is at,
settled and said, its phase, the best practice it is made by, the design, where its Answers go, its
questions and the shortfalls of the round before, giving 0; that no round is left, giving 1; or why
it could not, giving 2. And `... rounds.py check <run> <answers>`: whether the Answers hold, every
question the run was given answered once with lines the work holds, with the result the run gives
and the lines it ends with, giving 0; each fault, giving 1; or why it could not check, giving 2. It
hands each to phases.py in core/domain/."""

from __future__ import annotations

import os
import sys

# No module before it on the path has the name of Turn's.
sys.path.insert(
    0,  # pragma: no mutate
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core", "domain"),
)

import files
import phases
import runs

USAGE = (
    "usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/rounds.py round <run>\n"
    "       python3 ${CLAUDE_PLUGIN_ROOT}/scripts/rounds.py check <run> <answers>"
)
# What a round of each phase is of.
OF = {phases.CONTENT: "what the work says", phases.READING: "how the work reads"}


def settled(run: str) -> int:
    """Settles the next round, prints what it asks, and gives 0, 1 or 2."""
    try:
        work = runs.current(runs.load(run))
        short = phases.shortfalls(run, phases.last(work))
        made = phases.settle(run)
    except files.Unreadable as why:
        print(f"rounds.py: could not settle a round of {run}: {why}", file=sys.stderr)
        return 2
    if made is None:
        print(
            f"rounds.py: every question of {work['kind']} and of {work['reading']} is met: no round"
            " is left."
        )
        return 1
    reads = phases.READS[made["phase"]]
    name = runs.READING if reads else runs.STANDARD
    standard = files.load(os.path.join(work["folder"], name), "standard")
    kind = work["reading"] if reads else work["kind"]
    asks = {f"{kind}/{q['id']}": q["what"] for q in standard["intents"]}
    practice = runs.practice_in(runs.OWN, work["reading"]) if reads else work["practice"]
    lines = [
        f"rounds.py: round {made['round']} of {work['kind']} is of {OF[made['phase']]}.",
        f"Best practice: {practice}",
    ]
    if not reads:
        lines.append(f"Design: {os.path.join(work['folder'], runs.DESIGN)}")
    answers = os.path.join(phases.folder_of(work), runs.GENERATOR)
    lines.append(f"Answers: {answers}, in the form of {os.path.join(files.FORMS, 'answers.json')}")
    lines.append("Questions:")
    lines += [f"- {q}: {asks[q]}" for g in made["groups"] for q in g["questions"]]
    if short:
        lines.append("Shortfalls of the last round:")
        lines += [f"- {said}" for _, said in short]
    print("\n".join(lines))
    return 0


def checked(run: str, path: str) -> int:
    """Checks the Answers at the path, prints what it found, and gives 0, 1 or 2."""
    try:
        found, result, lines = phases.check(run, path)
    except files.Unreadable as why:
        print(f"rounds.py: could not check {path}: {why}", file=sys.stderr)
        return 2
    if found:
        print(f"rounds.py: {path} does not hold:")
        for fault in found:
            print(f"- {fault}")
        return 1
    said = f"rounds.py: {path} answers each question it was given. Give `{result}`"
    if result == "made":
        said += ", and end with these lines, one for each run of the evaluator:"
    elif lines:
        said += ", and end with this line, for up to start the generator with:"
    print("\n".join([said + ("" if lines else "."), *lines]))
    return 0


def main(argv: list[str]) -> int:
    """Runs the command on the run's folder given, or prints the usage and gives 2."""
    if argv[:1] == ["round"] and len(argv) == 2:
        return settled(argv[1])
    if argv[:1] == ["check"] and len(argv) == 3:
        return checked(argv[1], argv[2])
    print(USAGE, file=sys.stderr)
    return 2


# Run as the command, and not when the tests import it under the name rounds.
if __name__ == "__main__":  # pragma: no mutate
    sys.exit(main(sys.argv[1:]))
