---
name: up
description: Resume an rn session in a fresh conversation, from where the last one stopped. It writes files, commits, and pushes, so run it only on an explicit /rn:up.
disable-model-invocation: true
---

# /rn:up — Resume

The user cleared the conversation and comes back without explaining anything again.

1. Find the session: the `.rn/*/steering.md` the current branch added whose `status` is `running`.
   None: say there is no session on this branch, and stop.
2. Read, in order and only these: `steering.md`; the first task not marked `[x]`, and its
   `ccs/{id}.yaml`; what that CCS points to.
3. Say, in the `conversation-language`: `● resuming {slug} at #{id} {task name}`.
4. Go on from the CCS's `next` as `${CLAUDE_PLUGIN_ROOT}/skills/on/SKILL.md` says from step 5: put
   its `question` again, or, when it is `waiting for #1 Plan sign-off`, give that proposal again and
   stop. Any other move, such as working out the design, this rn cannot make yet: say so, and stop.
