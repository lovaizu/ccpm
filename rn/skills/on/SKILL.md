---
name: on
description: Start a new rn work session from a goal — restate the goal, turn it into tasks in a steering.md, open a draft PR, have the plan evaluated, then begin task #1 once the user approves. Has side effects (writes files, commits, pushes, opens a PR) — run only on explicit /rn:on.
disable-model-invocation: true
---

# /rn:on — Start a session

Turns a goal into `steering.md`, puts it on a draft PR, has it judged, and stops at the plan gate.

## Steps

1. **Capture the goal as the user means it, so the session builds what was asked and nothing
   else.** Take it from the message or `$ARGUMENTS`; ask if absent. Restate it in plain words and
   confirm only when it is ambiguous. The restatement becomes `Goal`.

2. **Give the session a stable home, so every later command can find it.** The path is
   `.rn/{yyyymmdd}-{slug}/steering.md`. Slug candidates: the current branch, an issue number
   (`#31` → `issue-31`), a kebab-case name from the goal. Propose one; if the user already named
   one, use it without asking.

3. **Write the plan as one reviewable file, so the user judges a whole, not a conversation.**
   Follow the template and section notes in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`. Stamp
   `Rn version:` from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`. Work `Tasks` backwards
   from the Success criteria; where the approach must be decided before build, add a "Design
   sign-off" task and write the `Design:` line with the path the design will live at; end with
   "Evaluation sign-off".

4. **Put the plan on record before anything is built, so it can be reviewed where diffs render.**
   Commit `chore: start session — {slug}`; branch off the default branch if on it; push; open a
   draft PR whose body is exactly
   `See [steering](https://github.com/{owner}/{repo}/blob/{branch}/.rn/{yyyymmdd}-{slug}/steering.md).`
   If push or PR creation fails, say so and carry on — the plan is then reviewed in the
   conversation and later verdicts are reported there.

5. **Have the plan judged before the user sees it, so their review starts from a plan already
   free of avoidable defects.** Run `${CLAUDE_PLUGIN_ROOT}/references/evaluate.md` with kind Plan.
   NG → fix, commit `docs: revise plan — {what changed}`, push, judge again; after three NG rounds
   stop and ask the user, opening with the session-status block.

6. **Stop at the plan gate — this decision is the user's.** Open with the session-status block
   (`${CLAUDE_PLUGIN_ROOT}/references/steering.md`) and ask for `/rn:ty` or `/rn:gm`. `/rn:ty`
   runs task #1 per `${CLAUDE_PLUGIN_ROOT}/references/task.md`.
