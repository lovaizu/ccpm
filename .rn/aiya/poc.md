# AIYA core PoC — result

> Feasibility evidence for the goal-convergence engine kernel described in
> [`aiya/docs/design.md`](../../aiya/docs/design.md). Not a
> shipped plugin — the artifact is proof the engine runs, though it happens to be a genuinely useful
> ccpm marketplace linter. Substrate: ccpm's **Workflow tool** (main-spawns-Turns, deterministic
> flow-control, structured handoff, generate→verify pipelines).
>
> **Note — raw artifacts removed (2026-06-26).** The throwaway PoC artifacts (`poc/`, `poc2/`: the
> linter `.mjs` files, the round-2 workflow script, and `poc2/ccs/t001..t005.md`) have served their
> purpose and were deleted. The measurements they produced — CCS sizes, the +18% creep, the redirect
> re-convergence — are recorded in this document, which is the evidence of record. The form-A design
> that builds on them is [`conductor.md`](./conductor.md).

## What was run

One real work-item — author and deliver a `marketplace-lint` tool for ccpm — driven through the
engine's three phases, each a `generate` Turn then a separate `verify` Turn, with the human gate at
each phase boundary **self-driven by the Conductor** (the run's explicit choice: a feasibility PoC
tests the machinery, not the human-gate UX).

| Phase | Workflow run | CCS size | verify verdict | what verify caught |
|---|---|---|---|---|
| 1 · Goal | `wf_8d73f6b6-9fd` | ≈ 3,758 chars | pass | 4 real detection-precision gaps |
| 2 · Approach | `wf_9ecc5456-860` | ≈ 9,303 chars | pass | 0 blocking (all 4 gaps closed); 2 non-defect notes |
| 3 · Delivery | `wf_31d23dc3-acb` | (artifact) | pass | 0 — verified by **executing** the linter |

Artifact: `poc/marketplace-lint.mjs` (201 lines, Node ESM, built-ins
only — raw file removed as throwaway, see note below). Independently re-run against this repo at the
time: `RESULT: 0 violation(s)`, exit 0. Against bad fixtures
it flags each of the 3 invariants with a precise message, and a top-level manifest `version` is
correctly **not** flagged.

## What the PoC proves (the kernel is feasible)

- **The Conductor loop runs on the substrate** — main spawns Turns, receives a bounded CCS + verdict,
  judges against the goal, advances. End-to-end across 3 phases.
- **Generate/verify split catches real defects** — Phase 1's verifier (no shared context with the
  author) found 4 gaps the author missed; they carried forward and Phase 2 closed them; Phase 3's
  verifier caught nothing **because it ran the code**, not because it trusted a self-report.
- **No transcript accumulation** — each phase ran from a bounded handoff, never the prior phase's raw
  transcript. (But see the ACC caveat below: the *compression* was done by hand, not by a mechanism.)
- **Autonomous convergence, no babysitting** — no human mid-phase; the Conductor self-drove every
  gate and still converged on a correct, executable artifact.

## What round 1 did NOT prove — the two load-bearing mechanisms (CLOSED in round 2)

> **Superseded by [Round 2](#round-2-result--the-two-mechanisms-exercised-as-mechanisms) below.** This
> section records the gap *as it stood after round 1*; round 2 exercised both mechanisms and closed it.

The engine rests on exactly two mechanisms: **ACC** (anti-bloat) and **TC** (anti-drift). In round 1
neither was actually exercised as a mechanism. Everything else (parallelism, gate UX) is downstream of these two
and is a practice-improvement question, not a PoC question.

- **ACC — the property held, but the mechanism did not run.** Each phase ran from a bounded CCS, so
  nothing accumulated. But the *compression was done by hand by the Conductor* — `GOAL_CCS` /
  `APPROACH_CCS` were constants typed from the steering notes, not produced by an ACC compression
  Turn. ACC's actual claim is to externalize state *out of* the Conductor so listening to more streams
  doesn't grow context; here the state lived in the Conductor's own notes. **Auto-compression and
  multi-stream non-growth are untested.** (3 phases, 1 stream: 3.7K → 9.3K is a trend, not a test.)
- **TC — the detector worked, the correction loop did not.** The generate/verify split genuinely
  caught real intent↔output gaps (Phase 1's 4 gaps; Phase 3 verified by *executing*). But every
  verdict was `pass`; the **redirect / re-aim loop never fired** (`design.md` §3 Stage ③), and **no drift was
  ever injected** — the gaps were organic, not a controlled test. We proved the engine passes correct
  work, not that it *steers back* incorrect work.
- **Downstream of the two (not PoC-able, improve in practice):** parallelism is arithmetic once
  per-stream attention is bounded (scaling unit = the *expert's* async attention, not Conductor
  concurrency — which the Workflow substrate already does 16-way); gate UX is the per-gate cost that
  the 6 sparse async touchpoints already make cheap.

## Round 2 result — the two mechanisms, exercised as mechanisms

> Run: workflow `aiya-poc2` (`wf_1717a3c1-a11`), 18 Turns, same Workflow substrate. Subject: extend
> round 1's linter with 5 new ccpm invariants (INV4–INV8), one per Turn — a sequential ACC chain
> (CCS_N depends on CCS_{N-1}). Artifacts (raw files removed as throwaway, see note below):
> `poc2/marketplace-lint.mjs`, CCS files `poc2/ccs/t001..t005.md`. This closes the two holes round 1 left.

### ACC — compression is now a real Turn, and the handoff stays bounded

Each `CCS_N` was produced by a dedicated **compression Turn** (an AI invocation given `CCS_{N-1}` +
the Turn's raw work + verdict, told to rewrite a fresh bounded CCS and **reference the artifact by
path, never inline it**). The Conductor never typed a CCS — round 1's sin is gone. Measured sizes:

| Turn | invariant | CCS (chars) | transcript-if-replayed (chars) |
|---|---|---|---|
| 1 | INV4 | 809 | 1,408 |
| 2 | INV5 | 807 | 2,975 |
| 3 | INV6 | 820 | 4,551 |
| 4 | INV7 | 904 | 6,240 |
| 5 | INV8 | 953 | 8,193 |

The CCS stayed **bounded** (807–953) while the would-be transcript grew ~linearly (~1,600/Turn) to
8.6× the CCS by Turn 5 — the gap widens every Turn. This is the paper's memory-usage result
reproduced on a real chain: replace-don't-accumulate holds because the CCS carries the goal +
constraints + invariant *ids* and points at the linter file, while the file itself grows from 3 to 8
rules. Independently checked: `grep` finds **no** CCS file inlining linter source.

**Honest caveat:** the CCS is bounded and near-flat, **not byte-constant** — it crept +144 chars
(+18%) across 5 Turns, entirely from the growing "invariants so far" id-list (`INV1..INV8`). Sub-linear
and itself compressible, but not zero-growth. And this was **one sequential stream**: per-chain
boundedness via real compression is now proven; the N-parallel-streams aggregate-non-growth claim
follows by arithmetic from it but was not separately measured.

### TC — the redirect loop fired on a controlled drift and re-converged

Turn 2's generate-Turn was handed a **deliberately wrong spec**: "INV5 — version must be a non-empty
string" (which only duplicates INV1 and accepts non-semver). The verify-Turn ran in a fresh context,
was told **nothing** of the injection, held only the true goal (semver MAJOR.MINOR.PATCH), built a
`version: "v1.0.0"` fixture, saw it pass uncaught, and returned **`fail`** with a precise gap ("the
code only checks non-empty string … no semver parse exists"). The Conductor **re-aimed**; the
re-generate fixed INV5; re-verify returned **`pass`** — `reconverged: true`. The other 4 Turns passed
on first try (no false redirects). Independently reproduced: the final INV5 flags `1.2` / `v1.0.0` /
`1.2.x` / `abc` and accepts `0.5.0` / `1.2.3-rc.1`. This is the proof round 1 lacked — the engine
**steers back incorrect work**, not just passes correct work.

### Integration — verified by execution

The finished 8-invariant linter reports `RESULT: 0 violation(s)` (exit 0) on the real repo, and an
all-invariants fixture trips **all 8** (INV1–INV8, 14 VIOLATION lines, exit 1) — none missing. Checked
independently, not from the agent's self-report.

### What round 2 settles, and what is left

Both load-bearing mechanisms are now demonstrated **as mechanisms**, on the substrate: ACC compresses
via a real Turn and stays bounded; TC detects an injected drift and the Conductor re-converges. What
remains is **not** mechanism-feasibility but practice/scale (per `design.md` §5 and the round-1 list):
genuine N-stream concurrent boundedness, the human gate-UX under real async load, and packaging
(smith plan-ahead, sandbox, auditor). Those improve in use; they are no longer open feasibility risks.

## Note on the gates (no design change needed)

An earlier draft of this doc proposed making gates "escalation-triggered / async-approve" — that was
a misread. The gates are already coarse and async by design (`design.md` §4.4 phase gates): exactly
**6 fixed touchpoints per work-item** (3 phases × {Planning Gate IN, Output Gate OUT}), all at phase
boundaries, over existing async chat (Slack / Channels), with `/ty` approve · `/gm` redirect. That
sparseness — 6 boundary points vs rn's per-turn watching — *is* the scaling lever, so 10 parallel
streams cost ≈60 async decisions total, not continuous attention. The PoC's all-self-driven run simply
chose not to exercise the gates; it revealed no gate-frequency problem. (Gate UX therefore stays in
the "not proven" list above — untested, not deficient.)
