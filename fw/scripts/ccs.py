"""Read and write a CCS, and read a task's state from the CCS files in its folder.

A CCS holds the nine components of the state of one role's turn, each a list of `type: value`
entries. Only the form fw writes is read: a component at the start of a line, its entries indented
as `  - type: value`, a value as a JSON string, which is also a YAML string.

A task's folder holds one CCS per role: `make.yaml`, `use.yaml` and `learn.yaml`. The hooks record
each turn of a role in its CCS under `retrieved_artifacts`: `turn` when the role is started,
`worked` once it has replied to go, and, for the maker, `made` when the work changed while it
worked. Each is valued `#<n> <the role's JSONL>`, `<n>` counting the turns of the whole task, so
their order is known.
"""
import hashlib
import json
import os
import re

COMPONENTS = ("episodic_trace", "semantic_gist", "focal_entities", "relational_map", "goal_orientation",
              "constraints", "predictive_cue", "uncertainty_signal", "retrieved_artifacts")
ROLES = {"make": "fw:maker", "use": "fw:first-user", "learn": "fw:learner"}
RECORDS = ("turn", "worked", "made")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(path):
    ccs = {c: [] for c in COMPONENTS}
    component = None
    with open(path) as f:
        for line in f:
            head = re.match(r"([a-z_]+):", line)
            entry = re.match(r"\s+- ([a-z_]+): (.*)$", line)
            if head:
                component = head.group(1)
                ccs.setdefault(component, [])
            elif entry and component:
                value = entry.group(2).strip()
                if value.startswith('"'):
                    value = json.loads(value)
                ccs[component].append((entry.group(1), value))
    return ccs


def dump(ccs, path):
    lines = []
    for component, entries in ccs.items():
        lines.append(f"{component}:" + ("" if entries else " []"))
        lines += [f"  - {kind}: {json.dumps(value, ensure_ascii=False)}" for kind, value in entries]
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def first(ccs, component, kind):
    """The first non-empty value of that type, or None."""
    return next((value for k, value in ccs.get(component, []) if k == kind and value), None)


def records(task):
    """Every turn recorded in the task's folder, in order: (n, role, record, JSONL)."""
    found = []
    for role in ROLES:
        path = os.path.join(task, f"{role}.yaml")
        if os.path.isfile(path):
            for kind, value in load(path)["retrieved_artifacts"]:
                number = re.match(r"#(\d+) (.*)", value) if kind in RECORDS else None
                if number:
                    found.append((int(number.group(1)), role, kind, number.group(2)))
    return sorted(found, key=lambda r: (r[0], RECORDS.index(r[2])))


def last(found, role, kind):
    """The number of the role's last record of that kind, or 0."""
    return max((n for n, r, k, _ in found if r == role and k == kind), default=0)


def digest(path):
    """What the work is now, to tell whether a turn changed it."""
    if not os.path.isfile(path):
        return "absent"
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def state(task):
    """The task's state in fw's table, read from the turns recorded in its folder."""
    found = records(task)
    if not found:
        return "fill"
    _, role, kind, _ = found[-1]
    used = last(found, "use", "worked")
    agreed = first(load(os.path.join(task, f"{role}.yaml")), "goal_orientation", "agreed")
    if role == "make":
        if kind == "made":
            return "align-recheck" if used else "align-use"
        if kind == "worked":
            return "fill"
        return "make" if agreed else "align-make"
    if role == "use":
        if kind == "worked":
            return "align-learn"
        phase = "recheck" if used else "use"
        return phase if agreed else f"align-{phase}"
    if kind == "worked":
        return "judge"
    return "learn" if agreed else "align-learn"
