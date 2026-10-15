"""What the user sees of a run as it goes: the plan, its aim and its steps."""

import os

from ccs import entries
from forms import check, without_good
from questions import question_faults
from state import Stop, read_json, the_work, write_json

PLAN = "Plan: 1 write → 2 read → 3 check"
INDENT = " " * 12


def aim(work, text):
    """Sets what the work will let its receiver do; the console shows it before the work is
    written."""
    with open(os.path.join(work, "aim.txt"), "w") as f:
        f.write(text)


def shown_lines(work):
    """Every line the console has for the run as it stands, each with a key it is shown once by."""
    run, ccs, _, path = the_work(work, written=False)
    receiver = "; ".join(entries(ccs, "focal_entities", "receiver"))
    said = [PLAN, ""]
    if os.path.isfile(os.path.join(work, "aim.txt")):
        with open(os.path.join(work, "aim.txt")) as f:
            said.append(f"  1 write   To make: {f.read().strip()}")
    if os.path.isfile(os.path.join(work, "first-user-brief.json")):
        said.append(
            f"  2 read    {'Read again, as' if run.get('second') else 'Read as'} {receiver}."
        )
    if os.path.isfile(path) and not check(work, "orchestrator"):
        if not without_good(work):
            said.append("  3 check   ✅ Nothing missing.")
        elif read_json(os.path.join(work, "learner.json"), "the form") and not check(
            work, "learner"
        ):
            aims = dict.fromkeys(
                p["aim"] for p in read_json(os.path.join(work, "learner.json"), "the form").values()
            )
            said += [
                ("  3 check   " if k == 0 else INDENT) + f"⚠️ Not yet: {a}"
                for k, a in enumerate(aims)
            ]
    return [(f"{k}:{line}", line) for k, line in enumerate(said)]


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
