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

**Step 4 — Classify untracked residue (gitignore or escalate; never delete)**

- Phase 1 already committed the tracked dirty changes, so the entries remaining here are **untracked**
  (`??` in `git status --porcelain`). Run `git status --porcelain` and classify **each** `??` path:
  - **Clearly a recurring test/build artifact** a future test or build run regenerates — e.g.
    `.pytest_cache/`, `.coverage`, `htmlcov/`, `coverage.xml`, `__pycache__/`, `dist/`, `node_modules/`,
    `.tox/` → append a matching rule to the **repo-root `.gitignore`** (create it if absent). This
    hides the path from `git status`. Only paths you are *sure* are regenerable — **any doubt → treat
    as the next bullet**. Do **not** delete it, and do **not** commit yet (Step 5 carries the commit).
  - **Anything you are not sure is a regenerable artifact** → **never delete, never gitignore**.
    Surface the path to the user and let them decide: commit it, gitignore it, delete it themselves,
    or keep it. For any such path the user does **not** resolve (defers, or no answer is available),
    **append it to `State` → `Notes` now**. The `State` section is still uncommitted at this point —
    Phase 1 wrote it but Step 5 has not committed it yet — so this just adds to the same pending
    change; do **not** create a separate commit for it.
- The agent **never** deletes a file on its own. Deletion is only ever the user's explicit choice.
- Gitignore applies only to untracked residue. A tracked-dirty path at this point is a deliverable to
  commit (Phase 1 / Step 5), not residue — gitignore is a no-op on a tracked path.

**Step 5 — Commit and push (single commit)**

- `git commit` the `State` changes (including any unresolved-path notes from Step 4) **and** any
  `.gitignore` edit — together, in a **single commit**. Then `git push`. If push fails, continue (the
  user can push later), but **record that the push did not succeed** so Step 7 can warn.

**Step 6 — Verify (bounded, never wedge)**

- Run `git status --porcelain`.
  - **Empty** → the tree is clean; go to Step 7.
  - **Non-empty, and every remaining path was already recorded in `State` → `Notes` as
    user-deferred** → this is the accepted terminal state (the user chose to keep these). Do **not**
    loop. Go to Step 7; it names them.
  - **Non-empty with a path that is NOT a recorded user-deferred path** (e.g. a `.gitignore` rule that
    didn't actually match its artifact) → it was mis-resolved. Return to Step 4 **once** to handle it
    (fix the rule, or escalate it as ambiguous). This back-step is bounded: a path can only end up
    (a) gitignored away or (b) recorded as user-deferred — after one corrective pass every path is in
    one of those two terminal buckets, so the flow cannot loop forever.

**Step 7 — Report**

- Output: last completed task, next task, and the branch name.
- If the push did **not** succeed (Step 5), state clearly that the commits are **local-only and must be
  pushed before they are safe** — do not let the user walk away believing the work is pushed.
- If any untracked path was left unresolved (user-deferred, recorded in Step 4), name it and note it
  is recorded in `State` → `Notes` for `/rn:up`.
- Remind the user to run `/clear`, then `/rn:up` in a new conversation.
