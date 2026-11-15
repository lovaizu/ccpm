"""The plugin's name, as its .claude-plugin/plugin.json gives it, by which Lane opens each answer,
keeps each run record, and tells the plugin's own skills and roles from another plugin's."""

from __future__ import annotations

import json
import os


def plugin_name(root: str) -> str:
    """The name of the plugin in the folder.

    Takes: the plugin's folder.
    Gives: the `name` that its .claude-plugin/plugin.json gives; the folder's own name where it
    holds no plugin.json, as a folder that `claude --plugin-dir` loads is named for its plugin.
    Changes: nothing.
    Refuses: ValueError, where plugin.json isn't JSON, and TypeError, where it gives no `name`
    that is a string, as Claude Code loads no such plugin.
    Carries: the plugin's name that each answer of S1 to S7 opens with, and the run record's place.
    """
    path = os.path.join(root, ".claude-plugin", "plugin.json")
    if not os.path.exists(path):
        return os.path.basename(os.path.normpath(root))
    with open(path, encoding="utf-8") as f:
        held = json.load(f)
    name = held.get("name") if isinstance(held, dict) else None
    if not isinstance(name, str):
        raise TypeError(f"{path}: `name` must be a string, not {name!r}")
    return name
