"""Tries rn's prompts one move at a time, as a unit test of them: each case, one move the steps of
rn's skills take, starts from a session state made beforehand by rn's own commands, sends one
message, or more on the same conversation where the move takes more, and checks by script what
the move must leave. The real skills and scripts run, on Opus, which trying.claude names in each
run, with everything but them stood in for: turn's turn:up by an agent giving back what the case
set, `gh` by a script keeping the pull request and the issues in a file, and the user by the
case's messages.

    python3 dev/rn/trials/moves/moves.py <case>... | all [--dry]

Each run makes a folder of its own, `rn/<yyyymmdd>-moves-<random>/` in the system's temporary
folder, outside any ccpm clone, so the conversations load none of its instructions, and prints its
path. Each case runs in a folder of its own in it, side by side with the others: `repo`, a
fresh repository whose origin is the bare repository `origin.git`; `rn` and `turn`, the copies of
this working tree's as installing makes them; `bin/gh` and `gh.json`, the stand-in gh and what it
kept; and `<n>.jsonl`, what Claude Code printed for message n. The trial removes nothing.

Prints, for each case, whether its starting state is what its step expects, each message sent with
the reply and each check of what its move left, whether all passed, the minutes, the cost, and the
records to read the move by against the skills' steps: what Claude Code printed, the conversation's
record and each agent's. With --dry, the state is made and checked and the messages printed, and no
message is sent; the checks of each move are run on the starting state, to show they run.

The cases, each with the steps of rn's skills it covers:
"""

from __future__ import annotations

import concurrent.futures
import contextlib
import glob
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "lane", "trials")
)

import trying
from cases import CASES, Case, Check
from place import DEFAULT_KEPT, RULES, Place, Seen, Stop, costed

USAGE = "usage: python3 dev/rn/trials/moves/moves.py <case>... | all [--dry]"
# The minutes a message waits for the stand-in turn, started in the background.
WAIT = 30
# Every move leaves the default branch as it was, as rn pushes to the session's branch alone.
DEFAULT_CHECK = Check(DEFAULT_KEPT, RULES[DEFAULT_KEPT])


def checked(seen: Seen, checks: list) -> tuple:
    """Each check's line, `ok` or `FAIL` before what it checks, and whether all held."""
    held = [(c.holds(seen), c.what) for c in [*checks, DEFAULT_CHECK]]
    return [f"  {'ok' if h else 'FAIL'} {what}" for h, what in held], all(h for h, _ in held)


def tried(name: str, case: Case, folder: str, dry: bool) -> tuple:
    """Runs the case in its folder; gives its report's lines and whether it passed."""
    start = time.time()
    p = Place(folder)
    report = [f"=== {name}: {case.move}", f"covers: {case.covers}"]
    try:
        p.make(case.replies)
        case.start(p)
    except Stop as stop:
        return report + [f"the starting state could not be made: {stop}"], False
    lines, passed = checked(p.seen(p.head(), ""), case.expects)
    report += ["the starting state:", *lines]
    session, costs = None, {}
    with contextlib.closing(trying.Conversation(p.plugins, p.repo, WAIT, p.env)) as conversation:
        for n, (message, checks) in enumerate(case.messages, 1):
            report.append(f"--- message {n}{', on ' + session if session else ''}: {message}")
            before, record, reply = p.head(), os.path.join(folder, f"{n}.jsonl"), ""
            if dry:
                report.append("  (dry: not sent; the checks below run on the starting state)")
            else:
                try:
                    end = conversation.send(message, record)
                except (SystemExit, OSError, ValueError) as stopped:
                    report.append(f"  stopped: {stopped}")
                    passed = False
                    break
                session = end["session_id"]
                # A conversation gone on with gives the cost of the whole conversation so far.
                costs[session] = end.get("total_cost_usd") or 0
                reply = end.get("result") or ""
                report += ["reply:", *(f"  | {line}" for line in reply.splitlines())]
            lines, held = checked(p.seen(before, reply, "" if dry else record), checks)
            report += lines
            passed = passed and (held or dry)
    verdict = (
        ("the starting state holds" if passed else "the starting state FAILS")
        if dry
        else ("PASSED" if passed else "FAILED")
    )
    report.append(
        f"{verdict}, minutes {round((time.time() - start) / 60, 1)}, cost {costed(costs)}"
    )
    for k in range(1, len(case.messages) + 1):
        if os.path.exists(os.path.join(folder, f"{k}.jsonl")):
            report.append(f"record: {os.path.join(folder, f'{k}.jsonl')}")
    for s in costs:
        report += [f"record: {r}" for r in glob.glob(trying.record.conversation(s))]
        report += [f"record: {r}" for r in sorted(trying.agents(s))]
    return report, passed


def main(argv: list[str]) -> int:
    """Runs the cases argv names in a folder of its own; prints the usage and gives 1 where argv
    names no case or a case not one of CASES."""
    if argv in (["-h"], ["--help"]):
        listed = "\n".join(f"  {n}: {c.move}; {c.covers}" for n, c in CASES.items())
        print(f"{__doc__}{listed}\n\n{USAGE}")
        return 0
    dry = "--dry" in argv
    given = [a for a in argv if a != "--dry"]
    names = list(CASES) if given == ["all"] else given
    unknown = [n for n in names if n not in CASES]
    if not given or unknown:
        print(f"{USAGE}\neach case one of: {', '.join(CASES)}")
        return 1
    place = trying.folder("rn", "moves")
    with concurrent.futures.ThreadPoolExecutor(len(names)) as pool:
        runs = {n: pool.submit(tried, n, CASES[n], os.path.join(place, n), dry) for n in names}
        results = {n: run.result() for n, run in runs.items()}
    for report, _ in results.values():
        print("\n".join(report) + "\n")
    print("passed:", ", ".join(n for n, (_, p) in results.items() if p) or "none")
    print("failed:", ", ".join(n for n, (_, p) in results.items() if not p) or "none")
    return 0 if all(p for _, p in results.values()) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
