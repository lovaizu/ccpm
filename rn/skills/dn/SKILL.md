---
name: dn
description: "Suspend the current rn session — commit and push the work, record resume context in steering.md, hand off to a manual /clear. Use when stopping: context nearly full, a break, or end of day, via /rn:dn. Has side effects (commits, pushes) — run only on explicit /rn:dn."
disable-model-invocation: true
---

# /rn:dn — Suspend a session

Records resume state and hands off. Runs no task.

## Steps

1. **Find the steering.md in play, so the right session is suspended.** Use the known path, else
   `git log --diff-filter=AM --name-only --pretty=format: -- '*/steering.md' | head -5`, keep paths
   on disk, prefer one whose `State` shows `Status: paused`.

2. **Check the version, so an older session gets reconciled before it's left mid-air.** Compare
   `Rn version:` to the installed version (`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`); on
   mismatch, run the migration section of `${CLAUDE_PLUGIN_ROOT}/references/steering.md` first.

3. **Check off what's actually done, so resume doesn't redo it.** In `steering.md`, check off
   completed steps.

4. **Write `State`, so a fresh conversation knows exactly where to pick up.** Follow the `State`
   placeholder in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`: `Status: paused`, `Date`,
   `Last completed`, `Next`, `Notes` (a forward pointer only — branch/PR, pending gate, blockers).

5. **Commit the work, so nothing is lost between conversations.** Tree clean → skip. Current task's
   steps all checked → commit normally. Some unchecked → prefix `wip:`. The message must never
   contain `complete task #`.

6. **Resolve untracked files, so the tree is genuinely clean, not just committed.** For each
   untracked path: regenerable build/test residue → add a rule to `.gitignore`; anything else → ask
   the user (commit / gitignore / delete themselves / keep), opening with the status block. Never
   delete a file yourself.

7. **Push, so the suspended session is visible outside this conversation.** Commit `State` and any
   `.gitignore` edit together, then push. If push fails, continue and report it.

8. **Report where things stand, so the user knows how to resume.** Open with the status block; give
   the branch name; if push failed, say the commits are local-only; name any paths the user still
   needs to resolve. Tell the user: `/clear`, then `/rn:up`.
