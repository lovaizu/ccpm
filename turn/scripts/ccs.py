"""The CCS, the form the callers' page gives, and the checklists it names."""

import os
import re

PARTS = {
    "focal_entities": {"deliverable", "receiver"},
    "goal_orientation": {"use", "acceptance"},
    "retrieved_artifacts": {"viewpoint", "source"},
    "constraints": {"language", "rule", "answer"},
    "predictive_cue": {"next"},
    "uncertainty_signal": None,
    "semantic_gist": {"difference"},
    "relational_map": None,
    "episodic_trace": None,
}


def entries(ccs, part, kind):
    return [v for e in ccs[part] for k, v in e.items() if k == kind]


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
    if len(entries(ccs, "focal_entities", "deliverable")) != 1:
        found.append("focal_entities needs one deliverable")
    for part, kind in (
        ("focal_entities", "receiver"),
        ("goal_orientation", "acceptance"),
        ("retrieved_artifacts", "viewpoint"),
    ):
        if not entries(ccs, part, kind):
            found.append(f"{part} needs {'an' if kind[0] in 'aeiou' else 'a'} {kind}")
    for kind in ("viewpoint", "source"):
        found += [
            f"{p} does not exist"
            for p in entries(ccs, "retrieved_artifacts", kind)
            if not os.path.isfile(p)
        ]
    found += [
        f"{p}: open the checklist with front matter giving its name and version"
        for p in entries(ccs, "retrieved_artifacts", "viewpoint")
        if os.path.isfile(p) and not {"name", "version"} <= front(p).keys()
    ]
    for p in entries(ccs, "focal_entities", "deliverable"):
        if os.path.isabs(p) or os.path.normpath(p).startswith(".."):
            found.append(f"{p} is outside the repository")
    return found


def front(path):
    """The fields of the front matter the file opens with."""
    with open(path) as f:
        lines = f.read().splitlines()
    if lines[:1] != ["---"] or "---" not in lines[1:]:
        return {}
    return dict(
        re.match(r"(\w+):\s*(.*)", line).groups()
        for line in lines[1 : lines.index("---", 1)]
        if re.match(r"\w+:", line)
    )


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
            heading = None if fence else re.match(r"(#{1,3}) (?:([A-Z]-\d+): )?(.+)", line)
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
