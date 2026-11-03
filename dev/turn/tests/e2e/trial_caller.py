"""The E2E test of O3 of Turn's UX, "rn has Turn make tidy's README": a plugin standing in for rn,
`caller`, kept beside this file, declares Turn in its dependencies, and its subagent `maker` starts
`turn:up` with the kind, the README's purpose and its path already settled, and passes on each of
Turn's questions. In an interactive session of Claude Code on Opus, with copies of Turn, pin and
caller, the main conversation starts maker and puts each of its messages to the person, stood in
for by an AI that answers from an intent written beforehand and never shown Turn.

Breaks it invites, beside those of trial_readme.py: the kind or the purpose caller settled asked
again, and caller's points left out of the design.

A run counts where Turn handed back the README. It passes where, beside what trial_readme.py's runs
pass on: no message asked the kind or the purpose again, and the design tree's goal is the one
caller gave. Run as `python3 dev/turn/tests/e2e/trial_caller.py [runs] [first]`."""

from __future__ import annotations

import os
import shutil
import time

import trial_readme
import turning

CALLER = os.path.join(turning.HERE, "caller")
GOAL = (
    "Someone who keeps a cluttered Downloads folder learns what tidy does, runs it on their folder"
    " and sees what moved."
)
FIRST = (
    "Start the subagent caller:maker in the background to have the README made. Whenever it ends"
    " with a message headed `For the person:`, give me that message word for word as your whole"
    " reply. When I answer, resume maker with SendMessage, giving it my answer word for word. When"
    " it ends with `Turn is working.`, say nothing and wait. When it ends with `Done:`, reply with"
    " that message. Do nothing else yourself."
)
INTENT = trial_readme.INTENT + (
    "\n\nYou already told caller, the tool that has the README made, that the work is a README and"
    f" its purpose: {GOAL} Being asked either again wastes your time."
)


def run(number: int) -> bool:
    """One run of the E2E test; prints what it found, and gives whether it passed and counted."""
    place = turning.trying.folder("turn", f"trial-caller-{number}")
    repo, copies = turning.made(place)
    copies["caller"] = os.path.join(place, "plugins", "caller")
    shutil.copytree(CALLER, copies["caller"])
    started = time.monotonic()
    session, turns = turning.talked(
        FIRST, [copies["turn"], copies["pin"], copies["caller"]], repo, place, INTENT
    )
    print(f"  {len(turns)} messages, {time.monotonic() - started:.0f} s")
    if not os.path.exists(os.path.join(repo, "README.md")):
        return turning.verdict(["Turn handed back no README.md"], [])
    wrong = turning.judged(session, turns, repo, place, INTENT, ["README.md"])
    run_folder = turning.run_folder(repo)
    tree = turning.read_json(os.path.join(run_folder, "design-tree.json")) if run_folder else None
    if not tree or tree.get("goal", {}).get("what") != GOAL:
        wrong.append("the design tree's goal is not the one caller gave")
    return turning.verdict([], wrong)


if __name__ == "__main__":
    turning.main(run)
