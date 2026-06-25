---
name: dn
description: Suspend the current rn work session. Use when the user needs to stop — context is nearly full, taking a break, or ending for the day — typically via /rn:dn. Commits and pushes the work, records resume context in the steering.md State section, and hands off to a manual /clear. This skill has side effects (commits, pushes) — only run it on explicit user invocation.
disable-model-invocation: true
---

# /rn:dn — Suspend a session

Record where the work stands so it survives across conversations, then hand off. This skill does
**not** execute tasks — it only captures and persists state.

After `/rn:dn` finishes, the user must run `/clear` manually (a skill cannot trigger `/clear`),
then `/rn:up` in a fresh conversation to resume.

## Phase 1: Capture — record where work stands

**Step 1 — Find steering.md**

- Use the `steering.md` path already known from this session.
- Fallback (path unknown): search commit history —
  `git log --diff-filter=AM --name-only --pretty=format: -- '*/steering.md' | head -5`, keep files
  that still exist on disk, and prefer one whose `State` shows `Status: paused`, else the most
  recent.

**Step 2 — Commit work**

- Clean tree → skip the commit.
- Dirty tree:
  - all of the current task's steps checked → normal commit.
  - some steps unchecked → commit with a `wip:` prefix.
- Either way, this is a plain commit — its message must **not** contain `complete task #{id}`. That
  marker rides only on the coordinator's post-approval check-off commit (one per task, per
  `task-workflow.md` Phase: Complete); a suspend-time commit is never a task-completion marker.

**Step 3 — Write State**

- Check off completed task steps. Add any new tasks or decisions discovered during the work.
- Write the `State` section: set `Status` to `paused`, then `Date`, `Last completed`, `Next`,
  `Notes`, per the `State` field semantics in `steering-template.md`.
- **Notes must carry enough context for `/rn:up` to resume without this conversation**: current
  work, blockers, pending decisions, and the next concrete action.

## Phase 2: Persist — push and confirm

**Step 4 — Resolve untracked residue (edit `.gitignore` only; never delete)**

- Phase 1 already committed the tracked dirty changes, so the entries remaining here are **untracked**
  (`??` in `git status --porcelain`). Run `git status --porcelain` and handle each `??` path:
  - **Recurring test/build artifact** a future test or build run regenerates — e.g. `.pytest_cache/`,
    `.coverage`, `htmlcov/`, `coverage.xml`, `__pycache__/`, `dist/`, `node_modules/`, `.tox/` → append
    a matching rule to the **repo-root `.gitignore`** (create it if absent). This hides the path from
    `git status`. Do **not** delete it and do **not** commit the artifact itself. **Do not commit
    `.gitignore` here** — Step 5 carries that commit.
  - **Anything else** (not clearly a regenerable artifact) → **never delete and never gitignore**.
    Surface the path to the user and let them decide: commit it, gitignore it, delete it themselves,
    or keep it. If the user defers or no answer is available, this is the terminal-escape case in
    Step 6 — do not loop.
- The agent **never** deletes a file on its own. Deletion is only ever the user's explicit choice.
- Gitignore applies only to untracked residue. A tracked-dirty path at this point is a deliverable to
  commit (Phase 1 / Step 5), not residue — gitignore is a no-op on a tracked path.

**Step 5 — Commit and push**

- `git commit` the `State` changes **and** any `.gitignore` edit from Step 4 — together, in a **single
  commit**. Then `git push`. If push fails, continue (the user can push later), but **record that the
  push did not succeed** so Step 7 can warn.

**Step 6 — Verify, with a terminal escape (never wedge)**

- Run `git status --porcelain`. If empty, the tree is clean — proceed to Step 7.
- If non-empty because a gitignore rule was just added but not yet committed, finish Step 5's commit,
  then re-check once.
- If an untracked path is left **unresolved** (the user deferred, or no answer is available), do
  **not** loop back forever — `/rn:dn` exists to hand off and stop. Instead **record the unresolved
  path(s) under `State` → `Notes`** (so `/rn:up` sees them), commit and push that note, then **suspend
  anyway** and carry a clear warning into Step 7. The suspend always completes.

**Step 7 — Report**

- Output: last completed task, next task, and the branch name.
- If the push did **not** succeed (Step 5), state clearly that the commits are **local-only and must be
  pushed before they are safe** — do not let the user walk away believing the work is pushed.
- If any untracked path was left unresolved (Step 6 terminal escape), name it and note it is recorded
  in `State` → `Notes` for `/rn:up`.
- Remind the user to run `/clear`, then `/rn:up` in a new conversation.
