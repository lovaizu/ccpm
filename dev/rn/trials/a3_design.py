#!/usr/bin/env python3
"""A3 at the Design sign-off: the account session with its plan approved and every design point
agreed, waiting for writ, paused; /rn:up to the Design sign-off, writ writing the documents on the
way. Two stand-ins, who decided the design points in the fixture's notes item, decide, one from the
proposal alone and one from the documents on the pull request; both are recorded, neither is sent."""
import os

from common import ACCOUNT_PART, FIXTURES, Trial, decide_at_sign_off, read

NOTES = os.path.join(FIXTURES, "account-design", "tree", ".rn", "20261005-account-to-typescript",
                     "open", "01-notes-design.md")
PART = ACCOUNT_PART + "\n- What you decided in the design, with rn:\n\n" + read(NOTES)

t = Trial(__doc__)
t.run(lambda: decide_at_sign_off(t, PART, "account-design", "Design sign-off",
                                 "the README, design document, and verification document"))
