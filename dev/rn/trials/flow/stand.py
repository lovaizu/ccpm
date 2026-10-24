"""Stands in for turn's flow in rn's conductor flow trial: from the call rn's conductor hands turn:up,
gives the stand-in agent the line it sends the main conversation and what it makes, then writes
turn's result for the work it made, every item of every checklist the CCS names with a Good at the
work's first line, or at each part's first line for an item asked of each part, and no lesson, so
the conductor goes on as it does once the real turn returns.

The trial copies it into the copy of turn's `scripts/`, beside turn's `call.py` and `forms.py`, which
read the call, the CCS, the checklists and the parts of the work as turn does:

    python3 stand.py given '<call>'
    python3 stand.py result '<call>'

Prints JSON and gives 0, or prints what was wrong and what to do and gives 1."""

from __future__ import annotations

import json
import os
import sys
from typing import Any

import call
import forms

# The work a CCS is of, named by the CCS's file, `ccs/<work>.json`, as rn.py writes it: the plan is
# written in the template of its checklist's F-1, the finished work left as it is, and any other
# work written as a few lines saying what its decisions say.
PLAN = "plan"
FINISHED = "deliverable"
MAKES = {PLAN: "plan", FINISHED: "none"}
# The CCS entry naming the work's decisions, as rn.py writes it.
DECISIONS = "decisions"
F1 = "### F-1: "
USAGE = "usage: stand.py given '<call>'\n       stand.py result '<call>'"


def work_of(run: dict[str, Any]) -> str:
    """The name of the work the call is for, from its CCS's file name."""
    return os.path.splitext(os.path.basename(run["call"]["ccs"]))[0]


def template(checklists: list[str]) -> str:
    """The template in the fence under F-1 of the first checklist holding one, as rn's plan
    checklist sets the plan's; "" where none holds one."""
    for path in checklists:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
        heading = next((n for n, line in enumerate(lines) if line.startswith(F1)), None)
        if heading is None:
            continue
        fences = [n for n in range(heading, len(lines)) if lines[n].startswith("```")]
        if len(fences) >= 2:
            return "\n".join(lines[fences[0] + 1 : fences[1]])
    return ""


def given(run: dict[str, Any]) -> dict[str, Any]:
    """What the stand-in agent is given: the `turn:` line it sends the main conversation, the work's
    paths, its decisions, what it makes, `plan`, `lines` or `none`, and for the plan the template it
    is written in."""
    work = work_of(run)
    decisions = call.entries(call.read_ccs(run["call"]["ccs"]), DECISIONS)
    out: dict[str, Any] = {
        "line": f"turn: Next, turn:up will make the work and give every item its Good, of"
        f" {', '.join(run['work'])}, for {len(run['items'])} items, round 1.",
        "work": run["work"],
        "decisions": decisions[0] if decisions else "",
        "make": MAKES.get(work, "lines"),
    }
    if work == PLAN:
        out["template"] = template(run["checklist"])
    return out


def first_line(part: str) -> str:
    """The first line of a part, `<path>:<from>-<to>`, as `<path>:<from>`."""
    path, _, span = part.rpartition(":")
    return f"{path}:{span.partition('-')[0]}"


def result(run: dict[str, Any]) -> dict[str, str]:
    """Writes turn's result for the call, every item Good at the work's first line, or at each
    part's for an item asked of each part, with no lesson; gives `{"returned": <result>}` as
    turn:up replies it. Stops where a file of the work is not there or empty, as a Good names a
    line of it."""
    for path in run["work"]:
        if not os.path.isfile(path) or os.path.getsize(path) == 0:
            raise call.Stop(f"stand: {path} is not there or empty; write the work there first")
    each = [forms.key_of(i) for i in run["each"]]
    good = "Given at this line, as the trial's stand-in for turn sets every item."
    items: list[dict[str, Any]] = []
    for item in run["items"]:
        if forms.key_of(item) in each:
            parts = [
                {"part": p, "good": good, "lines": [first_line(p)]}
                for p in forms.parts(run["work"])
            ]
            items.append(dict(item, parts=parts))
        else:
            items.append(dict(item, good=good, lines=[f"{run['work'][0]}:1"]))
    path = run["call"]["result"]
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        kept = {"work": run["work"], "items": items, "lessons": [], "checked": "no run: a stand-in"}
        json.dump(kept, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return {"returned": path}


def main(argv: list[str]) -> int:
    """Runs `given` or `result` on the call; prints the usage and gives 1 on any other arguments."""
    steps = {"given": given, "result": result}
    if len(argv) != 2 or argv[0] not in steps:
        print(USAGE)
        return 1
    try:
        print(json.dumps(steps[argv[0]](call.check(call.parse(argv[1]))), ensure_ascii=False))
    except call.Stop as stop:
        print(stop)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
