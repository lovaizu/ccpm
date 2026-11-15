"""The words of a run of Lane's own scripts, as a role types it and the guard reads it in a Bash
command: lay.py print with the line of its output that names a Proposal's ID, lay.py write with
its plugin and ID, and result.py with its role and Result, so that whoever writes them and whoever
reads them hold one form."""

from __future__ import annotations

import os
import re
import shlex
from collections.abc import Sequence

# What the role types for the plugin's folder in a command, as Claude Code fills it in a hook's
# command but not in a Bash command.
ROOT = "${CLAUDE_PLUGIN_ROOT}"
# The line of print's output that names the Proposal's ID.
ID_LINE = re.compile(r"^ID: (\S+)$", re.MULTILINE)
# What in a command makes the shell run more than one program, or read another file than the words
# name, so that the command is no single run of a script.
MORE = re.compile(r"[|&;<>()$`\\\n]")


def id_line(proposal_id: str) -> str:
    """The line of lay.py print's output that names the Proposal's ID.

    Takes: the ID.
    Gives: the line, such as `ID: b9fd8fd8`.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `L-->>UP: the Routes, each Step as it'll read, and the ID`.
    """
    return f"ID: {proposal_id}"


def printed(command: str, output: str) -> tuple[str, str] | None:
    """The Proposal's ID and what print showed, where a Bash command ran lay.py print.

    Takes: the Bash command of a PostToolUse, and its standard output.
    Gives: the ID that the output's ID line names and the whole output, or None where the command
    isn't a run of lay.py print or its output names no ID.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `CC->>G: the PostToolUse of lay.py print`.
    """
    words = _words(command)
    ran = any(
        os.path.basename(word) == "lay.py" and words[i + 1 : i + 2] == ["print"]
        for i, word in enumerate(words)
    )
    found = ID_LINE.search(output)
    return (found[1], output) if ran and found else None


def write_args(words: Sequence[str]) -> tuple[str, str] | None:
    """The plugin and the Proposal's ID that a call of lay.py write names.

    Takes: the words of a command, as shlex splits them, from the script on.
    Gives: the plugin's folder and the ID, or None where the words aren't `lay.py write <plugin>
    <ID>`.
    Changes: nothing.
    Refuses: nothing.
    Carries: S2 `CC->>G: the call` of lay.py write, through `write_call`.
    """
    if len(words) == 4 and os.path.basename(words[0]) == "lay.py" and words[1] == "write":
        return words[2], words[3]
    return None


def write_call(command: str) -> tuple[str, str] | None:
    """The plugin and the Proposal's ID of the lay.py write that a Bash command runs.

    Takes: the Bash command.
    Gives: what `write_args` reads from the words `lay.py write <plugin> <ID>` wherever they stand
    in the command, or None where it runs no lay.py write or shlex can't split it.
    Changes: nothing.
    Refuses: nothing.
    Carries: S2 `CC->>G: the call` of lay.py write, as the guard places it on the Run of up that
    showed its ID and checks it.
    """
    words = _words(command)
    for i, word in enumerate(words):
        if os.path.basename(word) == "lay.py" and words[i + 1 : i + 2] == ["write"]:
            return write_args(words[i : i + 4])
    return None


def result_command(role: str, result: str) -> str:
    """The command by which a role gives a Result, as a Lane's sentence names it.

    Takes: the role or skill, and the Result.
    Gives: `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py <role> <result>`.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `L->>T: checks each Lane, and makes its sentence`, for the Lane on a role's last
    Step.
    """
    return f"python3 {ROOT}/hooks/lane/result.py {role} {result}"


def result_args(command: str, root: str) -> tuple[str, str] | None:
    """The role and the Result that a Bash command gives by the plugin's result.py.

    Takes: the Bash command, and the plugin's folder, which `${CLAUDE_PLUGIN_ROOT}` names.
    Gives: the role and the Result, or None where the command isn't one run of the plugin's
    result.py with two arguments.
    Changes: nothing.
    Refuses: nothing.
    Carries: S6 `SA->>R: result.py <role> <result>` as the guard lets it through, its `CC->>G: the
    PostToolUse, with its agent_id`, and S2 and S5's `CC->>G: the PostToolUse, with no agent_id`.
    """
    if MORE.search(command.replace(ROOT, "")):
        return None
    words = _words(command.replace(ROOT, root))
    script = os.path.join(root, "hooks", "lane", "result.py")
    if len(words) == 4 and words[0] == "python3" and os.path.normpath(words[1]) == script:
        return words[2], words[3]
    return None


def _words(command: str) -> list[str]:
    """The command's words as shlex splits them; none where it can't, such as a here-document
    that holds an apostrophe, which then runs none of Lane's scripts as the guard reads them."""
    try:
        return shlex.split(command)
    except ValueError:
        return []
