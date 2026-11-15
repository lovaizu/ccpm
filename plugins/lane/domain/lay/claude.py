"""How lay.py runs Claude Code's `claude plugin validate` on a plugin and reads whether it
passed."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class Validation:
    """Whether `claude plugin validate` passed, and what it said."""

    passed: bool
    said: str


def validate(plugin: str) -> Validation:
    """Runs `claude plugin validate <plugin>`.

    Takes: the plugin's folder.
    Gives: passed where it exits 0 and says it passed; else not passed, with what it said, a
    `claude` that isn't on the PATH among them.
    Changes: nothing.
    Refuses: nothing.
    Carries: S2 `L->>CC: claude plugin validate <plugin>`, and its `alt it fails` and `else it
    passes`.
    """
    try:
        done = subprocess.run(
            ["claude", "plugin", "validate", plugin], capture_output=True, text=True, check=False
        )
    except FileNotFoundError:
        return Validation(
            False, "claude isn't on the PATH, so lay.py can't run claude plugin validate"
        )
    said = (done.stdout + done.stderr).strip()
    return Validation(done.returncode == 0 and "Validation passed" in said, said)
