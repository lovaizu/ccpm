---
name: up
description: Resume a suspended rn work session in a fresh conversation. Use when the user returns to continue earlier work, typically via /rn:up. Finds steering.md from git history, reconciles task state against the commit log, and resumes the next task. Has side effects (commits, executes tasks) — run only on explicit /rn:up.
disable-model-invocation: true
---

# /rn:up — Resume a session

Reconstructs prior session state, aligns it with git, and continues from the next unchecked task.

## Steps

1. **Handle a dirty tree.**
   - Tree clean → proceed.
   - Tree dirty → propose a `wip:` commit or a discard, and wait for confirmation before touching the working tree.

2. **Find steering.md.** Run `git log --diff-filter=AM --name-only --pretty=format: -- '*/steering.md' | head -5` and keep the paths that exist on disk.
   - One result → use it.
   - Multiple → rank by `State` showing `Status: paused`, then most recent commit, and propose the top candidate.
   - Zero → tell the user "No steering.md found. Run `/rn:on` to start." and stop.

3. **Read State.** Read the `State` section: last completed task, next task, and notes.

4. **Sync tasks.** Cross-check `git log` against the unchecked tasks. A commit matches a task when its message contains `complete task #{id}`; check that task off in steering.md.

5. **Check blockers.** If `State` notes mention a blocker, investigate and find an alternative approach before removing any task.

6. **Clean up State.** Replace the `State` section with its template placeholder and commit the reconciliation.

7. **Begin the next task.** Read `${CLAUDE_PLUGIN_ROOT}/references/task-workflow.md` and execute the next unchecked task following it.
   - All tasks already done → run the **evaluation gate**: propose running the `steering.md` Acceptance criteria and get the user's sign-off on the result, taken via `/rn:ty` (approve → close) or `/rn:gm` (revise) — not an inferred yes/no. This is the last of the three scheduled gates (plan / design / evaluation); do not close the session without it.
