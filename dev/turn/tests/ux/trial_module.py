"""The ux trial of O1 of Turn's UX on code, with parts that stand apart: in an interactive session
of Claude Code on Opus, with copies of Turn and pin, the person types `/turn:up` asking for two new
modules of tidy that use nothing of each other, and answers each message, stood in for by an AI
that answers from an intent written beforehand and never shown Turn.

Breaks it invites, beside those of trial_readme.py: the two modules made in order where they could
be made at once, and made as one where they stand apart.

A run counts where Turn handed back both modules and the design split the work into two parts or
more. It passes where, beside what trial_readme.py's runs pass on: the person would change nothing
in the modules, and two runs of generator that `up` started for two parts went at the same time.
Run as `python3 dev/turn/tests/ux/trial_module.py [runs] [first]`."""

from __future__ import annotations

import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
# What the trials of more than one level share lies in tests/.
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))

import turning

ASK = (
    "/turn:up two modules for tidy: rules.py, which reads a JSON file mapping an extension to a"
    " folder, and log.py, which keeps a log of each move so it can be undone later"
)
INTENT = (
    """You wrote `tidy`, a small Python tool in the repository the AI works in, that sorts a
cluttered Downloads folder into folders by kind. You want two new modules, which use nothing of
each other: tidy wires them in later, yourself.

What you want, which the AI may or may not ask:
- rules.py: `load(path)` reads a JSON object such as {".jpg": "images"} from the file at the path
  and gives it as a dict, extensions in lower case; a missing file gives tidy's own KINDS.
- log.py: `record(log_path, source, target)` appends one line of JSON, {"from": ..., "to": ...},
  to the log file; `moves(log_path)` gives each move recorded, oldest first.
- Python 3.9 and its standard library only; each module with unittest tests in tests/.

What you know of your repository, which the AI can read for itself: tidy.py holds KINDS and the
command; there are no tests yet.

"""
    + turning.HOW
)


def run(number: int) -> bool:
    """One run of the trial; prints what it found, and gives whether it passed and counted."""
    place = turning.trying.folder("turn", f"trial-module-{number}")
    repo, copies = turning.made(place)
    started = time.monotonic()
    session, turns = turning.talked(ASK, [copies["turn"], copies["pin"]], repo, place, INTENT)
    print(f"  {len(turns)} messages, {time.monotonic() - started:.0f} s")
    run_folder = turning.run_folder(repo)
    work = turning.read_json(os.path.join(run_folder, "work.json")) if run_folder else None
    untried = []
    paths = work.get("paths", []) if work else []
    if not paths or not all(os.path.exists(os.path.join(repo, p)) for p in paths):
        untried.append("Turn did not hand back the modules")
    if not work or len(work.get("parts", [])) < 2:
        untried.append("the design did not split the work into two parts")
    if untried or not work:
        return turning.verdict(untried, [])
    runs = turning.starts(session)
    wrong = turning.asked_wrong(turns) + turning.routes_wrong(runs)
    if not turning.overlapped(runs, "generator"):
        wrong.append("no two runs of generator went at the same time")
    wrong += turning.work_wrong(repo, work["paths"], place, INTENT)
    return turning.verdict([], wrong)


if __name__ == "__main__":
    turning.main(run)
