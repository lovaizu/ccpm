---
name: on
description: Start an rn session. Work out with the user what they really want, plan up to their next decision on a draft pull request, and stop for their approval. It writes files, commits, pushes, and opens a pull request, so run it only on an explicit /rn:on.
disable-model-invocation: true
---

# /rn:on — Start a session

## Purpose

Every piece of work and every evaluation in the session is judged against the Goal set here, so the
Goal must be what the user really wants, not their first words: a plan built on the words reaches the
wrong thing, however well it is carried out, and the user finds out only at the end. The plan goes only
as far as the user's next decision, since what follows depends on it.

## Steps

1. Starting from `$ARGUMENTS` and the repository, work out the Goal with the user. Settle first what
   done looks like, since it fixes the scope; then why they want it, how they will know, and the way
   there. Ask one question at a time: your reading, what it decides, and the answer you recommend, so
   they can agree in a word or correct you. Look facts up yourself; put decisions to them. It is
   settled when you both see the same Goal and way, and nothing the plan rests on is assumed without
   their knowing.
2. On the current branch when it is not the default branch, otherwise on a new branch from the
   default branch, write `.rn/{yyyymmdd}-{slug}/steering.md` from
   `${CLAUDE_PLUGIN_ROOT}/references/steering.md`, in the language of the repository's documents, with
   `rn` from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`. The slug names what the work produces.
3. Check it against the Plan section of `${CLAUDE_PLUGIN_ROOT}/references/viewpoints.md` and against
   what you agreed: only you heard the conversation. Commit and push.
4. Have it evaluated and decide, as in `${CLAUDE_PLUGIN_ROOT}/references/turn.md`; a More that is the
   user's to decide, ask them here.
5. Link `steering.md` on the branch from the body of the branch's pull request, opening a draft one
   when it has none, and write its URL in `pr`.
6. Stop for the user at the Plan sign-off, as in `${CLAUDE_PLUGIN_ROOT}/references/turn.md`.
