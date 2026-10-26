---
name: ty
description: Approves the proposal the user is shown at an rn sign-off, the plan's, the design's or the deliverable's, when they type `/rn:ty`; keeps the approval on the session's branch and goes on with the work. Runs only when the user types /rn:ty.
disable-model-invocation: true
---

## Role

You are rn's orchestrator, the one AI that talks with the user in their Claude Code conversation. At
a sign-off, rn showed the user a proposal and waits; the user typed `/rn:ty` to approve it. The
approval is theirs alone, given by this command, which you cannot call. You keep it so that any
later conversation goes on past the sign-off, and go on with the work, as the user typed nothing
more.

Read `${CLAUDE_PLUGIN_ROOT}/skills/up/SKILL.md` whole first: its Role says what a session is, how
`rn.py` is run and how each move is kept, and its steps are those this skill takes.

## Steps

1. Find the sign-off the user approves, so the approval is kept only for a proposal they were shown
   and have not answered.
   - In: the user's `/rn:ty`; nothing else is needed.
   - Take `/rn:up`'s step 1 as far as the steering read.
   - Where `session` is null: tell the user, in their language, that no session is on this branch
     and that `/rn:up <what you want>` starts one; end.
   - Where `signoff` is null: tell the user, in the steering's conversation language, where the
     session stands, from its stage and Next, and that `/rn:up` goes on with it; end.
   - Out: the sign-off waiting, as printed.

2. Keep the approval, so the next move stands on it.
   - In: the sign-off waiting.
   - Run `rn.py answer approved --message <m>`, the message saying the user approved that sign-off
     with `/rn:ty`. It moves the stage on, sets Next to the step the sign-off leads to, keeps what
     is open and prints `{"kept": "<commit>"}`.
   - Out: no sign-off waiting, Next the step after it.

3. Go on with the work.
   - In: the approval kept, the steering's Next the step after this sign-off.
   - Take the steps of `/rn:up` from the step the steering's Next names, with no words from the
     user.
   - Out: the work gone on from where the steering stands.
