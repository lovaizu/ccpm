"""Run turn's whole flow with stand-in agents, from a calling plugin, across turns and machines.

    python3 dev/turn/trials/flow.py <workdir>

The note plugin writes a CCS and calls the real turn:up; only turn's four agents are stand-ins that
return set reports. One task goes through every way a turn can go:

turn 1   round 1 has a stumble to fix and a rule; round 2 a question only the user can answer
turn 2   the skill adds the user's answer and calls again; the user stops it after the generator
turn 3   in another clone, with only the CCS and the deliverable, the task carries on and is done

Everything lands in <workdir>: both repositories, the stand-ins' log, each session's output and
summary.json. It passes when summary.json shows every check true; read the records (JSONL) beside it.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

TRIALS = Path(__file__).resolve().parent
REPO = TRIALS.parents[2]
ROLES = ("generator", "first-user", "learner", "evaluator")
ACCEPTANCE = "A visitor finds the opening hours in the note alone"
QUESTION = "Which day of the week is the shop closed?"
ANSWER = "Monday."
RULE = "Read every source of a fact before writing it."
DECISIONS = [
    {"endings": [{"stumble": "the hours are missing", "cause": "hours.txt was not read",
                  "ending": "fixed", "grounds": ["first-user-1#1", "NOTE.md:3"]}],
     "rules": [RULE], "gaps": [], "links": ["NOTE.md ← hours.txt"]},
    {"endings": [{"stumble": "the closing day is not known", "ending": "to the caller: ask the user",
                  "grounds": ["first-user-2#1"]}],
     "rules": [], "gaps": [QUESTION], "links": ["NOTE.md ← hours.txt"]},
    {"endings": [{"stumble": "the title is plain", "ending": "let go: the visitor still finds the hours",
                  "grounds": ["NOTE.md:1"]}],
     "rules": [], "gaps": [], "links": ["NOTE.md ← hours.txt"]},
]
CALLS = [*ROLES, *ROLES, "generator", *ROLES]
KEPT = ("focal_entities", "goal_orientation", "retrieved_artifacts")
WORKDIR = Path()

STANDIN = """\
---
name: {role}
description: Stands in for turn's {role} in a check of turn's flow.
model: sonnet
tools: Bash, Read
---

Run this one command, putting in the file you were told to write your report or decision to, or
`none` if you were told of none, and return its output word for word as your whole answer:

    {cd}python3 {script} {role} <file>

If you are then told to read files whole, read each of them with the Read tool, all of it, and give
the same answer again.
"""

SCRIPT = """\
import json, subprocess, sys
role, target = sys.argv[1], sys.argv[2]
log = {log!r}
try:
    files = [json.loads(line)["file"] for line in open(log) if json.loads(line)["role"] == role]
except FileNotFoundError:
    files = []
files = list(dict.fromkeys(files + [target]))
n = files.index(target) + 1
open(log, "a").write(json.dumps({{"role": role, "call": n, "file": target}}) + "\\n")
if role == "generator":
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    open(top + "/NOTE.md", "w").write("# Visiting\\n\\nOpen 9 to 5.\\n")
    print("Wrote NOTE.md from hours.txt.")
elif role == "evaluator":
    open(target, "w").write(json.dumps({decisions!r}[n - 1]))
    print(target)
elif role == "learner":
    open(target, "w").write(json.dumps({{"causes": []}}))
    print(target)
else:
    open(target, "w").write(f"{{role}} report: read the note, found the hours.\\n")
    print(target)
"""


def git(cwd, *args):
    return subprocess.run(["git", "-c", "user.name=trial", "-c", "user.email=trial@example.com", *args],
                          cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def setup(workdir):
    repo = workdir / "repo"
    repo.mkdir(parents=True)
    (repo / "hours.txt").write_text("Open 9 to 5, closed one day a week.\n")
    (repo / ".gitignore").write_text(".note/\nNOTE.md\n")
    git(repo, "init", "-q")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "shop")
    plugin = workdir / "turn"
    shutil.copytree(REPO / "turn", plugin)
    (workdir / "standin.py").write_text(SCRIPT.format(log=str(workdir / "calls.jsonl"), decisions=DECISIONS))
    for role in ROLES:
        (plugin / "agents" / f"{role}.md").write_text(
            STANDIN.format(role=role, script=workdir / "standin.py",
                           cd="cd <the folder you were told to work in> && " if role == "first-user" else ""))
    return repo, plugin


class Session:
    """A Claude Code conversation the user types into, one message at a time."""

    def __init__(self, workdir, name, repo, plugin):
        self.output = workdir / f"{name}.jsonl"
        cmd = ["claude", "-p", "--model", "opus", "--input-format", "stream-json",
               "--output-format", "stream-json", "--verbose", "--permission-mode", "auto",
               "--plugin-dir", str(plugin), "--plugin-dir", str(TRIALS / "note-plugin")]
        self.out = open(self.output, "w")
        self.p = subprocess.Popen(cmd, cwd=repo, stdin=subprocess.PIPE, stdout=self.out,
                                  stderr=subprocess.STDOUT, text=True)

    def results(self):
        return self.output.read_text().count('"type":"result"')

    def say(self, text):
        seen = self.results()
        self.p.stdin.write(json.dumps({"type": "user", "message": {"role": "user", "content": text}}) + "\n")
        self.p.stdin.flush()
        return seen

    def wait(self, seen):
        """Waits for the reply that comes after `seen` replies."""
        while self.p.poll() is None and self.results() <= seen:
            time.sleep(2)

    def close(self):
        self.p.stdin.close()
        self.p.wait()
        self.out.close()


def agent_calls(workdir):
    """The agents the orchestrator called, in order, as (role, prompt); a stand-in kept running by
    turn's check may run its command again, so the order is read from the calls, not the log."""
    out = []
    for path in sorted(workdir.glob("session-*.jsonl")):
        for line in path.read_text().splitlines():
            try:
                m = json.loads(line)
            except ValueError:
                continue
            content = m.get("message", {}).get("content") if m.get("type") == "assistant" else None
            out += [(c["input"].get("subagent_type", "").removeprefix("turn:"), c["input"].get("prompt", ""))
                    for c in content or [] if c.get("type") == "tool_use" and c["name"] == "Agent"]
    return out


def task(repo, k):
    path = repo / ".note" / f"task-{k}.json"
    return json.loads(path.read_text()) if path.exists() else {}


def evidence(ccs):
    """The evidence a returned CCS points to; the repository it lies in is found from the task."""
    places = [e["evidence"] for e in ccs.get("episodic_trace", []) if "evidence" in e]
    for top in (WORKDIR / "repo", WORKDIR / "other"):
        if places and (top / places[0]).exists():
            return json.loads((top / places[0]).read_text())
    return {"rounds": []}


def values(ccs, part, kind):
    return [e[kind] for e in ccs.get(part, []) if kind in e]


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip())
        return 2
    workdir = Path(argv[1]).resolve()
    if workdir.exists():
        sys.exit(f"{workdir} exists; give a new folder")
    workdir.mkdir(parents=True)
    global WORKDIR
    WORKDIR = workdir
    tries_before = {n for n in os.listdir(tempfile.gettempdir()) if n.startswith("turn-try-")}
    repo, plugin = setup(workdir)
    start = git(repo, "rev-parse", "HEAD")

    first = Session(workdir, "session-1", repo, plugin)
    first.wait(first.say("/note:note"))
    seen = first.say(ANSWER)
    while sum(r == "generator" for r, _ in agent_calls(workdir)) < 3 and first.p.poll() is None:
        time.sleep(2)
    first.say("Stop the task here, please.")
    first.wait(seen)
    first.close()

    other = workdir / "other"
    subprocess.run(["git", "clone", "-q", str(repo), str(other)], check=True)
    shutil.copytree(repo / ".note", other / ".note")
    shutil.copy2(repo / "NOTE.md", other / "NOTE.md")
    second = Session(workdir, "session-2", other, plugin)
    second.wait(second.say("/note:note"))
    second.close()

    tasks = [task(repo, k) for k in (1, 2, 3, 4)] + [task(other, 5)]
    left = {n for n in os.listdir(tempfile.gettempdir()) if n.startswith("turn-try-")} - tries_before
    checks = {
        "turns return ask the user, stopped, done": [values(tasks[k], "predictive_cue", "next")
                                                     for k in (1, 3, 4)]
        == [["ask the user"], ["stopped: first-user-1"], ["done"]],
        "the question is the one gap": values(tasks[1], "uncertainty_signal", "gap") == [QUESTION],
        "the agents are called in this order": [r for r, _ in agent_calls(workdir)] == CALLS,
        "the rule and the answer reach the last CCS": [
            (k, v if k == "rule" else v.startswith(QUESTION)) for e in tasks[4].get("constraints", [])
            for k, v in e.items() if k in ("rule", "answer")] == [("rule", RULE), ("answer", True)],
        "what the plugin wrote is unchanged": all(t.get(p) == tasks[0].get(p) for t in tasks for p in KEPT),
        "no commit": git(repo, "rev-list", "--count", f"{start}..HEAD") == "0"
        and git(other, "rev-list", "--count", f"{start}..HEAD") == "0",
        "no temporary folder left": not left,
        "the first user is never told the acceptance": not any(
            ACCEPTANCE in p for r, p in agent_calls(workdir) if r == "first-user"),
        "each returned CCS points to its evidence, with each round's steps": [
            [r["round"] for r in evidence(t)["rounds"] if any("first-user" in s["step"] for s in r["steps"])]
            for t in (tasks[1], tasks[3], tasks[4])] == [[1, 2], [], [1]],
    }
    (workdir / "summary.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2))
    print(json.dumps(checks, ensure_ascii=False, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
