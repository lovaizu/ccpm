#!/usr/bin/env python3
"""A2: the account session with the stand-in's reason recorded and no criterion yet written, /rn:up
to rn's second call to the stand-in, which answers the first; its answer to the second is recorded
but not sent, so whether it asks back shows."""
from common import ACCOUNT_PART, Trial


def scene():
    t.start_from("account-why")
    said, sid, _ = t.turn("/rn:up")
    said, sid, _ = t.turn(t.stand_in(ACCOUNT_PART, said), sid)
    t.log("stand-in, not sent", t.stand_in(ACCOUNT_PART, said))
    t.log("trial", "Ended at rn's second call.")


t = Trial(__doc__)
t.run(scene)
