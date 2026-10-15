"""Check 6: a stop commit leaves in open/ only what its kind allows; at a sign-off the latest
default branch is merged, and the proposal is in the form the proposal checklist gives: the map,
the goal, what it is judged by, how close the work is to every attractive criterion, and what was
decided for the user."""

import re
import subprocess
from itertools import takewhile

from record import criteria, git, last_line, open_items, steering

CLOSENESS = "Toward what you would choose it for:"
PARTS = (
    ("── ", "map line `── {slug}: {the goal} ──`"),
    ("Goal:", "`Goal:`"),
    ("Judged by:", "`Judged by:`"),
    (CLOSENESS, f"`{CLOSENESS}`"),
    ("Decided for you", "`Decided for you`"),
)


def closeness(lines):
    """The criterion IDs the proposal's `Toward what you would choose it for:` lines, the bullets
    right under that heading, say how close the work is to."""
    after = lines[lines.index(CLOSENESS) + 1 :]
    bullets = takewhile(lambda line: line.startswith("- "), after)
    return {m.group(1) for m in map(re.compile(r"^- ([A-Z]\d+):").match, bullets) if m}


def proposal(msg, attractive):
    problems = []
    lines = msg.splitlines()
    for mark, name in PARTS:
        if not any(line.startswith(mark) for line in lines):
            problems.append(
                f"stop at a sign-off: the proposal lacks its {name}, so the user cannot decide "
                "from it alone"
            )
    missing = sorted(set(attractive) - closeness(lines)) if CLOSENESS in lines else []
    if missing:
        problems.append(
            "stop at a sign-off: under `Toward what you would choose it for:` the proposal does "
            f"not say how close the work is to {', '.join(missing)}, by which the user decides "
            "when it is close enough"
        )
    return problems


def check(top, sdir, msg):
    problems = []
    last = last_line(msg)
    names = open_items(sdir)
    kinds = [n.split("-")[1] for n in names if n.count("-") >= 2]
    if "waiting for #" in last or "── approved →" in last:
        bad = [n for n, k in zip(names, kinds) if k != "notes" or "proposal" in n]
        if bad:
            problems.append(
                "stop at a sign-off: open/ must hold only notes, since the user approves the "
                "whole with nothing found about it left unsettled; not " + ", ".join(bad)
            )
        if "waiting for #" in last:
            problems += proposal(msg, [c for c in criteria(steering(sdir)) if c.startswith("A")])
            head = git("rev-parse", "--abbrev-ref", "origin/HEAD", cwd=top).strip()
            if (
                head
                and subprocess.run(
                    ["git", "merge-base", "--is-ancestor", head, "HEAD"], check=False, cwd=top
                ).returncode
                != 0
            ):
                problems.append(
                    f"stop at a sign-off: {head} is not merged into the branch, so the user "
                    "would approve work on files the default branch no longer has"
                )
    if "── feedback in " in last and "feedback" not in kinds:
        problems.append(
            "stop after /rn:gm: open/ holds no feedback item, so the user's words would be lost "
            "to the next conversation"
        )
    return problems
