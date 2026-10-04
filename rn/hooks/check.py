#!/usr/bin/env python3
"""rn's checks on its own record, run by Claude Code hooks (see hooks.json).

Each check is a function returning a list of problems. A hook prints the problems and exits 2, which
Claude Code shows to the agent so it corrects them; it exits 0 when there are none, or when no rn
session is running on this branch.
"""
import json
import os
import re
import subprocess
import sys

FIRST_USER = "rn:first-user"
KINDS = ("report", "feedback", "notes")
DECISION = re.compile(r"^● .+ ── .+ → .+$")
FRONT_KEYS = ("rn", "pr", "status", "artifact-language", "conversation-language", "readme", "design",
              "verification")
HEADINGS = ("# Goal", "# Acceptance criteria", "## Attractive quality", "## Must-be quality",
            "# Assumptions", "# Rules", "# Tasks")
TASK = re.compile(r"^### \[( |x)\] #(\d+): \S")
ID = re.compile(r"\b([AM]\d+)\b")


def git(*args, cwd=None):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def root(cwd):
    top = git("rev-parse", "--show-toplevel", cwd=cwd).strip()
    return os.path.realpath(top) if top else ""


def session(top):
    """The session directory on this branch whose status is not finished, or None."""
    base = os.path.join(top, ".rn")
    if not os.path.isdir(base):
        return None
    for name in sorted(os.listdir(base), reverse=True):
        st = os.path.join(base, name, "steering.md")
        if os.path.isfile(st):
            front = front_matter(open(st).read())
            if front is not None and front.get("status") != "finished":
                return os.path.join(base, name)
    return None


def front_matter(text):
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    out = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


# Check 1: steering.md keeps its form.
def check_steering(text):
    problems = []
    front = front_matter(text)
    if front is None:
        return ["steering.md: front matter between --- lines is missing"]
    for k in FRONT_KEYS:
        if k not in front:
            problems.append(f"steering.md: front matter has no `{k}`")
    if front.get("status") not in ("running", "finished"):
        problems.append("steering.md: `status` is neither running nor finished")
    lines = text.splitlines()
    for h in HEADINGS:
        if h not in lines:
            problems.append(f"steering.md: heading `{h}` is missing")
    ids = []
    for line in lines:
        if line.startswith("### "):
            m = TASK.match(line)
            if not m:
                problems.append(f"steering.md: task heading `{line}` is not `### [ ] #N: name`")
            else:
                ids.append(m.group(2))
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        problems.append("steering.md: task ids repeat: " + ", ".join("#" + i for i in dup))
    crit = criteria(text)
    dupc = sorted({i for i in crit if crit.count(i) > 1})
    if dupc:
        problems.append("steering.md: criterion ids repeat: " + ", ".join(dupc))
    return problems


def section(text, heading, stop_level):
    lines = text.splitlines()
    try:
        i = lines.index(heading)
    except ValueError:
        return []
    out = []
    for line in lines[i + 1:]:
        if re.match(r"^#{1,%d} " % stop_level, line):
            break
        out.append(line)
    return out


def criteria(text):
    out = []
    for line in section(text, "# Acceptance criteria", 1):
        m = re.match(r"^- ([AM]\d+):", line)
        if m:
            out.append(m.group(1))
    return out


# Check 2: open/ file names.
def check_open_names(sdir):
    problems = []
    od = os.path.join(sdir, "open")
    if not os.path.isdir(od):
        return problems
    for name in sorted(os.listdir(od)):
        m = re.match(r"^(\d{2})-([a-z]+)-[a-z0-9][a-z0-9-]*\.md$", name)
        if not m or m.group(2) not in KINDS:
            problems.append(f"open/{name}: not named {{NN}}-{{kind}}-{{about}}.md with kind "
                            + " | ".join(KINDS))
    return problems


# Check 3: IDs traced; the verification document's form.
def check_trace(top, sdir):
    problems = []
    text = open(os.path.join(sdir, "steering.md")).read()
    front = front_matter(text) or {}
    defined = set(criteria(text))
    tasks_text = "\n".join(section(text, "# Tasks", 1))
    for i in sorted(set(ID.findall(tasks_text)) - defined):
        problems.append(f"steering.md: task refers to {i}, which no acceptance criterion has")
    vpath = os.path.join(top, front.get("verification", "docs/verification.md"))
    if os.path.isfile(vpath):
        vtext = open(vpath).read()
        heads = re.findall(r"^### ([AM]\d+):", vtext, re.M)
        named = set(ID.findall(vtext))
        for i in sorted(named - defined):
            problems.append(f"verification: refers to {i}, which steering.md does not define")
        if "## Scenes" not in vtext.splitlines():
            problems.append("verification: `## Scenes` is missing")
        if "## Machine checks" not in vtext.splitlines():
            problems.append("verification: `## Machine checks` is missing")
        for i in sorted(d for d in defined if d.startswith("A") and d not in heads):
            problems.append(f"verification: attractive criterion {i} has no `### {i}:` scene")
        for i in sorted(d for d in defined if d.startswith("M") and d not in named):
            problems.append(f"verification: must-be criterion {i} is named in no scene or check")
    planned = any(TASK.match(l) and "sign-off" not in l.lower()
                  for l in section(text, "# Tasks", 1))
    if planned:
        served = set(ID.findall(tasks_text))
        for i in sorted(defined - served):
            problems.append(f"steering.md: criterion {i} is served by no task")
    return problems


def form_checks(top, sdir):
    st = os.path.join(sdir, "steering.md")
    return check_steering(open(st).read()) + check_open_names(sdir) + check_trace(top, sdir)


# Check 4: decision line.
def check_decision_line(msg):
    last = [l for l in msg.strip().splitlines() if l.strip()][-1:] or [""]
    if not DECISION.match(last[0].strip()):
        return ["commit message: the last line is not a decision line `● … ── … → …`"]
    return []


def norm(s):
    return " ".join(s.split())


# Check 5: a settled open/ item is whole in the commit message.
def check_settled_whole(top, rel_sdir, msg):
    problems = []
    gone = git("diff", "--name-only", "--diff-filter=D", "HEAD~1", "HEAD", "--",
               rel_sdir + "/open", cwd=top).split()
    flat = norm(msg)
    for path in gone:
        body = git("show", "HEAD~1:" + path, cwd=top)
        if norm(body) not in flat:
            problems.append(f"commit message: {os.path.basename(path)} left open/ but is not whole "
                            "in the message")
    return problems


# Check 6: a stop commit leaves in open/ only what its kind allows.
def check_stop(top, sdir, msg):
    problems = []
    last = msg.strip().splitlines()[-1] if msg.strip() else ""
    od = os.path.join(sdir, "open")
    names = sorted(os.listdir(od)) if os.path.isdir(od) else []
    kinds = [n.split("-")[1] for n in names if n.count("-") >= 2]
    if "waiting for #" in last or "── approved →" in last:
        bad = [n for n, k in zip(names, kinds) if k != "notes" or "proposal" in n]
        if bad:
            problems.append("stop at a sign-off: open/ must hold only notes of design points, not "
                            + ", ".join(bad))
        if "waiting for #" in last:
            head = git("rev-parse", "--abbrev-ref", "origin/HEAD", cwd=top).strip()
            if head and subprocess.run(["git", "merge-base", "--is-ancestor", head, "HEAD"],
                                       cwd=top).returncode != 0:
                problems.append(f"stop at a sign-off: {head} is not merged into the branch")
    if "── feedback in " in last:
        if "feedback" not in kinds:
            problems.append("stop after /rn:gm: open/ holds no feedback item")
    return problems


# Check 7: approval, feedback, and pause only after the user typed the command.
def notes_path(data, session_id):
    return os.path.join(data, f"typed-{session_id}.json")


def take_note(data, session_id, cmd, parent):
    """Spend one typed command on the commit on top of parent. Amending that commit keeps its parent,
    so it is the same record rewritten, not a second one, and passes without another command."""
    p = notes_path(data, session_id)
    given = os.path.join(data, f"given-{session_id}.json")
    try:
        notes = json.load(open(p))
    except Exception:
        notes = []
    try:
        spent = json.load(open(given))
    except Exception:
        spent = {}
    if parent and spent.get(cmd) == parent:
        return True
    if cmd in notes:
        notes.remove(cmd)
        json.dump(notes, open(p, "w"))
        spent[cmd] = parent
        json.dump(spent, open(given, "w"))
        return True
    return False


def needed_command(top, rel_sdir, msg):
    last = msg.strip().splitlines()[-1] if msg.strip() else ""
    diff = git("diff", "HEAD~1", "HEAD", "--", rel_sdir + "/steering.md", cwd=top)
    if re.search(r"^\+### \[x\] #\d+: .*sign-off", diff, re.M | re.I) or \
            re.search(r"^\+status: finished", diff, re.M):
        return "ty"
    if "── feedback in " in last:
        return "gm"
    if "→ paused at " in last:
        return "dn"
    return None


# Checks 9–11: keep agents apart.
GIT_WRITE = re.compile(r"\bgit\b[^|;&]*\b(commit|push)\b")
GIT_READ = re.compile(r"\bgit\b[^|;&]*\b(log|show|blame|reflog)\b")


def reads_maker_account(path, sdir, own):
    if not sdir:
        return False
    p = os.path.realpath(path)
    od = os.path.join(sdir, "open")
    if p.startswith(od + os.sep):
        name = os.path.basename(p)
        return name != own and ("-notes-" in name or "-report-" in name)
    return "/.git/" in p + "/" and p.split("/.git/")[0] == os.path.dirname(os.path.dirname(sdir))


def emit(problems):
    if problems:
        print("rn check:\n- " + "\n- ".join(problems), file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


def main():
    event = sys.argv[1]
    data = json.load(sys.stdin)
    cwd = data.get("cwd") or os.getcwd()
    top = root(cwd)
    store = os.environ.get("CLAUDE_PLUGIN_DATA") or os.path.join(os.path.expanduser("~"), ".rn-data")
    os.makedirs(store, exist_ok=True)
    if event == "prompt":
        name = (data.get("command_name") or "").split(":")[-1]
        if name in ("ty", "gm", "dn"):
            p = notes_path(store, data.get("session_id", ""))
            try:
                notes = json.load(open(p))
            except Exception:
                notes = []
            notes.append(name)
            json.dump(notes, open(p, "w"))
        sys.exit(0)
    if not top:
        sys.exit(0)
    sdir = session(top)
    if not sdir:
        sys.exit(0)
    rel = os.path.relpath(sdir, top)
    if event == "compact":
        print(f"rn: the conversation was just summarized, and a summary drops details. Before going "
              f"on, take up the session from its record as /rn:up does: read {rel}/steering.md, every "
              f"file in {rel}/open/, and the last decision line (git log -1), and go on from its next "
              f"move.")
        sys.exit(0)
    agent = data.get("agent_type") or ""
    tool = data.get("tool_name", "")
    inp = data.get("tool_input") or {}
    if event == "pre":
        cmd = inp.get("command", "") if tool == "Bash" else ""
        if agent and GIT_WRITE.search(cmd):
            emit([f"only the conductor uses git; {agent} may not commit or push"])
        if agent == FIRST_USER:
            own_p = os.path.join(store, f"first-user-{data.get('agent_id', '')}.txt")
            own = open(own_p).read().strip() if os.path.isfile(own_p) else ""
            if tool == "Bash" and GIT_READ.search(cmd):
                emit(["the first user does not read commit messages or history"])
            path = inp.get("file_path") or inp.get("path") or ""
            if tool in ("Write", "Edit", "NotebookEdit") and path:
                name = os.path.basename(path)
                target = os.path.realpath(path)
                if not own:
                    ok = (os.path.dirname(target) == os.path.join(sdir, "open")
                          and re.match(r"^\d{2}-report-", name)
                          and not git("ls-files", target, cwd=top).strip())
                    if not ok:
                        emit([f"the first user writes only its own new report in open/, not {name}"])
                    open(own_p, "w").write(name)
                elif name != own or os.path.dirname(target) != os.path.join(sdir, "open"):
                    emit([f"the first user writes only its report {own}"])
            if tool in ("Read", "Grep", "Glob") and path and reads_maker_account(path, sdir, own):
                emit(["the first user does not read notes or earlier reports"])
        # Check 12: an agent left running reports to a turn that has already ended.
        if not agent and tool == "Agent" and inp.get("run_in_background"):
            emit(["start the agent in the foreground and wait for what it returns; your turn ends "
                  "only when you stop for the user or ask them a question"])
        if not agent and tool == "SendMessage":
            emit(["an agent continued by message runs in the background; start a fresh agent in the "
                  "foreground with the paths of what the last one left, and wait for what it returns"])
        if not agent and tool == "Agent" and inp.get("subagent_type") == FIRST_USER:
            emit(form_checks(top, sdir))
        sys.exit(0)
    if event == "post":
        if tool in ("Write", "Edit"):
            path = os.path.realpath(inp.get("file_path", ""))
            if path.startswith(sdir + os.sep) or path.endswith("verification.md"):
                emit(form_checks(top, sdir))
        if tool == "Bash" and not agent and re.search(r"\bgit\b[^|;&]*\bcommit\b",
                                                      inp.get("command", "")):
            msg = git("log", "-1", "--format=%B", cwd=top)
            problems = check_decision_line(msg) + check_settled_whole(top, rel, msg) + \
                check_stop(top, sdir, msg)
            need = needed_command(top, rel, msg)
            parent = git("rev-parse", "HEAD~1", cwd=top).strip()
            if need and not take_note(store, data.get("session_id", ""), need, parent):
                problems.append(f"this commit records what only the user's /rn:{need} may; "
                                "undo it with git reset --soft HEAD~1")
            emit(problems)
        sys.exit(0)
    if event == "stop":
        if data.get("stop_hook_active"):
            sys.exit(0)
        problems = form_checks(top, sdir)
        ahead = git("rev-list", "--count", "@{u}..HEAD", cwd=top).strip()
        if not git("rev-parse", "--abbrev-ref", "@{u}", cwd=top).strip():
            problems.append("the branch has no remote branch; push it")
        elif ahead and ahead != "0":
            problems.append(f"{ahead} commit(s) not pushed; push them")
        # Check 13: the turn ends only where the user has something to decide.
        last = git("log", "-1", "--format=%B", cwd=top).strip().splitlines()
        last = last[-1] if last else ""
        stop = re.search(r"→ waiting for #|── approved →|── feedback in |→ paused at ", last)
        od = os.path.join(sdir, "open")
        asking = os.path.isdir(od) and any("-notes-question" in n for n in os.listdir(od))
        if not problems and not stop and not asking:
            problems.append("nothing here is for the user to decide: go on with the next move. End the "
                            "turn only at a sign-off or with a question, or again if you were answering "
                            "the user's own words")
        if problems:
            print(json.dumps({"decision": "block", "reason": "rn check:\n- " + "\n- ".join(problems)}))
        sys.exit(0)


if __name__ == "__main__":
    main()
