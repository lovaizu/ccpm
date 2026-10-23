"""Judges KR1.1 for the acceptance trials: one Claude Code run, an AI that took no part in any of the
runs, judges by one bar each item of the task's checklists in each work folder trial.py and
baseline.py kept, whether the receiver the CCS names gets from that work what the item asks. Writes
each folder's items met and not, each with its reason, to `judged.json` beside the first folder,
and prints each folder's count and its session.

    python3 dev/turn/trials/judge.py <work folder> [<work folder> ...]
"""

import json
import os
import shutil
import sys
import tempfile

import shared

PROMPT = """You judge work that was made for a task, by one bar, in each of these folders:
{folders}

Each folder holds the task at `.tasks/ccs.json`, a CCS: the work is what it names as
`deliverable`, the receiver its `audience`, what they use the work for its `purpose`, the
checklists its `checklist`, and what the receiver has with the work its `source`; its other
entries, such as the decisions, are what the work was made from. Read the CCS, its decisions and
each checklist whole. Each item of a checklist is a heading such as `### B-1: <title>`, with a
`Scope` line saying where it is answered.

For each item, judge whether the receiver, for that use, with what they have, gets from the work
what the item asks, where its Scope says, reading the whole work. Run what the
work tells the receiver to run, as they would, in a copy of the folder in a folder from
`mktemp -d` that the command removes at its end; change nothing in the folders. Judge every folder
by the same bar, each on its own.

Write your judgment to {out} as JSON: {{"<folder as above>": [{{"checklist": "<path as the CCS
names it>", "item": "<ID>", "met": true or false, "reason": "<what the receiver gets or lacks, at
which lines>"}}, ...]}}, every item of every checklist for every folder. Then reply `Written.`"""

folders = [os.path.abspath(p) for p in sys.argv[1:]]
if not folders:
    sys.exit("usage: judge.py <work folder> [<work folder> ...]")
for folder in folders:
    if not os.path.isfile(os.path.join(folder, ".tasks", "ccs.json")):
        sys.exit(f"{folder} holds no .tasks/ccs.json; give a folder trial.py or baseline.py kept")
out = os.path.join(os.path.dirname(folders[0]), "judged.json")
if os.path.exists(out):
    sys.exit(f"{out} is there already; move it away to judge again")
# Each folder's items, from the checklists its CCS names, to find any the judge left out.
asked = {}
for folder in folders:
    with open(os.path.join(folder, ".tasks", "ccs.json"), encoding="utf-8") as f:
        checklists = shared.entries(json.load(f), "checklist")
    asked[folder] = {
        (c, i) for c in checklists for _, i, _ in shared.items(os.path.join(folder, c))
    }
# The judge runs in a folder of its own, so it starts from none of the runs' folders.
place = tempfile.mkdtemp()
end = shared.claude(PROMPT.format(folders="\n".join(folders), out=out), [], cwd=place)
shutil.rmtree(place)
print("session:", end.get("session_id"), "cost:", end.get("total_cost_usd"))
with open(out, encoding="utf-8") as f:
    judged = json.load(f)
for folder in folders:
    given = judged.get(folder, [])
    met = asked[folder] & {
        (g.get("checklist"), g.get("item")) for g in given if g.get("met") is True
    }
    left = sorted(asked[folder] - {(g.get("checklist"), g.get("item")) for g in given})
    print(
        f"{folder}: {len(met)} of {len(asked[folder])} met"
        + (f"; not judged: {left}" if left else "")
    )
