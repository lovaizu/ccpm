Design: aiya/docs/design.md

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
- The verify-Turn standard viewpoint catalog (task #2, per D-5) is curated from established skills/
  plugins and industry best-practice checklists per domain — not authored from a blank page.

# Tasks

> Restructured per **D-2** (final-deliverable-first) on resume 2026-06-26. The old #1
> "design the procedure as a memo (`conductor.md`)" is retired; the salvageable design folds into the
> real artifact `aiya/docs/design.md`. README is split into its own task, written **after** SKILL.md
> settles (user choice: `design.md` first, alone).
>
> Re-aligned per **D-4** to `rn` 0.7.0's coordinator/experts process on 2026-07-05: per-task
> "user review (on the PR)" is dropped (the user now signs off only at the plan / design / evaluation
> gates); a standalone **Design sign-off** task (#1b) and a closing **Evaluation sign-off** task (#6)
> carry those two gates explicitly; build tasks close on self-check + QA/Craft/Verification/Design
> expert review instead. See [`State`](#state) and D-4.

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
- [x] self-check (record OK/NG per criterion in `.rn/20260701-aiya/checks/1.md`)
- [x] QA expert review (subagent)

**Completion criteria**: `aiya/docs/design.md` exists, intent-first, internally consistent, and relies
on no script to hold the loop; the salvageable design is preserved in the real artifact; `conductor.md`
is retired.

### #1b: Design sign-off

**Purpose**: Take the user's sign-off on `aiya/docs/design.md` — the design gate — before heavy build
(#2's `SKILL.md`) starts on it. Not settled at plan time: the design has been under user review on
PR #1 since #1 closed, most recently the round-6 figure-story feedback (see [`State`](#state)).

**Prerequisites**: #1.

**Steps**:

- [ ] Present `aiya/docs/design.md` to the user (on PR #1) and take the verdict via `/rn:ty` (approve)
      or `/rn:gm` (revise → address the feedback, re-present). Repeat until approved.

**Completion criteria**: `aiya/docs/design.md` is approved by the user.

### #2: Author the aiya Conductor skill (SKILL.md)

**Purpose**: Turn #1's design into the actual prompt-driven skill — the heart of the plugin.

**Prerequisites**: #1b.

**Steps**:

- [ ] Pick the skill verb (`/aiya:<verb>`) and write the frontmatter (model-invocable description with
      concrete trigger phrases; third-person; version-agnostic).
- [ ] Write the body: imperative Markdown, the Conductor cycle from #1's `design.md`, ACC and TC
      dissolved into the steps, the iteration cap and escalation stated. Lean.
- [ ] Author the standard viewpoint catalog (per D-5) as a reference doc the skill points to: per
      domain (coding / writing / visual), curate the base viewpoint set from established skills/
      plugins and industry best-practice checklists (e.g. this repo's own `code-review` /
      `security-review` skills, `rn`'s own Craft/Verification checklists in
      `task-verify-workflow.md`) — do not invent the catalog from a blank page.
- [ ] Cross-check item by item against `design.md` and `acc.md` / `tc.md` so no pillar is dropped (do
      not sample).
- [ ] self-check (record OK/NG per criterion in `.rn/20260701-aiya/checks/2.md`)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing)
- [ ] Verification expert review (subagent, fact-check)
- [ ] Design expert review (subagent — this task produces the Conductor's structure/approach)

**Completion criteria**: `aiya/skills/<verb>/SKILL.md` exists, is prompt-driven (no embedded JS loop),
and encodes the bounded-CCS / verify-Turn / re-aim / phase-gate cycle with a stated cap.

### #3: Author `aiya/README.md` (user-facing guide)

**Purpose**: The scenario + real-console guide, written **after** the skill settles so it reflects real
behavior (user choice: README is a separate, later task — not bundled with the design).

**Prerequisites**: #2.

**Steps**:

- [ ] Write `aiya/README.md` in scenario + real-console style (not a mechanical list; no controlling
      noun labels like "管理").
- [ ] self-check (record OK/NG per criterion in `.rn/20260701-aiya/checks/3.md`)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing)
- [ ] Verification expert review (subagent, fact-check)

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
- [ ] self-check (record OK/NG per criterion in `.rn/20260701-aiya/checks/4.md`)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing)
- [ ] Verification expert review (subagent, fact-check — validate output confirmed, not assumed)

**Completion criteria**: both strict validations pass; marketplace.json and root README both list aiya
and stay in sync; version lives only in plugin.json.

### #5: Dogfood — build techting via aiya, measure ACC & TC under prompt control

**Purpose**: Prove the two properties hold under prompt control (Level B). This is the point of the
whole build.

> Measurement-design note (PR-review discussion, 2026-07-02): check for **silent instruction-drift**
> — the Conductor reading raw Turn output, or the verify-Turn sourcing the goal from the running
> CCS's `goal_orientation` instead of the gate-approved `goal.md` — not just CCS-size numbers.
> Nothing in the design technically blocks either; boundedness and goal-provenance rest on prompt
> adherence (design.md §5.1's last entry is honest about this: default+observable, not guaranteed).

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
- [ ] Write the result to `.rn/20260701-aiya/dogfood.md` (honest scope: what was measured vs. asserted).
- [ ] self-check (record OK/NG per criterion in `.rn/20260701-aiya/checks/5.md`)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing)
- [ ] Verification expert review (subagent, fact-check — measurements verified, not asserted)

**Completion criteria**: the dogfood result shows ACC bounded-context and TC drift-catch-and-reconverge
**by measurement** under prompt control; the produced techting meets its own criteria; the honest-scope
result is recorded.

### #6: Evaluation sign-off

**Purpose**: Take the user's sign-off on the Acceptance criteria run — the session's closing gate.

**Prerequisites**: #5.

**Steps**:

- [ ] Present the Acceptance criteria run result (Level A + Level B, per #5's dogfood measurement) to
      the user and take the verdict via `/rn:ty` (approve → session closes) or `/rn:gm` (revise →
      address the feedback, re-present).

**Completion criteria**: the Acceptance criteria run is approved.

# Decisions

### D-1: Conductor form A (prompt-driven), not B (scripted)

Decided 2026-06-26 (originally recorded in the now-retired `core.md` §10 D-1; the settled design lives
in `aiya/docs/design.md` §5.1). Summary: the shipped Conductor is the main agent running a prompt-driven
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

### D-3: Design-doc format — canonical h2 sections, question h3s, explicit epistemic status (user, 2026-07-02)

Settled during the PR #1 user review of `design.md`; **revised the same day** after the user challenged
the first version's derivation (its question h2s were retrofitted from the text already written, and the
detailed-design h3s were noun labels again). The settled form:

- (a) **h2s are the canonical design-document sections** — Background & Goals / Assumptions &
  Constraints / Design overview / Detailed design / Alternatives considered. The canon fixes *which
  sections a complete design has* and makes the skeleton reusable across designs.
- (b) **h3s are the questions the section must answer**, derived **viewpoint-first**: per h2, first list
  what a design must convey there, then phrase each item as a question — never derive the questions from
  existing prose. Detailed design repeats one fixed question per part — "What is \<part\>'s contract,
  and how is a breach caught?" — with a coverage lead-in mapping every part in the overview's parts
  table to its contract home (closure check).
- (c) **No lone h3**: group the canon so every h2 carries ≥2 questions (Non-goals folds into
  Background & Goals; the overview question opens Design overview).
- (d) **Every claim's status is explicit** (unchanged from the first version): facts carry their source,
  hypotheses carry a "hypothesis / not yet shown" marker, decisions live in Alternatives with *Intent:*.

Rationale: noun labels alone let a reader pass a section they did not actually understand; question
headings retrofitted from the text inherit its blind spots. Deriving the questions from "what must a
design convey" makes coverage mechanically checkable (検討漏れ防止) and the template portable to other
designs. First version applied in `08ba166` + `7c8a79e`; revised form in `f914855`. Candidate to fold
into aiya's own gate artifacts (`goal.md` / `approach.md`) when authoring SKILL.md in #2.

Note this is **`aiya`'s own design-doc format**, a decision this session made for its one artifact — a
narrower, deliberate choice, not a claim that `rn`'s generic `design-template.md` (Context & constraints /
Approach / Structure / Flow / Open questions, one level of headings) is wrong for `rn`'s own sessions.

### D-4: Re-align task structure to `rn` 0.7.0's coordinator/experts process (2026-07-05)

`rn` was updated (merged to `main` in `ebf3f49`…`d58e8e3`, now installed at 0.7.0) while this session was
suspended. Brought current in three parts:

- **Session directory renamed** `.rn/aiya/` → `.rn/20260701-aiya/` (date-prefixed, per `rn`'s
  `.rn/{yyyymmdd}-{slug}/` convention) — `20260701` is this session's actual start date (`a18a3f7`).
- **`Design:` line added** at the top of this file, pointing to `aiya/docs/design.md` — required by the
  current `steering-template.md`; this session already treated that file as its design.md in substance,
  only the pointer line was missing.
- **Task structure re-aligned**: every task's dangling "user review (on the PR)" step is replaced by the
  axis-based expert reviews (`task-execute-workflow.md` / `task-verify-workflow.md`): self-check → QA
  (always) → Craft + Verification (per the task's medium) → Design (only for #2, which produces the
  Conductor's structure) → coordinator review. The user's sign-off is now carried by two dedicated
  tasks instead — **#1b: Design sign-off** (was the open item in #1) and the new closing **#6:
  Evaluation sign-off** — the only two points, alongside the plan gate already taken when this session
  opened, where the user's verdict (`/rn:ty` / `/rn:gm`) is asked for.

Rationale: this is exactly the process the currently-installed `rn` runs sessions with; keeping this
session on the pre-0.7.0 per-task-approval shape would silently diverge from how `/rn:up` now executes
tasks #2–#6. No re-litigation of already-closed work: #1's own steps are unchanged (it closed under the
old shape); only the still-open items move to the new one.

### D-5: verify-Turn decomposes per viewpoint, dispatched flat by the Conductor (user, 2026-07-05)

Raised during #1b's design review (console, PR #1 still open). §4.2 originally specified **one**
verify-Turn per Step, checking three targets — the goal, the approach's spec, stated rules — in
priority order inside that single call. The user's concern: bundling several checks into one verifier
reproduces the exact "reviewed together, something slips through" failure mode this session already
sees in its own PR-review loop (round-6's figure issues took several rounds for a human to catch).

**Decision**: verify-Turn decomposes into **one independent, flat, Conductor-dispatched Turn per
viewpoint** — a viewpoint being any independently-checkable concern (an Acceptance Scenario, a stated
rule, or a domain concern like class/method decomposition, naming, thread-safety, memory-leak for
code). The Conductor aggregates mechanically (pass only if every viewpoint's verdict is `pass`; the
gap is the union of the failing viewpoints' gaps) — aggregation is control flow, not domain work, so it
does not breach the Conductor's no-domain-work wall.

- **No nesting.** This does not put a subagent inside a Turn — §3.2's "Turns never nest, only the
  Conductor spawns" invariant is unchanged. What changes is that Stage ②'s "the verify-Turn" (singular)
  becomes **N flat, Conductor-dispatched verify-Turns** (N = the viewpoint count for that Step), still
  all direct children of the Conductor.
- **Viewpoint set = standard catalog (by domain) + Conductor-added, Step-specific ones.** A standard
  viewpoint catalog is curated per domain (coding / writing / visual) from established skills/plugins
  and industry best-practice checklists (task #2's new step; see Rules) — not invented from a blank
  page. At runtime the Conductor pulls the Step's domain's standard set from the catalog and adds any
  Step-specific viewpoint the catalog would not anticipate.

Rationale: this generalizes §5.1's existing independence argument (verify-Turn is separate from
generate-Turn so it cannot be fooled by a laundered self-report) one level finer — a verifier
concentrating on one narrow viewpoint is less likely to miss it than one juggling several at once. It
is not a new, unproven idea: this very session's own `rn` process already runs on the same shape
(`task-verify-workflow.md`'s per-axis QA/Design/Craft/Verification dispatch, each an independent
subagent concentrated on one lens) — D-5 brings that same shape down one level, into aiya's own
verify-Turn, at finer (per-viewpoint, not per-axis) grain.

**Design.md sections affected** (updated under #1b, before re-presenting for `/rn:ty`): §3.2 (the
"1 Step = 1 Turn" invariant's verify-Turn wording, singular → per-viewpoint plural, still uncounted),
§3.3 (Stage ② redrawn as a fan-out to N verify-Turns, Conductor aggregates), §4.2 (verify-Turn's
contract redefined per-viewpoint; the catalog-plus-runtime-addition rule stated; the catalog's actual
content is task #2's job, not design.md's), §5.2 (verification cost restated as scaling with viewpoint
count, still discarded/non-accumulating per Turn).

# State

(written by `/rn:dn`, read and reset to this placeholder by `/rn:up`. `Status` is `paused` while a
session is suspended — the signal `/rn:up` and `/rn:dn` search for — and resets to `not suspended`
here, so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Notes**: bounded forward pointer — branch/PR, next concrete action, open blockers, user-deferred paths, open questions / pending decisions not yet captured in `design.md`; not a re-narration of the session (that lives in `git log`)
