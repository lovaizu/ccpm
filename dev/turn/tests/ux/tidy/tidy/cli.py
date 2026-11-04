"""The `tidy` command: `tidy [--dry-run] [folder]` sorts the folder, ~/Downloads where none is
given, and prints each move."""

import argparse
import os

from . import __version__
from .mover import move, plan


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="tidy", description="Sort a folder into folders by the kind of each file."
    )
    parser.add_argument("folder", nargs="?", default=os.path.expanduser("~/Downloads"))
    parser.add_argument("--dry-run", action="store_true", help="show each move without making it")
    parser.add_argument("--version", action="version", version=f"tidy {__version__}")
    args = parser.parse_args(argv)
    if not os.path.isdir(args.folder):
        parser.error(f"{args.folder} is not a folder")
    moves, stays = plan(args.folder)
    for name, kind in moves:
        print(f"{name} -> {kind}/")
    for name, why in stays:
        print(f"{name} stays: {why}")
    if not args.dry_run:
        move(args.folder, moves)
    print(f"{len(moves)} moved, {len(stays)} stayed" + (" (dry run)" if args.dry_run else ""))
    return 0
