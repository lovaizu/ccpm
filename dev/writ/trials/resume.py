#!/usr/bin/env python3
"""Stop writ partway through agreeing a document's plan, start a fresh conversation on the same
document, and leave what writ said first in it, so whether the user has to explain again shows.

    python3 dev/writ/trials/resume.py <scene> <workdir>
"""
import sys
from pathlib import Path

from run import SCENES, STAND_IN, claude, setup, writ, writ_args


def main():
    name, workdir = sys.argv[1], Path(sys.argv[2]).resolve() / sys.argv[1]
    repo = setup(name, workdir)
    opening = SCENES[name]["opening"]
    said, _ = writ(opening, repo)
    talk = [("you", opening), ("writ", said)]
    sid = claude.session
    reply, _ = claude(STAND_IN.format(opening=opening, said=said), repo.parent, [])
    said, _ = claude(reply, repo, writ_args() + ["--resume", sid])
    talk += [("you", reply), ("writ", said), ("trial", "The conversation is cleared here.")]
    again = "/writ:up " + (SCENES[name]["target"] or "the document we were planning")
    fresh, _ = writ(again, repo)
    talk += [("you", again), ("writ, in a fresh conversation", fresh)]
    (workdir / "resume.md").write_text("".join(f"## {who}\n\n{text}\n\n" for who, text in talk))
    print(workdir / "resume.md")


if __name__ == "__main__":
    main()
