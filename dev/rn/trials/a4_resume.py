#!/usr/bin/env python3
"""A4: /rn:up on the coupon session paused in its first build task, carried by the stand-in to that
task's decision line."""

from common import COUPON_PART, MAX_TURNS, Trial


def decided():
    return "── decided:" in t.git("log", "-1", "--format=%B")


def scene():
    t.start_from("coupon-paused")
    said, sid, _ = t.turn("/rn:up")
    for _ in range(MAX_TURNS):
        if decided():
            t.log("trial", "Ended at the task's decision line.")
            return
        said, sid, _ = t.turn(t.stand_in(COUPON_PART, said), sid)
    t.log("trial", "Turn limit reached.")


t = Trial(__doc__)
t.run(scene)
