#!/usr/bin/env python3
"""A4: /rn:up on the coupon session paused under rn 0.8.0 in its first build task, until the Plan
sign-off."""
from common import COUPON_PART, MAX_TURNS, Trial


def scene():
    t.start_from("coupon-0.8.0")
    said, sid, _ = t.turn("/rn:up")
    for _ in range(MAX_TURNS):
        if t.waiting_for() == "Plan sign-off":
            t.log("trial", "Stopped at the Plan sign-off.")
            return
        said, sid, _ = t.turn(t.stand_in(COUPON_PART, said), sid)
    t.log("trial", "Turn limit reached.")


t = Trial(__doc__)
t.run(scene)
