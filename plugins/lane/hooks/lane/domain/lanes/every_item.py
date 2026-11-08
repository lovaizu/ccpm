"""Holds a role's end until a file it wrote names each item of its input.

The items come from the items port, in Lane's own form, which `items` reads, or through the
plugin's adapter. An item counts as answered where its ID stands as a word of its own in a file
that the role wrote after its last change of the input, the input aside.
"""

from __future__ import annotations

import re

import lanes

WORDING = "Answer every item of `<input>`."
END = True
# A top-level item of a Markdown list that begins with an ID, such as `B-1`, `R33`, or `KR1.1`,
# bare or in bold, code, or brackets.
ITEM = re.compile(r"^[-*+]\s+(?:\*\*|`|\[)?([A-Z][A-Za-z]*-?\d+(?:\.\d+)*)", re.MULTILINE)


def items(text: str) -> list[str]:
    """The ID of each item that Lane's own form of the items port reads in the text."""
    return list(dict.fromkeys(ITEM.findall(text)))


def answered(item: str, text: str) -> bool:
    """Whether the text names the item's ID as a word of its own, so that `B-1` answers neither
    `B-12`, `B-1.2`, nor `AB-1`."""
    return re.search(rf"(?<![\w.-]){re.escape(item)}(?![\w-]|\.\w)", text) is not None


def end(given: dict[str, list[str]], calls: list[lanes.Call], context: lanes.Context) -> str | None:
    """What's left to answer, or None where a file written since the last change of each input
    names every item of it."""
    for path in given["input"]:
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except OSError:
            return f"`{path}` isn't there to read its items."
        written = []
        for call in calls:
            if call.tool not in ("Write", "Edit", "NotebookEdit"):
                continue
            target = lanes.called_path(call) or ""
            if lanes.under(target, [path]):
                written = []
            elif target not in written:
                written.append(target)
        texts = [_text(p) for p in written]
        left = [i for i in items(text) if not any(answered(i, t) for t in texts)]
        if left:
            return (
                f"No file written since the last change of `{path}` answers"
                f" {', '.join(f'`{i}`' for i in left)}."
            )
    return None


def _text(path: str) -> str:
    """The file's text, or nothing where it's gone."""
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""
