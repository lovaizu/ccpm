"""Run turn:up with stand-in agents that return set reports, down one way a round can end.

    python3 dev/turn/trials/flow.py <workdir> fix|ended|ask|caller|stop

fix     round 1 has a stumble to fix; round 2 ends every stumble       next: done, two rounds
ended   round 1 ends every stumble                                     next: done, one round
ask     round 1 has a question only the user can answer                next: ask the user
caller  round 1 has a stumble the CCS cannot decide                    next: to the caller: ...
stop    the user asks to stop once the generator has finished          next: stopped: ...

The orchestrator is the real turn:up; only the four agents are stand-ins. Everything lands in
<workdir>: the repository, the stand-ins' log, the run's output and a summary to read beside the
conversation records (JSONL).
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
CCS = {
    "focal_entities": [{"deliverable": "NOTE.md"},
                       {"receiver": "A visitor who has only the note"}],
    "goal_orientation": [{"acceptance": ACCEPTANCE}, {"use": "Read the note to find when to come"}],
    "retrieved_artifacts": [{"viewpoint": "VIEWPOINT.md"}],
    "constraints": [{"language": "English"}],
    "episodic_trace": [], "semantic_gist": [], "relational_map": [], "predictive_cue": [],
    "uncertainty_signal": [],
}


def decision(endings, gaps=()):
    return {"endings": endings, "rules": [], "gaps": list(gaps), "links": ["NOTE.md ← hours.txt"]}


LET_GO = {"stumble": "the title is plain", "ending": "let go: the visitor still finds the hours"}
PATHS = {
    "fix": ([decision([{"stumble": "the hours are missing", "cause": "hours.txt was not read",
                        "ending": "fixed"}]), decision([LET_GO])], "done"),
    "ended": ([decision([LET_GO])], "done"),
    "ask": ([decision([{"stumble": "the closing day is not known",
                        "ending": "to the caller: ask the user"}],
                      ["Which day of the week is the shop closed?"])], "ask the user"),
    "caller": ([decision([{"stumble": "the note could be for staff or visitors",
                           "ending": "to the caller: the CCS does not say which visitors"}])],
               "to the caller: the CCS does not say which visitors"),
    "stop": ([], "stopped: first-user-1"),
}

STANDIN = """\
---
name: {role}
description: Stands in for turn's {role} in a check of the orchestrator's flow.
model: sonnet
tools: Bash
---

Run this one command, putting in the file you were told to write your report or decision to, or
`none` if you were told of none, and return its output word for word as your whole answer:

    python3 {script} {role} <file>
"""


def standin_script(workdir, decisions):
    """The script every stand-in runs: it logs the call and writes the set report."""
    return f"""\
import json, sys
role, target = sys.argv[1], sys.argv[2]
log = {str(workdir / "calls.jsonl")!r}
try:
    n = sum(1 for line in open(log) if json.loads(line)["role"] == role) + 1
except FileNotFoundError:
    n = 1
open(log, "a").write(json.dumps({{"role": role, "round": n, "file": target}}) + "\\n")
decisions = {decisions!r}
if role == "generator":
    open({str(workdir / "repo" / "NOTE.md")!r}, "w").write("# Visiting\\n\\nOpen 9 to 5.\\n")
    print("Wrote NOTE.md from hours.txt.")
elif role == "evaluator":
    open(target, "w").write(json.dumps(decisions[n - 1]))
    print(target)
else:
    open(target, "w").write(f"{{role}} report, round {{n}}: read the note, found the hours.\\n")
    print(target)
"""


def git(cwd, *args):
    return subprocess.run(["git", "-c", "user.name=trial", "-c", "user.email=trial@example.com", *args],
                          cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def setup(workdir, decisions):
    repo = workdir / "repo"
    repo.mkdir(parents=True)
    (repo / "hours.txt").write_text("Open 9 to 5, closed one day a week.\n")
    (repo / "VIEWPOINT.md").write_text("- A visitor learns when to come.\n")
    (repo / "NOTE.md").write_text("# Visiting\n")
    (repo / ".t").mkdir()
    (repo / ".t" / "in.json").write_text(json.dumps(CCS, indent=2))
    git(repo, "init", "-q")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "shop")
    plugin = workdir / "turn"
    shutil.copytree(REPO / "turn", plugin)
    (workdir / "standin.py").write_text(standin_script(workdir, decisions))
    for role in ROLES:
        (plugin / "agents" / f"{role}.md").write_text(
            STANDIN.format(role=role, script=workdir / "standin.py"))
    return repo, plugin


def calls(workdir):
    path = workdir / "calls.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def agent_calls(workdir):
    """The inputs of the orchestrator's Agent calls, from the run's output."""
    out = []
    for line in (workdir / "run.jsonl").read_text().splitlines():
        try:
            m = json.loads(line)
        except ValueError:
            continue
        content = m.get("message", {}).get("content") if m.get("type") == "assistant" else None
        out += [c["input"] for c in content or [] if c.get("type") == "tool_use" and c["name"] == "Agent"]
    return out


def results(workdir):
    return (workdir / "run.jsonl").read_text().count('"type":"result"')


def message(text):
    return json.dumps({"type": "user", "message": {"role": "user", "content": text}}) + "\n"


def run(workdir, repo, plugin, stop):
    cmd = ["claude", "-p", "--model", "opus", "--input-format", "stream-json",
           "--output-format", "stream-json", "--verbose", "--plugin-dir", str(plugin),
           "--permission-mode", "auto"]
    out = open(workdir / "run.jsonl", "w")
    p = subprocess.Popen(cmd, cwd=repo, stdin=subprocess.PIPE, stdout=out, stderr=subprocess.STDOUT,
                         text=True)
    p.stdin.write(message("/turn:up in: .t/in.json\nout: .t/out.json"))
    p.stdin.flush()
    seen = 0
    if stop:
        while not any(c["role"] == "generator" for c in calls(workdir)) and p.poll() is None:
            time.sleep(2)
        # The stop may be taken in the turn already running, so wait for the next result after it.
        seen = results(workdir)
        p.stdin.write(message("Stop the task here, please."))
        p.stdin.flush()
    while p.poll() is None:
        if results(workdir) > seen:
            break
        time.sleep(2)
    p.stdin.close()
    p.wait()
    out.close()


def main(argv):
    if len(argv) != 3 or argv[2] not in PATHS:
        print(__doc__.strip())
        return 2
    workdir = Path(argv[1]).resolve()
    if workdir.exists():
        sys.exit(f"{workdir} exists; give a new folder")
    decisions, expected = PATHS[argv[2]]
    workdir.mkdir(parents=True)
    tries_before = {n for n in os.listdir(tempfile.gettempdir()) if n.startswith("turn-try-")}
    repo, plugin = setup(workdir, decisions)
    start = git(repo, "rev-parse", "HEAD")
    run(workdir, repo, plugin, argv[2] == "stop")
    out = repo / ".t" / "out.json"
    ccs = json.loads(out.read_text()) if out.exists() else {}
    left = {n for n in os.listdir(tempfile.gettempdir()) if n.startswith("turn-try-")} - tries_before
    summary = {
        "next": [e["next"] for e in ccs.get("predictive_cue", [])],
        "expected next": expected,
        "calls": [f"{c['role']}-{c['round']}" for c in calls(workdir)],
        "commits since start": git(repo, "rev-list", "--count", f"{start}..HEAD"),
        "in.json unchanged": json.loads((repo / ".t" / "in.json").read_text()) == CCS,
        "temporary folders left": sorted(left),
        "acceptance told to the first user": any(
            ACCEPTANCE in a.get("prompt", "") for a in agent_calls(workdir)
            if a.get("subagent_type") == "turn:first-user"),
    }
    (workdir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
