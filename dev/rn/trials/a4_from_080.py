#!/usr/bin/env python3
"""A4: /rn:up on the coupon session paused under rn 0.8.0 in its first build task, to the first call
to the stand-in."""
from common import Trial


def scene():
    t.start_from("coupon-0.8.0")
    t.turn("/rn:up")


t = Trial(__doc__)
t.run(scene)
