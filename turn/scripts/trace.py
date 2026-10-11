"""Writes episodic_trace into the CCS to return, from the agents' conversation records and git.

    python3 trace.py <out> <session id> <start commit> <round>=<agent id> ...

<round> is generator-1, first-user-1, learner-1, evaluator-1 and so on; <agent id> is the id the
Agent tool returned. Each round's entry says what that agent read, wrote and ran; the git entry says
what changed in the repository since <start commit>.
"""
import glob
import json
import os
import subprocess
import sys

READS = {"Read": "file_path", "Grep": "path", "Glob": "path"}
WRITES = {"Write": "file_path", "Edit": "file_path", "NotebookEdit": "notebook_path"}


def record(session, agent):
    pattern = os.path.join(os.path.expanduser("~"), ".claude", "projects", "*", session, "subagents",
                           f"agent-{agent}.jsonl")
    found = glob.glob(pattern)
    return found[0] if found else ""


def calls(path):
    """The tool calls in a conversation record, in order, as (tool name, input)."""
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            content = json.loads(line).get("message", {}).get("content")
            for c in content if isinstance(content, list) else []:
                if c.get("type") == "tool_use":
                    out.append((c["name"], c.get("input", {})))
    return out


def summary(path):
    read, wrote, ran = [], [], []
    for name, given in calls(path):
        if name in READS and given.get(READS[name]):
            read.append(given[READS[name]])
        elif name in WRITES:
            wrote.append(given[WRITES[name]])
        elif name == "Bash":
            ran.append(given["command"].splitlines()[0])
    parts = [f"{label}: {', '.join(dict.fromkeys(items))}"
             for label, items in (("read", read), ("wrote", wrote)) if items]
    parts += [f"ran: {' | '.join(ran)}"] if ran else []
    return "; ".join(parts) or "used no tools"


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout.strip()


def changes(start):
    commits = git("rev-list", "--count", f"{start}..HEAD")
    changed = [line[3:] for line in git("status", "--porcelain").splitlines()]
    return f"commits since {start[:7]}: {commits}; changed: {', '.join(changed) or 'nothing'}"


def main(argv):
    if len(argv) < 4 or not all("=" in a for a in argv[4:]):
        print(__doc__.strip())
        return 2
    out, session, start = argv[1:4]
    trace, missing = [], []
    for pair in argv[4:]:
        name, agent = pair.split("=", 1)
        path = record(session, agent)
        if path:
            trace.append({name: summary(path)})
        else:
            missing.append(f"no conversation record for {name} ({agent})")
    if missing:
        print("\n".join(missing))
        return 1
    trace.append({"git": changes(start)})
    with open(out, encoding="utf-8") as f:
        ccs = json.load(f)
    ccs["episodic_trace"] = trace
    with open(out, "w", encoding="utf-8") as f:
        json.dump(ccs, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
