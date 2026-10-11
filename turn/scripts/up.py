"""Does the steps of a turn that need no judgment, so turn:up only calls the agents.

    python3 up.py start <in> <out>                              prints the work folder and what to pass on
    python3 up.py copy <work>                                   prints the copy the first user works in
    python3 up.py round <work> <n>                              prints "next round" or "end"
    python3 up.py end <work> <session id> [stopped: <where from>] <round>=<agent id> ...

Run from the repository. A problem is printed as it is, with exit code 1.
"""
import json
import os
import shutil
import subprocess
import sys

import assemble

HERE = os.path.dirname(os.path.abspath(__file__))
PLACES = (("focal_entities", "deliverable"), ("focal_entities", "receiver"),
          ("goal_orientation", "use"), ("retrieved_artifacts", "viewpoint"))


def script(name, *args):
    """Runs a script beside this one; its output, and whether it went through."""
    r = subprocess.run([sys.executable, os.path.join(HERE, name), *args], capture_output=True, text=True)
    return r.stdout.strip(), r.returncode == 0


def state(work, **change):
    path = os.path.join(work, "turn.json")
    with open(path, encoding="utf-8") as f:
        s = json.load(f)
    if change:
        s.update(change)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(s, f)
    return s


def start(in_path, out_path):
    if not shutil.which("jq"):
        return "jq is not installed. Install it (https://jqlang.org/download/) and call again.", 1
    problems, ok = script("check.py", "in", in_path, out_path)
    if not ok:
        return problems, 1
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    work, _ = script("tryout.py", "work")
    with open(os.path.join(work, "turn.json"), "w", encoding="utf-8") as f:
        json.dump({"in": os.path.abspath(in_path), "out": os.path.abspath(out_path), "start": commit,
                   "copy": ""}, f)
    with open(in_path, encoding="utf-8") as f:
        ccs = json.load(f)
    lines = [f"work: {work}"]
    lines += [f"{kind}: {e[kind]}" for part, kind in PLACES for e in ccs[part] if kind in e]
    return "\n".join(lines), 0


def copy(work):
    with open(state(work)["in"], encoding="utf-8") as f:
        deliverable = [e["deliverable"] for e in json.load(f)["focal_entities"] if "deliverable" in e][0]
    folder, _ = script("tryout.py", "make", deliverable)
    state(work, copy=folder)
    return folder, 0


def drop_copy(work):
    folder = state(work)["copy"]
    if folder:
        script("tryout.py", "drop", folder)
        state(work, copy="")


def round_(work, n):
    path = os.path.join(work, f"evaluator-{n}.json")
    decided = assemble.decision(path) if os.path.exists(path) else None
    if decided is None:
        return f"{path} is not a decision in the form the evaluator is to write", 1
    drop_copy(work)
    fixes = [e for e in decided["endings"] if e["ending"] == "fixed"]
    return ("next round" if fixes else "end"), 0


def end(work, session, rest):
    s = state(work)
    stopped = [a for a in rest if a.startswith("stopped: ")]
    pairs = [a for a in rest if not a.startswith("stopped: ")]
    drop_copy(work)
    for name, *args in (("assemble.py", s["in"], s["out"], work, *stopped),
                        ("trace.py", s["out"], session, s["start"], *pairs),
                        ("check.py", "out", s["in"], s["out"])):
        problems, ok = script(name, *args)
        if not ok:
            if os.path.exists(s["out"]):
                os.remove(s["out"])
            script("tryout.py", "drop", work)
            return problems, 1
    script("tryout.py", "drop", work)
    with open(s["out"], encoding="utf-8") as f:
        nexts = [e["next"] for e in json.load(f)["predictive_cue"]]
    return f"next: {nexts[0]}\nccs: {s['out']}", 0


def main(argv):
    args = argv[1:]
    if args[:1] == ["start"] and len(args) == 3:
        text, code = start(*args[1:])
    elif args[:1] == ["copy"] and len(args) == 2:
        text, code = copy(args[1])
    elif args[:1] == ["round"] and len(args) == 3:
        text, code = round_(*args[1:])
    elif args[:1] == ["end"] and len(args) >= 3:
        text, code = end(args[1], args[2], args[3:])
    else:
        print(__doc__.strip())
        return 2
    print(text)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
