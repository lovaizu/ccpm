"""Decides how Lane's code reaches a plugin's `hooks/lane/`: as a relative link where the plugin
lies in Lane's own marketplace, and as a copy that carries Lane's version elsewhere, as the
architecture's Deployment says.
"""

from __future__ import annotations

import json
import os
import shutil
from typing import NamedTuple

# The file in a copy of Lane's code that holds the version of Lane that `lay.py` copied.
VERSION = "VERSION"


class Laid(NamedTuple):
    """Lane's code in a plugin."""

    # `link` or `copy`.
    kind: str
    # The version of Lane that a copy came from, or None for a link or a copy that names none.
    version: str | None


def version(lane: str) -> str:
    """The version of Lane at the folder, from its manifest."""
    with open(os.path.join(lane, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
        return json.load(f)["version"]


def _marketplace(lane: str) -> str | None:
    """The nearest folder that holds both Lane and a marketplace, or None."""
    folder = os.path.realpath(lane)
    while os.path.dirname(folder) != folder:
        folder = os.path.dirname(folder)
        if os.path.isfile(os.path.join(folder, ".claude-plugin", "marketplace.json")):
            return folder
    return None


def lay(lane: str, root: str) -> Laid:
    """Lays Lane's code from the folder given into the plugin at the root, in place of any laid
    before, and says how it laid it."""
    target = os.path.join(root, "hooks", "lane")
    if os.path.islink(target):
        os.remove(target)
    elif os.path.isdir(target):
        shutil.rmtree(target)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    code = os.path.join(lane, "hooks", "lane")
    market = _marketplace(lane)
    real = os.path.realpath(root)
    if market is not None and real.startswith(market + os.sep):
        os.symlink(os.path.relpath(os.path.realpath(code), os.path.join(real, "hooks")), target)
        return Laid("link", None)
    shutil.copytree(code, target, ignore=shutil.ignore_patterns("__pycache__", VERSION))
    laid = version(lane)
    with open(os.path.join(target, VERSION), "w", encoding="utf-8") as f:
        f.write(laid + "\n")
    return Laid("copy", laid)


def state(root: str) -> Laid | None:
    """Lane's code in the plugin at the root, or None where the plugin holds none."""
    target = os.path.join(root, "hooks", "lane")
    if os.path.islink(target):
        return Laid("link", None)
    if not os.path.isdir(target):
        return None
    try:
        with open(os.path.join(target, VERSION), encoding="utf-8") as f:
            return Laid("copy", f.read().strip())
    except FileNotFoundError:
        return Laid("copy", None)


def older(laid: str | None, current: str) -> bool:
    """Whether a copy's version comes before Lane's, a copy naming no version among them."""
    if laid is None:
        return True
    return _numbers(laid) < _numbers(current)


def _numbers(given: str) -> tuple[int, ...]:
    return tuple(int(p) for p in given.split("."))
