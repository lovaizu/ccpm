"""Stands in for turn's flow in rn's conductor flow trial, as its generator alone: from the call rn's
conductor hands turn:up, gives the stand-in agent the line it sends the main conversation and what
it makes the work from, then takes the agent's claim, each item's Good with the lines that give it,
in turn's claim form, as turn's result, so the conductor reads a result it can check at its lines,
as it does once the real turn returns.

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

# The work a CCS is of, named by the CCS's file, `ccs/<work>.json`, as rn.py writes it: the finished
# work is left as it is, and any other work made from its decisions in its checklist's template.
FINISHED = "deliverable"
# The CCS entry naming the work's decisions, as rn.py writes it.
DECISIONS = "decisions"
F1 = "### F-1: "
CHECKED = "Read the work at each Good's lines against its item."
USAGE = "usage: stand.py given '<call>'\n       stand.py result '<call>' < <claim>"


def work_of(run: dict[str, Any]) -> str:
    """The name of the work the call is for, from its CCS's file name."""
    return os.path.splitext(os.path.basename(run["call"]["ccs"]))[0]


def template(checklists: list[str]) -> str:
    """The template in the fence under F-1 of the first checklist holding one, as each of rn's
    checklists sets its work's; "" where none holds one."""
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
    paths, its decisions, whether it makes the work, `write`, or leaves it, `none`, the checklists
    whose items it claims, the items asked of each part, and the template the work is written in."""
    decisions = call.entries(call.read_ccs(run["call"]["ccs"]), DECISIONS)
    return {
        "line": f"turn: Next, turn:up will make the work and give every item its Good, of"
        f" {', '.join(run['work'])}, for {len(run['items'])} items, round 1.",
        "work": run["work"],
        "decisions": decisions[0] if decisions else "",
        "make": "none" if work_of(run) == FINISHED else "write",
        "checklists": run["checklist"],
        "each": [f"{i['checklist']} {i['item']}" for i in run["each"]],
        "template": template(run["checklist"]),
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
    """Writes turn's result for the call from the claim, every item with its Good at its lines and
    no lesson; gives `{"returned": <result>}` as turn:up replies it. Stops where the claim is not in
    turn's claim form, saying each thing to give instead."""
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
