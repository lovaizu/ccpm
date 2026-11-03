"""The E2E test of O2 of Turn's UX, "The person gets a man page for tidy": in an interactive session
of Claude Code on Opus, with copies of Turn and pin, the person types `/turn:up a man page for
tidy`, a kind Turn ships no template for, and answers each message, stood in for by an AI that
answers from an intent written beforehand and never shown Turn.

Breaks it invites, beside those of trial_readme.py: the template made without the person's approval
of the kind's purpose and conditions, and a template out of its form.

A run counts where Turn handed back a man page. It passes where, beside what trial_readme.py's runs
pass on: `.turn/best-practices/` holds the kind's template, which Turn's practices.py check passes.
Run as `python3 dev/turn/tests/e2e/trial_new_kind.py [runs] [first]`."""

from __future__ import annotations

import glob
import os
import subprocess
import sys
import time

import turning

INTENT = (
    """You wrote `tidy`, a small Python tool in the repository the AI works in, that sorts a
cluttered Downloads folder into folders by kind. You want a man page for it, in the roff form
`man` reads, as `tidy.1`.

What you want, which the AI may or may not ask:
- A man page as people expect one: NAME, SYNOPSIS, DESCRIPTION, OPTIONS, EXAMPLES and EXIT
  STATUS, short and exact.
- Its example shows `--dry-run` first.
- It says that a file with no extension stays where it is.

Of a man page in general you want what makes one good to read in a terminal; where the AI shows you
the purpose of a man page and what a good one holds, say yes where it fits that, and otherwise say
what is to change.

What you know of your repository, which the AI can read for itself: tidy.py is the whole tool; it
takes --dry-run; it sorts by extension into images, documents, archives and other.

"""
    + turning.HOW
)


def run(number: int) -> bool:
    """One run of the E2E test; prints what it found, and gives whether it passed and counted."""
    place = turning.trying.folder("turn", f"trial-new-kind-{number}")
    repo, copies = turning.made(place)
    started = time.monotonic()
    session, turns = turning.talked(
        "/turn:up a man page for tidy", [copies["turn"], copies["pin"]], repo, place, INTENT
    )
    print(f"  {len(turns)} messages, {time.monotonic() - started:.0f} s")
    run_folder = turning.run_folder(repo)
    work = turning.read_json(os.path.join(run_folder, "work.json")) if run_folder else None
    if not work or not all(os.path.exists(os.path.join(repo, p)) for p in work["paths"]):
        return turning.verdict(["Turn handed back no man page"], [])
    wrong = turning.asked_wrong(turns) + turning.routes_wrong(turning.starts(session))
    templates = glob.glob(os.path.join(repo, ".turn", "best-practices", "*.json"))
    if not templates:
        wrong.append("no template was kept in .turn/best-practices/")
    for t in templates:
        script = os.path.join(copies["turn"], "scripts", "practices.py")
        done = subprocess.run(
            [sys.executable, script, "check", t], capture_output=True, text=True, check=False
        )
        if done.returncode:
            wrong.append(f"the template does not pass practices.py check: {done.stderr.strip()}")
    wrong += turning.work_wrong(repo, work["paths"], place, INTENT)
    return turning.verdict([], wrong)


if __name__ == "__main__":
    turning.main(run)
