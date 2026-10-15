"""The content file's place in a session, and the task rn hands turn, written in the form turn's
callers' page gives, so it is the same on every call."""

import argparse
import json
import os

from checklists import Stop

USAGE = (
    "usage: up.py task <session folder> --deliverable <path> [<path> ...] --receiver <who> "
    "[--use <what for>] --acceptance <what they can do> --checklist <path> [<path> ...] "
    "--content <path> [--reference <path> ...] [--opens <path> ...] [--language <language>]"
)


def inside(path):
    if os.path.isabs(path) or os.path.normpath(path).startswith(".."):
        raise Stop(f"{path} is outside the repository; name a path from its top")
    return os.path.normpath(path)


def content(session, document):
    """Prints where the content file of the document goes in the session: by the document's folder
    and name, so it is found from the document's path and not taken for the document."""
    stem = os.path.splitext(inside(document))[0]
    print(os.path.join(session, "content", f"{stem}.content.md"))


def task(session, *args):
    """Writes the task as a CCS in the session's tasks/, and prints the two lines turn is called
    with."""
    parser = argparse.ArgumentParser(usage=USAGE[len("usage: ") :], add_help=False)
    for name, nargs in (
        ("deliverable", "+"),
        ("checklist", "+"),
        ("reference", "*"),
        ("opens", "*"),
    ):
        # Given twice, the flag adds to what it was given before.
        parser.add_argument(
            f"--{name}", nargs=nargs, action="extend", default=[], required=nargs == "+"
        )
    for name in ("receiver", "acceptance", "content"):
        parser.add_argument(f"--{name}", required=True)
    for name in ("use", "language"):
        parser.add_argument(f"--{name}", default="")
    try:
        got = parser.parse_args(args)
    except SystemExit:
        raise Stop(USAGE)
    gone = [
        f"{p} does not exist; name it by its path from the top of the repository"
        for p in got.checklist + [got.content] + got.reference + got.opens
        if not os.path.exists(p)
    ]
    if gone:
        raise Stop("\n".join(gone))
    tasks = os.path.join(session, "tasks")
    stem = os.path.splitext(os.path.basename(got.deliverable[0]))[0]
    n = 1
    while os.path.exists(os.path.join(tasks, f"{stem}-{n}.json")):
        n += 1
    given, back = (os.path.join(tasks, f"{stem}-{n}{e}.json") for e in ("", ".back"))
    ccs = {
        "focal_entities": [{"deliverable": inside(d)} for d in got.deliverable]
        + [{"receiver": got.receiver}],
        "goal_orientation": ([{"use": got.use}] if got.use else [])
        + [{"acceptance": got.acceptance}],
        "retrieved_artifacts": [{"checklist": p} for p in got.checklist]
        + [{"content": got.content}]
        + [{"reference": p} for p in got.reference]
        + [{"receiver_opens": p} for p in got.opens],
        "constraints": [{"language": got.language}] if got.language else [],
        "predictive_cue": [],
        "uncertainty_signal": [],
        "semantic_gist": [],
        "relational_map": [],
        "episodic_trace": [],
    }
    os.makedirs(tasks, exist_ok=True)
    with open(given, "w") as f:
        json.dump(ccs, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"in: {given}\nout: {back}")
