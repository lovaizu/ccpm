#!/usr/bin/env python3
"""A1's first scene and A2: /rn:on move src/account to TypeScript on main, to rn's third call to
the stand-in, which answers the first two."""
from common import ACCOUNT_PART, Trial

CALLS = 3


def scene():
    said, sid, _ = t.turn("/rn:on move src/account to TypeScript")
    for _ in range(CALLS - 1):
        said, sid, _ = t.turn(t.stand_in(ACCOUNT_PART, said), sid)
    t.log("trial", f"Ended at rn's call {CALLS}.")


t = Trial(__doc__)
t.run(scene)
