---
name: dn
description: "Suspend the current rn work session — commit and push the work, record resume context in steering.md, and hand off to a manual /clear. Use when stopping: context nearly full, a break, or end of day, typically via /rn:dn. Has side effects (commits, pushes) — run only on explicit /rn:dn."
disable-model-invocation: true
---

# /rn:dn — Suspend a session

Records resume state and hands off. Does not execute tasks.

## Steps

1. **Locate steering.md.** Use the path known from this session. If unknown: run
   `git log --diff-filter=AM --name-only --pretty=format: -- '*/steering.md' | head -5`, keep the
   paths that exist on disk, and take the one whose `State` shows `Status: paused`, else the most
   recent.

2. **Check version.** Compare `steering.md`'s `Rn version:` line to the installed plugin's version
   (`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`'s `version` field); on a mismatch, run
   `${CLAUDE_PLUGIN_ROOT}/references/migration-workflow.md` first — on a match, do nothing.

3. **Check off progress.** In steering.md, check off completed task steps and add any tasks
   discovered during the work.

4. **Write the `State` section** per `steering-template.md`'s State placeholder: `Status: paused`,
   `Date`, `Last completed`, `Next`, `Notes` — cap `Notes` to the bounded forward pointer the
   placeholder's `Notes` line defines, never a re-narration of the session.

5. **Commit the work.**
   - Tree clean → skip this commit.
   - Current task's steps all checked → commit normally.
   - Some steps unchecked → commit with a `wip:` prefix.
   - The message must not contain `complete task #`.

6. **Resolve untracked residue.** Run `git status --porcelain`; the remaining entries are untracked
   (`??`). Handle each `??` path:
   - Regenerable test/build artifact — e.g. `.pytest_cache/`, `.coverage`, `htmlcov/`,
     `coverage.xml`, `__pycache__/`, `dist/`, `node_modules/`, `.tox/` → append a matching rule to the
     repo-root `.gitignore` (create it if absent). Any doubt → handle as the next item instead.
   - Anything else → ask the user how to handle it (commit / gitignore / delete themselves / keep),
     opening the message with the session-status block per
     `${CLAUDE_PLUGIN_ROOT}/references/status-display.md`. For any path the user does not resolve,
     append its exact `git status --porcelain` string to `State → Notes`.
   - Never delete a file yourself.

7. **Commit and push.** Commit the `State` changes and any `.gitignore` edit together in one commit,
   then `git push`. If push fails, continue and record that it failed (for step 9). Never amend, never
   force-push.

8. **Verify clean.** Run `git status --porcelain`:
   - Empty → go to step 9.
   - Non-empty → for each remaining (non-gitignored) untracked path, if its exact
     `git status --porcelain` string is not already recorded in `State → Notes` from step 6, record it
     there as user-deferred; then go to step 9. Never loop back to step 6. Never delete a file.

9. **Report.** Open the report with the session-status block per
   `${CLAUDE_PLUGIN_ROOT}/references/status-display.md`, then output the branch name. If the last
   push did not succeed, state that the commits are local-only and must be pushed. Name any
   user-deferred paths recorded in `State → Notes`.
