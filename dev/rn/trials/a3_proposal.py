#!/usr/bin/env python3
"""A3: the account session paused with its plan settled and its proposal not yet drafted, /rn:up to
the Plan sign-off. Two stand-ins with the same part and the same instruction decide, one from the
proposal alone and one from the pull request; both are recorded, neither is sent."""
from common import ACCOUNT_PART, Trial, decide_at_sign_off

t = Trial(__doc__)
t.run(lambda: decide_at_sign_off(t, ACCOUNT_PART, "account-ready", "Plan sign-off",
                                 "the plan (.rn/*/steering.md)"))
