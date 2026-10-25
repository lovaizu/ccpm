"""in_form: the subagent writes the output its step names in the form the step names, a file of the
plugin named as `${CLAUDE_PLUGIN_ROOT}/<path in the plugin>`, which Claude Code gives the subagent
as a path it can read, such as a changelog entry as JSON of a schema, or a report as Markdown with a template's
headings. A write of the output is held to the form before it is made: a Write by its content, an
Edit by the file's text with the edit made; a command writing the output is a drift whatever it
writes, as its text cannot be read before it runs, so the subagent writes it by Write or Edit. A
drift is told with the point the text is out of the form by."""

from __future__ import annotations

import os

import forms
import shell
import step
from call import Call

ACTION = "write"
WORDING = "Write `<output>` in the form of `<form>`."
TOOLS = ("Write", "Edit", "Bash")
# One output is held to one form, so the form's place, the last, takes one thing alone.
MOST = 2


def form(root: str, named: str) -> forms.Form:
    """The form named, a file of the plugin at root; stops with ValueError saying why where it is
    not named from the plugin's folder, is out of the plugin, which installing does not copy, or
    gives no form lane reads."""
    if not named.startswith(step.ROOT + "/"):
        raise ValueError(
            f"is not named as {step.ROOT}/<path in the plugin>, the path the subagent reads it by"
        )
    # The path is judged as named, not as a link in it resolves: installing copies the file a link
    # in the plugin points to into the plugin, as a plugin takes another's form.
    path = os.path.normpath(step.expanded(named, root))
    if not shell.inside(path, os.path.normpath(root)):
        raise ValueError("lies out of the plugin, whose folder alone installing copies")
    return forms.read(path)


def refused(takes: list[str], root: str) -> str:
    """Why the lane cannot be laid taking these in the plugin at root, where its form is no form lane
    reads there; "" where it can."""
    try:
        form(root, takes[1])
    except ValueError as why:
        return f"names the form {takes[1]}, which {why}"
    return ""


def drifts(call: Call, takes: list[str], root: str) -> str:
    """The point the call's write of the output taken is out of the form taken by, the output named
    from the folder the call is made in, where the guard stands, and the form from the plugin's;
    "" where the call keeps the form or writes no output, or an Edit would write nothing."""
    output, named = takes
    if os.path.realpath(output) not in call.written:
        return ""
    if call.action != ACTION:  # pragma: no mutate
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
            f"the form `{step.expanded(named, root)}` {why}. Stop here and reply that the form must be fixed in the"
            " plugin, and lane:up run again on it."
        )
    return forms.held(asked, output, call.text)
