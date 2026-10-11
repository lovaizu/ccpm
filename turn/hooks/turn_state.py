"""The turn running in a session, as the hooks need it: where its work is and what it was handed."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))

import tryout  # noqa: E402
from check import values  # noqa: E402


def files(path):
    """The files at path: itself, or every file under it."""
    if os.path.isfile(path):
        return [path]
    return sorted(os.path.join(d, n) for d, dirs, names in os.walk(path)
                  for n in names if ".git" not in os.path.relpath(d, path).split(os.sep))


def of(session):
    """The turn of this session, or None when none is running."""
    work = tryout.work_folder(session)
    try:
        with open(os.path.join(work, "turn.json"), encoding="utf-8") as f:
            s = json.load(f)
        with open(s["in"], encoding="utf-8") as f:
            ccs = json.load(f)
    except (OSError, ValueError):
        return None
    repo = s["repo"]
    place = lambda v: v if os.path.isabs(v) else os.path.join(repo, v)  # noqa: E731
    return {"work": work, "round": s["round"], "repo": repo, "copy": s["copy"],
            "deliverable": values(ccs, "focal_entities", "deliverable")[0],
            "acceptance": values(ccs, "goal_orientation", "acceptance"),
            "viewpoints": [place(v) for v in values(ccs, "retrieved_artifacts", "viewpoint")],
            "viewpoints_as_written": values(ccs, "retrieved_artifacts", "viewpoint"),
            "sources": [f for v in values(ccs, "retrieved_artifacts", "source") for f in files(place(v))]}
