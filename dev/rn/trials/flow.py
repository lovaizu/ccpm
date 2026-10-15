#!/usr/bin/env python3
"""The flow session: /rn:up add to README.md that the shop closes on Sundays, on main, carried by
the stand-in through the plan, the design and the one task to the Deliverable sign-off approved,
or until rn stops calling it; the smallest session that shows the course from /rn:up to the end."""

from common import MAX_TURNS, Trial

FLOW_PART = """You are the user of a small shop backend, talking with a tool called rn in Japanese.
You started with: /rn:up add to README.md that the shop closes on Sundays
- Why you want this, said only when asked why: customers kept coming on Sundays and found the shop
  closed.
- You want nothing else and know nothing else; when asked something you do not know, say you do not
  know and to go on as rn proposes.
- When rn asks which languages to use, you answer: both English.
- At a sign-off (rn shows a map with 👉 and asks for /rn:ty or /rn:gm), you approve with /rn:ty when
  the proposal shows nothing against your reason, and otherwise give /rn:gm followed by what you saw.
- When rn says to say "go on", you say: go on
You never look at the code or the pull request yourself."""


def scene():
    said, sid, _ = t.turn("/rn:up add to README.md that the shop closes on Sundays")
    for _ in range(MAX_TURNS):
        reply = t.stand_in(FLOW_PART, said)
        said, sid, _ = t.turn(reply, sid)
        if (
            reply.strip().startswith("/rn:ty")
            and t.git("log", "-1", "--format=%B").find("── approved → finished") >= 0
        ):
            t.log("trial", "The Deliverable sign-off is approved.")
            return
    t.log("trial", "Ended at the turn limit.")


t = Trial(__doc__)
t.run(scene)
