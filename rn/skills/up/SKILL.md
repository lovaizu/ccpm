---
name: up
description: Resume a suspended rn session in a fresh conversation — find steering.md in git history, reconcile it with the commit log, bring an older session current, and continue from the next unchecked task or the pending gate. Has side effects (commits, pushes, runs tasks) — run only on explicit /rn:up.
disable-model-invocation: true
---

# /rn:up — Resume a session

Rebuilds where the session stands from `steering.md` and git, then continues.

## Steps

1. **Take up the conductor's role, so someone works toward the Goal from this command's first
   step.** Read `${CLAUDE_PLUGIN_ROOT}/references/conductor.md`; what follows runs under it.

2. **Start from a known tree, so nothing half-done gets mixed into the resume.** Tree clean →
   proceed. Dirty → do step 3's first part read-only to name the session, then propose one of a
   `wip:` commit or a discard, with a recommendation, opening with the session-status block, and
   wait for the answer.

3. **Enter the session, so the right work continues in its current shape.** Run Entering a
   session in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`.

4. **Read `State`, so the resume knows what was last done, what is next, and what is pending.**
   Take `Last completed`, `Next`, `Pending` (the gate awaiting a verdict, open questions, deferred
   items, blockers) and `Notes` (branch, PR).

5. **Reconcile with git, so work committed before a crash is not redone.** A commit whose message
   contains `complete task #{id}` proves that task done: mark it per Checking a task off in
   `${CLAUDE_PLUGIN_ROOT}/references/steering.md`.

6. **Bring `steering.md` back in line with the record, so the session continues from what is
   true, not from what was last written.** A `Pending` item the commits show closed is closed; an
   Assumption a commit disproved is corrected; a blocker in `Pending` is investigated and a way
   through found — a task is removed only when it has become unnecessary. A change this forces on
   the Goal, the Success criteria or an approved design is the user's: raise it as one question
   with a recommendation, opening with the session-status block, before continuing.

7. **Mark the session live and commit, so only a genuinely suspended session reads `paused`.** Set
   `Status: active`; leave `Pending` and `Notes` as they are — they are still true and nothing
   else records them. Commit `chore: resume — {slug}`; push.

8. **Continue exactly where the session stopped.** A gate named in `Pending` → present it again
   with the session-status block and wait for `/rn:ty` or `/rn:gm`. Otherwise run the next
   unchecked task per `${CLAUDE_PLUGIN_ROOT}/references/task.md`.
