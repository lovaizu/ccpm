# Planning Workflow

Turns a goal into verifiable tasks in `steering.md`, then persists it, opens the session's draft PR, and
takes the plan-gate sign-off. Read by `on/SKILL.md` at the start of a session, before task #1 begins —
task execution then continues via [`task-execute-workflow.md`](./task-execute-workflow.md) /
[`task-verify-workflow.md`](./task-verify-workflow.md). Run once per session.

## Steps

Treat every user interaction as a proposal: lead with one concrete recommended option in plain language (no internal jargon), and proceed on confirmation. `AskUserQuestion` is fine when one option is your recommendation.

1. **Understand the goal.** Take it from the user's message or `$ARGUMENTS`; if neither is present, ask for it. Restate it as a clear, faithful understanding of what the user wants — capture full intent, never add scope or invent goals. If ambiguous, propose your restatement and let the user correct it. This restatement becomes `Goal`.

2. **Propose the location.** The session lives at `.rn/{yyyymmdd}-{slug}/steering.md`, where `{yyyymmdd}` is today's date (e.g. `20260702`) — the date prefix keeps accumulating session directories sorted chronologically under `.rn/`. Gather `{slug}` candidates:
   - current git branch — `!`git rev-parse --abbrev-ref HEAD`` (e.g. `feature/payment-fix` → `payment-fix`)
   - an issue reference in `$ARGUMENTS` (e.g. `#123` → `issue-123`)
   - a kebab-case name from the goal (e.g. "fix the payment screen bug" → `fix-payment-bug`)

   Propose one recommended slug plus the alternatives and let the user confirm or pick (`AskUserQuestion` is fine). When already on a non-default branch, recommend that branch's name as the slug. Use the confirmed slug for the path.

   Alongside the slug, decide the session's `design.md` location with the user — default `.rn/{yyyymmdd}-{slug}/design.md` (lowercase). A session may point its `Design:` line elsewhere when that suits the work (e.g. this plugin's own session uses `rn/docs/design.md`).

3. **Create steering.md.** Read `${CLAUDE_PLUGIN_ROOT}/references/steering-template.md` and follow its per-section guidance. Write the chosen design.md path into the template's top `Design:` line. Read the doc-division rule (in the template) and `${CLAUDE_PLUGIN_ROOT}/references/design-template.md`, then **allocate content at planning** per the doc-division: requirements & acceptance criteria → steering, structure & decisions → `design.md`, user-facing UX → README. Fill `Goal`, `Acceptance criteria`, `Assumptions`, and `Rules`. Leave `Tasks` and `State` as their placeholders for now. **Force no empty `design.md`**: a session with no design to record creates no `design.md` and omits the `Design:` line entirely (no file, no pointer), folding its design gate into the plan gate (Step 5) — never write an empty file and never leave a dangling pointer.

4. **Decompose tasks.** Work backwards from the Acceptance criteria end state (e.g. acceptance = "payments complete"; working back: regression check ← root-cause fix ← failing reproduction test). Define each task following the template's `Tasks` structure, inline `Completion criteria` rules, and `Task definition requirements` table in full.
   - **Design sign-off task.** When the session has a `design.md` not settled at plan time, place a **"Design sign-off"** task in the sequence, at the point where heavy build would otherwise start on the unapproved design. Completion criteria: `design.md` is approved. Steps: present `design.md` to the user and take the verdict via `/rn:ty` (approve) or `/rn:gm` (revise → address the feedback, re-present). When the design is settled at plan time — or the session has no `design.md` at all (Step 3's "force no empty `design.md`" rule) — place no separate task; it folds into the plan-gate hand-off instead (Step 5).
   - **Evaluation sign-off task.** Always place a final **"Evaluation sign-off"** task as the session's last task. Completion criteria: the Acceptance criteria run is approved. Steps: present the Acceptance criteria run result to the user and take the verdict via `/rn:ty` (approve) or `/rn:gm` (revise → address the feedback, re-present).
   - **Self-check before persisting.** Before persisting (Step 5), confirm the last task in the list is "Evaluation sign-off" — if it is not, add it before persisting.

5. **Persist and open a draft PR — the plan gate.** This is the first of the three scheduled user sign-offs (plan / design / evaluation).
   - Write the completed `steering.md` to `.rn/{yyyymmdd}-{slug}/steering.md`.
   - Commit it: `chore: start session — {slug}`.
   - Ensure the work is on a branch — if on the default branch, create `{slug}` first.
   - Push the branch, then open a draft PR (`gh pr create --draft`) titled from the goal. The PR body is a single link to the steering file and nothing else — do not copy the Goal, tasks, or any plan content into it. Use a branch-ref blob link: `See [steering](https://github.com/{owner}/{repo}/blob/{branch}/.rn/{yyyymmdd}-{slug}/steering.md).` This is the session's PR — later tasks add commits to it.
   - Report the PR link and a one-line task list, and ask the user to review the plan on the PR.
   - **Design gate.** A sign-off on the approach / key decisions before any task builds on them. When the design is settled at plan time, fold it into this plan-gate approval (one stop). When it is not, Step 4 placed a **Design sign-off** task earlier in the sequence — that task carries the separate user sign-off on `design.md` before heavy build begins.
   - If push or PR creation fails, report it and fall back to presenting the plan in the console.
   - **Take the sign-off via the user's verdict commands** — both the plan-gate approval and the design-gate sign-off come through `/rn:ty` (approve → proceed) or `/rn:gm` (revise → address and re-present); never infer approval and never record a verdict the user did not issue.
   - **CRITICAL: DO NOT proceed without explicit user approval.**
