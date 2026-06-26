---
name: on
description: Start a new rn work session from a goal — restate the goal, decompose it into verifiable tasks in a steering.md, open a draft PR for review, then begin task #1 once approved. Has side effects (writes files, commits, pushes, opens a PR) — run only on explicit /rn:on.
disable-model-invocation: true
---

# /rn:on — Start a session

Turns a goal into verifiable tasks in `steering.md`, opens a draft PR, then executes task #1 after approval.

## Steps

Treat every user interaction as a proposal: lead with one concrete recommended option in plain language (no internal jargon), and proceed on confirmation. `AskUserQuestion` is fine when one option is your recommendation.

1. **Understand the goal.** Take it from the user's message or `$ARGUMENTS`; if neither is present, ask for it. Restate it as a clear, faithful understanding of what the user wants — capture full intent, never add scope or invent goals. If ambiguous, propose your restatement and let the user correct it. This restatement becomes `Goal`.

2. **Propose the location.** The session lives at `.rn/{slug}/steering.md`. Gather `{slug}` candidates:
   - current git branch — `!`git rev-parse --abbrev-ref HEAD`` (e.g. `feature/payment-fix` → `payment-fix`)
   - an issue reference in `$ARGUMENTS` (e.g. `#123` → `issue-123`)
   - a kebab-case name from the goal (e.g. "fix the payment screen bug" → `fix-payment-bug`)

   Propose one recommended slug plus the alternatives and let the user confirm or pick (`AskUserQuestion` is fine). When already on a non-default branch, recommend that branch's name as the slug. Use the confirmed slug for the path.

   Alongside the slug, decide the session's `design.md` location with the user — default `.rn/{slug}/design.md` (lowercase). A session may point its `Design:` line elsewhere when that suits the work (e.g. this plugin's own session uses `rn/docs/design.md`).

3. **Create steering.md.** Read `${CLAUDE_PLUGIN_ROOT}/references/steering-template.md` and follow its per-section guidance. Write the chosen design.md path into the template's top `Design:` line. Read the doc-division rule (in the template) and `${CLAUDE_PLUGIN_ROOT}/references/design-template.md`, then **allocate content at planning** per the doc-division: requirements & acceptance criteria → steering, structure & decisions → `design.md`, user-facing UX → README. Fill `Goal`, `Acceptance criteria`, `Assumptions`, and `Rules`. Leave `Tasks` and `State` as their placeholders for now. **Force no empty `design.md`**: a session with no design to record creates no `design.md` and folds its design gate into the plan gate (Step 5) — never write an empty file.

4. **Decompose tasks.** Work backwards from the Acceptance criteria end state (e.g. acceptance = "payments complete"; working back: regression check ← root-cause fix ← failing reproduction test). Define each task following the template's `Tasks` structure, inline `Completion criteria` rules, and `Task definition requirements` table in full.

5. **Persist and open a draft PR.**
   - Write the completed `steering.md` to `.rn/{slug}/steering.md`.
   - Commit it: `chore: start session — {slug}`.
   - Ensure the work is on a branch — if on the default branch, create `{slug}` first.
   - Push the branch, then open a draft PR (`gh pr create --draft`) titled from the goal. The PR body is a single link to the steering file and nothing else — do not copy the Goal, tasks, or any plan content into it. Use a branch-ref blob link: `See [steering](https://github.com/{owner}/{repo}/blob/{branch}/.rn/{slug}/steering.md).` This is the session's PR — later tasks add commits to it.
   - Report the PR link and a one-line task list, and ask the user to review the plan on the PR.
   - If push or PR creation fails, report it and fall back to presenting the plan in the console.
   - **CRITICAL: DO NOT proceed without explicit user approval.**

6. **Begin task #1.** After approval, read `${CLAUDE_PLUGIN_ROOT}/references/task-workflow.md` and execute task #1 following it.
