"""rn's record as its hooks read it: the conversation that runs rn, and the session directory."""
import os
import subprocess

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


def session(top):
    """The session directory this branch changed whose status is not finished, or None: sessions
    already on the default branch, from earlier work, are not this branch's."""
    base = next((b for b in (git("merge-base", "HEAD", ref, cwd=top).strip()
                             for ref in ("origin/HEAD", "origin/main", "origin/master", "main", "master"))
                 if b), "")
    if not base:
        return None
    changed = git("diff", "--name-only", base, "HEAD", "--", ".rn/*/steering.md", cwd=top).split()
    for rel in sorted(changed, reverse=True):
        st = os.path.join(top, rel)
        if os.path.isfile(st) and "\nstatus: finished\n" not in open(st).read():
            return os.path.dirname(st)
    return None


def find(data):
    """(the directory the hook runs in, the repository's top, the session directory), or None when
    the conversation does not run rn, or no rn session is running on this branch."""
    sid = data.get("session_id")
    if not sid or not os.path.isfile(marker(store(), sid)):
        return None
    cwd = data.get("cwd") or os.getcwd()
    top = root(cwd)
    if not top:
        return None
    sdir = session(top)
    return (cwd, top, sdir) if sdir else None
