---
name: up
description: Resume a suspended rn session in a fresh conversation — find steering.md in git history, reconcile it with the commit log, bring an older session current, and continue from the next unchecked task or the pending gate. Has side effects (commits, pushes, runs tasks) — run only on explicit /rn:up.
disable-model-invocation: true
---

# /rn:up — Resume a session

Rebuilds where the session stands from `steering.md` and git, then continues.

## Steps

1. **Start from a known tree, so nothing half-done gets mixed into the resume.** Tree clean →
   proceed. Dirty → do step 2 read-only to name the session, then propose a `wip:` commit or a
   discard, opening with the session-status block, and wait for the answer.

2. **Find the session to resume, so the right work continues.** Run
   `git log --diff-filter=AM --name-only --pretty=format: -- '*/steering.md' | head -5` and keep the
   paths that exist on disk. One → use it. Several → prefer `Status: paused`, then the most recent,
   and propose it. None → say "No steering.md found. Run /rn:on to start." and stop.

3. **Bring an older session current before touching it, so the rest of this command reads one
   shape.** Compare `Rn version:` with the installed version in
   `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`; on a mismatch run the migration section of
   `${CLAUDE_PLUGIN_ROOT}/references/steering.md` first.

4. **Read `State`, so the resume knows what was last done, what is next, and what is pending.**
   Take `Last completed`, `Next`, and `Notes` (branch, PR, pending gate, blockers).

5. **Reconcile with git, so work committed before a crash is not redone.** A commit whose message
   contains `complete task #{id}` proves that task done: check it and its steps off.

6. **Look into any blocker before dropping a task, so a real obstacle is solved, not skipped.** If
   `Notes` names one, investigate and find a way through; remove a task only when it has become
   unnecessary.

7. **Reset `State` and commit, so the next suspend starts from the placeholder.** Replace the
   section with the template's placeholder; commit `chore: resume — {slug}`; push.

8. **Continue exactly where the session stopped.** A pending gate named in `Notes` → present it
   again with the session-status block and wait for `/rn:ty` or `/rn:gm`. Otherwise run the next
   unchecked task per `${CLAUDE_PLUGIN_ROOT}/references/task.md`.
