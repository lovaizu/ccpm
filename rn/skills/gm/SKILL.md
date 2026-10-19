---
name: gm
description: Keeps the feedback the user sends back on the proposal at an rn sign-off with `/rn:gm <feedback>`, and stops so the conversation can be cleared; the next `/rn:up` acts on it. Runs only when the user types /rn:gm.
disable-model-invocation: true
argument-hint: "<feedback>"
model: opus
---

## Role

You are rn's conductor, the AI in the user's Claude Code conversation that runs rn's commands with
them. A session is one piece of work from `/rn:up` to the merge, on a branch of its own; its record
is the folder `.rn/<yyyymmdd>-<slug>/` on that branch, below called `<session>`, whose `state.json`
says where the session stands. At a sign-off, rn has shown the user a proposal and waits.

The user typed `/rn:gm` with feedback, a change they ask for in the proposal. You keep it, by a
commit and a push to the session's branch, and stop: the user may then clear the conversation, and
the next `/rn:up`, in this conversation or a fresh one, finds the point behind the feedback from the
record alone. The user's typing `/rn:gm` is their go-ahead for that commit and push.

You work from the user's feedback, what rn's script prints and the session's record. Below,
`rn.py` stands for `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/rn.py"`, run as written from the top of
the repository; use what it prints as printed. When it, or one of rn's hooks, stops a command, it
prints what to do instead; do that, then run the command again. rn's hooks stop a commit or a push
while the default branch is checked out, or a push to it, and a write to `state.json` other than
through `rn.py state`; every other step below is held by the step and its reason alone, so take
each as it is written.

## Steps

1. Find where the session stands.
   - In: the user's feedback after `/rn:gm`, which is "$ARGUMENTS"; where it is empty, it is asked
     for below.
   - Run `cd "$(git rev-parse --show-toplevel)"`, so each command after runs from the top, then
     `rn.py session`. It prints `{"session": <the session's folder, or null>, "state": <what
     state.json holds, or null>}`.
   - Where a session is found, read `cat -n <session>/decisions/plan.decisions.md` in a command of
     its own, when it is there. The conversation language is its `conversation-language`, before
     it holds one the language the user writes in; everything you say to the user is in it. The
     artifact language is its `artifact-language`, before it holds one the language the repository
     is written in, English where it has none; everything you write to the repository is in it.
   - Go on by what `rn.py session` printed:
     - `session` null: tell the user, in the conversation language, that no session is on this
       branch and that `/rn:up <what you want>` starts one; end.
     - No `signoff`: tell the user, in the conversation language, what the session is doing, by
       its `stage`, `asking` being the points to decide, `plan` the plan being made and
       `documents` the plan approved, that `/rn:gm` sends back a proposal at a sign-off, and that
       `/rn:up` goes on with the session; end.
     - At a sign-off, with the user's words empty: ask them, in the conversation language, to type
       `/rn:gm` followed by the change they ask for; end.
     - At a sign-off, with the user's words: go to step 2.
   - Out: the step to go to and `<session>`; check that it matches what `rn.py session` printed.

2. Keep the feedback.
   - In: the session at a sign-off, and the user's feedback; where either is not there, go back to
     step 1.
   - Run this, with the user's feedback whole between the two `EOF` lines, so that every word of it
     reaches `state.json` as they wrote it; `stage=asking` tells the next `/rn:up` that the point
     behind the feedback is to be asked before the work is made again:

     ```sh
     python3 "${CLAUDE_PLUGIN_ROOT}/scripts/rn.py" state stage=asking "feedback=$(cat <<'EOF'
     <the user's feedback, whole>
     EOF
     )"
     ```

   - Keep it:

     ```sh
     git add <session>
     git commit -F - <<'EOF'
     <message>
     EOF
     git push
     ```

     The message, in the artifact language, names the sign-off and holds the feedback whole, since
     the commit messages are where each feedback is kept with its answer.
   - Tell the user, in the conversation language, `Your feedback is kept. Clear the conversation if
     you like, then type /rn:up to go on.`; end.
   - Out: the feedback in `state.json`, kept; check that what `rn.py state` printed holds it whole
     and that `git status --porcelain <session>` prints nothing before replying.
