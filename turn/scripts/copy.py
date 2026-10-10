#!/usr/bin/env python3
"""Makes, in the system's temporary folder, the state the receiver starts from: a fresh clone with
the work not yet committed added, so the first user meets what the receiver meets. Removes it after.
Usage: copy.py | copy.py --remove <path>"""
import os
import shutil
import subprocess
import sys
import tempfile

PREFIX = "turn-"


def git(*args, cwd=None):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout


def make(top):
    work = os.path.join(tempfile.mkdtemp(prefix=PREFIX), "work")
    git("clone", "-q", top, work)
    deleted = set(git("ls-files", "-d", "-z", cwd=top).split("\0")) - {""}
    for name in deleted:
        os.remove(os.path.join(work, name))
    for name in git("ls-files", "-m", "-o", "--exclude-standard", "-z", cwd=top).split("\0"):
        if name and name not in deleted:
            os.makedirs(os.path.dirname(os.path.join(work, name)), exist_ok=True)
            shutil.copy2(os.path.join(top, name), os.path.join(work, name))
    return work


def remove(path):
    """Only a copy this script made is removed."""
    parent = os.path.dirname(os.path.realpath(path))
    if os.path.dirname(parent) != os.path.realpath(tempfile.gettempdir()) or \
            not os.path.basename(parent).startswith(PREFIX):
        print(f"turn: {path} is not a copy turn made", file=sys.stderr)
        return 2
    shutil.rmtree(parent)
    return 0


def main(argv):
    if argv[1:2] == ["--remove"] and len(argv) == 3:
        return remove(argv[2])
    if len(argv) != 1:
        print("usage: copy.py | copy.py --remove <path>", file=sys.stderr)
        return 2
    print(make(git("rev-parse", "--show-toplevel").strip()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
