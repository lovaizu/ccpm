---
name: on
description: Start an rn session. Work out with the user what they really want, plan up to their next decision on a draft pull request, and stop for their approval. It writes files, commits, pushes, and opens a pull request, so run it only on an explicit /rn:on.
disable-model-invocation: true
---

# /rn:on — Start a session

The user gives a goal, roughly. Find out what they really want, and plan the way there only as far as
their next decision — a choice of taste, scope, or cost against benefit — since what follows depends
on it. The work then goes on without them until that decision. A plan built on their literal words
is evaluated against the wrong Goal, and they find that out only at the end.

## Work out the Goal

Start from `$ARGUMENTS` and the repository. Settle first what done looks like, since it fixes the
scope; then why they want it, how they will know, and the way there. Ask one question at a time: your
reading, what it decides, and the answer you recommend, so they can agree in a word or correct you.
Look facts up yourself; put decisions to them. You are done when you both see the same Goal and way,
and nothing the plan rests on is assumed without their knowing.

## Write the plan

On a new branch from the default branch, write `.rn/{yyyymmdd}-{slug}/steering.md` from
`${CLAUDE_PLUGIN_ROOT}/references/steering.md`, in the language of the repository's documents, with
`rn` from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`. The slug names what the work produces.
Check it against the Plan section of `${CLAUDE_PLUGIN_ROOT}/references/viewpoints.md` and against
what you agreed: only you heard the conversation. Commit and push.

## Have it evaluated

As in `${CLAUDE_PLUGIN_ROOT}/references/turn.md`, and decide on it there; a More that is the user's
to decide, ask them here.

## Stop

Open a draft pull request whose body links `steering.md` on the branch, write its URL in `pr`, and
stop for the user at the Plan sign-off as in `${CLAUDE_PLUGIN_ROOT}/references/turn.md`.
