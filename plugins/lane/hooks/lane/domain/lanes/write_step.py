"""write_step: a lane of the trace kind, whose step the subagent has done once it made an output the
lane names in this start: a Write, Edit or NotebookEdit call of it, or of a file under it where it's
a folder, came back, judged by the path the call names."""

from __future__ import annotations

from lanes.done import WRITERS, Done, under, written
from lanes.write_only import in_plugin

ACTION = "write"
WORDING = "Make `<output>`."
CALLS = True
TRACE = True


def traces(tool: str, value: str, given: dict[str, list[str]], done: Done) -> bool:
    """Whether a call of the tool on the value, the field of its input a lane judges, is the trace
    of the lane taking the things given: a write of one of its outputs, or of a file under one."""
    file = done.full(value)
    outputs = [done.full(in_plugin(o, done.root)) for o in given["output"]]
    return tool in WRITERS and any(under(file, o) for o in outputs)


def missing(given: dict[str, list[str]], done: Done) -> str:
    """What's missing: that the subagent made none of the outputs in this start; "" where it made
    one."""
    outputs = [done.full(in_plugin(o, done.root)) for o in given["output"]]
    if any(under(f, o) for f in written(done, done.run) for o in outputs):
        return ""
    return f"{' or '.join(f'`{o}`' for o in given['output'])} not made"
