"""Does the steps of a turn that need no judgment, so turn:up only calls the agents.

    python3 up.py start <in> <out> <session id>                 prints the work folder and what to pass on
    python3 up.py copy <work>                                   prints the copy the first user works in
    python3 up.py steps <work> <generator id> <first user id>   writes the round's steps
    python3 up.py round <work>                                  prints "next round" or "end"
    python3 up.py end <work> [stopped: <where from>] <round>=<agent id> ...

Run from the repository. A problem is printed as it is, with exit code 1.
"""
import json
import os
import subprocess
import sys

import assemble
import steps
import trace

HERE = os.path.dirname(os.path.abspath(__file__))
PLACES = (("focal_entities", "deliverable"), ("focal_entities", "receiver"),
          ("goal_orientation", "use"), ("retrieved_artifacts", "viewpoint"))
SHOULD = (("focal_entities", "deliverable"), ("focal_entities", "receiver"),
          ("goal_orientation", "acceptance"), ("goal_orientation", "use"),
          ("retrieved_artifacts", "viewpoint"), ("retrieved_artifacts", "source"),
          ("constraints", "language"), ("constraints", "rule"), ("constraints", "answer"),
          ("semantic_gist", "difference"))


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


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def start(in_path, out_path, session):
    problems, ok = script("check.py", "in", in_path, out_path)
    if not ok:
        return problems, 1
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    repo = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    work, _ = script("tryout.py", "work", session)
    with open(os.path.join(work, "turn.json"), "w", encoding="utf-8") as f:
        json.dump({"in": os.path.abspath(in_path), "out": os.path.abspath(out_path), "given_out": out_path,
                   "start": commit, "repo": os.path.realpath(repo), "session": session, "round": 1, "copy": ""}, f)
    ccs = load(in_path)
    should = [f"- {kind}: {e[kind]}" for part, kind in SHOULD for e in ccs[part] if kind in e]
    with open(os.path.join(work, "should.md"), "w", encoding="utf-8") as f:
        f.write("# What the deliverable should be\n\n" + "\n".join(should) + "\n")
    lines = [f"work: {work}"]
    lines += [f"{kind}: {e[kind]}" for part, kind in PLACES for e in ccs[part] if kind in e]
    return "\n".join(lines), 0


def copy(work):
    ccs = load(state(work)["in"])
    deliverable = [e["deliverable"] for e in ccs["focal_entities"] if "deliverable" in e][0]
    folder, ok = script("tryout.py", "make", deliverable)
    if not ok:
        script("tryout.py", "drop", work)
        return folder, 1
    leave_out_acceptance(folder, deliverable, [e["acceptance"] for e in ccs["goal_orientation"] if "acceptance" in e])
    state(work, copy=folder)
    return folder, 0


def leave_out_acceptance(folder, deliverable, acceptance):
    """Deletes from the copy each file but the deliverable that holds the acceptance, such as a
    committed CCS: the receiver is never told it, so the first user must not find it either."""
    kept = os.path.join(folder, deliverable)
    for top, dirs, names in os.walk(folder):
        dirs[:] = [d for d in dirs if d != ".git"]
        for path in [os.path.join(top, n) for n in names]:
            if not (os.path.samefile(path, kept) or path.startswith(kept + os.sep)) and holds(path, acceptance):
                os.remove(path)


def holds(path, words):
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    return any(w in text for w in words)


def make_steps(work, generator, first_user):
    s = state(work)
    for role, agent in (("generator", generator), ("first-user", first_user)):
        name = f"{role}-{s['round']}"
        record = trace.record(s["session"], agent)
        if not record:
            return f"no conversation record for {name} ({agent})", 1
        steps.write(work, name, steps.steps(record, name))
    return "", 0


def drop_copy(work):
    folder = state(work)["copy"]
    if folder:
        script("tryout.py", "drop", folder)
        state(work, copy="")


def round_(work):
    n = state(work)["round"]
    path = os.path.join(work, f"evaluator-{n}.json")
    decided = assemble.decision(path) if os.path.exists(path) else None
    if decided is None:
        return f"{path} is not a decision in the form the evaluator is to write", 1
    drop_copy(work)
    if any(e["ending"] == "fixed" for e in decided["endings"]):
        state(work, round=n + 1)
        return "next round", 0
    return "end", 0


def found(work, name, key=None):
    path = os.path.join(work, name)
    if not os.path.exists(path):
        return []
    return load(path)[key] if key else load(path)


def evidence(work, s):
    """Each round's steps, and the causes and endings with the steps and lines they rest on."""
    rounds = []
    for n in range(1, s["round"] + 1):
        taken = [step for role in ("generator", "first-user") for step in found(work, f"steps-{role}-{n}.json")]
        rounds.append({"round": n, "steps": taken, "causes": found(work, f"learner-{n}.json", "causes"),
                       "endings": found(work, f"evaluator-{n}.json", "endings")})
    given = s["given_out"]
    place = (given[:-len(".json")] if given.endswith(".json") else given) + ".evidence.json"
    with open(os.path.join(os.path.dirname(s["out"]), os.path.basename(place)), "w", encoding="utf-8") as f:
        json.dump({"rounds": rounds}, f, ensure_ascii=False, indent=2)
        f.write("\n")
    ccs = load(s["out"])
    ccs["episodic_trace"].append({"evidence": place})
    with open(s["out"], "w", encoding="utf-8") as f:
        json.dump(ccs, f, ensure_ascii=False, indent=2)
        f.write("\n")


def end(work, rest):
    s = state(work)
    stopped = [a for a in rest if a.startswith("stopped: ")]
    pairs = [a for a in rest if not a.startswith("stopped: ")]
    drop_copy(work)
    for name, *args in (("assemble.py", s["in"], s["out"], work, *stopped),
                        ("trace.py", s["out"], s["session"], s["start"], *pairs),
                        ("check.py", "out", s["in"], s["out"])):
        problems, ok = script(name, *args)
        if not ok:
            if os.path.exists(s["out"]):
                os.remove(s["out"])
            script("tryout.py", "drop", work)
            return problems, 1
    evidence(work, s)
    script("tryout.py", "drop", work)
    nexts = [e["next"] for e in load(s["out"])["predictive_cue"]]
    return f"next: {nexts[0]}\nccs: {s['out']}", 0


def main(argv):
    args = argv[1:]
    if args[:1] == ["start"] and len(args) == 4:
        text, code = start(*args[1:])
    elif args[:1] == ["copy"] and len(args) == 2:
        text, code = copy(args[1])
    elif args[:1] == ["steps"] and len(args) == 4:
        text, code = make_steps(*args[1:])
    elif args[:1] == ["round"] and len(args) == 2:
        text, code = round_(args[1])
    elif args[:1] == ["end"] and len(args) >= 2:
        text, code = end(args[1], args[2:])
    else:
        print(__doc__.strip())
        return 2
    if text:
        print(text)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
