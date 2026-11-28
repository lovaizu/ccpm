"""The command line of `overnight`: the options it takes, and what it prints for each."""

from __future__ import annotations

import argparse
import json
import os


def main(argv: list[str], root: str) -> None:
    """Runs `overnight` with `argv`, the arguments after its name, for the plugin in the folder
    `root`. With `--version`, prints `overnight <version>`, the version of the plugin's manifest,
    and exits 0 by SystemExit."""
    with open(os.path.join(root, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
        version = json.load(f)["version"]
    parser = argparse.ArgumentParser(prog="overnight")
    parser.add_argument("--version", action="version", version=f"overnight {version}")
    parser.parse_args(argv)
