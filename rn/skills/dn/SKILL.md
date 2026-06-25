---
name: dn
description: Suspend the current rn work session — commit and push the work, record resume context in steering.md, and hand off to a manual /clear. Use when stopping: context nearly full, a break, or end of day, typically via /rn:dn. Has side effects (commits, pushes) — run only on explicit /rn:dn.
disable-model-invocation: true
---

# /rn:dn — Suspend a session

Records resume state and hands off. Does not execute tasks.

## Steps

1. **Locate steering.md.** Use the path known from this session. If unknown: run
   `git log --diff-filter=AM --name-only --pretty=format: -- '*/steering.md' | head -5`, keep the
   paths that exist on disk, and take the one whose `State` shows `Status: paused`, else the most
   recent.

2. **Check off progress.** In steering.md, check off completed task steps and add any tasks or
   decisions discovered during the work.

3. **Write the `State` section** (fields per `steering-template.md`): `Status: paused`, `Date`,
   `Last completed`, `Next`, `Notes`. Write `Notes` so `/rn:up` can resume without this conversation:
   current work, blockers, pending decisions, next concrete action.

4. **Commit the work.**
   - Tree clean → skip this commit.
   - Current task's steps all checked → commit normally.
   - Some steps unchecked → commit with a `wip:` prefix.
   - The message must not contain `complete task #`.

5. **Resolve untracked residue.** Run `git status --porcelain`; the remaining entries are untracked
   (`??`). Handle each `??` path:
   - Regenerable test/build artifact — e.g. `.pytest_cache/`, `.coverage`, `htmlcov/`,
     `coverage.xml`, `__pycache__/`, `dist/`, `node_modules/`, `.tox/` → append a matching rule to the
     repo-root `.gitignore` (create it if absent). Any doubt → handle as the next item instead.
   - Anything else → ask the user how to handle it (commit / gitignore / delete themselves / keep).
     For any path the user does not resolve, append its exact `git status --porcelain` string to
     `State → Notes`.
   - Never delete a file yourself.
   - On a corrective re-entry from step 7: act only on the returned path, and annotate it in
     `State → Notes` as having used its one correction.

6. **Commit and push.** Commit the `State` changes and any `.gitignore` edit together in one commit,
   then `git push`. If push fails, continue and record that it failed (for step 8). A corrective pass
   adds a follow-up commit — never amend, never force-push.

7. **Verify clean.** Run `git status --porcelain`:
   - Empty → go to step 8.
   - Non-empty, every path already recorded in `State → Notes` as user-deferred → go to step 8.
   - A path not recorded as user-deferred → if `State → Notes` does not already annotate it as having
     used its correction, return to step 5 to fix its `.gitignore` rule once; otherwise record it in
     `State → Notes` as user-deferred. Never fix the same path twice.

8. **Report.** Output last completed task, next task, and the branch name. If the last push did not
   succeed, state that the commits are local-only and must be pushed. Name any user-deferred paths
   recorded in `State → Notes`. Tell the user to run `/clear`, then `/rn:up` in a new conversation.
