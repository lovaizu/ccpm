"""The CCS, the form the callers' page gives, and the checklists it names."""

import os
import re

PARTS = {
    "focal_entities": {"deliverable", "receiver"},
    "goal_orientation": {"use", "acceptance"},
    "retrieved_artifacts": {"checklist", "decisions", "reference", "receiver_opens"},
    "constraints": {"language", "rule"},
    "predictive_cue": {"next"},
    "uncertainty_signal": None,
    "semantic_gist": {"question", "unmet", "rule"},
    "relational_map": None,
    "episodic_trace": None,
}


def entries(ccs, part, kind):
    return [v for e in ccs[part] for k, v in e.items() if k == kind]


def deliverables(ccs):
    """Where each file of the work goes, in the order the caller names them."""
    return entries(ccs, "focal_entities", "deliverable")


def should(ccs):
    """What the work should be, as the orchestrator and the agents that make it are given it."""
    return {
        "receiver": "; ".join(entries(ccs, "focal_entities", "receiver")),
        "use": "; ".join(entries(ccs, "goal_orientation", "use")),
        "acceptance": entries(ccs, "goal_orientation", "acceptance"),
        "decisions": entries(ccs, "retrieved_artifacts", "decisions"),
        "references": entries(ccs, "retrieved_artifacts", "reference"),
        "constraints": [f"{k}: {v}" for e in ccs["constraints"] for k, v in e.items()],
    }


def faults(ccs):
    """Says each way the CCS does not match the form the callers' page gives."""
    found = []
    for part, kinds in PARTS.items():
        if part not in ccs:
            found.append(f"{part} is missing")
        elif not isinstance(ccs[part], list):
            found.append(f"{part} is not a list")
        else:
            for e in ccs[part]:
                if not (
                    isinstance(e, dict) and len(e) == 1 and isinstance(next(iter(e.values())), str)
                ):
                    found.append(f"{part} has an entry that is not one kind and a string")
                elif kinds is not None and next(iter(e)) not in kinds:
                    found.append(f"{part} has a kind it cannot hold: {next(iter(e))}")
    if found:
        return found
    found += [
        f"focal_entities names {p} twice"
        for k, p in enumerate(deliverables(ccs))
        if p in deliverables(ccs)[:k]
    ]
    for part, kind in (
        ("focal_entities", "deliverable"),
        ("focal_entities", "receiver"),
        ("goal_orientation", "acceptance"),
        ("retrieved_artifacts", "checklist"),
    ):
        if not entries(ccs, part, kind):
            found.append(f"{part} needs {'an' if kind[0] in 'aeiou' else 'a'} {kind}")
    for kind, there in (
        ("checklist", os.path.isfile),
        ("decisions", os.path.isfile),
        ("reference", os.path.exists),
        ("receiver_opens", os.path.exists),
    ):
        found += [
            f"{p} does not exist; name the {kind} by its path from the top of the repository"
            for p in entries(ccs, "retrieved_artifacts", kind)
            if not there(p)
        ]
    found += [
        f"{p}: open the checklist with front matter giving its name and version"
        for p in entries(ccs, "retrieved_artifacts", "checklist")
        if os.path.isfile(p) and not {"name", "version"} <= front(p).keys()
    ]
    for p in deliverables(ccs):
        if os.path.isabs(p) or os.path.normpath(p).startswith(".."):
            found.append(f"{p} is outside the repository")
    return found


def front(path):
    """The fields of the front matter the file opens with."""
    with open(path) as f:
        lines = f.read().splitlines()
    if lines[:1] != ["---"] or "---" not in lines[1:]:
        return {}
    fields = (re.match(r"(\w+):\s*(.*)", line) for line in lines[1 : lines.index("---", 1)])
    return dict(m.groups() for m in fields if m)


def checklist(path):
    """Reads a checklist: its name and version, its opening, and each item with its whole text."""
    named = front(path)
    name = named["name"]
    opening, items, item, fence, seen = [], [], None, False, False
    with open(path) as f:
        lines = f.read().splitlines(keepends=True)
        for line in lines[lines.index("---\n", 1) + 1 :]:
            if line.startswith("```"):
                fence = not fence
            heading = None if fence else re.match(r"(#{1,3}) (?:([A-Z]-?\d+): )?(.+)", line)
            if heading:
                seen = seen or heading.group(1) == "##"
                item = None
                if heading.group(2):
                    item = {
                        "id": f"{name} {heading.group(2)}",
                        "title": heading.group(3).strip(),
                        "text": "",
                    }
                    items.append(item)
            elif item is not None:
                item["text"] += line
            elif not seen:
                opening.append(line)
    for i in items:
        i["text"] = i["text"].strip()
    return {
        "checklist": name,
        "version": named["version"],
        "opening": "".join(opening).strip(),
    }, items
