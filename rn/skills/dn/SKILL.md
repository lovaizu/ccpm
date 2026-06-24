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

**Step 4 — Commit and push**

- `git commit` the `State` changes, then `git push`. If push fails, continue (the user can push
  later).

**Step 5 — Verify clean**

- Run `git status`; the tree must be clean.

**Step 6 — Report**

- Output: last completed task, next task, and the branch name.
- Remind the user to run `/clear`, then `/rn:up` in a new conversation.
