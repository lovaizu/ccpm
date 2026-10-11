"""Checks the form of a CCS when turn receives one and when it returns one.

    python3 check.py in <in> <out>
    python3 check.py out <in> <out>

Prints what does not match and exits 1; prints nothing and exits 0 when the CCS holds.
"""
import json
import os
import re
import sys

import tryout

# The kinds each part may hold. episodic_trace holds an agent and its round, git, or the evidence.
KINDS = {
    "focal_entities": {"deliverable", "receiver"},
    "goal_orientation": {"acceptance", "use"},
    "retrieved_artifacts": {"viewpoint", "source"},
    "constraints": {"language", "rule", "answer"},
    "predictive_cue": {"next"},
    "uncertainty_signal": {"gap"},
    "semantic_gist": {"difference"},
    "relational_map": {"link"},
    "episodic_trace": set(),
}
TRACE = re.compile(r"^(generator|first-user|learner|evaluator)-[1-9][0-9]*$|^git$|^evidence$")
REQUIRED = [
    ("focal_entities", "deliverable"),
    ("focal_entities", "receiver"),
    ("goal_orientation", "acceptance"),
    ("retrieved_artifacts", "viewpoint"),
]
KEPT = ["focal_entities", "goal_orientation", "retrieved_artifacts"]
NEXT = re.compile(r"^(done|ask the user|to the caller: .+|stopped: .+)$")


def load(path):
    """The CCS at path, or a string saying why it cannot be read."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        return f"{path}: cannot be read as JSON ({e})"


def form(ccs):
    """What does not match the tables in the README."""
    if not isinstance(ccs, dict):
        return ["the CCS is not a JSON object"]
    out = []
    for part in sorted(set(KINDS) - set(ccs)):
        out.append(f"part {part} is missing")
    for part in sorted(set(ccs) - set(KINDS)):
        out.append(f"part {part} is not one of the nine")
    for part in sorted(set(ccs) & set(KINDS)):
        entries = ccs[part]
        if not isinstance(entries, list):
            out.append(f"{part} is not a list")
            continue
        for e in entries:
            if not (isinstance(e, dict) and len(e) == 1):
                out.append(f"{part}: {json.dumps(e)} is not one {{\"kind\": \"value\"}}")
                continue
            (kind, value), = e.items()
            if not (kind in KINDS[part] or (part == "episodic_trace" and TRACE.match(kind))):
                out.append(f"{part}: kind {kind} is not in the tables")
            if not isinstance(value, str):
                out.append(f"{part}: the value of {kind} is not a string")
    return out


def values(ccs, part, kind):
    return [v for e in ccs[part] for k, v in e.items() if k == kind]


def places(ccs, repo):
    """What does not match in the places the CCS points to."""
    out = []
    for kind in ("viewpoint", "source"):
        for v in values(ccs, "retrieved_artifacts", kind):
            if not os.path.exists(os.path.join(repo, v)):
                out.append(f"{kind} {v} does not exist")
    for v in values(ccs, "focal_entities", "deliverable"):
        inside = os.path.realpath(os.path.join(repo, v))
        if os.path.isabs(v) or os.path.commonpath([repo, inside]) != repo:
            out.append(f"deliverable {v} is not a path inside the repository")
    return out


def received(ccs, repo, out_path):
    problems = form(ccs)
    if problems:
        return problems
    for part, kind in REQUIRED:
        if not values(ccs, part, kind):
            problems.append(f"{part} has no {kind}")
    problems += places(ccs, repo)
    if os.path.exists(out_path):
        problems.append(f"{out_path} already exists")
    return problems


def returned(given, ccs):
    """What does not match in the CCS to return, against the one received, which passed received."""
    problems = form(ccs)
    if problems:
        return problems
    for part in KEPT:
        if ccs[part] != given[part]:
            problems.append(f"{part} is not as received")
    before = given["constraints"]
    if ccs["constraints"][: len(before)] != before:
        problems.append("constraints does not keep its received lines first")
    nexts = values(ccs, "predictive_cue", "next")
    if len(nexts) != 1 or not NEXT.match(nexts[0]):
        problems.append("predictive_cue needs exactly one next of: done, ask the user, "
                        "to the caller: <reason>, stopped: <where from>")
    return problems


def main(argv):
    if len(argv) != 4 or argv[1] not in ("in", "out"):
        print(__doc__.strip())
        return 2
    _, mode, in_path, out_path = argv
    repo = tryout.top()
    if not repo:
        print("not inside a git repository")
        return 1
    given = load(in_path)
    if isinstance(given, str):
        print(given)
        return 1
    if mode == "in":
        problems = received(given, repo, out_path)
    else:
        ccs = load(out_path)
        problems = [ccs] if isinstance(ccs, str) else returned(given, ccs)
    for p in problems:
        print(p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
