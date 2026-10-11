"""Keep the learner and the evaluator running until their output is in form, each learning and judgment names
steps or deliverable lines that exist, each point judged is one of what the deliverable should be, and every
acceptance criterion is judged."""
import json
import os

import assemble


def steps(work, name):
    path = os.path.join(work, f"steps-{name}.json")
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def line_of(line, path):
    if not (line.isdigit() and os.path.isfile(path)):
        return False
    with open(path, encoding="utf-8", errors="replace") as f:
        return 1 <= int(line) <= len(f.read().splitlines())


def wrong(ground, t):
    """Why the ground does not exist, or None when it does."""
    if ":" in ground and "#" not in ground:
        place, line = ground.rsplit(":", 1)
        deliverable = t["deliverable"].rstrip("/")
        inside = place == deliverable or place.startswith(deliverable + "/")
        if inside and line_of(line, os.path.join(t["repo"], place)):
            return None
        return f"{ground} is not a line of the deliverable"
    name, _, k = ground.rpartition("#")
    if name and k.isdigit() and 1 <= int(k) <= len(steps(t["work"], name)):
        return None
    return f"{ground} is not a step"


def not_a_point(point, t):
    """Why the point is not one of what the deliverable should be, or None when it is. Each round names a point
    the same way, so that whether a remake brought the deliverable closer can be told point by point."""
    if point in t["acceptance"]:
        return None
    place, _, line = point.rpartition(":")
    for written, path in zip(t["viewpoints_as_written"], t["viewpoints"]):
        if place == written and line_of(line, path):
            return None
    return f"{point} is neither an acceptance criterion as written nor a line of a viewpoint file"


FORM = {
    "learner": '{"learnings": [{"learning": "...", "grounds": ["first-user-1#3", "SETUP.md:12"]}]}',
    "evaluator": ('{"points": [{"point": "<an acceptance criterion as written, or <viewpoint file>:<line>>", '
                  '"judgment": "good" | "more" | "unsettled", "fell_short": "<on a More>", '
                  '"why": "<on an unsettled point>", "question": "<only on an unsettled point only the user can '
                  'settle>", "grounds": ["first-user-1#3", "SETUP.md:12"]}]}'),
}


def check(data, t):
    role = data["agent_type"].split(":", 1)[1]
    if role not in FORM:
        return []
    path = os.path.join(t["work"], f"{role}-{t['round']}.json")
    entries = assemble.learnings(path) if role == "learner" else assemble.judgments(path)
    if entries is None:
        return [f"{path} is not in the form to write: {FORM[role]}"]
    named = [g for e in entries for g in e["grounds"]]
    out = [w for w in (wrong(g, t) for g in dict.fromkeys(named)) if w]
    if role == "evaluator":
        judged = dict.fromkeys(e["point"] for e in entries)
        out += [w for w in (not_a_point(p, t) for p in judged) if w]
        # A script cannot list a viewpoint file's points, so only the acceptance criteria are checked for a judgment.
        out += [f"{a} is an acceptance criterion with no judgment" for a in t["acceptance"] if a not in judged]
    return out
