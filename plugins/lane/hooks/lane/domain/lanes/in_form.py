"""in_form: the subagent writes an output its step names in the form the step names, a file of the
plugin named as `${CLAUDE_PLUGIN_ROOT}/<path in the plugin>`, the path the subagent reads it by,
such as a changelog entry as JSON of a schema, or a report as Markdown with a template's headings.
A write of the output is held to the form before it is made: a Write by its content, an Edit by the
file's text with the edit made; a NotebookEdit of it is stopped, as no form holds a notebook's
text. As the subagent gives its result, each output there is held to the form again, as a command
its lanes name may have written it."""

from __future__ import annotations

import os
from typing import Any

from lanes import forms, run_only, write_only
from lanes.done import Done, text

ACTION = "write"
WORDING = "Write `<output>` in the form of `<form>`."
CALLS = False


def form(named: str, root: str) -> forms.Form:
    """The form named, a file of the plugin at root; stops with ValueError saying why where it is
    not named from the plugin's folder, lies out of the plugin, which installing does not copy, or
    gives no form lane reads."""
    if not named.startswith(run_only.ROOT + "/"):
        raise ValueError(
            f"is not named as {run_only.ROOT}/<path in the plugin>, so the subagent has no path to"
            " read it by"
        )
    # The path is judged as named, not as a link in it resolves: installing copies the file a link
    # in the plugin points to into the plugin.
    # One form named gives one path.
    path = os.path.normpath(run_only.named([named], root)[0])  # pragma: no mutate
    if not write_only.allows(path, [os.path.normpath(root)], root, root):
        raise ValueError("lies out of the plugin, whose folder alone installing copies")
    return forms.read(path)


def refused(named: str, root: str) -> str:
    """Why the form named cannot be laid in the plugin at root; "" where it can."""
    try:
        form(named, root)
    except ValueError as why:
        return f"names the form {named}, which {why}"
    return ""


def text_written(tool: str, given: dict[str, Any], file: str) -> str | None:
    """The text the call leaves in the file, a full path: a Write's content, or the file's text
    with an Edit made; None where an Edit would make no change, its text not found."""
    # The guard holds a write of Write or Edit to the form, Write the last of them in order.
    if tool == "Write":  # pragma: no mutate
        return str(given.get("content", ""))
    try:
        with open(file, encoding="utf-8") as f:
            now = f.read()
    except (OSError, UnicodeDecodeError):
        now = ""
    old, new = str(given.get("old_string", "")), str(given.get("new_string", ""))
    if not old or old not in now:
        return None
    return now.replace(old, new) if given.get("replace_all") is True else now.replace(old, new, 1)


def out_of(
    tool: str, given: dict[str, Any], places: dict[str, list[str]], root: str, cwd: str
) -> str:
    """The point the call's write of an output taken is out of the forms taken by, as the first of
    them holds it, each output named from the folder the call is made in; "" where the call writes
    no output, an Edit would change nothing, or the text holds to one of the forms."""
    path = given.get("notebook_path") if tool == "NotebookEdit" else given.get("file_path")
    file = os.path.realpath(os.path.join(cwd, str(path)))
    outputs = [o for o in places["output"] if write_only.allows(file, [o], root, cwd)]
    if not outputs:
        return ""
    if tool == "NotebookEdit":
        return f"`{outputs[0]}`: expected a write by Write or Edit, found NotebookEdit"
    said = text_written(tool, given, file)
    return "" if said is None else held(places, file, said, root)


def held(places: dict[str, list[str]], file: str, said: str, root: str) -> str:
    """The point the text of the file is out of the forms by, as the first of them holds it; ""
    where it holds to one of them."""
    points = [forms.held(form(f, root), file, said) for f in places["form"]]
    return "" if not all(points) else points[0]


def missing(given: dict[str, list[str]], done: Done) -> str:
    """What is out of form, as the subagent gives its result: the first output there whose text is
    out of the forms, with the point; "" where each holds."""
    for output in given["output"]:
        said = text(done.full(output))
        point = held(given, done.full(output), said, done.root) if said is not None else ""
        if point:
            return f"`{output}`: {point}"
    return ""
