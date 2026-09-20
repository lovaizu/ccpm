---
name: up
description: Resume a suspended rn session in a fresh conversation. Finds steering.md from git history, reconciles task state against the commit log, and resumes the next task. Has side effects (commits, executes tasks) — run only on explicit /rn:up.
disable-model-invocation: true
---

# /rn:up — Resume a session

Reconstructs prior session state, aligns it with git, and continues from the next unchecked task.

## Steps

1. **Clear a dirty tree first, so resume starts from a known state.** Tree clean → proceed. Dirty →
   run step 2 read-only to identify the session, then propose a `wip:` commit or a discard (opening
   with the status block) and wait for confirmation.

2. **Find the steering.md to resume, so the right session continues.** Run
   `git log --diff-filter=AM --name-only --pretty=format: -- '*/steering.md' | head -5`, keep paths
   on disk. One → use it. Several → prefer `Status: paused`, then newest, and propose it. None →
   tell the user "No steering.md found. Run /rn:on to start." and stop.

3. **Check the version, so an older session is current before it's touched.** Compare `Rn version:`
   to the installed version; on mismatch, run the migration section of
   `${CLAUDE_PLUGIN_ROOT}/references/steering.md` first.

4. **Read `State`, so resume knows what was last done and what's next.** Read `Last completed`,
   `Next`, `Notes`.

5. **Reconcile check-offs against git, so a commit made before a crash isn't redone.** Cross-check
   `git log` against unchecked tasks: a commit whose message contains `complete task #{id}` checks
   that task off.

6. **Investigate any blocker before dropping a task.** If `Notes` names a blocker, resolve or
   confirm it still stands before proceeding.

7. **Reset `State` and commit, so the placeholder is ready for the next suspend.** Replace `State`
   with its template placeholder; commit `chore: resume — {slug}`; push.

8. **Continue where the session left off.** If `Notes` names a pending gate, re-present it (status
   block) and wait. Otherwise run the next unchecked task per
   `${CLAUDE_PLUGIN_ROOT}/references/task.md`.
