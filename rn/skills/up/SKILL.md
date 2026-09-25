---
name: up
description: Resume an rn session in a fresh conversation — bring an older session up to date, act on the user's recorded answer, and run the work to their next decision. It writes files, commits, pushes, and posts replies on the pull request, so run it only on an explicit /rn:up.
disable-model-invocation: true
---

# /rn:up — Resume

A fresh conversation takes the session up from `steering.md` and git, and carries it on as if it had
never stopped, until the user's next decision.

Find the session as in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`, bringing it up to date if it
is older, and say:

```
● Resuming {slug} at #{id}: {task name}
```

Set `status` to `running`, remove `paused_at`, and go on as in After the user decides in
`${CLAUDE_PLUGIN_ROOT}/references/turn.md`.
