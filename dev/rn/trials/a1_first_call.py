#!/usr/bin/env python3
"""A1's first scene: /rn:on move src/account to TypeScript on main, the stand-in settling the
languages, to rn's next call to it."""
from common import ACCOUNT_PART, Trial


def scene():
    said, sid, _ = t.turn("/rn:on move src/account to TypeScript")
    t.turn(t.stand_in(ACCOUNT_PART, said), sid)
    t.log("trial", "Ended at rn's first call after the languages.")


t = Trial(__doc__)
t.run(scene)
