"""Where the plugin whose skill runs lies, as the base directory of the skill that Claude Code
writes into the conversation's transcript gives it."""

from __future__ import annotations


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
    raise NotImplementedError("plugin.plugin_root")
