#!/usr/bin/env python3
"""Print the state a task is in, read from the CCS files in its folder, and what the conductor does
next, so a cleared conversation goes on from the same state.

    python3 state.py <the task's folder>
"""
import sys

import ccs

NEXT = {
    "fill": "Fill make.yaml, then start the maker with `request <task>/make.yaml`.",
    "align-make": "Start the maker with `request <task>/make.yaml`, agree what it will make, write goal_orientation: agreed, send go.",
    "make": "agreed is written: start the maker with `request <task>/make.yaml` and, once it has replied, send go.",
    "align-use": "Write use.yaml and start the first user with `request <task>/use.yaml`.",
    "align-recheck": "Write use.yaml with a recheck entry for each stumbled place and start the first user with `request <task>/use.yaml`.",
    "use": "agreed is written: start the first user with `request <task>/use.yaml` and, once it has replied, send go.",
    "recheck": "agreed is written: start the first user with `request <task>/use.yaml` and, once it has replied, send go.",
    "align-learn": "Write learn.yaml and start the learner with `request <task>/learn.yaml`.",
    "learn": "agreed is written: start the learner with `request <task>/learn.yaml` and, once it has replied, send go.",
    "judge": "Judge the first user's report against the pass condition, with the learnings in learn.yaml.",
}


def main(argv):
    found = ccs.state(argv[1])
    print(f"state: {found}\nnext: {NEXT[found]}")


if __name__ == "__main__":
    main(sys.argv)
