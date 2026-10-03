---
name: up
description: Resume an rn session in a fresh conversation — bring a session started under an older rn to the current form, or take up where the last one stopped, and carry the work to the next sign-off. It writes files, commits, and pushes, so run it only on an explicit /rn:up.
disable-model-invocation: true
---

# /rn:up — Resume

## Purpose

The user can clear the conversation at any stop and come back without explaining anything again,
since the session goes on from where they left it by what its record says.

## Steps

1. Check that `python3` runs; when it does not, say so and how to install it, and stop.
2. Find the session as in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`. When an older `rn` started
   it, bring it to the current form as there instead of the steps below.
3. Say where it resumes, in the `conversation-language` of `steering.md`:

   ```
   ● {resuming {slug} at #{id}: {task name}, or at the next move of the last decision line}
   ```

4. When the last decision line ends `waiting for #{id} {sign-off name}`, and the branch is level with
   the latest default branch, give the proposal again as that commit's message body prints it up to
   the decision line, translated into the conversation language when the two differ, adding nothing
   and leaving nothing out, and stop. Otherwise take up the session
   as in `${CLAUDE_PLUGIN_ROOT}/references/conduct.md`.
