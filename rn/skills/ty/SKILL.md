---
name: ty
description: Approves the sign-off the rn session on the current branch is waiting for, records the approval, and stops. Used when the user types /rn:ty after reading a proposal.
disable-model-invocation: true
---

## Role

You are the conductor of an rn session. `/rn:ty` approves the sign-off the session is waiting
for, records it and stops. The approval becomes the ground everything the session does later
stands on, so the session goes on from it, taking what it approved as settled.

## Steps

1. Read step 1 of `${CLAUDE_PLUGIN_ROOT}/references/conduct.md`, The frame, and keep it from here
   on.
2. Read `${CLAUDE_PLUGIN_ROOT}/references/record.md` whole, and find the session as its step 1
   says.
3. When the session is not waiting for a sign-off, as record.md's step 7 tells, tell the user what
   the session is doing, from the last decision line, and end, since there is no sign-off to
   approve.
4. In `steering.md`, mark that sign-off's task `[x]`.
5. At the Deliverable sign-off, set `status` in `steering.md` to `finished`, and mark the pull
   request ready with `gh pr ready <pr>`.
6. Commit and push as record.md's step 5 says, with the decision line its step 6 gives after
   `/rn:ty`.
7. Give the user what `git log -1 --format=%b` prints, then:
   - at the Deliverable sign-off, that the pull request is ready, with its URL, and that the merge
     is theirs; end;
   - otherwise, `Say "go on", or /clear and then /rn:up.`, and end.
8. When the user says to go on, read the rest of `${CLAUDE_PLUGIN_ROOT}/references/conduct.md`,
   from step 2 to the end, and go on as its step 8, Taking up the session, says.
