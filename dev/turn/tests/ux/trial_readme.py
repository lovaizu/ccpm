"""The E2E test of O1 of Turn's UX, "The person gets a README for tidy", as the README's walkthrough
runs it: in an interactive session of Claude Code on Opus, with copies of Turn and pin, the person
types `/turn:up a README for tidy` in tidy's repository and answers each message, stood in for by
an AI that answers from an intent written beforehand and never shown Turn.

Breaks it invites: a question about a fact of the repository, such as what --dry-run does, which
Turn is to find; several points in one message; a decision that follows from the repository put to
the person; and a README the person would still change, such as one that shows no --dry-run first.

A run counts where Turn handed back a README. It passes where: the person would change nothing in
the README; no message put more than one point, asked a fact, asked again what was settled, or a
point not the person's; and the roles started as Turn's routes say, from planner to proofreader.
Run as `python3 dev/turn/tests/ux/trial_readme.py [runs] [first]`; it prints the folder of each
run, where the terminal, the person's view and the records are kept, and what it found."""

from __future__ import annotations

import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
# What the trials of more than one level share lies in tests/.
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))

import turning

INTENT = (
    """You wrote `tidy`, a small Python tool in the repository the AI works in, that sorts a
cluttered Downloads folder into folders by kind. You want a README for it.

What you want, which the AI may or may not ask:
- The README is for people who keep a cluttered Downloads folder and can run a command in a
  terminal, not for developers of tidy.
- Its walkthrough shows `python3 tidy.py --dry-run ~/Downloads` first, so the reader sees what
  would move before anything moves, then the run without it.
- It says plainly that a file with no extension stays where it is, and that tidy moves files and
  never deletes them.

What you know of your repository, which the AI can read for itself: tidy.py is the whole tool; it
takes --dry-run; it sorts by extension into images, documents, archives and other; the LICENSE is
MIT.

"""
    + turning.HOW
)


def run(number: int) -> bool:
    """One run of the E2E test; prints what it found, and gives whether it passed and counted."""
    place = turning.trying.folder("turn", f"trial-readme-{number}")
    repo, copies = turning.made(place)
    started = time.monotonic()
    session, turns = turning.talked(
        "/turn:up a README for tidy", [copies["turn"], copies["pin"]], repo, place, INTENT
    )
    print(f"  {len(turns)} messages, {time.monotonic() - started:.0f} s")
    if not os.path.exists(os.path.join(repo, "README.md")):
        return turning.verdict(["Turn handed back no README.md"], [])
    wrong = turning.judged(session, turns, repo, place, INTENT, ["README.md"])
    return turning.verdict([], wrong)


if __name__ == "__main__":
    turning.main(run)
