---
name: on
description: Start an rn session. Work out with the user what they really want, plan up to their next decision on a draft pull request, and stop for their approval. It writes files, commits, pushes, and opens a pull request, so run it only on an explicit /rn:on.
disable-model-invocation: true
---

# /rn:on — Start a session

The user gives a goal, roughly. Find out what they really want, and plan the way to it, so the work can
go on without them until a decision is theirs. A plan built on the literal words is judged against the
wrong thing, and the user finds that out only at the end.

## Work out the goal

Start from `$ARGUMENTS` and what the repository shows. First settle what done looks like, since it
fixes the scope every later answer is measured against; then why they want it, how they will know it
is done, and the way to get there.

Ask one question at a time, and wait for the answer before the next. Put it as your reading, with
what it decides and the answer you recommend, so the user can agree in a word or correct you. Ask
only what the answers so far let you ask without guessing; each answer changes what comes next.
Facts are yours to find: look up what the repository or the environment can answer instead of
asking. Decisions are the user's: put each one to them. You are done when nothing the plan rests on
is left assumed without their knowing, and they agree you both see the same aim and way.

## Write the plan

The plan goes only as far as the next decision that is the user's: a choice of taste, scope, or cost
against benefit. What comes after depends on their answer, so it is planned once they give it. If no
such choice remains, the plan ends at the user's check of the finished work.

Uncommitted changes in the tree are the user's, so ask what to do with them first. Then create a new
branch from the default branch, and write the plan to `.rn/{yyyymmdd}-{slug}/steering.md` from the
template in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`, reading what each part is for. The slug is a
short kebab-case name for what the work produces. `rn` is `version` in
`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`. Write it in the language the repository's documents
are written in. What the plan must reach is the Plan section of
`${CLAUDE_PLUGIN_ROOT}/references/purpose.md`; check the plan against it, and against what you and the
user agreed: only you heard the conversation, so a goal written down wrong is yours to catch. Commit it
and push.

## Have the plan judged

Have the plan judged as the Plan kind, as in Having a result judged in
`${CLAUDE_PLUGIN_ROOT}/references/turn.md`.

Then decide by the goal, reading its Mores. Fix the plan and have it judged again; ask the user in the
conversation when a More is theirs to decide; or go on when the plan does its job. A fixed plan is
committed and pushed before it is judged again. Show each decision as one line:

```
● plan ── judged: {passes | fails ({the More that decides it})} → {what you do next}
```

## Put it on record and stop

Open a draft pull request whose body links `steering.md` on the branch. Write its URL in `pr`. Then
stop for the user at #1 Plan sign-off, as in Stopping for the user in
`${CLAUDE_PLUGIN_ROOT}/references/turn.md`.
