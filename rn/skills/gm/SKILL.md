---
name: gm
description: Start a new rn work session from a goal. Use when the user states something they want to accomplish, typically via /rn:gm. Restates the goal as a faithful understanding, decomposes it into verifiable tasks in a steering.md, opens a draft PR so the plan can be reviewed, and begins task #1 once approved. This skill has side effects (writes files, commits, pushes, opens a PR) — only run it on explicit user invocation.
disable-model-invocation: true
---

# /rn:gm — Start a session

Start a goal-driven work session. Understand the user's goal, turn it into verifiable tasks inside a
`steering.md`, open a draft PR so the plan can be read comfortably, then execute task #1 once
approved.

All user interactions are **proposals, not open-ended questions**: lead with a concrete recommended
option — written so it makes sense without prior context (plain language, no internal jargon) — and
proceed on confirmation (`AskUserQuestion` is fine when one of the options is your recommendation).
Restate the goal as a faithful understanding of what the user wants — never add scope or invent
intent; the user confirms it in the PR review.

## Phase 1: Define — fix the goal and where it lives

**Step 1 — Understand the goal**

- Take the goal from the user's message or `$ARGUMENTS`. If neither is present, ask for it.
- Restate it as a **clear, faithful understanding** of what the user wants to achieve — capture the
  full intent, but never add scope or invent goals. If the intent is ambiguous, propose your
  restatement and let the user correct it. This restatement is what goes in `Goal`.

**Step 2 — Propose the location**

- The session lives at `.rn/{slug}/steering.md`. Propose a `{slug}` from the situation rather than
  a fixed rule. Gather candidates:
  - the current git branch — `!`git rev-parse --abbrev-ref HEAD`` (e.g. `feature/payment-fix` →
    `payment-fix`)
  - an issue reference in `$ARGUMENTS` (e.g. `#123` → `issue-123`)
  - a kebab-case work name derived from the goal (e.g. "fix the payment screen bug" →
    `fix-payment-bug`)
- Propose **one recommended slug plus the alternatives** and let the user confirm or pick (you may
  use `AskUserQuestion` for this). When already on a non-default branch, recommend that branch's
  name as the slug so the slug and the PR branch stay aligned. Use the confirmed slug for the path.

## Phase 2: Plan — turn the goal into verifiable tasks

**Step 3 — Create steering.md**

- Read `${CLAUDE_PLUGIN_ROOT}/references/steering-template.md`.
- Fill `Goal`, `Acceptance criteria`, `Assumptions`, and `Rules`. Leave `Tasks`, `Decisions`, and
  `State` as their placeholders for now.
- In `Acceptance criteria`, define how the goal is judged achieved along two axes: goal alignment +
  quality. Write them exhaustively, never sample — the complete set is what defines scope (in / out).
- In `Assumptions`, separate facts from assumptions and mark anything unverified — these are the
  things taken to be true in pursuit of the goal; if one proves false, the plan changes.

**Step 4 — Decompose tasks**

- Work **backwards from the Acceptance criteria end state** (e.g. acceptance = "payments complete";
  working back: regression check ← root-cause fix ← failing reproduction test).
- Give each task a `Purpose`, `Prerequisites`, `Steps` (including the verify-phase review steps as
  `- [ ]` checkboxes), and `Completion criteria` — following both the inline `Completion criteria`
  rules and the `Task definition requirements` table in the template, in full.

## Phase 3: Launch — open for review, then start

**Step 5 — Persist and open a draft PR**

- Write the completed `steering.md` to `.rn/{slug}/steering.md`.
- Commit it: `chore: start session — {slug}`.
- Ensure the work is on a branch — a PR needs one. If on the default branch, create `{slug}` first.
- Push the branch, then open a **draft PR** (`gh pr create --draft`) titled from the goal, with a
  body that points to `.rn/{slug}/steering.md` so the plan can be read on GitHub. This is the
  session's PR — later tasks add commits to it.
- Report the PR link and a one-line task list, and ask the user to review the plan on the PR. The
  steering is too long to review in the console — **the PR is where it gets read**.
- If push or PR creation fails, report it and fall back to presenting the plan in the console.
- **CRITICAL: DO NOT proceed without explicit user approval.**

**Step 6 — Begin task #1**

- After approval, read `${CLAUDE_PLUGIN_ROOT}/references/task-workflow.md` and execute task #1
  following it.
