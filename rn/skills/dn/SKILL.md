---
name: dn
description: Pauses the rn session on the current branch wherever it is, leaves in the record what the next conversation needs, pushes everything, and stops. Used when the user types /rn:dn to stop for now.
disable-model-invocation: true
---

## Role

You are the conductor of an rn session. `/rn:dn` pauses the session wherever it is, leaves what
the next conversation needs, pushes everything and stops. The next conversation knows only the
record, so everything it needs is left there.

## Steps

1. Read step 1 of `${CLAUDE_PLUGIN_ROOT}/references/conduct.md`, The frame, and keep it from here
   on.
2. Read `${CLAUDE_PLUGIN_ROOT}/references/record.md` whole, and find the session as its step 1
   says.
3. When the session is waiting for a sign-off, as record.md's step 7 tells, tell the user the
   session is already stopped there and safe to clear, and that `/rn:ty` or `/rn:gm` answers it,
   and end.
4. When a `turn:up` run is at work in this conversation, ask the user to stop it by pressing Esc,
   since a run stopped that way keeps what it made in turn's evidence, and go on once it has
   stopped.
5. Write to a `notes` item in `open/`, named as record.md's step 3 says, what the next
   conversation needs that nothing else in the record holds, in this form, its headings in the
   artifact language, leaving out a part that has nothing:

   ```
   ## Under way

   <what was under way, and how far it came>

   ## Task

   - Content: <the task's content file>
   - Last handed to turn: <the in path of the last task handed to turn>

   ## Talk

   - Agreed: <each point agreed with the user>
   - Open: <the point still open>
   ```

   Task is for a task that was under way, and Talk for a talk with the user.

6. Read `${CLAUDE_PLUGIN_ROOT}/checklists/proposal.md` whole. Commit and push as record.md's step 5
   says, with this body: the map, the lines that head every message where rn stops, as the
   template in proposal.md shows them, with the first task in `steering.md` not yet `[x]`, a
   sign-off included, as `👉 #{id} {task name} ── paused here`; then the decision line record.md's step 6 gives for a
   pause by `/rn:dn`.
7. Give the user what `git log -1 --format=%b` prints, then `Next: /clear, then /rn:up.`, and end.
