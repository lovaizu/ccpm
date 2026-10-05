#!/usr/bin/env python3
"""A3: the account session paused with its plan settled and its proposal not yet drafted, /rn:up to
the Plan sign-off. The stand-in decides from the proposal alone and a second stand-in from the pull
request; both are recorded, neither is sent."""
import os
import re
import subprocess

from common import ACCOUNT_PART, MAX_TURNS, Trial, clone

PR_READER = """You decide this sign-off by reading the real thing, not rn's message: the pull request
{url} (use gh pr view / gh pr diff, and read the files on its branch in this clone; run git fetch and
git checkout of the branch first). Read the plan (.rn/*/steering.md) and anything else on the branch
as far as you need to decide. Do not change, commit, or push anything. You know only your part above.

Reply with /rn:ty if what is on the pull request shows nothing against your reason and decisions,
and otherwise /rn:gm followed by what you saw. Then, after a line '---', list in a few lines what on
the pull request you based it on."""


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
            t.log("stand-in, from the proposal alone (not sent)", t.stand_in(ACCOUNT_PART, said))
            t.log("second stand-in, from the pull request (not sent)", pr_reader(said))
            return
        said, sid, _ = t.turn(t.stand_in(ACCOUNT_PART, said), sid)
    t.log("trial", "Turn limit reached.")


t = Trial(__doc__)
t.run(scene)
