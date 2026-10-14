"""What every part of writ:up shares: a command's end with its reason, and the job's files."""

import json
import os

JOB = os.path.join(".writ", "job.json")


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
