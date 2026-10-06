"""Check 11: the first user does not read the session's commit messages or history, notes, or
earlier reports. A question or proposal item it is given to take up is the work it uses, so it reads
that."""
import os
import re

from shell import on_repo
from checks.first_user_writes import FIRST_USER, own_report


def reads_quoted(name):
    """A question or proposal item is the work a first user is given to take up."""
    return re.match(r"^\d{2}-notes-(question|proposal)\.md$", name) is not None


def reads_maker_account(path, sdir, own):
    p = os.path.realpath(path)
    od = os.path.join(sdir, "open")
    if p.startswith(od + os.sep):
        name = os.path.basename(p)
        return name != own and not reads_quoted(name) and ("-notes-" in name or "-report-" in name)
    return "/.git/" in p + "/" and p.split("/.git/")[0] == os.path.dirname(os.path.dirname(sdir))


def check_history(data, runs, top):
    if data.get("agent_type") == FIRST_USER and \
            on_repo(runs, ("log", "show", "blame", "reflog"), top):
        return ["the first user does not read commit messages or history"]
    return []


def check_files(data, sdir, store):
    inp = data.get("tool_input") or {}
    path = inp.get("file_path") or inp.get("path") or ""
    if data.get("agent_type") == FIRST_USER and data.get("tool_name") in ("Read", "Grep", "Glob") \
            and path and reads_maker_account(path, sdir, own_report(store, data)):
        return ["the first user does not read notes or earlier reports"]
    return []
