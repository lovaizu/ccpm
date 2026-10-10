#!/usr/bin/env python3
"""Writes into the new record what each of turn's agents read, wrote and ran, from the JSONL and
git, not from what the agents say, once, as the turn returns. Usage: trace.py <in> <out>"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "hooks")]

import ccs  # noqa: E402
import transcript  # noqa: E402
from checks import order, returned  # noqa: E402

TOOLS = {"Read": "read", "Write": "wrote", "Edit": "wrote", "NotebookEdit": "wrote"}


def rel(path, cwd):
    """A path in the repository as the repository names it; any other as it is."""
    inside = os.path.isabs(path or "") and os.path.commonpath([path, cwd]) == cwd
    return os.path.relpath(path, cwd) if inside else path


def acts(path, cwd):
    """What the agent read, wrote and ran, in order."""
    out = []
    for e in transcript.entries(path) if os.path.isfile(path) else []:
        for b in transcript.blocks(e):
            if b.get("type") != "tool_use":
                continue
            inp = b.get("input") or {}
            if b.get("name") in TOOLS:
                out.append(f"{TOOLS[b['name']]} {rel(inp.get('file_path') or inp.get('notebook_path'), cwd)}")
            elif b.get("name") == "Bash":
                out.append("ran " + (inp.get("command") or "").strip().split("\n")[0])
    return out


def trace(path, calls, cwd):
    lines, count = [], {}
    for what, aid in calls:
        if what == "made" or not aid:
            continue
        count[what] = count.get(what, 0) + 1
        kind = f"{what}-{count[what]}"
        lines += [(kind, a) for a in acts(transcript.agent_path(path, aid), cwd)]
    status = subprocess.run(["git", "status", "--porcelain"], cwd=cwd, capture_output=True,
                            text=True).stdout
    lines += [("git", "uncommitted " + l[3:]) for l in status.splitlines()]
    return lines


def main(argv):
    if len(argv) != 3:
        print("usage: trace.py <in> <out>", file=sys.stderr)
        return 2
    cwd = os.getcwd()
    path = transcript.session_path()
    if not path:
        print("turn: this conversation's JSONL was not found from CLAUDE_CODE_SESSION_ID",
              file=sys.stderr)
        return 2
    items = transcript.entries(path)
    start, _ = transcript.last_turn(items)
    calls = transcript.calls(items, start) if start is not None else []
    handed = ccs.load(ccs.read(argv[1]))
    parts = ccs.load(ccs.read(argv[2]))
    problems = returned.check(handed, parts)
    if ccs.values(parts, "predictive_cue", "next") == ["done"]:
        problems += order.check([w for w, a in calls], "done")
    if problems:
        print("turn check:\n- " + "\n- ".join(problems), file=sys.stderr)
        return 2
    before = [i for name, items_ in handed if name == "episodic_trace" for i in items_]
    parts = [p for p in parts if p[0] != "episodic_trace"]
    parts.append(("episodic_trace", before + trace(path, calls, cwd)))
    with open(argv[2], "w") as f:
        f.write(ccs.dump(parts))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
