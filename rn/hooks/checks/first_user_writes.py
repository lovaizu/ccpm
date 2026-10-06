"""Check 10: the first user writes only its own report file."""
import os
import re

from record import git

FIRST_USER = "rn:first-user"


def own_path(store, data):
    return os.path.join(store, f"first-user-{data.get('agent_id', '')}.txt")


def own_report(store, data):
    """The name of the report this first user has written, or ""."""
    p = own_path(store, data)
    return open(p).read().strip() if os.path.isfile(p) else ""


def check(data, top, sdir, store):
    inp = data.get("tool_input") or {}
    path = inp.get("file_path") or inp.get("path") or ""
    if data.get("agent_type") != FIRST_USER or not path or \
            data.get("tool_name") not in ("Write", "Edit", "NotebookEdit"):
        return []
    own = own_report(store, data)
    name = os.path.basename(path)
    target = os.path.realpath(path)
    if not own:
        ok = (os.path.dirname(target) == os.path.join(sdir, "open")
              and re.match(r"^\d{2}-report-", name)
              and not git("ls-files", target, cwd=top).strip())
        if not ok:
            return [f"the first user writes only its own new report in open/, not {name}"]
        open(own_path(store, data), "w").write(name)
    elif name != own or os.path.dirname(target) != os.path.join(sdir, "open"):
        return [f"the first user writes only its report {own}"]
    return []
