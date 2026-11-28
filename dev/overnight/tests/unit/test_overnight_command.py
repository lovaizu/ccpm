"""The unit cases of the `overnight` command, as the user runs it from Claude Code's shell, which
has the plugin's bin/ on its PATH."""

from __future__ import annotations

import json
import os
import subprocess
import sys

# The top of the repository, four folders above this file's: unit/, tests/, overnight/, and dev/.
TOP = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
PLUGIN = os.path.join(TOP, "plugins", "overnight")
COMMAND = os.path.join(PLUGIN, "bin", "overnight")

# TODO: the cases of one work that retries, as the README's Walkthrough and How it works say: its
# start apart from the session, with its folder, its prompt, and the tools it may use; a run that
# is done; a run that stops, by the usage limit or any other error, and its retry in the same
# session after its wait; the retries run out; `--retries`; and each wrong input refused.


def test_version_shows_the_version_that_plugin_json_holds(tmp_path):
    """Given the plugin, whose .claude-plugin/plugin.json holds its version
    When the user runs `overnight --version`, from the repository's top, as the checks run each test
    Then it exits 0, having written `overnight <that version>` on stdout and nothing on stderr"""
    with open(os.path.join(PLUGIN, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
        version = json.load(f)["version"]
    env = {"PATH": os.path.dirname(sys.executable) + os.pathsep + os.environ["PATH"]}
    ran = subprocess.run(
        [COMMAND, "--version"],
        cwd=TOP,
        env={**os.environ, **env, "HOME": str(tmp_path)},
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        check=False,
    )
    assert (ran.returncode, ran.stdout, ran.stderr) == (0, f"overnight {version}\n", "")
