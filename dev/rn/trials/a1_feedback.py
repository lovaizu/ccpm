#!/usr/bin/env python3
"""A1's second scene: the account session at its first Plan sign-off is given
/rn:gm a user whose last name is null is shown "Ann null", to the next Plan sign-off."""
from common import ACCOUNT_PART, MAX_TURNS, Trial

FEEDBACK = '/rn:gm a user whose last name is null is shown "Ann null"'


def scene():
    t.start_from("account-plan")
    start = t.head()
    said, sid, _ = t.turn(FEEDBACK)
    for _ in range(MAX_TURNS):
        if t.head() != start and t.waiting_for() == "Plan sign-off":
            t.log("trial", "Ended at the next Plan sign-off.")
            return
        said, sid, _ = t.turn(t.stand_in(ACCOUNT_PART, said), sid)
    t.log("trial", "Turn limit reached.")


t = Trial(__doc__)
t.run(scene)
