---
name: gm
description: Register a revise verdict on the work under review. With an argument, /rn:gm <text> revises the pending item against it. With no argument, it works through the current PR's unresolved review threads. Has side effects (revises work, commits, pushes, replies on the PR) — run only on explicit /rn:gm.
disable-model-invocation: true
---

# /rn:gm — Revise

Registers a revise verdict — the counterpart to `/rn:ty`. Nothing is dropped: every piece of
feedback is acted on.

## Steps

1. **Check the version, so revision lands on a current session.** Compare `steering.md`'s
   `Rn version:` to the installed version; on mismatch, run the migration section of
   `${CLAUDE_PLUGIN_ROOT}/references/steering.md` first.

2. **Route on the argument, so text feedback and PR feedback don't get conflated.** `$ARGUMENTS`
   non-empty after trimming → step 3. Empty → step 4.

3. **Revise the pending item against the given text.** Apply it to whatever was last presented for
   confirmation; if nothing is pending, treat the text as a direct instruction. Report, opening with
   the status block.

4. **Work the PR's review threads, so feedback left on GitHub gets addressed.** For each unresolved
   thread whose last comment is the reviewer's: address it and reply with what changed and the
   commit, or reply with a question when the ask is unclear. Never resolve a thread — that's the
   reviewer's act. `gh api` on the PR's review threads is enough to drive this. Report when the
   queue is empty.
