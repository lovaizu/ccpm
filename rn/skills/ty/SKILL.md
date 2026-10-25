---
name: ty
description: Approves the proposal the user is shown at an rn sign-off, the plan's, the design's or the deliverable's, when they type `/rn:ty`; keeps the approval on the session's branch, has the learnings of the stretch just answered made through turn, and goes on with the work. Runs only when the user types /rn:ty.
disable-model-invocation: true
---

## Role

You are rn's orchestrator, the one AI that talks with the user in their Claude Code conversation. At
a sign-off, rn showed the user a proposal and waits; the user typed `/rn:ty` to approve it. The
approval is theirs alone, given by this command, which you cannot call. You keep it so that any
later conversation goes on past the sign-off; have the learnings of the stretch that led to it made
while that stretch is near and small enough to read whole; and go on with the work, as the user
typed nothing more.

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
replaced whole. The message, in the artifact language, says what the move records. Pass a message of
more than one line as `--message "$(cat <<'EOF'`, the message on the lines after, then `EOF` and
`)"`. Everything you say to the user is in the steering's `conversation-language`, everything you
write to the repository in its `artifact-language`.

## Steps

1. Find the sign-off the user approves, so the approval is kept only for a proposal they were shown
   and have not answered.
   - In: the user's `/rn:ty`; nothing else is needed.
   - Run `cd "$(git rev-parse --show-toplevel)"`, then `rn.py session`, which prints
     `{"session": <the session's folder, or null>, "stage": <its stage, or null>, "signoff": <the
     sign-off waiting for the user's answer, or null>}`. Where `session` is not null, read
     `<session>/steering.md` whole with `cat -n`.
   - Where `session` is null: tell the user, in their language, that no session is on this branch
     and that `/rn:up <what you want>` starts one; end.
   - Where `signoff` is null: tell the user where the session stands, from the steering's stage and
     Next, and that `/rn:up` goes on with it; end.
   - Out: the sign-off waiting, as printed.

2. Keep the approval, so the next move stands on it.
   - In: the sign-off waiting.
   - Run `rn.py answer approved --next <n> [--open <o>]... --message <m>`, Next the step the approved
     sign-off leads to: after the plan's, `Step 7 of /rn:up on plan: hear which documents the
     purpose needs`; after the design's, `Step 8 of /rn:up on plan: make the tasks that build the
     finished work`; after the deliverable's, `Step 11 of /rn:up: put each learning to the user`.
     Open is what the steering's Open holds still open; the message says the user approved that
     sign-off with `/rn:ty`. It moves the stage on and prints `{"kept": "<commit>"}`.
   - Out: no sign-off waiting, Next the step after it.

3. Have the learnings of the stretch just answered made, so a slip of rn's is found while what led
   to it is near.
   - In: the answer kept.
   - Run `rn.py records`, which prints the paths of the stretch's texts: its history on the branch,
     the session's files and the orchestrator's conversations of it.
   - Read `${CLAUDE_PLUGIN_ROOT}/skills/up/SKILL.md` whole, then take its step 4 on work
     `learnings`: no path, kind `learnings`, receiver `the user deciding each learning once the
     finished work is approved`, use `deciding where each learning goes: their checklists, an issue
     to rn's makers, both, or neither`, a `--has` for each path `rn.py records` printed, and as the
     step that comes after, the Next step 2 set, so the call is kept with `--put`, that Next, and
     an `--open` for each point the steering's Open holds, as Open is replaced whole.
   - Out: the stretch's learnings in `<session>/learnings.md`, kept; they are put to the user once
     the finished work is approved, not now.

4. Go on with the work.
   - In: the learnings kept, the steering's Next the step after this sign-off.
   - Take the steps of `${CLAUDE_PLUGIN_ROOT}/skills/up/SKILL.md` from the step the steering's Next
     names, with no words from the user.
   - Out: the work gone on from where the steering stands.
