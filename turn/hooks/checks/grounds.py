"""Keep the learner and the evaluator running until each cause and ending names steps or deliverable
lines that exist, and every step of the first user that ended in an error has an ending."""
import json
import os

import assemble


def causes(path):
    """The learner's causes, or None when out of form."""
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return None
    if not (isinstance(d, dict) and isinstance(d.get("causes"), list)):
        return None
    for c in d["causes"]:
        if not (isinstance(c, dict) and isinstance(c.get("stumble"), str) and isinstance(c.get("cause"), str)
                and isinstance(c.get("way_of_working"), bool) and assemble.grounded(c)):
            return None
    return d["causes"]


def steps(work, name):
    path = os.path.join(work, f"steps-{name}.json")
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def wrong(ground, t):
    """Why the ground does not exist, or None when it does."""
    if ":" in ground and "#" not in ground:
        place, line = ground.rsplit(":", 1)
        deliverable = t["deliverable"].rstrip("/")
        path = os.path.join(t["repo"], place)
        inside = place == deliverable or place.startswith(deliverable + "/")
        if inside and line.isdigit() and os.path.isfile(path):
            with open(path, encoding="utf-8", errors="replace") as f:
                if 1 <= int(line) <= len(f.read().splitlines()):
                    return None
        return f"{ground} is not a line of the deliverable"
    name, _, k = ground.rpartition("#")
    if name and k.isdigit() and 1 <= int(k) <= len(steps(t["work"], name)):
        return None
    return f"{ground} is not a step"


FORM = {
    "learner": ('{"causes": [{"stumble": "...", "cause": "...", "way_of_working": true, '
                '"grounds": ["first-user-1#3"]}]}'),
    "evaluator": ('{"endings": [{"stumble": "...", "cause": "...", "ending": "fixed", '
                  '"grounds": ["first-user-1#3", "SETUP.md:12"]}], "rules": [], "gaps": [], "links": []}, '
                  'each ending exactly "fixed", "let go: <why>", "to the caller: <why>" or "to the caller: ask the user"'),
}


def check(data, t):
    role = data["agent_type"].split(":", 1)[1]
    if role not in FORM:
        return []
    path = os.path.join(t["work"], f"{role}-{t['round']}.json")
    if role == "learner":
        entries = causes(path)
    else:
        decided = assemble.decision(path) if os.path.isfile(path) else None
        entries = decided and decided["endings"]
    if entries is None:
        return [f"{path} is not in the form to write: {FORM[role]}"]
    named = [g for e in entries for g in e["grounds"]]
    out = [w for w in (wrong(g, t) for g in dict.fromkeys(named)) if w]
    if role == "evaluator":
        out += [f"{s['step']} ended in an error and no ending names it"
                for s in steps(t["work"], f"first-user-{t['round']}") if s["error"] and s["step"] not in named]
    return out
