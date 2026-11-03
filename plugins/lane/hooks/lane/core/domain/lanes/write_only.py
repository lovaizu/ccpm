"""write_only: the subagent writes no file but the outputs its step names, such as `CHANGELOG.md`
alone, by the path Write, Edit or NotebookEdit is given; an output may be a folder, under which it
writes anything. An output, or an input of read_only or read_whole, may begin with
`${CLAUDE_PLUGIN_ROOT}`, which names the plugin's folder, as Claude Code fills it in the step the
subagent reads."""

from __future__ import annotations

import os

from step import ROOT

ACTION = "write"
CALLS = False
WORDING = "Write only `<output>`."


def in_plugin(named: str, root: str) -> str:
    """The path named, the folder of the plugin at root put in where it begins with ROOT."""
    return root + named[len(ROOT) :] if named.startswith(ROOT) else named


def allows(path: str, takes: list[str], root: str, cwd: str) -> bool:
    """Whether the file at the path is one of the outputs taken or lies under one, each named from
    the folder the call is made in, as the tools take a path, or from the plugin's folder where it
    begins with ROOT, and each link followed, so a file is judged by what it is."""

    def full(named: str) -> str:
        return os.path.realpath(os.path.join(cwd, named))

    file = full(path)
    outputs = [full(in_plugin(t, root)) for t in takes]
    return any(file == o or file.startswith(o + os.sep) for o in outputs)
