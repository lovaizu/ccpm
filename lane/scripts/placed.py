"""lane's code placed in a plugin's hooks/lane/: a relative link to lane's in a plugin of the ccpm
marketplace, a copy with lane's version in VERSION anywhere else."""

from __future__ import annotations

import json
import os
import re
import shutil

LANE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE = os.path.join(LANE, "hooks", "lane")

# The marketplace whose plugins take lane's code through a link to lane beside them, as installing
# copies what a link within the marketplace points to.
MARKETPLACE = "ccpm"


def marketplace(folder: str) -> str | None:
    """The name of the marketplace kept in the folder; None where it keeps none, or none that can
    be read."""
    try:
        with open(
            os.path.join(folder, ".claude-plugin", "marketplace.json"), encoding="utf-8"
        ) as f:
            given = json.load(f)
    except (OSError, ValueError):
        return None
    return given.get("name") if isinstance(given, dict) else None


def lanes_own(place: str) -> bool:
    """Whether the folder is lane's code itself, as hooks/lane/ is on lane."""
    return os.path.realpath(place) == os.path.realpath(CODE)


def lane_version() -> str:
    """lane's version, as its plugin.json gives it."""
    with open(os.path.join(LANE, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
        return json.load(f)["version"]


def code_put(root: str) -> None:
    """Puts lane's code in the plugin's hooks/lane/, in place of what was there; on lane itself,
    whose hooks/lane/ is that code, leaves it as it is."""
    place = os.path.join(root, "hooks", "lane")
    if lanes_own(place):
        return
    if os.path.islink(place):
        os.remove(place)
    elif os.path.isdir(place):
        shutil.rmtree(place)
    os.makedirs(os.path.dirname(place), exist_ok=True)
    above = os.path.dirname(os.path.abspath(root))
    beside = os.path.join(above, "lane", "hooks", "lane")
    if marketplace(above) == MARKETPLACE and os.path.isdir(beside):
        os.symlink(os.path.join("..", "..", "lane", "hooks", "lane"), place)
        return
    shutil.copytree(CODE, place, ignore=shutil.ignore_patterns("__pycache__"))
    with open(os.path.join(place, "VERSION"), "w", encoding="utf-8") as f:
        f.write(lane_version() + "\n")


def semver(text: str) -> tuple[int, ...]:
    """The version the text gives as major, minor and patch, to be compared as numbers; none,
    which is lower than every version, where it gives none."""
    found = re.fullmatch(r"([0-9]+)\.([0-9]+)\.([0-9]+)", text.strip())
    return tuple(map(int, found.groups())) if found else ()


def older(root: str) -> str | None:
    """The version of the plugin's copy of lane's code, as its VERSION gives it, where the copy is
    older than lane: its version lower, or not given; None where hooks/lane/ is no copy, being a
    link, lane's own or not there, or is a copy of lane's version or a newer."""
    place = os.path.join(root, "hooks", "lane")
    if os.path.islink(place) or not os.path.isdir(place) or lanes_own(place):
        return None
    try:
        with open(os.path.join(place, "VERSION"), encoding="utf-8") as f:
            given = f.read().strip()
    except OSError:
        return "a copy with no VERSION"
    return given if semver(given) < semver(lane_version()) else None
