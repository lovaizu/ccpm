#!/usr/bin/env python3
"""What turn:up needs to come out the same on every run: the CCS checked, the list and the forms
laid out, each form checked, the first user's copy, and the work and the CCS written back."""

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

PARTS = {
    "focal_entities": {"deliverable", "receiver"},
    "goal_orientation": {"use", "acceptance"},
    "retrieved_artifacts": {"viewpoint", "source"},
    "constraints": {"language", "rule", "answer"},
    "predictive_cue": {"next"},
    "uncertainty_signal": {"gap"},
    "semantic_gist": {"difference"},
    "relational_map": None,
    "episodic_trace": None,
}
ROLES = ("generator", "first-user", "evaluator", "orchestrator")
RUN = os.path.join(".turn", "run.json")
LINES = re.compile(r"\s*\d+(\s*-\s*\d+)?(\s*,\s*\d+(\s*-\s*\d+)?)*\s*$")
USAGE = """usage: up.py start <in> <out> <session>
       up.py copy <work folder> <round>
       up.py drop <copy>
       up.py records <work folder> <agent id>
       up.py check <work folder> <round> <generator|first-user|evaluator|orchestrator>
       up.py end <work folder> <round>"""


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
                if not (isinstance(e, dict) and len(e) == 1 and isinstance(next(iter(e.values())), str)):
                    found.append(f"{part} has an entry that is not one kind and a string")
                elif kinds is not None and next(iter(e)) not in kinds:
                    found.append(f"{part} has a kind it cannot hold: {next(iter(e))}")
    if found:
        return found
    if len(entries(ccs, "focal_entities", "deliverable")) != 1:
        found.append("focal_entities needs one deliverable")
    for part, kind in (("focal_entities", "receiver"), ("goal_orientation", "acceptance"),
                       ("retrieved_artifacts", "viewpoint")):
        if not entries(ccs, part, kind):
            found.append(f"{part} needs {'an' if kind[0] in 'aeiou' else 'a'} {kind}")
    for kind in ("viewpoint", "source"):
        found += [f"{p} does not exist" for p in entries(ccs, "retrieved_artifacts", kind)
                  if not os.path.isfile(p)]
    for p in entries(ccs, "focal_entities", "deliverable"):
        if os.path.isabs(p) or os.path.normpath(p).startswith(".."):
            found.append(f"{p} is outside the repository")
    return found


def checklist(path):
    """Reads a checklist: its opening, and each item with its whole text."""
    name = os.path.splitext(os.path.basename(path))[0]
    opening, items, item, fence, seen = [], [], None, False, False
    with open(path) as f:
        for line in f:
            if line.startswith("```"):
                fence = not fence
            heading = None if fence else re.match(r"(#{1,3}) (?:([A-Z]-\d+): )?(.+)", line)
            if heading:
                seen = seen or heading.group(1) == "##"
                item = None
                if heading.group(2):
                    item = {"id": f"{name} {heading.group(2)}", "title": heading.group(3).strip(),
                            "text": ""}
                    items.append(item)
            elif item is not None:
                item["text"] += line
            elif not seen:
                opening.append(line)
    for i in items:
        i["text"] = i["text"].strip()
    return {"checklist": name, "opening": "".join(opening).strip()}, items


def forms(ids):
    return {
        "generator": {i: {"lines": ""} for i in ids},
        "first-user": {i: {"took": "", "lines": ""} for i in ids},
        "evaluator": {},
        "orchestrator": {i: {"met": None, "lines": "", "note": ""} for i in ids},
    }


def start(src, out, session):
    if os.path.exists(out):
        raise Stop(f"{out} already exists; turn never writes over a file, so name a new out")
    ccs = read_json(src, src)
    found = faults(ccs)
    if found:
        raise Stop("\n".join(found))
    work = os.path.join(".turn", os.path.splitext(os.path.basename(out))[0])
    lists = [checklist(p) for p in entries(ccs, "retrieved_artifacts", "viewpoint")]
    listed = {"checklists": [c for c, _ in lists], "items": [i for _, items in lists for i in items]}
    write_json(os.path.join(work, "list.json"), listed)
    laid = forms([i["id"] for i in listed["items"]])
    for role in ROLES:
        write_json(os.path.join(work, "1", f"{role}.json"), laid[role])
    deliverable = entries(ccs, "focal_entities", "deliverable")[0]
    write_json(RUN, {"session": session, "work": work, "in": src, "out": out, "round": 1})
    print(json.dumps({
        "folder": work,
        "list": os.path.join(work, "list.json"),
        "forms": {r: os.path.join(work, "1", f"{r}.json") for r in ROLES},
        "work": os.path.join(work, "1", os.path.basename(deliverable)),
        "deliverable": deliverable,
        "receiver": "; ".join(entries(ccs, "focal_entities", "receiver")),
        "use": "; ".join(entries(ccs, "goal_orientation", "use")),
        "acceptance": entries(ccs, "goal_orientation", "acceptance"),
        "sources": entries(ccs, "retrieved_artifacts", "source"),
        "constraints": [f"{k}: {v}" for e in ccs["constraints"] for k, v in e.items()],
    }, indent=1, ensure_ascii=False))


def the_work(work, n):
    """The run's CCS as received, and the path of the work made in round n."""
    run = read_json(RUN, RUN)
    ccs = read_json(run["in"], run["in"])
    deliverable = entries(ccs, "focal_entities", "deliverable")[0]
    path = os.path.join(work, str(n), os.path.basename(deliverable))
    if not os.path.isfile(path):
        raise Stop(f"{path} is not written")
    return run, ccs, deliverable, path


def bad_lines(given, count):
    if not LINES.match(given):
        return True
    return any(not 1 <= int(a) <= int(b or a) <= count
               for a, b in re.findall(r"(\d+)(?:\s*-\s*(\d+))?", given))


def check(work, n, role):
    """Says each place of the role's form that is left or wrong; nothing when every place is filled."""
    _, _, _, path = the_work(work, n)
    with open(path) as f:
        count = len(f.read().splitlines())
    ids = [i["id"] for i in read_json(os.path.join(work, "list.json"), "the list")["items"]]
    form = read_json(os.path.join(work, str(n), f"{role}.json"), "the form")
    found = [f"{i}: not an item of the list" for i in form if i not in ids]
    for i in ids if role != "evaluator" else [i for i in ids if i in form]:
        place = form.get(i)
        if place is None:
            found.append(f"{i}: not filled")
            continue
        lines = place.get("lines", "")
        needed = role in ("generator", "evaluator") or (role == "orchestrator" and place.get("met"))
        if role == "first-user" and not place.get("took"):
            found.append(f"{i}: what was taken is not given")
        if role == "evaluator" and not place.get("grounds"):
            found.append(f"{i}: grounds are not given")
        if role == "orchestrator" and not isinstance(place.get("met"), bool):
            found.append(f"{i}: not decided")
        if role == "orchestrator" and not place.get("note"):
            found.append(f"{i}: the note is not given")
        if needed and not lines:
            found.append(f"{i}: lines are not given")
        elif lines and bad_lines(lines, count):
            found.append(f"{i}: lines {lines} are not in the work")
    return found


def copy(work, n):
    run, _, deliverable, path = the_work(work, n)
    place = tempfile.mkdtemp(prefix="turn-copy-")
    subprocess.run(["git", "clone", "-q", ".", place], check=True)
    os.makedirs(os.path.dirname(os.path.join(place, deliverable)), exist_ok=True)
    shutil.copyfile(path, os.path.join(place, deliverable))
    print(place)


def drop(place):
    if not os.path.basename(place).startswith("turn-copy-") or \
            os.path.dirname(os.path.realpath(place)) != os.path.realpath(tempfile.gettempdir()):
        raise Stop(f"{place} is not a copy turn made")
    shutil.rmtree(place)


def records(work, agent):
    session = read_json(RUN, RUN)["session"]
    found = glob.glob(os.path.join(os.path.expanduser("~"), ".claude", "projects", "*", session,
                                   "subagents", f"agent-{agent}.jsonl"))
    if not found:
        raise Stop(f"no records of agent {agent} in session {session}")
    print(found[0])


def end(work, n):
    found = check(work, n, "orchestrator")
    if found:
        raise Stop("\n".join(found))
    run, ccs, deliverable, path = the_work(work, n)
    items = {i["id"]: i for i in read_json(os.path.join(work, "list.json"), "the list")["items"]}
    form = read_json(os.path.join(work, str(n), "orchestrator.json"), "the form")
    differences = [{"difference": f"{i} ({items[i]['text'].splitlines()[0]}): {p['note']}"}
                   for i, p in form.items() if not p["met"]]
    nxt = "ask the user" if differences else "done"
    os.makedirs(os.path.dirname(deliverable) or ".", exist_ok=True)
    shutil.copyfile(path, deliverable)
    ccs.update(predictive_cue=[{"next": nxt}], semantic_gist=differences,
               episodic_trace=[{"evidence": os.path.join(work, str(n), "orchestrator.json")}])
    write_json(run["out"], ccs)
    os.remove(RUN)
    print(nxt)


COMMANDS = {"start": (start, 3), "copy": (copy, 2), "drop": (drop, 1), "records": (records, 2),
            "end": (end, 2)}


def main(argv):
    try:
        if argv[:1] == ["check"] and len(argv) == 4:
            found = check(*argv[1:])
            print("\n".join(found) or "filled")
            return 1 if found else 0
        command, count = COMMANDS.get(argv[0] if argv else "", (None, -1))
        if command is None or len(argv) - 1 != count:
            raise Stop(USAGE)
        command(*argv[1:])
        return 0
    except Stop as stop:
        print(stop)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
