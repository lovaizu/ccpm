"""Decides what the `overnight` command takes from the user and what it gives back."""

from __future__ import annotations

import argparse
import datetime
import json
import os
import shutil
from collections.abc import Sequence

from overnight import work


def main(argv: Sequence[str], plugin: str) -> None:
    """Runs the `overnight` command on the words the user gave after its name.

    Takes: the words, and the plugin's folder, whose .claude-plugin/plugin.json holds its version.
    The words are `--dir <folder> --allowed-tools <tools> [--retries <count>] <prompt>`, or
    `--version`.
    Gives: for `--version`, `overnight <version>` on stdout, and exits 0. For a work, starts it
    apart from the session in a folder of its own, `~/.local/state/overnight/<yyyymmdd-hhmmss>/`,
    and returns at once, having written on stdout `overnight: work <id> started in <folder>` and
    `overnight: state and log in <its folder>/`.
    Refuses: with exit code 2 and the reason on stderr, before it starts the work: a word missing,
    a `--dir` that names no folder, a `--retries` that isn't a whole number from 0, an empty
    prompt, and a PATH with no `claude` on it.
    """
    with open(os.path.join(plugin, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
        version = json.load(f)["version"]
    parser = argparse.ArgumentParser(prog="overnight")
    parser.add_argument("--version", action="version", version=f"overnight {version}")
    parser.add_argument("--dir", required=True, help="the folder that Claude works in")
    parser.add_argument(
        "--allowed-tools", required=True, metavar="TOOLS", help="the tools that Claude may use"
    )
    parser.add_argument(
        "--retries",
        type=_count,
        default=work.RETRIES,
        metavar="COUNT",
        help=f"how many times a stopped run is retried (default: {work.RETRIES})",
    )
    parser.add_argument("prompt", help="what Claude is asked to do")
    args = parser.parse_args(argv)
    if not os.path.isdir(args.dir):
        parser.error(f"--dir {args.dir}: no such folder")
    if not args.prompt.strip():
        parser.error("the prompt is empty: give the work's prompt as the last word, in quotes")
    if shutil.which("claude") is None:
        parser.error(
            "claude isn't on the PATH: run overnight from Claude Code, as `! overnight ...`"
        )
    started = f"{datetime.datetime.now():%Y%m%d-%H%M%S}"
    folder = os.path.join(os.path.expanduser("~"), ".local", "state", "overnight", started)
    os.makedirs(folder)
    where = os.path.abspath(args.dir)
    work.start(folder, work.Work(where, args.allowed_tools, args.retries, args.prompt))
    print(f"overnight: work {os.path.basename(folder)} started in {where}")
    print(f"overnight: state and log in {folder}/")


def _count(text: str) -> int:
    try:
        count = int(text)
    except ValueError:
        count = -1
    if count < 0:
        raise argparse.ArgumentTypeError(f"must be a whole number from 0, not {text!r}")
    return count
