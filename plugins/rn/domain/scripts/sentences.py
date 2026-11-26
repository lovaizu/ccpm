"""Decides how rn splits Markdown words into sentences, as the pull request's title is the first
sentence of the run's goal: after `.`, `?`, or `!` before a space, after the full stop, the
question mark, or the exclamation mark of Japanese or Chinese, and at each newline, with a code
span or a link kept whole."""

from __future__ import annotations

import re

# A code span of Markdown, and a link or a figure, each kept whole in a sentence.
_CODE_SPAN = re.compile(r"`[^`\n]*`")
_LINK = re.compile(r"!?\[([^\]\n]*)\]\([^)\n]*\)")
# A sentence ends at `.`, `?`, or `!` before a space, or at a full stop, a question mark, or an
# exclamation mark of Japanese or Chinese, which takes no space after it, after the closing quote
# or bracket that holds it, as in 「…。」.
_SENTENCE_END = re.compile(
    r"(?<=[.!?])\s+|(?<=[.!?][\"')\]])\s+|(?<=[。！？][」』）])\s*|(?<=[。！？])(?![」』）])\s*"
)


def sentences(text: str) -> list[str]:
    """The sentences of the words.

    Takes: Markdown words, such as the run's goal.
    Gives: each sentence, in its order, split as the module says, a newline among the ends, such as
    the one that a line ending with a backslash gives; [] for words that hold none.
    Changes: nothing.
    Refuses: nothing.
    """
    spans: list[str] = []

    def hide(match: re.Match[str]) -> str:
        spans.append(match.group(0))
        return f"\0{len(spans) - 1}\0"

    def show(hidden: str) -> str:
        return re.sub(r"\0(\d+)\0", lambda m: show(spans[int(m.group(1))]), hidden)

    # A NUL of the text is hidden first, so that each NUL left marks a span hidden, and a span
    # hidden inside a link comes back with it.
    hidden = _LINK.sub(hide, _CODE_SPAN.sub(hide, re.sub("\0", hide, text)))
    found = []
    for line in hidden.split("\n"):
        found += [each for each in _SENTENCE_END.split(line) if each.strip()]
    return [show(each) for each in found]
