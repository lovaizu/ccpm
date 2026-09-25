---
name: up
description: Resume an rn session in a fresh conversation — bring an older session up to date, act on the user's recorded answer, and run the work to their next decision. It writes files, commits, pushes, and posts replies on the pull request, so run it only on an explicit /rn:up.
disable-model-invocation: true
---

# /rn:up — Resume

A fresh conversation takes the session up from `steering.md` and git, and carries it on as if it had
never stopped, until the next decision that is the user's.

Find the session as in Finding the session in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`, and read
`steering.md` in full. Say which session you resume and where:

```
● Resuming {slug} at #{id}: {task name}
```

## Bring an older session up to date

A session started under an earlier `rn` has no `rn` field in its frontmatter, or one that differs
from `version` in `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`. Rewrite it in the shape of the
template in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`, so this `rn` can run it, with nothing it
recorded lost:

- Carry the Goal, the Assumptions, the Rules, and every task with its id, name, fields, and
  check-offs; a checked step stays word for word. Old names for the same thing take the template's
  names: Acceptance criteria become Goal reached when, Completion criteria become Purpose reached when.
- Lift the old header lines, and the issue and pull request the old `State` names, into the
  frontmatter; carry every other fact of the old `State` into `Next`, `Feedback`, and `Notes`.
- Drop an unchecked step that only ran the old `rn`'s own review — a self-check, an expert review, a
  record into `checks/` — and remove those records. A sign-off task gets the one step
  `Approved by the user`, checked if the old task was complete.

Check the rewrite against the commit before it, part by part, so nothing is lost. Set `rn` to the
installed version, commit `chore: bring session up to rn {version}`, push, and have the plan
evaluated as in Having it evaluated in `${CLAUDE_PLUGIN_ROOT}/references/turn.md`. Lines the old
`rn` wrote as work to do rather than a state reached will show up there as Mores; fix them before
going on.

## Act on the user's answer

Set `status` to `running` and remove `paused_at`.

When `Feedback` holds a revision, it is about what the session stopped for at `Next`. Revise that — the
plan, the design choice, or the finished work — so it answers every point, and have the revision
evaluated as its kind. For a point from a pull request review thread, reply on the thread with what
changed and the commit, in the language of the comment; leave resolving it to the user. Set
`Feedback` to none, commit, push, and stop for the user at the same sign-off, as in Stopping for the
user in `${CLAUDE_PLUGIN_ROOT}/references/turn.md`.

## Go on

Otherwise, run the session from `Next` as in `${CLAUDE_PLUGIN_ROOT}/references/turn.md`, until it
stops for the user.
