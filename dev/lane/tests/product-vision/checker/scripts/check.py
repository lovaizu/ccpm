"""Prints `ok` where the file given holds an `## Unreleased` heading, and exits 1 otherwise."""

import sys

with open(sys.argv[1], encoding="utf-8") as f:
    held = "## Unreleased" in f.read().splitlines()
print("ok" if held else "no `## Unreleased` heading")
sys.exit(0 if held else 1)
