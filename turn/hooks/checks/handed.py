"""The record handed in has what turn cannot start without, and the record to write is new, since a
record once written is never rewritten."""
import os

import ccs


def check(args, cwd):
    path = os.path.join(cwd, args.get("in", ""))
    if not args.get("in") or not os.path.isfile(path):
        return [f"in: no record at `{args.get('in', '')}`; turn:up needs `in:` naming the task's record"]
    try:
        parts = ccs.load(ccs.read(path))
    except ccs.Bad as e:
        return [f"in: {e}"]
    problems = [f"in: `{m}` is missing; return to the caller, which writes it"
                for m in ccs.missing(parts)]
    if not args.get("out"):
        problems.append("turn:up needs `out:` naming where the new record goes")
    elif os.path.exists(os.path.join(cwd, args["out"])):
        problems.append(f"out: `{args['out']}` exists, and a record is never rewritten; "
                        "return to the caller for a new path")
    return problems
