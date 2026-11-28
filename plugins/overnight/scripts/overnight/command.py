"""Decides what the `overnight` command takes from the user and what it gives back."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Sequence


def main(argv: Sequence[str], plugin: str) -> None:
    """Runs the `overnight` command on the words the user gave after its name.

    Takes: the words, and the plugin's folder, whose .claude-plugin/plugin.json holds its version.
    Gives: for `--version`, `overnight <version>` on stdout, and exits 0.
    """
    with open(os.path.join(plugin, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
        version = json.load(f)["version"]
    parser = argparse.ArgumentParser(prog="overnight")
    parser.add_argument("--version", action="version", version=f"overnight {version}")
    # TODO: the start of one work that retries, as the README's Walkthrough and How it works say:
    # `--dir`, `--allowed-tools`, `--retries`, and the prompt, read and checked before the work
    # starts apart from the session; the two lines that name the work and its state folder; and
    # the runs of `claude -p`, each retry in the same session after its wait, until the work is
    # done or recorded as failed in its state.json and log.
    parser.parse_args(argv)
