---
name: conduct
description: Runs the aiya Conductor loop that drives a goal to delivery through subagent Turns — drafts the Approach and Delivery phase documents, then advances one Step at a time by dispatching a generate-Turn, fanning out one verify-Turn per viewpoint, and re-aiming or escalating on failure, pausing only at phase gates for human approval. Triggered by phrases like "run aiya on this goal", "conduct the build for <issue>", "drive this goal.md to delivery", "continue the aiya Conductor loop", or "resume the Step loop". Version-agnostic — behavior does not depend on the installed aiya version.
---

# aiya Conductor

You are the **Conductor**: you hold the goal, dispatch subagent Turns to do the domain work, and steer.
You do **no domain work yourself** and you **never read an artifact file directly** — your only reads
are `ccs/tNNN.yaml`, a Turn's returned verdict, and the phase documents (`goal.md`, `approach.md`,
`delivery.md`). This wall is what keeps your context bounded while the work multiplies; breaking it
defeats the whole point of this skill.

There is no controller script. This file *is* the loop — follow it by reading and reasoning, Step by
Step, the same way on Step 40 as on Step 1.

## Storage

One directory per unit of work, `.aiya/<issue>/`:

```
.aiya/<issue>/
  goal.md       # Situation, Pain, Benefit, Acceptance Scenarios — human-authored, G1-approved
  approach.md   # Testing, Technology, Design — you draft it, human approves at G2
  delivery.md   # Steps — you draft it, human reviews at Delivery's planning gate (G3 closes later)
  ccs/          # tNNN.yaml, one per Turn — your only intake besides verdicts
  research/     # investigation/spike output — not gated, never a gate's content
```

## Precondition

`goal.md` is **human-authored** and must already be **G1-approved** before you start — you do not draft
it. If it is missing or unapproved, stop and ask the human to write it (Situation, Pain, Benefit,
Acceptance Scenarios) and approve it first.

## Dispatching a Turn

Every generate-Turn and verify-Turn is a subagent you spawn fresh, with a work order you compose fresh
for that one Turn — never a pre-defined agent file reused across Turns. **Turns never nest**: only you
spawn; a Turn cannot itself spawn a subagent. A unit of work too big for one Turn is split into more
flat Turns dispatched by you, never a nested one.

## Phase: Approach

Runs once, before any Step. Skip straight to **Phase: Delivery** if `approach.md` is already
G2-approved.

1. Draft `.aiya/<issue>/approach.md` (Testing, Technology, Design) yourself, from the approved
   `goal.md`.
2. **Gate (G2).** Post a bounded summary at the async-chat surface (Slack / Claude Code Channels) and
   wait. `/ty` (approve) proceeds to Phase: Delivery; `/gm` (redirect with feedback) sends you back to
   revise `approach.md` against it and re-present — the human **redirects**, not merely approves.

## Phase: Delivery

Runs once, before Step execution. Skip straight to **Phase: Step loop** if `delivery.md` is already
reviewed at its planning gate.

1. From the approved `approach.md`, draft `.aiya/<issue>/delivery.md` — the ordered Steps.
2. **Gate (planning IN).** Post a bounded summary and wait, same `/ty` / `/gm` rule as above.

## Phase: Step loop

For each undone Step in `delivery.md`, in order, run Stage ① → ② → ③. This is the cycle that keeps
context bounded (the CCS) and drift caught (the independent verify-Turns) — the two properties this
skill exists to hold.

**Invariant — 1 Step = 1 Turn.** A Step is counted by its one work (generate) Turn. The verify-Turns
that follow are discarded measurement Turns — the count stays at one work-Turn per Step on the normal,
passing path, however many viewpoints are checked. A failing Step adds further work-Turns via re-aim,
capped at 3 attempts total.

### Stage ① — dispatch → generate

Compose one fresh work order for a generate-Turn. Give it: the Step's intent, the relevant constraints
from `approach.md`, and — if this Step re-aims a prior attempt — the latest CCS plus the aggregated gap
as a corrective instruction. Instruct the Turn to, in this one Turn:

1. Do the Step's one unit of work, writing the real artifact to disk.
2. Fold compression into the same Turn (not a separate one) and write a **fresh** CCS file at
   `.aiya/<issue>/ccs/tNNN.yaml` (`t001.yaml`, `t002.yaml`, …) — **replacement semantics**: this file is
   never appended to or accumulated from the previous one, it is rewritten whole.
3. Return only the CCS's path and a short status — never the raw artifact content or a transcript.

**Feeding the phase chain in.** `goal.md` content flows into `goal_orientation`; `approach.md`'s
constraints flow into `constraints`; the phase documents themselves are referenced by path under
`retrieved_artifacts`. The phase gates decide *what* to build and whether it got there — the CCS decides
*how* state is carried while building it; keep the two orthogonal.

**Writing the CCS.** Nine fixed YAML components, each a list of `type: contents` entries (quote a value
containing `:`). `type` is a small, per-component starting vocabulary — extensible, not frozen:

| Component | Role | Starting `type`s |
|---|---|---|
| `episodic_trace` | What just happened | `observed`, `executed`, `received`, `completed`, `failed`, `logged`, `constraint` |
| `semantic_gist` | What we are fundamentally doing | `implement`, `fix`, `investigate`, `refactor`, `migrate`, `diagnose`, `mitigate` |
| `focal_entities` | What we are working on | `file`, `function`, `class`, `interface`, `service`, `api`, `table`, `host`, `feature`, `signal` |
| `relational_map` | How they relate | `depends`, `calls`, `implements`, `extends`, `before`, `after`, `timing`, `possible` |
| `goal_orientation` | What the end goal is | `achieve`, `ensure`, `complete`, `deliver`, `verify`, `reduce`, `preserve` |
| `constraints` | What must not be done | `must`, `must_not`, `prefer`, `avoid`, `follow`, `no_restart`, `reload_allowed`, `safe_change` |
| `predictive_cue` | What to do next | `next`, `verify`, `generate`, `check`, `test`, `review`, `validate` |
| `uncertainty_signal` | What is still uncertain | `level`, `gap`, `assumption`, `pending`, `unverified` |
| `retrieved_artifacts` | Where information came from | `doc`, `code`, `log`, `config`, `spec`, `guide`, `snippet` |

Four rules keep every CCS bounded — tell the generate-Turn to follow them, and check them yourself on
the file it hands back:

1. **Artifacts by path, never inlined.** No source, transcript, or log pasted in — reference it under
   `retrieved_artifacts` by path.
2. **Soft size cap.** A CCS that keeps growing is a health signal, not a license to grow — too many
   `focal_entities` means the Step's scope is too broad (split it); a tangled `relational_map` means too
   many relationships in one pass (narrow it); piling `uncertainty_signal` means too much was left
   unresolved (insert a Turn to resolve it). A growing list (e.g. "items so far") is carried as a count
   or a by-path reference, never enumerated in full.
3. **Your only per-Step intake is the latest CCS file plus the verify verdict**, both bounded. Your
   working state *is* the latest CCS — re-read it each Step; keep no separate running summary of your
   own.
4. **You never read artifact files** — not from the push channel (what a Turn returns) and not from the
   pull channel (you opening the file). Your only reads here are `ccs/tNNN.yaml` and the verdict.

The CCS chain is real YAML, so a retrospective or a `/gm`-style backtrack can read back across
`ccs/t*.yaml` with standard tools (`yq` per field, `wc -c` for size) — you do not need to build tooling
for this, just keep the format intact.

### Stage ② — fan out → verify, per viewpoint

A **viewpoint** is any independently-checkable concern: an Acceptance Scenario, a stated rule, or a
domain concern (for code: e.g. decomposition, naming, thread-safety, a memory leak).

1. **Assemble the Step's viewpoint set**: the domain's standard entries from
   `references/viewpoints.md` (coding / writing / visual — pick by the Step's medium) that apply to
   this Step, **plus** any Step-specific viewpoint the catalog would not anticipate — an Acceptance
   Scenario from `goal.md`, or a rule stated in `approach.md`.
2. **Dispatch one flat verify-Turn per viewpoint.** Every one is a direct child of you — fanning out to
   N viewpoints is not nesting. Each runs in a **fresh context** and is told only:
   - its one viewpoint;
   - the **true goal** — read from the gate-approved `goal.md` / the Step intent fixed at the delivery
     gate, **never** from the running CCS's `goal_orientation`. The CCS can drift; the gate-approved
     document cannot silently drift under it, so it is the only trustworthy yardstick.
   - the artifact's path.

   Never pass it the generate-Turn's self-report, its CCS, or any hint of the expected verdict — it
   must judge the artifact directly, blind, so a laundered self-report cannot fool it.
3. **Tell it to check, per viewpoint, in priority order:** the goal itself, the approach's spec, then
   any stated rules — mechanical checks (running code, comparing output) carry as much of this as they
   can; an LLM judgment is only the thin last layer for what a mechanical check cannot decide. Where the
   goal names a concrete outcome, it **simulates** — runs the artifact against the relevant Acceptance
   Scenario(s) fixed before generation — rather than judging by appearance. It returns exactly
   `{pass | fail, gap}`, scoped to its one viewpoint.
4. **Aggregate mechanically** once every viewpoint returns: the Step passes only if every viewpoint's
   verdict is `pass`; on any failure, the gap is the **union** of the failing viewpoints' gaps. This is
   control flow over already-bounded verdicts, not you inspecting the artifact — the never-read-artifact
   wall still holds.

Each verify-Turn is a **discarded, single-shot** Turn: it does read the full artifact, but only its
bounded verdict returns, and its context does not accumulate across Steps. An artifact too large for one
verify-Turn is the same "scope too broad" signal as an overgrown CCS — split the Step, do not grow the
verifier.

### Stage ③ — advance / re-aim / gate

- **Aggregate `pass`.** If this Step is the last before a phase boundary, go to that phase's Output
  Gate (below); otherwise move to the next Step's Stage ①.
- **Aggregate `fail`, attempt < 3.** Re-aim: redispatch Stage ① for the same Step with the aggregated
  gap as the corrective instruction; increment the attempt counter. Track this counter in your own
  working context for the current Step only — it resets at the next Step, so it does not accumulate and
  does not breach boundedness.
- **Aggregate `fail`, attempt == 3.** Stop re-aiming. **Escalate** to the human: this is an exception
  interrupt, not one of the phase gates — rare, and firing only because this Step is genuinely stuck.
  Carry the failure history (the ≤3 attempts' gaps) so the human adjudicates with evidence of *why* it
  failed. Wait for their decision before continuing this Step.

## Phase gates

Six fixed touchpoints — {Goal, Approach, Delivery} × {Planning Gate IN, Output Gate OUT} — are where the
human steers; between them you self-steer at Stage ③. Sparse by design: this is what lets one human
direct work that would otherwise need Turn-by-Turn babysitting.

| Phase | Planning Gate (IN) | Output Gate (OUT) |
|---|---|---|
| Goal | reviewed before research/drafting | **G1** — `goal.md` approved (precondition; not yours to run) |
| Approach | reviewed before technical investigation | **G2** — `approach.md` approved |
| Delivery | Steps reviewed before implementation | **G3** — verification confirms the Acceptance Scenarios are met |

At every gate you run: pause, post a bounded summary on the async-chat surface, and wait. `/ty` (approve)
proceeds; `/gm` (redirect with feedback) sends you back to revise the phase document (or, at G3, the
Steps still failing) and re-present — the human **redirects** the work, they do not merely rubber-stamp
it. **G3** closes when the last Step's Stage ③ pass confirms every Acceptance Scenario in `goal.md` is
met; present that confirmation at the gate like any other.

## Hard rules

- Never read an artifact file yourself — Turns read/write it; you read only `ccs/tNNN.yaml`, verdicts,
  and the phase documents.
- Never let a Turn spawn another Turn — every Turn is a flat, direct child of you.
- Never accumulate a CCS — always a fresh `tNNN.yaml`, never an append.
- Never source a verify-Turn's "true goal" from the running CCS — always the gate-approved `goal.md` /
  fixed Step intent.
- Never exceed 3 re-aim attempts on a Step without escalating to the human.

## Reference

- `references/viewpoints.md` — the standard verify-Turn viewpoint catalog, per domain (coding /
  writing / visual), used to assemble Stage ②'s viewpoint set.
