"""Where the plugin whose skill runs lies, as the base directory of the skill that Claude Code
writes into the conversation's transcript gives it."""

from __future__ import annotations

import json
import os

# How the line that names a skill's base directory opens.
_OPENS = "Base directory for this skill: "


def plugin_root(transcript_path: str, skill: str) -> str | None:
    """The folder of the plugin whose skill runs.

    Takes: the conversation's `transcript_path`, and the skill's name as its call gives it, such as
    `<plugin>:<skill>`.
    Gives: the plugin's folder, from the latest line of the transcript that opens
    `Base directory for this skill: <the plugin's folder>/skills/<skill>`; None where the
    transcript holds no such line for the skill.
    Changes: nothing.
    Refuses: OSError, where the transcript can't be read.
    """
    plugin, _, name = skill.partition(":")
    found = None
    with open(transcript_path, encoding="utf-8") as f:
        for line in f:
            for text in _texts(json.loads(line)):
                folder, _, rest = text[len(_OPENS) :].partition("\n")[0].rpartition("/skills/")
                if text.startswith(_OPENS) and rest == name and os.path.basename(folder) == plugin:
                    found = folder
    return found


def _texts(line: object) -> list[str]:
    """The texts of a user message of the transcript's line, as Claude Code writes them."""
    message = line.get("message") if isinstance(line, dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    if isinstance(content, str):
        return [content]
    if not isinstance(content, list):
        return []
    return [part["text"] for part in content if isinstance(part, dict) and "text" in part]
