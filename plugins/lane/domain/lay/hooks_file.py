"""How lay.py tells Lane's entries in a plugin's hooks.json from the user's own, as the guard's code
names Lane's, and replaces Lane's while it leaves the user's as they stand."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from typing import Any

from form import OutOfForm

# What every entry of Lane's runs, by which an earlier Lane's entries are told from the user's.
HOOK = "hooks/lane/hook.py"


def replace_entries(plugin: str, entries: Mapping[str, Any]) -> None:
    """Puts Lane's entries in the plugin's hooks.json in place of those of an earlier Lane.

    Takes: the plugin's folder, and Lane's entries from `events.hook_entries`.
    Gives: nothing.
    Changes: hooks/hooks.json, made where it isn't there, each entry that runs
    hooks/lane/hook.py replaced and each other entry kept.
    Refuses: form.OutOfForm, where hooks.json isn't JSON in Claude Code's form, and OSError,
    where it can't be written.
    Carries: S2 `L->>LS: replaces Lane's hook entries, as the guard's code names them`.
    """
    path = os.path.join(plugin, "hooks", "hooks.json")
    hooks: dict[str, Any] = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            try:
                hooks = json.load(f)["hooks"]
            except (ValueError, KeyError, TypeError) as e:
                raise OutOfForm([f"{path} isn't hooks.json in Claude Code's form: {e}"]) from e
    for event in hooks:
        groups = [dict(g, hooks=[h for h in g["hooks"] if not _lanes(h)]) for g in hooks[event]]
        hooks[event] = [g for g in groups if g["hooks"]]
    for event, groups in entries.items():
        hooks[event] = [*hooks.get(event, []), *groups]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps({"hooks": {k: v for k, v in hooks.items() if v}}, indent=2) + "\n")


def _lanes(entry: Mapping[str, Any]) -> bool:
    """Whether the entry runs Lane's hook.py."""
    return any(HOOK in str(word) for word in [entry.get("command"), *entry.get("args", [])])
