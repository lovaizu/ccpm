"""Stands in for turn's turn:up in rn's move trials: from the call rn's orchestrator hands turn,
writes what the case set for the call's work as turn's flow leaves it once a run returns, the work's
files and the result, each item's Good at the lines of the work that give it and each choice its
maker made that the CCS left open, and gives the reply
turn:up ends with: `{"returned": "<result>"}`, or the questions it asks the calling AI. Nothing is
made: the work is the case's, so the move judged is the orchestrator's alone.

The trial copies it into the copy of turn's `scripts/`, beside turn's `call.py`, which checks the
call and reads the CCS and the checklists' items as turn does:

    python3 stand.py '<call>'           the stand-in agent's: the next of the replies the case set
                                        for the call's work, in ../stand/replies.json, counted
    python3 stand.py '<call>' '<made>'  the trial's, making a case's state: the made given as JSON

A made is `{"files": {<path>: <text>}, "goods": {<checklist's file name>: {<item>: {"good": ...,
"at": ...}}}, "chosen": [{"chosen": ..., "why": ...}]}`, the path "" standing for the call's first
work, wherever the orchestrator's plan put it, an item left out of goods having no Good, and no
choice where chosen is left out; or `{"questions": [...]}`. `at` is "whole",
or a list of the lines' marks, each the words a line holds, or `<from>..<to>` for the lines from
one holding the first to one holding the second, to the end where it is empty; `in` names the
file, the work's first by default.

Prints `{"line": <the line for the main conversation>, "reply": <the reply>}` and gives 0, or
prints what was wrong and gives 1."""

from __future__ import annotations

import json
import os
import sys
from typing import Any

import call

HERE = os.path.dirname(os.path.abspath(__file__))
REPLIES = os.path.join(os.path.dirname(HERE), "stand", "replies.json")
USAGE = "usage: stand.py '<call>' ['<made>']"


def numbered(path: str, at: Any) -> list[str]:
    """The lines of the file the marks name, each as `<path>:<from>[-<to>]`; stops where a mark is
    on no line."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    if at == "whole":
        return [f"{path}:1-{len(lines)}"]

    def first(words: str, start: int = 0) -> int:
        n = next((k for k in range(start, len(lines)) if words in lines[k]), None)
        if n is None:
            raise call.Stop(f"stand: no line of {path} from {start + 1} holds {words!r}")
        return n + 1

    found = []
    for mark in at:
        start, _, end = mark.partition("..")
        n = first(start)
        if ".." not in mark:
            found.append(f"{path}:{n}")
        else:
            found.append(f"{path}:{n}-{first(end, n) if end else len(lines)}")
    return found


def returned(run: dict[str, Any], made: dict[str, Any]) -> dict[str, str]:
    """Writes the made's files, "" at the call's first work, and the result, in the form turn's
    flow writes it; gives the reply of a run returned."""
    work = run["work"]
    texts = {path or work[0]: text for path, text in made.get("files", {}).items()}
    for path, text in texts.items():
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    items = []
    for item in run["items"]:
        good = made.get("goods", {}).get(os.path.basename(item["checklist"]), {}).get(item["item"])
        if good is not None:
            lines = numbered(good.get("in", work[0]), good["at"])
            items.append(dict(item, good=good["good"], lines=lines))
    result = run["call"]["result"]
    with open(result, "w", encoding="utf-8") as f:
        made_as = {"work": work, "items": items, "chosen": made.get("chosen", [])}
        json.dump(made_as, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return {"returned": result}


def next_made(work: str) -> dict[str, Any]:
    """The next of the replies set for the work, the last again once all are given, each call
    counted in a file beside them; stops where none is set."""
    with open(REPLIES, encoding="utf-8") as f:
        replies = json.load(f).get(work)
    if not replies:
        raise call.Stop(
            f"stand: the case sets no reply for the work {work}; it calls no turn there"
        )
    count = os.path.join(os.path.dirname(REPLIES), f"{work}.count")
    n = 0
    if os.path.exists(count):
        with open(count, encoding="utf-8") as f:
            n = int(f.read())
    with open(count, "w", encoding="utf-8") as f:
        f.write(str(n + 1))
    return replies[min(n, len(replies) - 1)]


def told(run: dict[str, Any], reply: dict[str, Any]) -> str:
    """What the stand-in agent is given for the run: the line turn sends the main conversation and
    the reply turn ends with, as one line of JSON."""
    count = len(run["items"])
    line = (
        "turn: Next, turn:first-user will use the work in the receiver's place and give each item's"
        f" Good, of {', '.join(run['work'])}, for {count} item{'' if count == 1 else 's'}, round 1."
    )
    return json.dumps({"line": line, "reply": reply}, ensure_ascii=False)


def main(argv: list[str]) -> int:
    """Gives the reply to the call, from the made given or set; prints the usage and gives 1 on any
    other arguments."""
    if len(argv) not in (1, 2):
        print(USAGE)
        return 1
    try:
        run = call.laid_out(call.parse(argv[0]))
        work = (call.entries(call.read_ccs(run["call"]["ccs"]), "work") or [""])[0]
        made = json.loads(argv[1]) if len(argv) == 2 else next_made(work)
        reply = {"questions": made["questions"]} if "questions" in made else returned(run, made)
    except call.Stop as stop:
        print(stop)
        return 1
    print(told(run, reply))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
