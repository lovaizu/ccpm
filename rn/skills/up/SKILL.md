---
name: up
description: Resume an rn session in a fresh conversation — bring an older session up to date, act on the user's recorded answer, and run the work to their next decision. It writes files, commits, pushes, and posts replies on the pull request, so run it only on an explicit /rn:up.
disable-model-invocation: true
---

# /rn:up — Resume

A fresh conversation takes the session up from `steering.md` and git, and carries it on as if it had
never stopped, until the next decision that is the user's.

Find the session as in Finding the session in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`, and read
`steering.md` in full. A session started under an earlier `rn` is brought up to date first, as in
Bringing an older session up to date there. Say which session you resume and where:

```
● Resuming {slug} at #{id}: {task name}
```

Set `status` to `running` and remove `paused_at`. Then go on as in After the user decides in
`${CLAUDE_PLUGIN_ROOT}/references/turn.md`, and run turns from `Next` until the session stops for the
user.
