# Goal

Build **`aiya`** — a Claude Code plugin whose core is a **prompt-driven Conductor** (form **A**; see
[D-1](#decisions) below). The main agent is the Conductor/Runner, flat subagents are Turns, and
ACC (anti-bloat compression) and TC (anti-drift steering) are **dissolved into the skill's Markdown
steps** — no JavaScript orchestration script holds the loop.

The deliverable is the plugin. The proof that it works is a **dogfood**: run aiya to build the
`techting` plugin from its requirements alone ([`techting-requirements.md`](./techting-requirements.md)),
and show that **under prompt control** the Conductor's context stays **bounded** (ACC) and a real or
injected **drift is caught at a gate and re-aimed** (TC).

**End vs means.** The end is the plugin plus those two properties holding under prompt control.
`techting` is the *test subject*, not a deliverable — the real techting ships from its own worktree;
aiya's dogfood build of it is evidence (compared against the hand-built one), not shipped.

Inputs of record:

- [`aiya/docs/design.md`](../../aiya/docs/design.md) — the aiya design (single source of truth; folds
  in the ACC/CCS runtime and the Traceability Chain × Steering Gates content that used to live in
  `core.md` / `.rn/smith/{acc,tc,approach}.md` — those are retired, superseded).
- [`techting-requirements.md`](./techting-requirements.md) — the dogfood goal (requirements only).
- [`poc.md`](./poc.md) — round 1+2 PoC results. Mechanisms were proven *when scripted* (form B); A's
  burden is to show the same hold *under prompt control*.

# Acceptance criteria

**Level A — the `aiya` plugin artifact:**

- `aiya/skills/<conductor>/SKILL.md` exists: a prompt-driven workflow skill where the main agent is
  the Conductor and subagents are Turns. The procedure dissolves in the full cycle — dispatch a Turn →
  receive a **bounded CCS** (not raw output) → an independent **verify-Turn** measures the gap to the
  goal → the Conductor advances or re-aims → a **human gate** at phase boundaries. An iteration cap and
  an escalation path are stated in the procedure, not left to improvisation.
- **ACC is structural, not advisory:** the procedure keeps the Conductor's running state in a bounded
  external CCS it rewrites each step and has it **never read raw Turn output**, so the Conductor's
  context does not grow as Turns multiply. (The end is bounded Conductor context; the procedure is how.)
- **TC is structural:** drift is measured by a verify-Turn that does not trust the generator's
  self-report; the human steers only at phase gates; the Conductor re-aims on a detected gap.
- `aiya/.claude-plugin/plugin.json` has name / description / version (semver) / author; the version
  lives only in plugin.json. `aiya/README.md` is scenario + real-console style. `aiya/CHANGELOG.md`
  exists (Keep a Changelog, `## [Unreleased]` on top).
- `.claude-plugin/marketplace.json` and the root `README.md` both list aiya, kept in sync.
- `claude plugin validate ./aiya --strict` and `claude plugin validate . --strict` both pass.
- All shipped artifacts are in English.

**Level B — the dogfood proves the two properties under prompt control:**

- Running aiya on `techting-requirements.md` produces a techting plugin that **satisfies techting's
  own acceptance criteria** (the nested goal is reached, not approximated).
- **ACC holds:** across the run the CCS handed Turn-to-Turn stays bounded and the Conductor never
  ingests raw Turn transcripts — shown by measurement, not assertion (the round-2 method: CCS size
  bounded while the replay-if-inlined transcript would grow).
- **TC holds:** a real or injected drift in the run is caught by the verify-Turn / gate and re-aimed to
  reconverge — with no script holding the loop.
- The human phase-gate is exercised for real at least once (not self-driven).

# Assumptions

- The dogfood builds techting to a **throwaway / compare location**, never over the real techting
  worktree.
- `claude plugin validate` and `claude -p … --plugin-dir` are available; if not, manual verification
  is used and recorded.
- Plugin name and skill name are independent slots (the `rn` precedent), so `aiya` + a short skill verb
  is fine.
- The marketplace `category` is a free string; reuse `"development"` or pick a fitting one.

# Rules

- 1 task = 1 commit.
- Shipped artifacts (plugin.json / SKILL.md / README / commit messages / PR) are in English, including
  this steering.
- The version lives only in `aiya/.claude-plugin/plugin.json` (no version in marketplace.json).
- On any add / rename / remove, update `.claude-plugin/marketplace.json` and the root `README.md` in
  the same commit.
- README is scenario + real-console style, not a mechanical list.
- **The shipped Conductor loop is prompt-driven (A): no JS Workflow-tool script holds the iteration
  loop in the plugin.** Form B stays a PoC substrate only.
- ACC and TC must be **structural** (built into the procedure) and **measured by running**, not
  asserted.

# Tasks

> Restructured per **D-2** (final-deliverable-first) on resume 2026-06-26. The old #1
> "design the procedure as a memo (`conductor.md`)" is retired; the salvageable design folds into the
> real artifact `aiya/docs/design.md`. README is split into its own task, written **after** SKILL.md
> settles (user choice: `design.md` first, alone). See [`State`](#state) and D-2.

### #1: Scaffold `aiya/` and author the design document (`docs/design.md`)

**Purpose**: Stand up the real plugin directory and write `aiya/docs/design.md` as the first real
deliverable — not a side memo (D-2). Fold the QA-hardened design from `conductor.md` into it, then
retire the memo. `design.md` only; README is task #3.

**Prerequisites**: none (the inputs are `conductor.md`'s already-worked-out design, plus `acc.md` /
`tc.md` as background).

**Steps**:

- [x] Create the `aiya/` plugin skeleton and `aiya/docs/design.md`.
- [x] Author `design.md` **intent-first** (背景→ペイン→ベネフィット→UX→構造→部品), folding in the
      salvageable design from `conductor.md`: the **CCS contract**, the
      **dispatch→generate→verify→re-aim→gate cycle**, the **6 gates**, and the
      **compression-forcing mechanism** (so ACC is structural, not advisory).
- [x] Retire `conductor.md`; stop using `core.md` as a working design doc (keep it as background).
- [x] self-check (record OK/NG per criterion in `.rn/aiya/checks/1.md`)
- [x] QA engineer review (subagent)
- [ ] user review (on the PR)

**Completion criteria**: `aiya/docs/design.md` exists, intent-first, internally consistent, and relies
on no script to hold the loop; the salvageable design is preserved in the real artifact; `conductor.md`
is retired.

### #2: Author the aiya Conductor skill (SKILL.md)

**Purpose**: Turn #1's design into the actual prompt-driven skill — the heart of the plugin.

**Prerequisites**: #1.

**Steps**:

- [ ] Pick the skill verb (`/aiya:<verb>`) and write the frontmatter (model-invocable description with
      concrete trigger phrases; third-person; version-agnostic).
- [ ] Write the body: imperative Markdown, the Conductor cycle from #1's `design.md`, ACC and TC
      dissolved into the steps, the iteration cap and escalation stated. Lean.
- [ ] Cross-check item by item against `design.md` and `acc.md` / `tc.md` so no pillar is dropped (do
      not sample).
- [ ] self-check (record OK/NG per criterion in `.rn/aiya/checks/2.md`)
- [ ] QA engineer review (subagent)
- [ ] user review (on the PR)

**Completion criteria**: `aiya/skills/<verb>/SKILL.md` exists, is prompt-driven (no embedded JS loop),
and encodes the bounded-CCS / verify-Turn / re-aim / phase-gate cycle with a stated cap.

### #3: Author `aiya/README.md` (user-facing guide)

**Purpose**: The scenario + real-console guide, written **after** the skill settles so it reflects real
behavior (user choice: README is a separate, later task — not bundled with the design).

**Prerequisites**: #2.

**Steps**:

- [ ] Write `aiya/README.md` in scenario + real-console style (not a mechanical list; no controlling
      noun labels like "管理").
- [ ] self-check (record OK/NG per criterion in `.rn/aiya/checks/3.md`)
- [ ] QA engineer review (subagent)
- [ ] user review (on the PR)

**Completion criteria**: `aiya/README.md` exists, scenario + real-console style, and matches the shipped
skill's actual behavior.

### #4: Package aiya and register it in the marketplace

**Purpose**: Make aiya a standalone, validated plugin reachable from both the marketplace manifest and
the root README.

**Prerequisites**: #3.

**Steps**:

- [ ] Create `aiya/.claude-plugin/plugin.json` (name / description / version `0.1.0` / author).
- [ ] Create `aiya/CHANGELOG.md` (`## [Unreleased]` on top).
- [ ] Add an aiya entry to `.claude-plugin/marketplace.json` (no version field) and link aiya in the
      root `README.md` Plugins list — in the same commit.
- [ ] Run `claude plugin validate ./aiya --strict` and `claude plugin validate . --strict`; clear every
      warning/error (or record manual verification if the CLI is absent).
- [ ] self-check (record OK/NG per criterion in `.rn/aiya/checks/4.md`)
- [ ] QA engineer review (subagent)
- [ ] user review (on the PR)

**Completion criteria**: both strict validations pass; marketplace.json and root README both list aiya
and stay in sync; version lives only in plugin.json.

### #5: Dogfood — build techting via aiya, measure ACC & TC under prompt control

**Purpose**: Prove the two properties hold under prompt control (Level B). This is the point of the
whole build.

**Prerequisites**: #4.

**Steps**:

- [ ] Run the aiya Conductor skill with `techting-requirements.md` as the goal, building techting to a
      throwaway/compare location (not the real techting worktree).
- [ ] **Measure ACC**: capture the CCS handed Turn-to-Turn; show it stays bounded while the
      replay-if-inlined transcript would grow; confirm the Conductor never read raw Turn output.
- [ ] **Exercise TC**: let a real drift surface, or inject a controlled one; show the verify-Turn / gate
      catches it and the Conductor re-aims to reconverge — with no script holding the loop.
- [ ] Exercise the human phase-gate for real at least once.
- [ ] Check the produced techting against techting's own acceptance criteria; compare to the hand-built
      techting and record the delta.
- [ ] Write the result to `.rn/aiya/dogfood.md` (honest scope: what was measured vs. asserted).
- [ ] self-check (record OK/NG per criterion in `.rn/aiya/checks/5.md`)
- [ ] QA engineer review (subagent)
- [ ] user review (on the PR)

**Completion criteria**: the dogfood result shows ACC bounded-context and TC drift-catch-and-reconverge
**by measurement** under prompt control; the produced techting meets its own criteria; the honest-scope
result is recorded.

# Decisions

### D-1: Conductor form A (prompt-driven), not B (scripted)

Decided 2026-06-26 (originally recorded in the now-retired `core.md` §10 D-1; the settled design lives
in `aiya/docs/design.md` §5). Summary: the shipped Conductor is the main agent running a prompt-driven
workflow skill with ACC/TC dissolved into Markdown steps; the JS Workflow tool (PoC round-2 substrate)
is not the delivery form. Rationale: A is the target form; deliberately differentiate from the field's
B trend; avoid future `claude -p` plan limits. The dogfood (#5) must show ACC/TC hold under prompt
control, which the scripted PoC did not establish.

### D-2: Build from the final deliverable — no intermediate design memos (user, 2026-06-26)

**Course-correction (overrides the original task structure).** The user judges intermediate
artifacts an **anti-pattern**: a separate design memo in `.rn/aiya/` (`conductor.md`, and `core.md`
used as a working design doc) is throwaway, keeps the work **机上 (armchair)**, and is a detour that
never converges on the real plugin. **Always build from the final deliverable and brush it up.**

Concretely, the deliverables to author and iterate are the **real plugin files**:

- **`aiya/README.md`** — the user-facing guide.
- **`aiya/docs/design.md`** — the design document (intent-first; the salvageable thinking from
  `conductor.md` — the CCS contract, the dispatch→generate→verify→re-aim→gate cycle, the gates, the
  compression-forcing mechanism — folds in here, in the real plugin, not a side memo).

Rationale (user's words): without the real artifacts you **can't implement, can't even discuss** — it
stays armchair, never approaches the final deliverable, a detour. **Note vs `loop-feasibility-first`:**
that "PoC/feasibility first" was about *proving the mechanism* (now done, round 1+2). This decision is
about *building the plugin* — for that phase, work from the final artifacts, not separate memos. Not a
contradiction; a different phase. Apply on resume (the user said "再開後に軌道修正して").

# State

- **Status**: paused
- **Date**: 2026-07-01
- **Last completed**: **Memo layer retired and folded into `design.md`, then the branch history
  squashed into one commit.** This session's full arc — the pure-design rewrite (dropped Form-A/B
  contrast, PoC numbers, defensive framing; new structure Requirements → Approach → Structure & flow →
  Details → Decisions), the **CCS format = YAML** decision, the cast-and-relations diagram (added then
  simplified to 4 actors + 2 boundaries), and the memo-layer retirement/fold-in (see the Notes bullet
  below for exactly what was deleted and what was folded in) — now all lives in a **single squashed
  commit `a18a3f7`** at the head of `feature/smith-plugin` (force-pushed at the user's explicit request;
  the prior multi-commit history no longer exists, so do not reference old hashes). Task #1 itself is
  still **awaiting user review** (not yet checked off) on PR #1. Ledger `.rn/aiya/checks/1.md` was
  written before this session's rewrite — **it is now stale** (still references the old structure /
  TOON); re-validate or rewrite it at `/ty`.
- **Next**:
  1. **User reviews `aiya/docs/design.md` on PR #1** (the only unchecked step of Task #1) — the single
     squashed commit `a18a3f7` includes the pure-design rewrite, CCS=YAML, the diagram, and today's
     memo-layer fold-in. On `/ty`: check off Task #1's "user review" step and commit the **single
     completion marker** (`docs: complete task #1 — …`) per `task-workflow.md` Phase: Complete; **first
     re-validate/rewrite the stale ledger `.rn/aiya/checks/1.md`** against the current doc (it predates
     both the pure-design rewrite and today's fold-in), and let it ride on that check-off commit. On
     `/gm`: re-aim per the feedback.
  2. Then start **Task #2** — author the aiya Conductor skill `aiya/skills/<verb>/SKILL.md`
     (prompt-driven, no JS loop), realizing the cycle from the revised `design.md`. Follow
     `task-workflow.md`.
- **Notes**:
  - **Memo layer retired (2026-07-01), one step further than D-2.** `.rn/aiya/core.md` and
    `.rn/smith/{acc,tc,approach,design,steering}.md` are deleted — the untracked `smith/` plugin stub
    too. Every point in them worth keeping was exhaustively diffed against `design.md` and folded in
    where missing: the `rn`-comparison / bounded-state-vs-alternatives rationale (§1), the
    never-nest-Turns invariant (§3), the CCS bloat symptom table (§4.1), the verify-Turn's 3 check
    targets + mechanical-first + simulation method (§4.2), the phase-authoring-split hypothesis + the
    `.aiya/<issue>/` storage layout + the Chain→CCS component mapping (§4.4). What did **not** carry
    over: PoC evaluation numbers/paper citations (already-decided defensive-framing exclusion), the
    external `agents-in-your-area` product-vision links, the obsolete `/hi`/`/go` CLI surface, and
    smith's own plan-ahead/domain-expert-registry axis (out of scope now that aiya absorbed smith's
    role). `design.md` is the only design doc left; nothing else needs consulting for design content.
  - Branch `feature/smith-plugin`, PR #1 (https://github.com/lovaizu/ccpm/pull/1). Review milestones
    on the PR, not the console — but this session the user reviewed design content turn-by-turn in the
    console and had each fix pushed immediately; PR is where the rendered diagrams/tables are confirmed.
  - **`design.md` is now the source of truth for the design**, and it diverged from the older `.rn/`
    memos this session. Where they conflict, `design.md` wins. Specifically:
    - **CCS = YAML** (NOT TOON). Any note saying "CCS = 9-component TOON" (incl. the old bullet below,
      `core.md`, `acc.md`) is **superseded** — only the format changed; the 9 components + `type` vocab
      + by-path/soft-cap/Conductor-reads-only-CCS rules carry over.
    - The doc no longer contains Form-A/B or PoC framing; that history is steering-only (D-1/D-2).
  - **Tasks restructured per D-2** (final-deliverable-first): old design-memo #1 retired; work builds
    the real plugin artifacts. README is its own task (#3), authored **after** SKILL.md settles.
    Dogfood is #5. Don't relitigate D-2.
  - The design substance (now authoritative in `aiya/docs/design.md`): 1 Step = 1 work-Turn
    (generate+folded-compress), then an independent discarded verify-Turn; **CCS = YAML**, 9 components,
    artifacts by path never inlined, soft size cap, Conductor reads only latest CCS + verdict;
    verify-Turn fresh-context with the true goal sourced from the **immutable gate-approved goal.md**
    (not the running CCS); re-aim cap 3 → escalation as an exception outside the 6 gates (carries the
    ≤3-gap failure history); boundedness enforced structurally (return contract + read-restriction +
    size-budget/grep), default+observable rather than guaranteed (proof = the dogfood, #5).
  - 6 gates = 3 phases (Goal/Approach/Delivery) × {Planning IN, Output OUT}; steer on `/ty` approve,
    `/gm` redirect; surface = async chat.
  - PoC proved ACC/TC *when scripted* (`poc.md`, measurements only — raw artifacts deleted). The
    prompt-driven form's burden = show they hold under prompt control; proof is the dogfood (#5).
  - The dogfood builds techting to a throwaway/compare location, never over the real techting worktree
    (branch `worktree-techting`, its own PR #5).
  - Working method: 1問ずつ・素の対話で合意してから書く（全体→詳細）. Artifacts in English, console in 敬体.
