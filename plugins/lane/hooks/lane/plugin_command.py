"""How Lane runs a command that a plugin's rule names, such as its check or the command of a
checklist: by the shell, in the folder that the conversation works in, with its output kept."""

from __future__ import annotations

import subprocess


class Unchecked(Exception):
    """A rule that Lane couldn't check, as the plugin's command that it runs couldn't give its
    answer, said with what Lane couldn't check and why, so that the move goes on and the AI reads
    it."""


def run(command: str, cwd: str) -> subprocess.CompletedProcess[str]:
    """Runs the plugin's command.

    Takes: the command, as the rule names it, and the folder that the conversation works in.
    Gives: its exit code, stdout, and stderr, whatever the code, as the rule type judges them.
    Changes: whatever the command changes.
    Refuses: OSError, where the command can't be run.
    """
    return subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True, check=False)


def exited(command: str, done: subprocess.CompletedProcess[str]) -> str:
    """Why a command that couldn't give its answer couldn't: the command, the code it exits with,
    and what it printed on either output, where it printed anything."""
    said = (done.stdout + done.stderr).strip()
    return f"{command} exits {done.returncode}" + (f":\n{said}" if said else "")
