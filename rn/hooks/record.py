"""rn's record as the checks read it: the session directory, its steering.md, and git."""
import os
import re
import subprocess
import sys

TRAILER = re.compile(r"^[A-Za-z][A-Za-z0-9-]*: \S")
COMMANDS = ("on", "up", "dn", "ty", "gm")


def git(*args, cwd=None):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def root(cwd):
    top = git("rev-parse", "--show-toplevel", cwd=cwd).strip()
    return os.path.realpath(top) if top else ""


def store():
    """Where rn keeps what a hook must remember between calls, such as the commands the user
    typed."""
    path = os.environ.get("CLAUDE_PLUGIN_DATA") or os.path.join(os.path.expanduser("~"), ".rn-data")
    os.makedirs(path, exist_ok=True)
    return path


def rn_command(command_name):
    """The rn command the user typed, such as `up` for `/rn:up`, or None for any other command."""
    space, _, name = (command_name or "").rpartition(":")
    return name if space in ("", "rn") and name in COMMANDS else None


def marker(store, session_id):
    return os.path.join(store, f"rn-{session_id}")


def mark(store, session_id):
    """Remember that this conversation runs rn: the user typed an rn command in it."""
    open(marker(store, session_id), "w").close()


def front_matter(text):
    """The front matter's keys and values, or None when the text has none: a session started by an
    older rn, which /rn:up brings to the current form."""
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


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


def find(data, finished_too=False):
    """(the directory the hook runs in, the repository's top, the session directory), or None when
    the conversation does not run rn, or no rn session is running on this branch. An agent's tool
    call carries the session_id of the conversation that started it. With finished_too, the session
    the last commit finished counts as running."""
    sid = data.get("session_id")
    if not sid or not os.path.isfile(marker(store(), sid)):
        return None
    cwd = data.get("cwd") or os.getcwd()
    top = root(cwd)
    if not top:
        return None
    sdir = session(top)
    if not sdir and finished_too:
        sdir = finished_by_head(top)
    return (cwd, top, sdir) if sdir else None


def steering(sdir):
    return open(os.path.join(sdir, "steering.md")).read()


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


def open_items(sdir):
    od = os.path.join(sdir, "open")
    return sorted(os.listdir(od)) if os.path.isdir(od) else []


def last_line(msg):
    """The message's last line, past the trailers (e.g. Co-Authored-By) git or the harness adds."""
    lines = [l.strip() for l in msg.strip().splitlines() if l.strip()]
    while lines and TRAILER.match(lines[-1]):
        lines.pop()
    return lines[-1] if lines else ""


def head_message(top):
    return git("log", "-1", "--format=%B", cwd=top)


def report(problems):
    """Show the problems to the agent, which Claude Code does on exit code 2, so it corrects
    them."""
    if problems:
        print("rn check:\n- " + "\n- ".join(problems), file=sys.stderr)
        return 2
    return 0
