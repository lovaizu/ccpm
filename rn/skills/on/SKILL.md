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

Write it to `.rn/{yyyymmdd}-{slug}/steering.md` on a new branch from the default branch, from the
template in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`, reading what each part is for. The slug
is a short kebab-case name for what the work produces. `rn` is `version` in
`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`. Uncommitted changes in the tree are the user's,
so ask what to do with them before you create the branch.

## Have the plan judged

Start a fresh agent with `Agent` to judge the plan. Give it
`${CLAUDE_PLUGIN_ROOT}/references/evaluate.md`, the kind `Plan`, the path of `steering.md`, and the
file for its verdict: `evaluations/{NN}-plan.md` next to `steering.md`, `{NN}` counting up from
`01`. Give it nothing else. Your reasons and how the plan came about would pull it toward your view.

Then decide by the goal, reading its Mores. Fix the plan and have it judged again; bring the user in
when a More is theirs to decide; or go on when the plan does its job. Show each decision as one line:

```
● plan ── judged: {passes | fails ({the More that decides it})} → {what you do next}
```

## Put it on record and stop

Commit `steering.md` and `evaluations/`, and push. Open a draft pull request whose body links
`steering.md` on the branch. Write its URL in `pr`, commit, and push.

Then stop. Open your message with the session's map, in the user's language:

```
── {slug}: {the goal in one line} ──
👉 #1   Plan sign-off ── {what you need from the user}
⬜ #{ids}   {task names, separated by /}
({what happens after this stop})
```

Ask them to read the plan on the pull request, with your recommendation. They answer with `/rn:ty` to
approve, or `/rn:gm <feedback>` to ask for changes.
