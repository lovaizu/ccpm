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

Start from `$ARGUMENTS` and what the repository shows. Tell the user how you read the goal, one point
at a time: what they want, why they want it, how they will know it is done, and how to get there. Move
to the next point only when they agree. You are done when you both agree on the aim behind their words
and on the way.

## Write the plan

The plan goes only as far as the next decision that is the user's: a choice of taste, scope, or cost
against benefit. What comes after depends on their answer, so it is planned once they give it. If no
such choice remains, the plan ends at the user's check of the finished work.

Write it to `.rn/{yyyymmdd}-{slug}/steering.md` on a new branch from the default branch. The slug is a
short kebab-case name for what the work produces. Uncommitted changes in the tree are the user's, so
ask what to do with them before you create the branch. Later commands, and later conversations, find
their way by these fields and headings:

```markdown
---
rn: <version in ${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json>
pr: <the pull request URL>
---

# Goal

<what the user wants and why, as agreed>

# Acceptance criteria

- <something the user can see is true once the goal is reached>

# Approach

<the way agreed, the choices the user made, and what the plan rests on, each marked checked or assumed>

# Tasks

- [ ] #1 Plan sign-off
- [ ] #2 <name>: <the outcome it reaches, and the criterion it serves>
  - Check: <how to tell, on the real thing, that the outcome is reached>
- [ ] #3 <Design sign-off: the choice | Evaluation sign-off>
```

## Have the plan judged

Start a fresh agent with `Agent` to judge the plan. Give it the path of `steering.md`, the questions
below, and the file for its verdict: `verdicts/{NN}-plan.md` next to `steering.md`, `{NN}` counting
up from `01`. Give it nothing else. Your reasons and how the plan came about would pull it toward your
view.

- If every criterion held, would the user have what they want: the aim, not only the words?
- Can each criterion and each check be seen on the real thing, not only as a file made or a step done?
- Do the tasks, in order, reach the next decision, and is that decision really the user's?
- Is what the plan rests on true?

Ask it to write whether the plan does its job and which faults decide that, with evidence for each
answer.

Then decide by the goal. Fix the plan and have it judged again; bring the user in when a fault is theirs
to decide; or go on when the plan does its job. Show each decision as one line:

```
● plan ── judged: {passes | fails ({the fault that decides it})} → {what you do next}
```

## Put it on record and stop

Commit `steering.md` and the verdicts, and push. Open a draft pull request whose body links
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
