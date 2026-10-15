"""The checklists a kind of document is made and judged by: writ's for the kind, the user's for it,
and each one their openings say applies with them."""

import json
import os
import re

WRIT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "checklists")
USER = os.path.join(".writ", "checklists")
KIND = re.compile(r"^[a-z]+(-[a-z]+)*$")


class Stop(Exception):
    """Ends the command, saying why."""


def front(path):
    """The fields of the front matter the file opens with."""
    with open(path) as f:
        lines = f.read().splitlines()
    if lines[:1] != ["---"] or "---" not in lines[1:]:
        return {}
    fields = (re.match(r"(\w+):\s*(.*)", line) for line in lines[1 : lines.index("---", 1)])
    return dict(m.groups() for m in fields if m)


def applies(path):
    """The names of writ's checklists the opening, the text before the first section, says apply."""
    with open(path) as f:
        opening = f.read().partition("\n## ")[0]
    return [n for n in re.findall(r"`([a-z-]+)\.md`", opening) if os.path.isfile(writs(n))]


def writs(name):
    return os.path.join(WRIT, f"{name}.md")


def named(path):
    fields = front(path)
    if not {"name", "version"} <= fields.keys():
        raise Stop(f"{path}: open the checklist with front matter giving its name and version")
    return {"path": path, "name": fields["name"], "version": fields["version"]}


def checklists(kind):
    """Prints, as JSON, the checklists for the kind, those that apply with them first."""
    if not KIND.match(kind):
        raise Stop(f"{kind}: a kind is a word or words joined by hyphens, such as release-notes")
    own = [p for p in (writs(kind), os.path.join(USER, f"{kind}.md")) if os.path.isfile(p)]
    found = [writs(n) for p in own for n in applies(p)]
    print(json.dumps([named(p) for p in dict.fromkeys(found + own)], indent=1))
