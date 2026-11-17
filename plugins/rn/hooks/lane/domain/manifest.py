"""The plugin's name, as its .claude-plugin/plugin.json gives it, by which Lane opens each answer,
keeps each run record, and tells the plugin's own skills and roles from another plugin's."""

from __future__ import annotations

import json
import os


def plugin_name(root: str) -> str:
    """The name of the plugin in the folder.

    Takes: the plugin's folder.
    Gives: the `name` that its .claude-plugin/plugin.json gives; the folder's own name where it
    holds no plugin.json, or one that gives no `name` that is a string, as a folder that
    `claude --plugin-dir` loads is named for its plugin, and `claude plugin validate`, which
    lay.py write runs, refuses such a plugin.json.
    Changes: nothing.
    Refuses: ValueError, where plugin.json isn't JSON.
    Carries: the plugin's name that each answer of S4 to S6 opens with, and the run record's place.
    """
    path = os.path.join(root, ".claude-plugin", "plugin.json")
    held = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            held = json.load(f)
    name = held.get("name") if isinstance(held, dict) else None
    return name if isinstance(name, str) else os.path.basename(os.path.normpath(root))
