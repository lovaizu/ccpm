"""What the user sees of a run as it goes: the plan, each round's aim and steps, and the questions."""

import os

from ccs import entries
from forms import check, without_good
from questions import asked, question_faults
from state import RUN, Stop, read_json, the_work, write_json

PLAN = "Plan: 1 write → 2 read → 3 check   (once more if something is missing; two rounds at most)"
INDENT = " " * 12


def aim(work, n, text):
    """Sets what round n's work will let its receiver do; the console shows it before the work is
    written."""
    if int(n) != read_json(RUN, RUN)["round"]:
        raise Stop(f"round {read_json(RUN, RUN)['round']} is running")
    with open(os.path.join(work, str(n), "aim.txt"), "w") as f:
        f.write(text)


def shown_lines(work):
    """Every line the console has for the run as it stands, each with a key it is shown once by."""
    _, ccs, _, _ = the_work(work, 1, written=False)
    receiver = "; ".join(entries(ccs, "focal_entities", "receiver"))
    lines = [("plan", PLAN)]
    for n in (1, 2):
        here = os.path.join(work, str(n))
        if not os.path.isdir(here):
            continue
        said = [f"Round {n}"]
        if os.path.isfile(os.path.join(here, "aim.txt")):
            with open(os.path.join(here, "aim.txt")) as f:
                said.append(f"  1 write   To make: {f.read().strip()}")
        if os.path.isfile(os.path.join(here, "first-user-brief.json")):
            said += [INDENT + the_work(work, n)[3],
                     f"  2 read    {'Read as' if n == 1 else 'Read again, as'} {receiver}."]
        if not os.path.isfile(the_work(work, n, written=False)[3]):
            lines += [(f"{n}:{line}", line) for line in said]
            continue
        reading = read_json(os.path.join(here, "first-user.json"), "the form")
        if reading and not check(work, n, "first-user"):
            said.append(INDENT + os.path.join(here, "first-user.json"))
        if not check(work, n, "orchestrator"):
            if not without_good(work, n):
                said.append("  3 check   ✅ Nothing missing.")
            elif read_json(os.path.join(here, "learner.json"), "the form") and not check(work, n, "learner"):
                aims = dict.fromkeys(p["aim"] for p in read_json(os.path.join(here, "learner.json"), "the form").values())
                said += [("  3 check   " if k == 0 else INDENT) + f"⚠️ Not yet: {a}" for k, a in enumerate(aims)]
        lines += [(f"{n}:{line}", line) for line in said]
    if os.path.isfile(os.path.join(work, "1", "aim.txt")):
        lines += [(f"q:{q['question']}", f"{INDENT}❓ {q['question']}") for q in asked(work) if q.get("ask")]
    return lines


def console(work):
    """Each line of the console not yet shown, now marked shown."""
    found = question_faults(work, decided=False)
    if found:
        raise Stop("\n".join(found))
    record = os.path.join(work, "console.json")
    shown = read_json(record, "the console") if os.path.isfile(record) else []
    new = [(key, line) for key, line in shown_lines(work) if key not in shown]
    write_json(record, shown + [key for key, _ in new])
    return [line for _, line in new]
