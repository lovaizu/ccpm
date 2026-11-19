"""The form of the words that name a start's lane in its text, which the main conversation passes
as the Agent call's prompt: how the guard writes them into the text of a start due, and finds them
again in the prompt of a start made."""

from __future__ import annotations

from dataclasses import dataclass

from routes import Due


@dataclass
class Named:
    """What a start's prompt gives: the name of its lane, and the start's text without the words
    that name it."""

    lane: str
    text: str


def text(start: Due) -> str:
    """The text that the main conversation passes as the prompt of a start due.

    Takes: the start due, with its lane and its text, empty where the plugin gives none.
    Gives: the start's text with the words that name its lane, such that lane gives that lane back
    from it.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("lane_text.text")


def read(prompt: str) -> Named | None:
    """The lane that a start's prompt names, and the start's text.

    Takes: the `tool_input.prompt` of an Agent call at its PreToolUse.
    Gives: the name of the lane that the words text wrote name, and the prompt without them; None
    where the prompt holds no such words.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("lane_text.read")
