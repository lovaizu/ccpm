#!/usr/bin/env python3
"""A4: the coupon session at its first build task, stopped once the generator has edited a file,
then /rn:dn, /clear, and /rn:up, until that task is checked off."""
import os
import re

from common import COUPON_PART, MAX_TURNS, Trial

TASK_DONE = re.compile(r"^### \[x\] #3:", re.M)


def task_done():
    with open(os.path.join(t.work, ".rn", "20261004-coupon-discount", "steering.md")) as f:
        return bool(TASK_DONE.search(f.read()))


def edited():
    return bool(t.git("status", "--porcelain", "--", "src", "test").strip())


def scene():
    t.start_from("coupon")
    said, sid, _ = t.turn("/rn:up")
    paused = False
    for _ in range(MAX_TURNS):
        if task_done():
            t.log("trial", "Task #3 is checked off.")
            return
        said, sid, stopped = t.turn(t.stand_in(COUPON_PART, said), sid,
                                    None if paused else edited)
        if stopped:
            paused = True
            t.turn("/rn:dn", sid)
            t.log("trial", "/clear")
            said, sid, _ = t.turn("/rn:up")
    t.log("trial", "Turn limit reached.")


t = Trial(__doc__)
t.run(scene)
