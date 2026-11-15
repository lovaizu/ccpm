"""How the plugins' prompt and E2E cases run the real Claude Code on Opus: only on the developer's
login, a prompt in a folder with the plugins it loads, or a judgment that replies in JSON."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from collections.abc import Mapping, Sequence
from typing import Any

import pytest

# A case that runs the real Claude Code runs on the developer's login alone, so it is skipped
# without one.
NEEDS_LOGIN = pytest.mark.skipif(
    not os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"), reason="runs the real Claude Code on Opus"
)
# What a run of a prompt may not do. Also in dev/scripts/e2e.py.
RULE = (
    "Install nothing, and send nothing to a translator, a web API, or any other service outside"
    " this repository's git."
)


def prompted(
    prompt: str, folder: str, env: Mapping[str, str], flags: Sequence[str], timeout: int
) -> str:
    """What Claude Code printed for the prompt, run once by `claude -p` on Opus in the folder, with
    the environment and the developer's login, every permission granted but RULE added to its
    system prompt, and the flags, such as each `--plugin-dir`, whatever it exits with."""
    login = dict(env, CLAUDE_CODE_OAUTH_TOKEN=os.environ["CLAUDE_CODE_OAUTH_TOKEN"])
    command = ["claude", "-p", "--model", "opus", "--permission-mode", "bypassPermissions"]
    command += ["--append-system-prompt", RULE, *flags]
    done = subprocess.run(
        [*command, prompt],
        cwd=folder,
        env=login,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return done.stdout


def judged(prompt: str) -> Any:
    """The JSON that Opus replies with to the prompt, run by `claude -p` with a settings folder of
    its own."""
    done = subprocess.run(
        ["claude", "-p", "--model", "opus", "--output-format", "json", prompt],
        capture_output=True,
        text=True,
        check=True,
        env=dict(os.environ, CLAUDE_CONFIG_DIR=tempfile.mkdtemp()),
    )
    return json.loads(json.loads(done.stdout)["result"])
