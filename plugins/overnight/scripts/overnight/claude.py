"""How a run is asked of Claude Code, and how its reply is read: done, or stopped and why."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class Reply:
    """What a run of Claude Code gave: `done`, the `session_id` of its conversation where its reply
    names one, else None, and, where it isn't done, the `reason` it stopped, on one line, else ""."""

    done: bool
    session_id: Optional[str]
    reason: str


def ask(folder: str, allowed_tools: str, prompt: str, session_id: Optional[str]) -> Reply:
    """Runs `claude -p` in `folder` with `prompt` on stdin and the tools that `allowed_tools` names,
    as `claude --allowed-tools` takes them; in the conversation `session_id` by `--resume`, or in a
    new one where it's None; and waits until it ends. The run is done only where claude exits 0 and
    its result says no error. Raises FileNotFoundError where no `claude` is on the PATH."""
    args = ["claude", "-p", "--output-format", "json", "--allowed-tools", allowed_tools]
    if session_id is not None:
        args += ["--resume", session_id]
    ran = subprocess.run(
        args, input=prompt, capture_output=True, text=True, cwd=folder, check=False
    )
    result = _result(ran.stdout)
    found = result.get("session_id")
    if ran.returncode == 0 and result.get("is_error") is False:
        return Reply(done=True, session_id=found, reason="")
    message = result.get("result") or ran.stderr.strip()
    if not message:
        message = f"claude ended with code {ran.returncode} and no message"
    return Reply(done=False, session_id=found, reason=" ".join(message.split()))


def _result(stdout: str) -> dict[str, Any]:
    """The result object that claude printed in JSON, or {} where it printed none."""
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {}
