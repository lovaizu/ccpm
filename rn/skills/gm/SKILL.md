---
name: gm
description: Start a new rn work session from a goal. Use when the user states something they want to accomplish, typically via /rn:gm. Captures the goal verbatim, decomposes it into verifiable tasks in a steering.md, and begins task #1. This skill has side effects (writes files, commits to git) — only run it on explicit user invocation.
disable-model-invocation: true
---

# /rn:gm — Start a session

Start a goal-driven work session. Capture the user's goal exactly, turn it into verifiable tasks
inside a `steering.md`, get approval, then execute task #1.

All user interactions are **proposals, not questions**: propose a concrete option and proceed on
confirmation. Never paraphrase or reinterpret the goal.

## Phase 1: Define — fix the goal and where it lives

**Step 1 — Hear the goal**

- Use the user's message or `$ARGUMENTS` as the goal. If neither is present, ask for it.
- Record the user's **exact words**. Never paraphrase.

**Step 2 — Propose the location**

- The session lives at `.rn/{slug}/steering.md`. Propose a `{slug}` from the situation rather than
  a fixed rule. Gather candidates:
  - the current git branch — `!`git rev-parse --abbrev-ref HEAD`` (e.g. `feature/payment-fix` →
    `payment-fix`)
  - an issue reference in `$ARGUMENTS` (e.g. `#123` → `issue-123`)
  - a kebab-case work name derived from the goal (e.g. "fix the payment screen bug" →
    `fix-payment-bug`)
- Propose **one recommended slug plus the alternatives** and let the user confirm or pick (you may
  use `AskUserQuestion` for this). Use the confirmed slug for the path.

## Phase 2: Plan — turn the goal into verifiable tasks

**Step 3 — Create steering.md**

- Read `${CLAUDE_PLUGIN_ROOT}/references/steering-template.md`.
- Fill `Goal`, `Verification`, `Assumptions`, and `Rules`. Leave `Tasks`, `Decisions`, and `State`
  as their placeholders for now.
- In `Verification`, define how the goal is checked along two axes: goal alignment + quality.
- In `Assumptions`, separate facts from assumptions, mark anything unverified, and define the
  complete scope — never sample.

**Step 4 — Decompose tasks**

- Work **backwards from the Verification end state**.
- Give each task a `Purpose`, `Prerequisites`, `Steps`, and `Completion criteria`, following the
  task definition requirements in the template (one-sentence purpose; specific, not "implement X";
  third-party-verifiable criteria; explicit prerequisites).

## Phase 3: Launch — get approval and start

**Step 5 — Present and approve**

- Show the complete `steering.md`.
- **CRITICAL: DO NOT proceed without explicit user approval.**

**Step 6 — Begin task #1**

- After approval, write the completed `steering.md` to `.rn/{slug}/steering.md`.
- Commit it: `chore: start session — {slug}`.
- Read `${CLAUDE_PLUGIN_ROOT}/references/task-workflow.md` and execute task #1 following it.
