---
name: on
description: Start a new rn work session from a goal — restate the goal, turn it into tasks in a steering.md, open a draft PR, have the plan evaluated, then begin task #1 once the user approves. Has side effects (writes files, commits, pushes, opens a PR) — run only on explicit /rn:on.
disable-model-invocation: true
---

# /rn:on — Start a session

Turns a goal into `steering.md`, puts it on a draft PR, has it judged, and stops at the plan gate.

## Steps

1. **Take up the conductor's role.** Read `${CLAUDE_PLUGIN_ROOT}/references/conductor.md`; what
   follows runs under it.

2. **Capture the goal as the user means it, so the session builds what was asked and nothing
   else.** Take it from the message or `$ARGUMENTS`; ask if absent. Restate it in plain words —
   one sentence saying what is wanted, then why — and confirm only when it is ambiguous. The
   restatement becomes `Goal`; its first sentence is the session's name from here on.

3. **Name the session after what it produces, so a directory listing reads as work rather than as
   references.** The path is `.rn/{yyyymmdd}-{slug}/steering.md`, the slug a kebab-case name taken
   from the Goal — never a ticket id or a branch that carries one, since those point at the work
   instead of naming it; the issue goes in the `issue` field. Propose one; if the user already
   named one, use it without asking.

4. **Write the plan as one reviewable file, so the user judges a whole, not a conversation.**
   Follow the template and field notes in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`. Fill the
   frontmatter: `rn` from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`, `issue` when the goal
   came from one, `status: running`. Work `Tasks` backwards from the Success criteria; where the
   approach must be decided before build, add a "Design sign-off" task and set the `design` field
   to the path the design will live at; end with "Evaluation sign-off".

5. **Put the plan on record before anything is built, so it can be reviewed where diffs render.**
   Commit `chore: start session — {slug}`; branch off the default branch if on it; push; open a
   draft PR whose body is exactly
   `See [steering](https://github.com/{owner}/{repo}/blob/{branch}/.rn/{yyyymmdd}-{slug}/steering.md).`
   Then write the PR's URL into the `pr` field, commit `chore: record the session PR`, and push. If
   push or PR creation fails, say so and carry on — the plan is then reviewed in the conversation
   and later verdicts are reported there.

6. **Have the plan judged before the user sees it, so their review starts from a plan already
   free of avoidable defects.** Run Judging the plan in
   `${CLAUDE_PLUGIN_ROOT}/references/steering.md`.

7. **Stop at the plan gate — this decision is the user's.** Ask: `/rn:ty` or `/rn:gm`. `/rn:ty`
   runs task #1 per `${CLAUDE_PLUGIN_ROOT}/references/task.md`.
