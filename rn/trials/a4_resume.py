#!/usr/bin/env python3
"""A4: /rn:up on the coupon session paused in its first build task, to the first edit of the code or
the first call to the stand-in."""
from common import Trial


def edited():
    return bool(t.git("status", "--porcelain", "--", "src").strip())


def scene():
    t.start_from("coupon-paused")
    t.turn("/rn:up", stop_when=edited)


t = Trial(__doc__)
t.run(scene)
