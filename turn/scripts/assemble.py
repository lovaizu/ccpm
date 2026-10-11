"""Builds the CCS to return from the CCS received and the evaluator's decisions.

    python3 assemble.py <in> <out> <work> [stopped: <where from>]

<work> holds evaluator-1.json, evaluator-2.json and so on, one per round, each
{"endings": [{"stumble": "...", "ending": "...", "grounds": ["first-user-1#3", "SETUP.md:12"]}],
"rules": [...], "gaps": [...], "links": [...]}.
episodic_trace is left empty for trace.py.
"""
import copy
import json
import os
import re
import sys

ENDING = re.compile(r"^(fixed|let go: .+|to the caller: .+)$")
ASK = "to the caller: ask the user"


def rounds(work):
    names = [n for n in os.listdir(work) if re.match(r"^evaluator-[0-9]+\.json$", n)]
    return [os.path.join(work, n) for n in sorted(names, key=lambda n: int(n[10:-5]))]


def grounded(entry):
    """Whether the entry names the steps or deliverable lines it rests on."""
    g = entry.get("grounds")
    return isinstance(g, list) and bool(g) and all(isinstance(x, str) for x in g)


def decision(path):
    """The decision in path, or None when it is out of form."""
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except ValueError:
        return None
    keys = ("endings", "rules", "gaps", "links")
    if not (isinstance(d, dict) and all(isinstance(d.get(k), list) for k in keys)):
        return None
    for e in d["endings"]:
        if not (isinstance(e, dict) and isinstance(e.get("stumble"), str)
                and isinstance(e.get("ending"), str) and ENDING.match(e["ending"]) and grounded(e)):
            return None
    return d


def next_step(last):
    reasons = [e["ending"][len("to the caller: "):] for e in last["endings"]
               if e["ending"].startswith("to the caller: ") and e["ending"] != ASK]
    if reasons:
        return "to the caller: " + "; ".join(reasons)
    return "ask the user" if last["gaps"] else "done"


def main(argv):
    if len(argv) not in (4, 5):
        print(__doc__.strip())
        return 2
    in_path, out_path, work = argv[1:4]
    stopped = argv[4] if len(argv) == 5 else ""
    decisions = []
    for path in rounds(work):
        d = decision(path)
        if d is None:
            print(f"{path} is not a decision in the form this script reads")
            return 1
        decisions.append(d)
    if not decisions and not stopped:
        print(f"no evaluator decision in {work}")
        return 1
    with open(in_path, encoding="utf-8") as f:
        ccs = json.load(f)
    out = copy.deepcopy(ccs)
    rules = [r for d in decisions for r in d["rules"]]
    known = {e.get("rule") for e in ccs["constraints"]}
    out["constraints"] += [{"rule": r} for r in dict.fromkeys(rules) if r not in known]
    out["semantic_gist"] = [{"difference": f"{e['stumble']} → {e['ending']}"}
                            for d in decisions for e in d["endings"]]
    last = decisions[-1] if decisions else {"endings": [], "gaps": [], "links": []}
    out["uncertainty_signal"] = [{"gap": g} for g in last["gaps"]]
    out["relational_map"] = [{"link": link} for link in last["links"]]
    out["predictive_cue"] = [{"next": stopped or next_step(last)}]
    out["episodic_trace"] = []
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
