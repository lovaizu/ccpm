"""Check 7: a sign-off is passed, or the session finished, only after the user typed /rn:ty;
feedback is taken only after /rn:gm, and a pause made only after /rn:dn."""
import json
import os
import re

from record import git, last_line

COMMANDS = ("ty", "gm", "dn")


def notes_path(store, session_id):
    return os.path.join(store, f"typed-{session_id}.json")


def note(store, session_id, command_name):
    """Remember that the user typed one of the commands."""
    name = (command_name or "").split(":")[-1]
    if name in COMMANDS:
        p = notes_path(store, session_id)
        try:
            notes = json.load(open(p))
        except Exception:
            notes = []
        notes.append(name)
        json.dump(notes, open(p, "w"))


def take_note(store, session_id, cmd, parent):
    """Spend one typed command on the commit on top of parent. Amending that commit keeps its
    parent, so it is the same record rewritten, not a second one, and passes without another
    command."""
    p = notes_path(store, session_id)
    given = os.path.join(store, f"given-{session_id}.json")
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


def check(top, rel_sdir, msg, store, session_id):
    need = needed_command(top, rel_sdir, msg)
    parent = git("rev-parse", "HEAD~1", cwd=top).strip()
    if need and not take_note(store, session_id, need, parent):
        return [f"this commit records what only the user's /rn:{need} may; "
                "undo it with git reset --soft HEAD~1"]
    return []
