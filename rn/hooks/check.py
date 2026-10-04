#!/usr/bin/env python3
"""rn's checks on its own record, run by Claude Code hooks (see hooks.json).

Each check is a function returning a list of problems. A hook prints the problems and exits 2, which
Claude Code shows to the agent so it corrects them; it exits 0 when there are none, or when no rn
session is running on this branch.
"""
import json
import os
import re
import shlex
import subprocess
import sys

FIRST_USER = "rn:first-user"
KINDS = ("report", "feedback", "notes")
DECISION = re.compile(r"^● .+ ── .+ → .+$")
TRAILER = re.compile(r"^[A-Za-z][A-Za-z0-9-]*: \S")
FRONT_KEYS = ("rn", "pr", "status", "artifact-language", "conversation-language", "readme", "design",
              "verification")
HEADINGS = ("# Goal", "# Acceptance criteria", "## Attractive quality", "## Must-be quality",
            "# Assumptions", "# Rules", "# Tasks")
TASK = re.compile(r"^### \[( |x)\] #(\d+): \S")
ID = re.compile(r"\b([AM]\d+)\b")
PROPOSAL_POINT = re.compile(r"^- (Good|More)\b(.*?):")


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


def finished_by_head(top):
    """The session directory whose steering.md the last commit set to finished, or None: the commit
    that finishes a session is still checked, and still has to be pushed."""
    for path in git("diff", "--name-only", "HEAD~1", "HEAD", "--", ".rn", cwd=top).split():
        parts = path.split("/")
        if len(parts) == 3 and parts[2] == "steering.md":
            front = front_matter(git("show", "HEAD:" + path, cwd=top)) or {}
            before = front_matter(git("show", "HEAD~1:" + path, cwd=top)) or {}
            if front.get("status") == "finished" and before.get("status") != "finished":
                return os.path.join(top, ".rn", parts[1])
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


def last_line(msg):
    """The message's last line, past the trailers (e.g. Co-Authored-By) git or the harness adds."""
    lines = [l.strip() for l in msg.strip().splitlines() if l.strip()]
    while lines and TRAILER.match(lines[-1]):
        lines.pop()
    return lines[-1] if lines else ""


# Check 4: decision line.
def check_decision_line(msg):
    if not DECISION.match(last_line(msg)):
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
    last = last_line(msg)
    od = os.path.join(sdir, "open")
    names = sorted(os.listdir(od)) if os.path.isdir(od) else []
    kinds = [n.split("-")[1] for n in names if n.count("-") >= 2]
    if "waiting for #" in last or "── approved →" in last:
        bad = [n for n, k in zip(names, kinds) if k != "notes" or "proposal" in n]
        if bad:
            problems.append("stop at a sign-off: open/ must hold only notes of design points, not "
                            + ", ".join(bad))
        if "waiting for #" in last:
            defined = set(criteria(open(os.path.join(sdir, "steering.md")).read()))
            for line in msg.splitlines():
                m = PROPOSAL_POINT.match(line)
                if m and not (set(ID.findall(m.group(2))) & defined):
                    problems.append(f"proposal: `{line.strip()[:60]}` names no acceptance criterion "
                                    "by its ID")
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
    last = last_line(msg)
    diff = git("diff", "HEAD~1", "HEAD", "--", rel_sdir + "/steering.md", cwd=top)
    if re.search(r"^\+### \[x\] #\d+: .*sign-off", diff, re.M | re.I) or \
            re.search(r"^\+status: finished", diff, re.M):
        return "ty"
    if "── feedback in " in last:
        return "gm"
    if "→ paused at " in last:
        return "dn"
    return None


# Checks 9–11: keep agents apart. Only git run as a command counts, and only on the session's
# repository: a first user runs the work in a clone of its own, and text such as `grep 'git push'`
# runs no git.
GIT_WRITE = ("commit", "push")
GIT_READ = ("log", "show", "blame", "reflog")
HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
PREFIX = ("env", "command", "exec", "time", "nohup", "sudo")


def without_heredocs(cmd):
    out, end = [], None
    for line in cmd.split("\n"):
        if end is not None:
            if line.strip() == end:
                end = None
            continue
        out.append(line)
        m = HEREDOC.search(line)
        if m:
            end = m.group(2)
    return "\n".join(out)


def git_runs(cmd, cwd):
    """Each git command the shell command runs, as (subcommand, the directory it acts in)."""
    text = without_heredocs(cmd)
    try:
        lex = shlex.shlex(text.replace("\n", " ; "), posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        tokens = list(lex)
    except ValueError:
        tokens = re.findall(r"[;&|()]+|[^\s;&|()]+", text.replace("\n", " ; "))
    runs, dirs, here, words = [], [], cwd, []

    def flush():
        nonlocal here
        w = list(words)
        words.clear()
        while w and (re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", w[0]) or w[0] in PREFIX):
            w.pop(0)
        if not w:
            return
        if w[0] == "cd":
            target = w[1] if len(w) > 1 else "~"
            here = os.path.join(here, os.path.expanduser(target))
        elif os.path.basename(w[0]) == "git":
            d, i = here, 1
            while i < len(w) and w[i].startswith("-"):
                if w[i] == "-C" and i + 1 < len(w):
                    d = os.path.join(d, os.path.expanduser(w[i + 1]))
                    i += 1
                elif w[i] in ("-c", "--git-dir", "--work-tree", "--namespace") and i + 1 < len(w):
                    i += 1
                i += 1
            if i < len(w):
                runs.append((w[i], d))

    for t in tokens:
        if t and set(t) <= set(";&|()<>"):
            flush()
            if "(" in t:
                dirs.append(here)
            if ")" in t and dirs:
                here = dirs.pop()
        else:
            words.append(t)
    flush()
    return runs


def on_repo(runs, subs, top):
    return [s for s, d in runs if s in subs and os.path.isdir(d) and root(d) == top]


def reads_quoted(name):
    """A question or proposal item is the work a first user is given to take up."""
    return re.match(r"^\d{2}-notes-(question|proposal)\.md$", name) is not None


def reads_maker_account(path, sdir, own):
    if not sdir:
        return False
    p = os.path.realpath(path)
    od = os.path.join(sdir, "open")
    if p.startswith(od + os.sep):
        name = os.path.basename(p)
        return name != own and not reads_quoted(name) and ("-notes-" in name or "-report-" in name)
    return "/.git/" in p + "/" and p.split("/.git/")[0] == os.path.dirname(os.path.dirname(sdir))


# Check 14: the conductor talks in the conversation language, judged by script.
SCRIPTS = (  # script, ranges, whether it spaces its words
    ("latin", ((0x41, 0x5A), (0x61, 0x7A), (0xC0, 0x24F)), True),
    ("cyrillic", ((0x400, 0x4FF),), True),
    ("greek", ((0x370, 0x3FF),), True),
    ("arabic", ((0x600, 0x6FF),), True),
    ("hebrew", ((0x590, 0x5FF),), True),
    ("devanagari", ((0x900, 0x97F),), True),
    ("kana", ((0x3040, 0x30FF),), False),
    ("han", ((0x3400, 0x4DBF), (0x4E00, 0x9FFF)), False),
    ("hangul", ((0x1100, 0x11FF), (0xAC00, 0xD7AF)), False),
    ("thai", ((0xE00, 0xE7F),), False),
)
LANGUAGES = {  # language name, lower-cased, to the scripts its text is written in
    ("japanese", "日本語"): ("kana", "han"),
    ("chinese", "中文", "中国語"): ("han",),
    ("korean", "한국어", "韓国語"): ("hangul",),
    ("russian", "ukrainian", "bulgarian"): ("cyrillic",),
    ("greek",): ("greek",),
    ("arabic", "persian", "urdu"): ("arabic",),
    ("hebrew",): ("hebrew",),
    ("hindi",): ("devanagari",),
    ("thai",): ("thai",),
    ("english", "french", "german", "spanish", "portuguese", "italian", "dutch", "swedish",
     "norwegian", "danish", "finnish", "polish", "czech", "turkish", "vietnamese", "indonesian",
     "英語"): ("latin",),
}


def script_of(ch):
    o = ord(ch)
    for name, ranges, spaced in SCRIPTS:
        if any(a <= o <= b for a, b in ranges):
            return name, spaced
    return None, False


def script_share(text, scripts):
    """How much of the text's prose is in the given scripts: a word of a script that spaces its
    words counts one, a character of one that does not counts a half. None when too short to say."""
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"^\s*● .*$", " ", text, flags=re.M)  # a decision line quoted from the record
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"\S*[/\\]\S*", " ", text)
    units, prev = {}, None
    for ch in text:
        name, spaced = script_of(ch)
        if name and (not spaced or name != prev):
            units[name] = units.get(name, 0) + (1 if spaced else 0.5)
        prev = name
    total = sum(units.values())
    if total < 3:
        return None
    return sum(units.get(n, 0) for n in scripts) / total


def text_of(sdir):
    return open(os.path.join(sdir, "steering.md")).read()


def unquoted(steering, message):
    """The message without what it quotes from the record, which is in the artifact language: the
    map's goal line, the goal, and the task names."""
    message = re.sub(r"^\s*── .* ──\s*$", " ", message, flags=re.M)
    quoted = [l.strip() for l in section(steering, "# Goal", 1) if l.strip()]
    for line in steering.splitlines():
        m = re.match(r"^### \[[ x]\] #\d+: (.+)$", line)
        if m:
            quoted.append(m.group(1).strip())
    for q in sorted(quoted, key=len, reverse=True):
        message = message.replace(q, " ")
    return message


def check_language(sdir, message):
    front = front_matter(text_of(sdir)) or {}
    lang = front.get("conversation-language", "").strip().lower()
    scripts = next((v for k, v in LANGUAGES.items() if lang in k), None)
    if not scripts or not message:
        return []
    share = script_share(unquoted(text_of(sdir), message), scripts)
    if share is not None and share < 0.5:
        return [f"your message to the user is not in {front['conversation-language']}, the "
                "conversation language steering.md records: say it again in that language"]
    return []


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
    if not sdir and event in ("post", "stop"):
        sdir = finished_by_head(top)
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
    runs = git_runs(inp.get("command", ""), cwd) if tool == "Bash" else []
    if event == "pre":
        if agent and on_repo(runs, GIT_WRITE, top):
            emit([f"only the conductor uses git; {agent} may not commit or push"])
        # Checks 4–7 run once the commit is made; a push in the same command would carry a breach
        # to the pull request before they could stop it.
        if not agent and on_repo(runs, ("commit",), top) and on_repo(runs, ("push",), top):
            emit(["commit and push in separate commands, so rn's checks run on the commit before "
                  "it is pushed"])
        if agent == FIRST_USER:
            own_p = os.path.join(store, f"first-user-{data.get('agent_id', '')}.txt")
            own = open(own_p).read().strip() if os.path.isfile(own_p) else ""
            if on_repo(runs, GIT_READ, top):
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
        if not agent and on_repo(runs, ("commit",), top):
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
        # Every end is checked, the second included, but for check 13: any end may speak to the
        # user, and any may leave commits only on this machine.
        language = check_language(sdir, data.get("last_assistant_message") or "")
        problems = form_checks(top, sdir)
        ahead = git("rev-list", "--count", "@{u}..HEAD", cwd=top).strip()
        if not git("rev-parse", "--abbrev-ref", "@{u}", cwd=top).strip():
            problems.append("the branch has no remote branch; push it")
        elif ahead and ahead != "0":
            problems.append(f"{ahead} commit(s) not pushed; push them")
        # Check 13: the turn ends only where the user has something to decide.
        last = last_line(git("log", "-1", "--format=%B", cwd=top))
        stop = re.search(r"→ waiting for #|── approved →|── feedback in |→ paused at ", last)
        od = os.path.join(sdir, "open")
        asking = os.path.isdir(od) and any("-notes-question" in n for n in os.listdir(od))
        if not problems and not stop and not asking and not data.get("stop_hook_active"):
            problems.append("nothing here is for the user to decide: go on with the next move. End the "
                            "turn only at a sign-off or with a question, or again if you were answering "
                            "the user's own words")
        problems = language + problems
        if problems:
            print(json.dumps({"decision": "block", "reason": "rn check:\n- " + "\n- ".join(problems)}))
        sys.exit(0)

if __name__ == "__main__":
    main()
