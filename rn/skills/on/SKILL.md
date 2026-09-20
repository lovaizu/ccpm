---
name: on
description: Start a new rn work session from a goal — restate the goal, decompose it into tasks in a steering.md, open a draft PR, evaluate the plan, then begin task #1 once approved. Has side effects (writes files, commits, pushes, opens a PR) — run only on explicit /rn:on.
disable-model-invocation: true
---

# /rn:on — Start a session

Turns a goal into tasks in `steering.md`, opens a draft PR, evaluates the plan, then runs task #1
after approval.

## Steps

1. **Capture the goal faithfully, so the session builds exactly what was asked.** Take it from the
   user's message or `$ARGUMENTS`; ask if absent. Restate it in plain language; confirm only if
   ambiguous. This becomes `Goal`.

2. **Choose where the session lives, so it's findable later.** Location is
   `.rn/{yyyymmdd}-{slug}/steering.md`. Candidate slugs: the current branch, an issue number
   (`#31` → `issue-31`), or a kebab-case name from the goal. Propose one and let the user confirm.

3. **Write `steering.md`, so the plan is a single reviewable artifact.** Follow
   `${CLAUDE_PLUGIN_ROOT}/references/steering.md`'s template: stamp `Rn version:` from
   `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`; write `Goal`, exhaustive `Acceptance criteria`
   (states, not artifacts), `Assumptions` (facts marked as facts), `Rules` (first line always
   "commit and push every change; one completion marker per task"). Work `Tasks` back from the
   Acceptance criteria; add a "Design sign-off" task wherever the approach must be decided before
   build; always end with "Evaluation sign-off".

4. **Persist and open the PR, so the plan is on record before anything is built.** Commit
   `chore: start session — {slug}`; branch off the default branch if needed; push; open a draft PR
   whose body is exactly
   `See [steering](https://github.com/{owner}/{repo}/blob/{branch}/.rn/{yyyymmdd}-{slug}/steering.md).`

5. **Have the plan judged before asking the user, so their review starts from a plan already free of
   avoidable defects.** Run `${CLAUDE_PLUGIN_ROOT}/references/evaluate.md` with kind Plan; post the
   verdict on the PR; fix any NG and re-run before step 6.

6. **Stop at the plan gate — this decision is the user's.** Report with the session-status block
   (see `${CLAUDE_PLUGIN_ROOT}/references/steering.md`); ask for `/rn:ty` or `/rn:gm` on the PR.

7. **Once approved, hand off to the task loop.** Run task #1 per
   `${CLAUDE_PLUGIN_ROOT}/references/task.md`.
