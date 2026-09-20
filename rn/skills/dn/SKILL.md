---
name: dn
description: "Suspend the current rn session — record where it stands in steering.md, commit and push everything, and hand off to a manual /clear. Use when stopping: context nearly full, a break, end of day. Has side effects (commits, pushes) — run only on explicit /rn:dn."
disable-model-invocation: true
---

# /rn:dn — Suspend a session

Writes down where the session stands so a fresh conversation can pick it up. Runs no task.

## Steps

1. **Take up the conductor's role, so someone works toward the Goal from this command's first
   step.** Read `${CLAUDE_PLUGIN_ROOT}/references/conductor.md`; what follows runs under it.

2. **Name the session being suspended, so the right `steering.md` is written.** Use the path
   known in this conversation; otherwise run
   `git log --format= --name-only --diff-filter=AM -- '*/steering.md' | awk 'NF && !seen[$0]++'`,
   keep the paths on disk, and take the most recent.

3. **Bring an older session current before leaving it, so the next resume reads one shape.**
   Compare `Rn version:` with the installed version in
   `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`; on a mismatch run the migration section of
   `${CLAUDE_PLUGIN_ROOT}/references/steering.md` first.

4. **Record what is actually done, so the resume does not redo it.** Check off a step only when
   the thing itself shows it done — not because the conversation says so; add any task the work
   uncovered.

5. **Write `State`, so a cold reader knows exactly where to pick up.** Fill every field from the
   template in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`: `Status: paused`, today's `Date`,
   `Last completed`, `Next`, `Pending` — the gate awaiting a verdict, open questions, items the
   user deferred, blockers — and `Notes` as branch, PR and what else the next conversation needs.
   History stays in git and on the PR.

6. **Commit the work in progress, so nothing lives only in this conversation.** Tree clean → skip.
   Current task's steps all checked → a plain conventional message. Some unchecked → prefix `wip:`.
   Never include `complete task #` — that marker belongs to the check-off commit alone.

7. **Leave the tree genuinely clean, so the next conversation starts from git alone.** For each
   untracked path: regenerable build or test residue → add a rule to `.gitignore`; anything else →
   ask the user (commit, ignore, keep, or delete it themselves), one path at a time with a
   recommendation, opening with the session-status block. Never delete a file yourself; note any
   path the user leaves unresolved in `Pending`.

8. **Push, so the suspended session exists outside this machine.** Commit `State` and any
   `.gitignore` change together, then push. If the push fails, continue and say so in the report.

9. **Tell the user how to come back.** Open with the session-status block; give the branch; say if
   commits are local-only; name any unresolved paths. Then: `/clear`, and `/rn:up` in the new
   conversation.
