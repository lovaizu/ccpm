"""Stands in for turn's flow in rn's flow trial, as its generator alone: from the call rn's
orchestrator hands turn:up, gives the stand-in agent the line it sends the main conversation and what
it makes the work from, then takes the agent's claim, each item's Good with the lines that give it,
in turn's claim form, as turn's result, so the orchestrator reads a result it can check at its
lines, as it does once the real turn returns.

The trial copies it into the copy of turn's `scripts/`, beside turn's `call.py` and `forms.py`, which
read the call, the CCS, the checklists and the parts of the work and check the claim as turn does:

    python3 stand.py given '<call>'
    python3 stand.py result '<call>' < <claim>

Prints JSON and gives 0, or prints what was wrong and what to do and gives 1."""

from __future__ import annotations

import json
import os
import sys
from typing import Any

import call
import forms

# The CCS entries rn.py writes that name the work, the stage it is made in, each of its decisions as
# `<title>: <what it says>`, and the goal and each criterion it serves, each as one line.
WORK = "work"
STAGE = "stage"
DECISION = "decision"
SERVES = "serves"
# The finished work is left as it is; any other work is made from its decisions.
FINISHED = "deliverable"
# The plan's call makes the part of the steering from its title to its tasks, so its template is the
# plan checklist's cut from the title to the learnings, as rn's scripts write the rest.
PLAN = "plan"
TITLE = "# "
LEARNINGS = "## Learnings"
F1 = "### F-1: "
FENCE = "```"
CHECKED = "Read the work at each Good's lines against its item."
USAGE = "usage: stand.py given '<call>'\n       stand.py result '<call>' < <claim>"


def template(checklists: list[str], work: str) -> str:
    """The template in the fence under F-1 of the first checklist holding one, closed by a fence of
    the same marks, as each of rn's checklists sets its work's, cut to the plan's part for the plan;
    "" where none holds one."""
    for path in checklists:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
        heading = next((n for n, line in enumerate(lines) if line.startswith(F1)), None)
        if heading is None:
            continue
        opening = next((n for n in range(heading, len(lines)) if lines[n].startswith(FENCE)), None)
        if opening is None:
            continue
        marks = lines[opening][: len(lines[opening]) - len(lines[opening].lstrip("`"))]
        closing = next((n for n in range(opening + 1, len(lines)) if lines[n] == marks), None)
        if closing is None:
            continue
        shape = lines[opening + 1 : closing]
        if work == PLAN:
            start = next((n for n, line in enumerate(shape) if line.startswith(TITLE)), 0)
            end = next((n for n, line in enumerate(shape) if line == LEARNINGS), len(shape))
            shape = shape[start:end]
        return "\n".join(shape).strip("\n")
    return ""


def given(run: dict[str, Any]) -> dict[str, Any]:
    """What the stand-in agent is given: the `turn:` line it sends the main conversation, the work's
    name, paths and stage, its decisions and what it serves, whether it makes the work, `write`, or
    leaves it, `none`, the checklists whose items it claims, what the receiver has, the items asked
    of each part, and the template the work is written in."""
    ccs = call.read_ccs(run["call"]["ccs"])
    work = (call.entries(ccs, WORK) or [""])[0]
    return {
        "line": f"turn: Next, turn:up will make the work and give every item its Good, of"
        f" {', '.join(run['work'])}, for {len(run['items'])} items, round 1.",
        "name": work,
        "work": run["work"],
        "stage": (call.entries(ccs, STAGE) or [""])[0],
        "decisions": call.entries(ccs, DECISION),
        "serves": call.entries(ccs, SERVES),
        "make": "none" if work == FINISHED else "write",
        "checklists": run["checklist"],
        "has": run["has"],
        "each": [f"{i['checklist']} {i['item']}" for i in run["each"]],
        "template": template(run["checklist"], work),
    }


def spread(claim: Any, run: dict[str, Any]) -> Any:
    """The claim with each item asked of each part given one Good, `good` alone, spread over every
    part of the work at the part's own lines, as turn's claim form takes it."""
    if not isinstance(claim, dict) or not isinstance(claim.get("items"), list):
        return claim
    each = [forms.key_of(i) for i in run["each"]]
    spread_items = []
    for item in claim["items"]:
        named = isinstance(item, dict) and isinstance(item.get("checklist"), str)
        if named and forms.key_of(item) in each and set(item) == {"checklist", "item", "good"}:
            parts = [
                {"part": p, "good": item["good"], "lines": [p]} for p in forms.parts(run["work"])
            ]
            item = {"checklist": item["checklist"], "item": item["item"], "parts": parts}
        spread_items.append(item)
    return dict(claim, items=spread_items)


def result(run: dict[str, Any], text: str) -> dict[str, str]:
    """Writes turn's result for the call from the claim, in the form turn's flow writes it, every
    item with its Good at its lines and no lesson; gives `{"returned": <result>}` as turn:up replies
    it. Stops where the claim is not in turn's claim form, saying each thing to give instead."""
    try:
        claim = spread(json.loads(forms.unfenced(text)), run)
    except json.JSONDecodeError:
        claim = None
    said = forms.check(
        json.dumps(claim),
        run["items"],
        run["work"],
        forms.CLAIM,
        each=[(i["checklist"], i["item"]) for i in run["each"]],
    )
    if claim is not None and claim.get("questions"):
        said.append('give "questions" as []: every item is given its Good here')
    if said or claim is None:
        raise call.Stop("stand: the claim is not yet in its form:\n- " + "\n- ".join(said))
    path = run["call"]["result"]
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        kept = {"work": run["work"], "items": claim["items"], "lessons": [], "checked": CHECKED}
        json.dump(kept, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return {"returned": path}


def main(argv: list[str]) -> int:
    """Runs `given` or `result` on the call, `result` on the claim read from stdin; prints the usage
    and gives 1 on any other arguments."""
    if len(argv) != 2 or argv[0] not in ("given", "result"):
        print(USAGE)
        return 1
    try:
        run = call.check(call.parse(argv[1]))
        out = given(run) if argv[0] == "given" else result(run, sys.stdin.read())
        print(json.dumps(out, ensure_ascii=False))
    except call.Stop as stop:
        print(stop)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
