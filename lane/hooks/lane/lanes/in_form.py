"""in_form: the subagent writes the output its step names in the form the step names, a file of the
plugin, such as a changelog entry as JSON of a schema, or a report as Markdown with a template's
headings. A write of the output is held to the form before it is made: a Write by its content, an
Edit by the file's text with the edit made; a command writing the output is a drift whatever it
writes, as its text cannot be read before it runs, so the subagent writes it by Write or Edit. A
drift is told with the point the text is out of the form by."""

from __future__ import annotations

import os

import forms
import shell
from call import Call

ACTION = "write"
WORDING = "Write `<output>` in `<form>`."
TOOLS = ("Write", "Edit", "Bash")


def form(root: str, named: str) -> forms.Form:
    """The form named, a file of the plugin at root; stops with ValueError saying why where it is
    out of the plugin, which installing does not copy, or gives no form lane reads."""
    path = os.path.realpath(os.path.join(root, named))
    if not shell.inside(path, os.path.realpath(root)):
        raise ValueError("lies out of the plugin, whose folder alone installing copies")
    return forms.read(path)


def drifts(call: Call, takes: list[str], root: str) -> str:
    """The point the call's write of the output taken is out of the form taken by, the output named
    from the folder the call is made in, where the guard stands, and the form from the plugin's;
    "" where the call keeps the form or writes no output, or an Edit would write nothing."""
    output, named = takes
    if os.path.realpath(output) not in call.written:
        return ""
    if call.action not in (ACTION,):
        return (
            f"`{output}`: expected a write by Write or Edit, whose text is held to the form,"
            " found a command writing it"
        )
    if call.text is None:
        return ""
    try:
        asked = form(root, named)
    except ValueError as why:
        return (
            f"the form `{named}` {why}. Stop here and reply that the form must be fixed in the"
            " plugin, and lane:up run again on it."
        )
    return forms.held(asked, output, call.text)
