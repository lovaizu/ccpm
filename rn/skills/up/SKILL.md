---
name: up
description: Resume a suspended rn work session in a fresh conversation. Use when the user returns to continue earlier work, typically via /rn:up. Finds the steering.md from git history, reconciles task state against the commit log, and resumes the next task. This skill has side effects (commits, executes tasks) — only run it on explicit user invocation.
disable-model-invocation: true
---

# /rn:up — Resume a session

Reconstruct the prior session state, align it with git reality, and continue execution from the
next unchecked task.

## Phase 1: Recover — reconstruct the prior state

**Step 1 — Handle a dirty tree**

- Clean tree → proceed.
- Dirty tree → propose a `wip:` commit or a discard. **Wait for confirmation before touching the
  working tree.**

**Step 2 — Find steering.md**

- Search commit history:
  `git log --diff-filter=AM --name-only --pretty=format: -- '*/steering.md' | head -5`.
- Keep files that still exist on disk. One result → use it. Multiple → rank by (a) `State` showing
  `Status: paused`, then (b) most recent commit, and propose the top candidate. Zero → tell the
  user "No steering.md found. Run `/rn:on` to start."

**Step 3 — Read State**

- Read the `State` section: last completed task, next task, and notes.

## Phase 2: Reconcile — align the file with git reality

**Step 4 — Sync tasks**

- Cross-check `git log` against the unchecked tasks. A commit matches a task when its message
  contains `complete task #{id}` (the format written by task-workflow Complete). Check that task
  off in `steering.md`.

**Step 5 — Check blockers**

- If the `State` notes mention a blocker, investigate and find an alternative approach **before**
  removing any task. The goal is fixed; means adapt.

**Step 6 — Clean up State**

- Replace the `State` section with its template placeholder. Commit the reconciliation.

## Phase 3: Resume — continue execution

**Step 7 — Begin the next task**

- Read `${CLAUDE_PLUGIN_ROOT}/references/task-workflow.md` and execute the next unchecked task
  following it.
- If all tasks are already done, propose running the `steering.md` Acceptance criteria.
