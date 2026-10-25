"""Judges the work each acceptance trial gave back by one bar, a measure beside KR1.1, which is the
calling AI's own check of each Good: for each work folder trial.py kept, an AI that took no part in
any of the runs judges each item of the task's checklists afresh, whether the receiver the CCS
names gets from that work what the item asks, with what it read and ran for it, on one prompt and
each folder in a Claude Code run of its own, all at once, so no folder's reading cuts another's
short. Writes each folder's judgment to `<folder>.judged.json` beside it, and prints each folder's
count and its session.

    python3 dev/turn/trials/judge.py <work folder> [<work folder> ...]
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import threading

import shared

KIND = shared.call("has")["kind"]
PROMPT = """You judge work that was made for a task, in the folder {folder}.

The folder holds the task at `.tasks/ccs.json`, a CCS: the work is what it names as
`{work}`, the receiver its `{receiver}`, what they use the work for its `{use}`, the
checklists its `{checklist}`, and what the receiver has with the work its `{has}`; its other
entries, such as the decisions, are what the work was made from. Read the CCS, its decisions, each
checklist and the whole work, each file whole with `cat -n`. Each item of a checklist is a heading
such as `### B-1: <title>`, with a `Scope` line saying where it is answered.

For each item, judge whether the receiver, for that use, with what they have, gets from the work
what the item asks, where its Scope says. Check what the work says rather than trust it: run each
command it tells the receiver to run and compare what it prints with what the work says, try each
claim of what the code does on an input it is about, and look up each file and link it points to;
each in a copy of the folder in a folder from `mktemp -d` that the command removes at its end.
Change nothing in the folder.

Write your judgment to {out} as JSON: [{{"checklist": "<path as the CCS names it>", "item":
"<ID>", "met": true or false, "read": ["<file>:<from>-<to>", ...], "ran": ["<command>", ...],
"reason": "<what the receiver gets or lacks, and what showed it>"}}, ...], every item of every
checklist. Then reply `Written.`"""


def judged(folder: str) -> str:
    """Where the judgment of the folder is written, beside it."""
    return folder.rstrip("/") + ".judged.json"


def judge(folder: str, ends: dict) -> None:
    """Runs the judge on the folder, in a folder of its own, so it starts from none of the runs'
    folders."""
    place = tempfile.mkdtemp()
    with shared.removed(place):
        prompt = PROMPT.format(folder=folder, out=judged(folder), **KIND)
        ends[folder] = shared.claude(prompt, [], cwd=place)


folders = [os.path.abspath(p) for p in sys.argv[1:]]
if not folders:
    sys.exit("usage: judge.py <work folder> [<work folder> ...]")
for folder in folders:
    if not os.path.isfile(os.path.join(folder, ".tasks", "ccs.json")):
        sys.exit(f"{folder} holds no .tasks/ccs.json; give a folder trial.py kept")
    if os.path.exists(judged(folder)):
        sys.exit(f"{judged(folder)} is there already; move it away to judge again")
ends: dict = {}
runs = [threading.Thread(target=judge, args=(f, ends)) for f in folders]
for run in runs:
    run.start()
for run in runs:
    run.join()
for folder in folders:
    with open(os.path.join(folder, ".tasks", "ccs.json"), encoding="utf-8") as f:
        checklists = shared.entries(json.load(f), "checklist")
    # The folder's items, from the checklists its CCS names, to find any the judge left out.
    asked = {(c, i) for c in checklists for _, i, _ in shared.items(os.path.join(folder, c))}
    with open(judged(folder), encoding="utf-8") as f:
        given = json.load(f)
    met = asked & {(g.get("checklist"), g.get("item")) for g in given if g.get("met") is True}
    left = sorted(asked - {(g.get("checklist"), g.get("item")) for g in given})
    end = ends[folder]
    print(
        f"{folder}: {len(met)} of {len(asked)} met"
        + (f"; not judged: {left}" if left else "")
        + f"; session {end.get('session_id')}, cost {end.get('total_cost_usd')}"
    )
