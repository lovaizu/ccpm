---
name: dn
description: "Suspend the current rn session — record where it stands in steering.md, commit and push everything, and hand off to a manual /clear. Use when stopping: context nearly full, a break, end of day. Has side effects (commits, pushes) — run only on explicit /rn:dn."
disable-model-invocation: true
---

# /rn:dn — Suspend a session

Writes down where the session stands so a fresh conversation can pick it up. Runs no task.

## Steps

1. **Name the session being suspended, so the right `steering.md` is written.** Use the path
   known in this conversation; otherwise run
   `git log --format= --name-only --diff-filter=AM -- '*/steering.md' | awk 'NF && !seen[$0]++'`,
   keep the paths on disk, and take the most recent.

2. **Bring an older session current before leaving it, so the next resume reads one shape.**
   Compare `Rn version:` with the installed version in
   `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`; on a mismatch run the migration section of
   `${CLAUDE_PLUGIN_ROOT}/references/steering.md` first.

3. **Record what is actually done, so the resume does not redo it.** Check off the steps completed
   in this conversation; add any task the work uncovered.

4. **Write `State`, so a cold reader knows exactly where to pick up.** Fill every field from the
   template in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`: `Status: paused`, today's `Date`,
   `Last completed`, `Next`, `Pending` — the gate awaiting a verdict, open questions, items the
   user deferred, blockers — and `Notes` as branch, PR and what else the next conversation needs.
   History stays in git and on the PR.

5. **Commit the work in progress, so nothing lives only in this conversation.** Tree clean → skip.
   Current task's steps all checked → a plain conventional message. Some unchecked → prefix `wip:`.
   Never include `complete task #` — that marker belongs to the check-off commit alone.

6. **Leave the tree genuinely clean, so the next conversation starts from git alone.** For each
   untracked path: regenerable build or test residue → add a rule to `.gitignore`; anything else →
   ask the user (commit, ignore, keep, or delete it themselves), opening with the session-status
   block. Never delete a file yourself; note any path the user leaves unresolved in `Pending`.

7. **Push, so the suspended session exists outside this machine.** Commit `State` and any
   `.gitignore` change together, then push. If the push fails, continue and say so in the report.

8. **Tell the user how to come back.** Open with the session-status block; give the branch; say if
   commits are local-only; name any unresolved paths. Then: `/clear`, and `/rn:up` in the new
   conversation.
