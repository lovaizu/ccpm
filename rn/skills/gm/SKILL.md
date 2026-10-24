---
name: gm
description: Keeps the feedback the user sends back on the proposal at an rn sign-off with `/rn:gm <feedback>`, has the learnings of the stretch just answered made through turn, and stops so the conversation can be cleared; the next `/rn:up` finds the point behind the feedback and acts on it. Runs only when the user types /rn:gm.
disable-model-invocation: true
argument-hint: "<feedback>"
---

## Role

You are rn's orchestrator, the one AI that talks with the user in their Claude Code conversation. At
a sign-off, rn showed the user a proposal and waits; the user typed `/rn:gm` with feedback, a change
they ask for. You keep the feedback whole, as their words are what the next `/rn:up`, in this
conversation or a fresh one, finds the point behind it from; have the learnings of the stretch that
led to it made while that stretch is near; and stop, so the user may clear the conversation.

A session is one piece of work on a branch of its own; its record, the folder `<session>`
(`.rn/<yyyymmdd>-<slug>/`), holds `steering.md`, the plan and where the session stands, which rn's
scripts alone write, and `turn/`, each call to turn. You never edit the steering, and never run
`git commit` or `git push`: each move is kept by a subcommand of `rn.py`, which stands for
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/rn.py"`, run from the top of the repository. Use what it
prints as printed; where it stops, it prints what went wrong and what to do: do that, then run it
again; where what it says to do is the user's to do, tell the user and end.

`--next` is the step of `/rn:up` to take next, by its number and on what, as
`Step <n> of /rn:up on <work>: <what is left of it>`, so a fresh conversation takes it from the
steering alone; `--open` each point still open, a checked fact, one `--open` each, as Open is
replaced whole. The message, in the artifact language, says what the move records, and for
feedback the feedback whole, as the steering keeps only what holds now. Pass a message of more than
one line as `--message "$(cat <<'EOF'`, the message on the lines after, then `EOF` and `)"`.
Everything you say to the user is in the steering's `conversation-language`, everything you write
to the repository in its `artifact-language`.

## Steps

1. Find the sign-off the feedback answers, so it is kept only for a proposal the user was shown and
   has not answered.
   - In: the user's feedback after `/rn:gm`, which is "$ARGUMENTS".
   - Run `cd "$(git rev-parse --show-toplevel)"`, then `rn.py session`, which prints
     `{"session": <the session's folder, or null>, "stage": <its stage, or null>, "signoff": <the
     sign-off waiting for the user's answer, or null>}`. Where `session` is not null, read
     `<session>/steering.md` whole with `cat -n`.
   - Where `session` is null: tell the user, in their language, that no session is on this branch
     and that `/rn:up <what you want>` starts one; end.
   - Where `signoff` is null: tell the user where the session stands, from the steering's stage and
     Next, and that `/rn:up` goes on with it; end.
   - Where the feedback is empty: ask the user to type `/rn:gm` followed by the change they ask
     for; end.
   - Out: the sign-off waiting and the feedback.

2. Keep the feedback whole, so the next `/rn:up` acts on the user's own words.
   - In: the sign-off waiting and the feedback.
   - Run `rn.py answer feedback --next "Step 10 of /rn:up on <the sign-off>: find the point behind
     the feedback" --open "<the feedback whole, as the user wrote it>" [--open <o>]... --message
     <m>`, the other `--open` each point the steering's Open holds still open, the message naming
     the sign-off and holding the feedback whole. It prints `{"kept": "<commit>"}`.
   - Out: the feedback whole in the steering's Open, kept.

3. Have the learnings of the stretch just answered made: take step 3 of
   `${CLAUDE_PLUGIN_ROOT}/skills/ty/SKILL.md` as it is written there, that step alone.
   - In: the feedback kept.
   - Out: the stretch's learnings kept, Next as step 2 set it.

4. Stop, so the user may clear the conversation.
   - Tell the user `Your feedback is kept. Clear the conversation if you like, then type /rn:up to
     go on.`, in the conversation language with the command as it is; end.
