"""Decides what the `overnight` command takes from the user and what it gives back."""

from __future__ import annotations

import argparse
import datetime
import json
import os
import shutil
import time
from collections.abc import Sequence

from overnight import queue, work


def main(argv: Sequence[str], plugin: str) -> None:
    """Runs the `overnight` command on the words the user gave after its name.

    Takes: the words, and the plugin's folder, whose .claude-plugin/plugin.json holds its version.
    The words are `--dir <folder> --allowed-tools <tools> [--retries <count>] <prompt>` to add a
    work, none to go on with the works pending, or `--version`.
    Gives: for `--version`, `overnight <version>` on stdout, and exits 0. For a work, adds it to
    the queue in `~/.local/state/overnight/<yyyymmdd-hhmmss>/`, starts the runner, and returns at
    once, having written on stdout `overnight: work <id> started in <folder>`, or, where works are
    pending before it, `overnight: work <id> waits in the queue after <n> work(s), to run in
    <folder>`, then `overnight: state and log in <its folder>/`. For no words, starts the runner
    and writes `overnight: the queue goes on with <n> work(s), from work <id>`, with `<id>` the
    first pending, or, where none is pending, writes `overnight: no work waits in the queue` and
    starts nothing. The runner runs one work at a time, as `queue.run` says.
    Refuses: with exit code 2 and the reason on stderr, before it adds or starts anything: a word
    of a work missing, a `--dir` that names no folder, a `--retries` that isn't a whole number
    from 0, an empty prompt, and a PATH with no `claude` on it.
    """
    parser = _parser(plugin)
    args = parser.parse_args(argv)
    added = _work(parser, args)
    if shutil.which("claude") is None:
        parser.error(
            "claude isn't on the PATH: run overnight from Claude Code, as `! overnight ...`"
        )
    top = os.path.join(os.path.expanduser("~"), ".local", "state", "overnight")
    if added is None:
        _go_on(top)
    else:
        _add(top, added)


def _parser(plugin: str) -> argparse.ArgumentParser:
    with open(os.path.join(plugin, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
        version = json.load(f)["version"]
    parser = argparse.ArgumentParser(prog="overnight")
    parser.add_argument("--version", action="version", version=f"overnight {version}")
    parser.add_argument("--dir", help="the folder that Claude works in")
    parser.add_argument("--allowed-tools", metavar="TOOLS", help="the tools that Claude may use")
    parser.add_argument(
        "--retries",
        type=_count,
        metavar="COUNT",
        help=f"how many times a stopped run is retried (default: {work.RETRIES})",
    )
    parser.add_argument(
        "prompt", nargs="?", help="what Claude is asked to do; with no work, the queue goes on"
    )
    return parser


def _work(parser: argparse.ArgumentParser, args: argparse.Namespace) -> work.Work | None:
    """The work that the words give, or None where they give no word of one."""
    words = {"--dir": args.dir, "--allowed-tools": args.allowed_tools, "prompt": args.prompt}
    if args.retries is None and all(value is None for value in words.values()):
        return None
    missing = [name for name, value in words.items() if value is None]
    if missing:
        parser.error(f"the following arguments are required: {', '.join(missing)}")
    if not os.path.isdir(args.dir):
        parser.error(f"--dir {args.dir}: no such folder")
    if not args.prompt.strip():
        parser.error("the prompt is empty: give the work's prompt as the last word, in quotes")
    retries = work.RETRIES if args.retries is None else args.retries
    return work.Work(os.path.abspath(args.dir), args.allowed_tools, retries, args.prompt)


def _add(top: str, added: work.Work) -> None:
    ahead = len(queue.pending(top))
    folder = queue.add(top, added, datetime.datetime.now, time.sleep)
    queue.start(top)
    name = os.path.basename(folder)
    if ahead:
        waits = f"waits in the queue after {_works(ahead)}"
        print(f"overnight: work {name} {waits}, to run in {added.dir}")
    else:
        print(f"overnight: work {name} started in {added.dir}")
    print(f"overnight: state and log in {folder}/")


def _go_on(top: str) -> None:
    folders = queue.pending(top)
    if not folders:
        print("overnight: no work waits in the queue")
        return
    queue.start(top)
    first = os.path.basename(folders[0])
    print(f"overnight: the queue goes on with {_works(len(folders))}, from work {first}")


def _works(count: int) -> str:
    return "1 work" if count == 1 else f"{count} works"


def _count(text: str) -> int:
    try:
        count = int(text)
    except ValueError:
        count = -1
    if count < 0:
        raise argparse.ArgumentTypeError(f"must be a whole number from 0, not {text!r}")
    return count
