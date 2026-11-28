"""The cases of the `overnight` command, as its user types it in Claude Code's bash mode."""

from __future__ import annotations

import os
import subprocess

from conftest import PLUGIN

OVERNIGHT = os.path.join(PLUGIN, "bin", "overnight")


def test_version_names_the_plugin_and_its_version() -> None:
    """Given overnight 0.1.0, installed
    When the user runs `overnight --version`
    Then it prints `overnight 0.1.0` and exits 0."""
    ran = subprocess.run([OVERNIGHT, "--version"], capture_output=True, text=True, check=False)

    assert (ran.returncode, ran.stdout, ran.stderr) == (0, "overnight 0.1.0\n", "")
