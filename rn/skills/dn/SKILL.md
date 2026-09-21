---
name: dn
description: "Suspend the current rn session — record where it stands in steering.md, commit and push everything, and hand off to a manual /clear. Use when stopping: context nearly full, a break, end of day. Has side effects (commits, pushes) — run only on explicit /rn:dn."
disable-model-invocation: true
---

# /rn:dn — Suspend a session

Writes down where the session stands so a fresh conversation can pick it up. Runs no task.

## Steps

1. **Take up the conductor's role and enter the session.** Read
   `${CLAUDE_PLUGIN_ROOT}/references/conductor.md`, then run Entering a session in
   `${CLAUDE_PLUGIN_ROOT}/references/steering.md`.

2. **Record what is actually done, so the resume does not redo it.** Check off a step only when
   the thing itself shows it done — not because the conversation says so; add any task the work
   uncovered.

3. **Write `State`, so a cold reader knows exactly where to pick up.** Fill every field as the
   template in `${CLAUDE_PLUGIN_ROOT}/references/steering.md` says, with `Status: paused` and
   today's `Date`.

4. **Leave the tree genuinely clean, so the next conversation starts from git alone.** For each
   untracked path: regenerable build or test residue → add a rule to `.gitignore`; anything else →
   ask the user (commit, ignore, keep, or delete it themselves), one path at a time. Never delete
   a file yourself; note any
   path the user leaves unresolved in `Pending`.

5. **Commit and push, so nothing lives only in this conversation or this machine.** One commit
   holding the work in progress, `State` and any `.gitignore` change: `wip: suspend — {slug}`
   while the current task has unchecked steps, a plain conventional message otherwise; never
   `complete task #` — that marker belongs to the check-off commit alone. Push; if the push fails,
   continue and say so in the report.

6. **Tell the user how to come back.** Give the branch; say if
   commits are local-only; name any unresolved paths. Then: `/clear`, and `/rn:up` in the new
   conversation.
