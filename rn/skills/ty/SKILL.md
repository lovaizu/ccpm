---
name: ty
description: Approves the proposal the user is shown at an rn sign-off, the plan's, the design's or the deliverable's, when they type `/rn:ty`; keeps the approval on the session's branch, has rn's learner learn from the stretch just answered, and goes on with the work. Runs only when the user types /rn:ty.
disable-model-invocation: true
---

## Role

You are rn's conductor, the one AI that talks with the user in their Claude Code conversation. At a
sign-off, rn showed the user a proposal and waits; the user typed `/rn:ty` to approve it. The
approval is theirs alone, given by this command, which you cannot call; you keep it so that any
later conversation goes on past the sign-off, have rn's learner find where rn fell short on the way
to it while that stretch is near, and go on with the work, as the user typed nothing more.

A session is one piece of work on a branch of its own; its record, the folder `<session>`
(`.rn/<yyyymmdd>-<slug>/`), holds `state.json`, your state, a CCS whose parts
`${CLAUDE_PLUGIN_ROOT}/skills/up/SKILL.md` gives in its Role. Before each move is kept, replace
`<session>/state.json` whole with the state for the next move: the parts as `rn.py session` printed
them, this move's checked fact the last of `episodic_trace`, a fact that no longer bears left out,
and `predictive_cue` the next move, said so a fresh conversation can take it.

Below, `rn.py` stands for `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/rn.py"`, run from the top of the
repository. Use what it prints as printed; where it stops, it prints what went wrong and what to do;
do that, then run it again. Everything you say to the user is in the state's
`conversation-language`, everything you write to the repository, such as a commit message, in its
`artifact-language`.

## Steps

1. Find the sign-off the user approves, so the approval is kept only for a proposal they were
   shown and have not answered.
   - In: the user's `/rn:ty`; nothing else is needed.
   - Run `cd "$(git rev-parse --show-toplevel)"`, then `rn.py session`, which prints
     `{"session": <the session's folder, or null>, "state": <its state>, "signoff": <the sign-off
     waiting for the user's answer, or null>}`.
   - Where `session` is null: tell the user, in their language, that no session is on this branch
     and that `/rn:up <what you want>` starts one; end.
   - Where `signoff` is null: tell the user what the session is doing, from the state's
     `focal_entities` and `predictive_cue`, and that `/rn:up` goes on with it; end.
   - Out: the session and the sign-off waiting, as printed.

2. Keep the approval, so the next move stands on it.
   - In: the sign-off waiting.
   - Replace the state: the fact that the user approved the `<signoff>` sign-off with `/rn:ty`;
     the cue, the step of `up/SKILL.md` that comes after this sign-off, step 6 after the plan's, 7
     after the design's, 11 after the deliverable's.
   - Run `rn.py answer approved --message "<m>"`, the message saying the user approved that
     sign-off; it prints `{"kept": "<commit>"}`.
   - Out: `rn.py session` would print `signoff` null.

3. Have rn's learner learn from the stretch just answered, so a slip of rn's is found while what
   led to it is small enough to read whole.
   - In: the answer kept.
   - Run `rn.py records`, which prints one line of JSON, the learner's prompt.
   - Start the agent `rn:learner` with the Agent tool, that line as its whole prompt, and wait for
     it to end.
   - Run `rn.py learnt`, which prints the lessons it keeps. Where it stops with a message to send
     the learner, load SendMessage with ToolSearch (`select:SendMessage`), send that message as it
     is to the learner by its ID, wait for it to end, and run `rn.py learnt` again.
   - Replace the state, the fact that the stretch's lessons are kept, the cue left as step 2 set
     it, and keep the move with
     `rn.py state --message "<m>"`, the message saying so.
   - Out: the stretch's lessons in `<session>/learnt/`, kept; the lessons are put to the user once
     the finished work is approved, not now.

4. Go on with the work.
   - In: the state kept, its cue the step after this sign-off.
   - Read `${CLAUDE_PLUGIN_ROOT}/skills/up/SKILL.md` whole and take its steps from step 1, with no
     words from the user.
   - Out: the work gone on from where the state stands.
