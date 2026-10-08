"""Read and write a CCS: the nine components of a task's state, each a list of `type: value` entries.

Only the form pith writes is read: a component at the start of a line, its entries indented as
`  - type: value`, a value as a JSON string, which is also a YAML string.
"""
import json
import re

COMPONENTS = ("episodic_trace", "semantic_gist", "focal_entities", "relational_map", "goal_orientation",
              "constraints", "predictive_cue", "uncertainty_signal", "retrieved_artifacts")
PATH = re.compile(r"[^\s'\"`]+\.yaml")


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
