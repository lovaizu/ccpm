"""How the plugins' prompt and E2E cases run the real Claude Code on Opus: only on the developer's
login, a prompt in a folder with the plugins it loads, or a judgment that replies in JSON."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from collections.abc import Mapping, Sequence
from typing import Any

import pytest

# The developer's login: CLAUDE_CODE_OAUTH_TOKEN where it is set, as in CI, or else the
# credentials file of the developer's own Claude Code, which a configuration folder of a test's
# own takes a copy of, as a container or a Linux machine keeps the login there.
TOKEN = "CLAUDE_CODE_OAUTH_TOKEN"
CREDENTIALS = os.path.join(
    os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude"), ".credentials.json"
)

# The settings by which the developer's machine reaches the model, such as a proxy that a sandbox
# puts in front of it and through which the login works, which a bench's own environment leaves out.
NETWORK = {
    "HTTPS_PROXY",
    "HTTP_PROXY",
    "NO_PROXY",
    "NODE_USE_ENV_PROXY",
    "NODE_EXTRA_CA_CERTS",
    "SSL_CERT_FILE",
}

# A case that runs the real Claude Code runs on the developer's login alone, so it is skipped
# without one.
NEEDS_LOGIN = pytest.mark.skipif(
    not os.environ.get(TOKEN) and not os.path.isfile(CREDENTIALS),
    reason="runs the real Claude Code on Opus",
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
    login = logged_in(env)
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
    its own. The prompt goes on standard input, as the records of a run that a judge reads can pass
    what the system takes as a command's arguments, such as ARG_MAX's 2 MiB on Linux."""
    with tempfile.TemporaryDirectory() as config:
        done = subprocess.run(
            ["claude", "-p", "--model", "opus", "--output-format", "json"],
            input=prompt,
            capture_output=True,
            text=True,
            check=True,
            env=logged_in(dict(os.environ, CLAUDE_CONFIG_DIR=config)),
        )
    reply = json.loads(done.stdout)["result"]
    # Opus may put the JSON in a code block or after a sentence, so the reply's object is read from
    # its first brace to its last.
    return json.loads(reply[reply.index("{") : reply.rindex("}") + 1])


def logged_in(env: Mapping[str, str]) -> dict[str, str]:
    """The environment with the developer's login: the token where it is set, or else a copy of
    the credentials file in the configuration folder that env names; and with the settings by
    which the developer's machine reaches the model, as NETWORK names them."""
    network = {name: value for name, value in os.environ.items() if name.upper() in NETWORK}
    token = os.environ.get(TOKEN)
    if token:
        return dict(env, **network, **{TOKEN: token})
    config = env["CLAUDE_CONFIG_DIR"]
    os.makedirs(config, exist_ok=True)
    shutil.copyfile(CREDENTIALS, os.path.join(config, ".credentials.json"))
    return dict(env, **network)
