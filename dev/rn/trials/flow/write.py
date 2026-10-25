"""Stands in for turn's turn:up in rn's flow trial with the stand-in agent, an AI that makes each work
itself from the CCS rn hands turn, as the flow trial's user answers in words no fixture can foresee:
gives the agent what the call asks it to make, then writes the result as turn's flow leaves it once
a run returns, by the move trials' stand.py, which the trial copies beside it.

    python3 write.py '<call>'      the work, the files the CCS gives, and each item to give its
                                   Good, by its checklist's file name, ID and title
    python3 write.py '<call>' -    the made on standard input, `{"goods": ..., "lessons": [...]}`
                                   as stand.py takes it, its files written by the agent already

Prints JSON and gives 0, or prints what was wrong and gives 1."""

from __future__ import annotations

import json
import os
import sys

import call
import stand
import template

USAGE = "usage: write.py '<call>' [-]"


def shown(run: dict) -> dict:
    """What the agent makes the work from: the work, the files given, and each item with its
    title."""
    titles = {}
    for path in run["checklist"]:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        lines = text.splitlines()
        # Each heading's text by its line, of which turn's reading gives the items' lines.
        said = {n: words for n, _, words in template.headings(lines, template.body(lines))}
        for number, item in call.READ_ITEMS(text):
            titles[(path, item)] = said[number][len(f"{item}: ") :]
    items = [
        {
            "checklist": os.path.basename(i["checklist"]),
            "item": i["item"],
            "title": titles.get((i["checklist"], i["item"]), ""),
        }
        for i in run["items"]
    ]
    return {
        "work": run["work"],
        "given": run["given"],
        "checklists": run["checklist"],
        "items": items,
    }


def main(argv: list[str]) -> int:
    """Gives what to make, or the reply once made; prints the usage and gives 1 on any other
    arguments."""
    if len(argv) not in (1, 2) or argv[1:] not in ([], ["-"]):
        print(USAGE)
        return 1
    try:
        run = call.laid_out(call.parse(argv[0]))
        if len(argv) == 1:
            print(json.dumps(shown(run), ensure_ascii=False))
            return 0
        made = json.loads(sys.stdin.read())
        reply = stand.returned(run, {k: made[k] for k in ("goods", "lessons") if k in made})
    except call.Stop as stop:
        print(stop)
        return 1
    except ValueError as wrong:
        print(f"write: the made is not JSON: {wrong}")
        return 1
    print(stand.told(run, reply))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
