"""What every part of turn:up shares: a command's end with its reason, the run's file and the work it
makes."""

import json
import os

from ccs import entries

RUN = os.path.join(".turn", "run.json")
CLOSING = "closing.txt"


class Stop(Exception):
    """Ends the command, saying why."""


def read_json(path, name):
    try:
        with open(path) as f:
            return json.load(f)
    except ValueError:
        raise Stop(f"{name} is not JSON")


def write_json(path, value):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(value, f, indent=1, ensure_ascii=False)
        f.write("\n")


def the_work(work, written=True):
    """The run's CCS as received, and the path of the work it makes."""
    run = read_json(RUN, RUN)
    ccs = read_json(run["in"], run["in"])
    deliverable = entries(ccs, "focal_entities", "deliverable")[0]
    path = os.path.join(work, os.path.basename(deliverable))
    if written and not os.path.isfile(path):
        raise Stop(f"{path} is not written")
    return run, ccs, deliverable, path
