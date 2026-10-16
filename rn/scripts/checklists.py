"""The checklists a kind is made and checked by: rn's, those their openings apply, the user's."""

import json
import os
import re

KIND = re.compile(r"[a-z]+(-[a-z]+)*")
NAMED = re.compile(r"`([a-z]+(?:-[a-z]+)*)\.md`")
# The opening, the text before the first section, is where a checklist names those that apply.
CHECKLIST = re.compile(r"---\n(.*?)\n---\n(.*?)(?:^## |\Z)", re.DOTALL | re.MULTILINE)
RN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "checklists")


# Those for every document lie at the top, those for what goes into the product in product/, and
# those for rn's own conduct of a session in session/.
FOLDERS = [RN, os.path.join(RN, "product"), os.path.join(RN, "session")]


def rn_checklist(kind):
    for folder in FOLDERS:
        path = os.path.join(folder, kind + ".md")
        if os.path.isfile(path):
            return path
    return None


def read(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    match = CHECKLIST.match(text)
    front_matter, opening = match.groups() if match else ("", "")
    fields = dict(re.findall(r"(\w+): *(.+)", front_matter))
    if "name" not in fields or "version" not in fields:
        raise ValueError(
            f"{path}: open the checklist with front matter giving its name and version"
        )
    return {"path": path, "name": fields["name"], "version": fields["version"]}, opening


def find(kind):
    if not KIND.fullmatch(kind):
        raise ValueError(
            f"{kind}: a kind is a word or words joined by hyphens, such as release-notes"
        )
    user = os.path.join(".rn", "checklists", kind + ".md")
    found = [read(path) for path in [rn_checklist(kind), user] if path and os.path.isfile(path)]
    applied = [
        read(rn_checklist(name))
        for _, opening in found
        for name in NAMED.findall(opening)
        if rn_checklist(name)
    ]
    listed = []
    for checklist, _ in applied + found:
        if checklist not in listed:
            listed.append(checklist)
    return json.dumps(listed)
