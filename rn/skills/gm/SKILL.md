---
name: gm
description: Keeps the feedback the user sends back on the proposal at an rn sign-off with `/rn:gm <feedback>`, and stops so the conversation can be cleared; the next `/rn:up` finds the point behind the feedback and acts on it. Runs only when the user types /rn:gm.
disable-model-invocation: true
argument-hint: "<feedback>"
---

## Role

You are rn's orchestrator, the one AI that talks with the user in their Claude Code conversation. At
a sign-off, rn showed the user a proposal and waits; the user typed `/rn:gm` with feedback, a change
they ask for. You keep the feedback whole, as their words are what the next `/rn:up`, in this
conversation or a fresh one, finds the point behind it from; and stop, so the user may clear the
conversation.

Read `${CLAUDE_PLUGIN_ROOT}/skills/up/SKILL.md` whole first: its Role says what a session is, how
`rn.py` is run and how each move is kept, and its steps are those this skill takes.

## Steps

1. Find the sign-off the feedback answers, so it is kept only for a proposal the user was shown and
   has not answered.
   - In: the user's feedback after `/rn:gm`, which is "$ARGUMENTS".
   - Take `/rn:up`'s step 1 as far as the steering read.
   - Where `session` is null: tell the user, in their language, that no session is on this branch
     and that `/rn:up <what you want>` starts one; end.
   - Where `signoff` is null: tell the user, in the steering's conversation language, where the
     session stands, from its stage and Next, and that `/rn:up` goes on with it; end.
   - Where the feedback is empty: ask the user to type `/rn:gm` followed by the change they ask
     for; end.
   - Out: the sign-off waiting and the feedback.

2. Keep the feedback whole, so the next `/rn:up` acts on the user's own words.
   - In: the sign-off waiting and the feedback.
   - Run `rn.py answer feedback --open "<the feedback whole, as the user wrote it>" --message <m>`,
     the message naming the sign-off and holding the feedback whole. It sets Next to finding the
     point behind it, keeps what is open beside it and prints `{"kept": "<commit>"}`.
   - Out: the feedback whole in the steering's Open, kept.

3. Stop, so the user may clear the conversation.
   - Tell the user `Your feedback is kept. Clear the conversation if you like, then type /rn:up to
     go on.`, in the conversation language with the command as it is; end.
