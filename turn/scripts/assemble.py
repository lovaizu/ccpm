"""Builds the CCS to return from the CCS received and each round's judgments and learnings.

    python3 assemble.py <in> <out> <work> [stopped: <where from>]

<work> holds, for each judged round n, evaluator-n.json
{"points": [{"point": "...", "judgment": "good" | "more" | "unsettled", "fell_short": "<on a More>",
"why": "<on an unsettled point>", "question": "<when only the user can settle it>",
"before": "same" | "not" (on a More from round 2 on), "grounds": ["first-user-1#3"]}]}
and learner-n.json {"learnings": [{"learning": "...", "grounds": ["generator-1#2", "SETUP.md:12"]}]}.
The returned CCS carries the judgments of the version returned. episodic_trace is left empty for trace.py.
"""
import copy
import json
import os
import re
import sys

NEEDS = {"good": (), "more": ("fell_short",), "unsettled": ("why",)}


def text(d, key):
    return isinstance(d.get(key), str) and bool(d[key])


def grounded(entry):
    """Whether the entry names the steps or deliverable lines it rests on."""
    g = entry.get("grounds")
    return isinstance(g, list) and bool(g) and all(isinstance(x, str) for x in g)


def load(path, key, holds):
    """The list under key in path, or None when it is out of form."""
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return None
    if not (isinstance(d, dict) and isinstance(d.get(key), list)):
        return None
    if not all(isinstance(e, dict) and grounded(e) and holds(e) for e in d[key]):
        return None
    return d[key]


def judgments(path):
    def holds(p):
        return (text(p, "point") and p.get("judgment") in NEEDS and all(text(p, k) for k in NEEDS[p["judgment"]])
                and ("question" not in p or (p["judgment"] == "unsettled" and text(p, "question")))
                and ("before" not in p or (p["judgment"] == "more" and p["before"] in ("same", "not"))))
    return load(path, "points", holds)


def learnings(path):
    return load(path, "learnings", lambda e: text(e, "learning"))


def judged(work):
    """The numbers of the rounds with a judgment, in order."""
    names = [n for n in os.listdir(work) if re.match(r"^evaluator-[1-9][0-9]*\.json$", n)]
    return sorted(int(n[len("evaluator-"):-len(".json")]) for n in names)


def closer(before, after):
    """Whether after turns at least one More of before into Good and no Good into More. A More whose version before
    fell short the same way was More before too: the Good given then was a slip, not something the remake undid."""
    was = {p["point"]: p["judgment"] for p in before}
    was.update({p["point"]: "more" for p in after if p.get("before") == "same"})
    now = {p["point"]: p["judgment"] for p in after}
    return (any(now.get(p) == "good" for p, j in was.items() if j == "more")
            and not any(now.get(p) == "more" for p, j in was.items() if j == "good"))


def returned(rounds):
    """Which of the judged rounds' versions is returned (0 for none), and whether the last remake brought it no
    closer. Every remake the loop goes on from brought it closer, so only the last needs comparing."""
    if len(rounds) < 2 or closer(rounds[-2], rounds[-1]):
        return len(rounds), False
    return len(rounds) - 1, True


def next_step(points, no_closer):
    reasons = ["a remake brought the deliverable no closer"] if no_closer else []
    reasons += [f"{p['point']}: {p['why']}" for p in points if p["judgment"] == "unsettled" and "question" not in p]
    if reasons:
        return "to the caller: " + "; ".join(reasons)
    return "ask the user" if any("question" in p for p in points) else "done"


def read(work):
    """Each judged round's points and learnings, in order, or a string naming the file out of form."""
    rounds = []
    for n in judged(work):
        path = os.path.join(work, f"evaluator-{n}.json")
        points = judgments(path)
        if points is None:
            return f"{path} is not a judgment in the form this script reads"
        path = os.path.join(work, f"learner-{n}.json")
        learned = learnings(path)
        if learned is None:
            return f"{path} is not learnings in the form this script reads"
        rounds.append((points, learned))
    return rounds


def main(argv):
    if len(argv) not in (4, 5):
        print(__doc__.strip())
        return 2
    in_path, out_path, work = argv[1:4]
    stopped = argv[4] if len(argv) == 5 else ""
    rounds = read(work)
    if isinstance(rounds, str):
        print(rounds)
        return 1
    if not rounds and not stopped:
        print(f"no evaluator judgment in {work}")
        return 1
    with open(in_path, encoding="utf-8") as f:
        out = copy.deepcopy(json.load(f))
    k, no_closer = returned([points for points, _ in rounds])
    if k:
        points, learned = rounds[k - 1]
        mores = [p for p in points if p["judgment"] == "more"]
        if k < len(rounds):
            # A More the next round found this version shared is a fact about the version on disk.
            own = {p["point"] for p in mores}
            mores += [p for p in rounds[k][0] if p.get("before") == "same" and p["point"] not in own]
        out["uncertainty_signal"] = ([{"more": f"{p['point']}: {p['fell_short']}"} for p in mores]
                                     + [{"gap": q} for q in dict.fromkeys(p["question"] for p in points
                                                                          if "question" in p)])
        out["relational_map"] = [{"learning": e["learning"]} for e in learned]
    out["predictive_cue"] = [{"next": stopped or next_step(rounds[k - 1][0], no_closer)}]
    out["semantic_gist"] = []
    out["episodic_trace"] = []
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
