"""The command line of `overnight`: the options it takes, how it checks them, and what it prints as
it starts a work apart from the session that starts it."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

from overnight import record

# The retries of a work where the user gives no count: with the waits of the work module, 7 retries
# wait 5 hours and 15 minutes in all, past the 5-hour limit after any stop.
RETRIES = 7
# What the work's own process runs: overnight's code from `scripts/`, the first argument, and the
# work module's main with the rest, so that it finds the code wherever the plugin lies.
_WORKER = (
    "import sys; sys.path.insert(0, sys.argv.pop(1));"
    " from overnight import work; work.main(sys.argv[1:])"
)


def main(argv: list[str], root: str) -> None:
    """Runs `overnight` with `argv`, the arguments after its name, for the plugin in the folder
    `root`. Starts the work that the arguments give in a process of its own, in a session of its
    own, so that closing Claude Code doesn't stop it; prints the work's ID, its folder, and the
    folder that holds its state and log; and returns at once. With `--version` or `--help`, prints
    the plugin's version or every option, and exits 0 by SystemExit. Where an argument is wrong, or
    no `claude` is on the PATH, prints what to fix on stderr and exits 2 by SystemExit before it
    starts anything."""
    parser = _parser(_version(root))
    args = parser.parse_args(argv)
    folder = os.path.abspath(args.dir)
    if not os.path.isdir(folder):
        parser.error(f"--dir {args.dir}: no such folder")
    if not args.allowed_tools:
        parser.error("--allowed-tools is empty: name the tools that Claude may use for the work")
    if not args.prompt:
        parser.error("the prompt is empty: say what the work is")
    if shutil.which("claude") is None:
        parser.error("no claude is on the PATH: install Claude Code, or add its folder to the PATH")
    work = record.start(datetime.now(), folder)
    with open(os.path.join(work, record.LOG), "a", encoding="utf-8") as log:
        subprocess.Popen(
            [sys.executable, "-c", _WORKER, os.path.join(root, "scripts")]
            + [work, folder, args.allowed_tools, str(args.retries), args.prompt],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=log,
            start_new_session=True,
        )
    print(f"overnight: work {os.path.basename(work)} started in {folder}")
    print(f"overnight: state and log in {work}/")


def _parser(version: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="overnight",
        description="Runs a work through `claude -p` apart from Claude Code, and retries it in the"
        " same conversation after the usage limit or an error stops it.",
    )
    parser.add_argument("prompt", help="what the work is, as you would ask Claude (required)")
    parser.add_argument(
        "--dir",
        default=".",
        help="the folder the work runs in (default: the folder overnight is started in)",
    )
    parser.add_argument(
        "--allowed-tools",
        required=True,
        metavar="TOOLS",
        help="the tools that Claude may use for the work, as `claude --allowed-tools` takes them,"
        ' such as "Read,Edit,Bash(pytest:*)" (required)',
    )
    parser.add_argument(
        "--retries",
        type=_retries,
        default=RETRIES,
        metavar="COUNT",
        help=f"how many times a stopped work is retried (default: {RETRIES})",
    )
    parser.add_argument("--version", action="version", version=f"overnight {version}")
    return parser


def _retries(text: str) -> int:
    if not text.isdigit():
        raise argparse.ArgumentTypeError(f'must be a whole number from 0, not "{text}"')
    return int(text)


def _version(root: str) -> str:
    with open(os.path.join(root, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
        return json.load(f)["version"]
