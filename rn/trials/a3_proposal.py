#!/usr/bin/env python3
"""A3: the account session paused with its plan settled and its proposal not yet drafted, /rn:up to
the Plan sign-off. Two stand-ins with the same part and the same instruction decide, one from the
proposal alone and one from the pull request; both are recorded, neither is sent."""
import os
import re
import subprocess

from common import ACCOUNT_PART, MAX_TURNS, Trial, clone

DECIDE = """Decide this sign-off as the user. Reply with /rn:ty if what you read shows nothing against
your reason, what you know, and your decisions, and otherwise /rn:gm followed by what you saw. Then,
after a line '---', list in a few lines what you based it on."""

PROPOSAL_READER = """rn has put this proposal to you:

{said}

You read only this proposal; do not look at the code, the pull request, or anything else.

""" + DECIDE

PR_READER = """Read the real thing, not rn's message: the pull request {url} (use gh pr view / gh pr diff,
and read the files on its branch in this clone; run git fetch and git checkout of the branch first).
Read the plan (.rn/*/steering.md) and anything else on the branch as far as you need to decide. Do not
change, commit, or push anything.

""" + DECIDE


def proposal_reader(said):
    r = subprocess.run(["claude", "-p", ACCOUNT_PART + "\n\n" + PROPOSAL_READER.format(said=said),
                        "--model", "opus", "--tools", ""], cwd=t.out, capture_output=True, text=True)
    return r.stdout.strip()


def pr_reader(said):
    reader = os.path.join(t.out, "reader")
    clone(reader)
    m = re.search(r"https://github\.com/\S+/pull/\d+", said)
    url = m.group(0) if m else "(the open pull request of lovaizu/rn-try)"
    part = ACCOUNT_PART.replace("You never look at the code or the pull request yourself.", "")
    r = subprocess.run(["claude", "-p", part + "\n\n" + PR_READER.format(url=url), "--model", "opus",
                        "--allowedTools", "Bash(gh:*) Bash(git fetch:*) Bash(git checkout:*) "
                        "Bash(git log:*) Bash(git show:*) Bash(git diff:*) Read Grep Glob"],
                       cwd=reader, capture_output=True, text=True)
    return r.stdout.strip()


def scene():
    t.start_from("account-ready")
    said, sid, _ = t.turn("/rn:up")
    for _ in range(MAX_TURNS):
        if t.waiting_for() == "Plan sign-off":
            t.log("stand-in, from the proposal alone (not sent)", proposal_reader(said))
            t.log("second stand-in, from the pull request (not sent)", pr_reader(said))
            return
        said, sid, _ = t.turn(t.stand_in(ACCOUNT_PART, said), sid)
    t.log("trial", "Turn limit reached.")


t = Trial(__doc__)
t.run(scene)
