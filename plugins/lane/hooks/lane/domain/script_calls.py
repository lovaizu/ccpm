"""The words of a run of Lane's own scripts, as a role types it and the guard reads it in a Bash
command: lay.py print with the line of its output that names a Proposal's ID, lay.py write with
its plugin and ID, and result.py with its role and Result, so that whoever writes them and whoever
reads them hold one form."""

from __future__ import annotations

from collections.abc import Sequence


def id_line(proposal_id: str) -> str:
    """The line of lay.py print's output that names the Proposal's ID.

    Takes: the ID.
    Gives: the line, such as `ID: b9fd8fd8`.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `L-->>UP: the Routes, each Step as it'll read, and the ID`.
    """
    raise NotImplementedError


def printed(command: str, output: str) -> tuple[str, str] | None:
    """The Proposal's ID and what print showed, where a Bash command ran lay.py print.

    Takes: the Bash command of a PostToolUse, and its standard output.
    Gives: the ID that the output's ID line names and the whole output, or None where the command
    isn't a run of lay.py print or its output names no ID.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `CC->>G: the PostToolUse of lay.py print`.
    """
    raise NotImplementedError


def write_args(words: Sequence[str]) -> tuple[str, str] | None:
    """The plugin and the Proposal's ID that a call of lay.py write names.

    Takes: the words of a command, as shlex splits them, from the script on.
    Gives: the plugin's folder and the ID, or None where the words aren't `lay.py write <plugin>
    <ID>`.
    Changes: nothing.
    Refuses: nothing.
    Carries: S2 `CC->>G: the call` of lay.py write, and lay.py's own reading of its write command.
    """
    raise NotImplementedError


def result_command(role: str, result: str) -> str:
    """The command by which a role gives a Result, as a Lane's sentence names it.

    Takes: the role or skill, and the Result.
    Gives: `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py <role> <result>`.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `L->>T: checks each Lane, and makes its sentence`, for the Lane on a role's last
    Step.
    """
    raise NotImplementedError


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
    raise NotImplementedError
