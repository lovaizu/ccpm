Rn version: 0.8.0
Design: aiya/docs/design.md

# Goal

One expert delivers what used to take a team.

Getting there means AI running many work-streams at a single goal, with the human steering at a few
points rather than supervising. Two things break that today: what the directing agent has to hold
grows with the work until it collapses, and the work drifts off the goal with nobody noticing until
the end.

`aiya` is the Claude Code plugin that removes both.

# Acceptance criteria

**The purpose is reached — one person got real work delivered, and was not needed in between:**

- Real work came back from a goal alone: the human said what they wanted, and what arrived met that
  goal's own acceptance criteria, with any shortfall recorded rather than omitted.
- The human was asked to act only a few times, and every time it was a decision — approve or
  redirect — never watching work in progress.
- The work stayed on the goal: a deviation that arose during the run was caught during the run and
  corrected, not discovered at the end.
- Directing stayed affordable as the work grew: what the directing agent had to hold did not scale
  with the amount of work done.

Each of the four is shown by evidence a third party can open and re-read. None is asserted.

**The benefit is available to someone other than its author:**

- A reader who has never seen aiya can install it and drive one goal from start to finish, knowing at
  every stop what they are being shown and what to say back.
- The shipped artifacts describe one plugin, and no load-bearing term is left undefined.
- Every user-facing choice in the shipped plugin was ratified by the user; none traces back to an
  unratified inference.
- aiya installs from this marketplace and validates cleanly.

# Assumptions

- `claude plugin validate` and `claude -p … --plugin-dir` are available; if not, verification is done
  by hand and recorded as such.
- `dogfood/techting-requirements.md` is a carried-forward input whose source no longer exists on disk —
  the `worktree-techting` branch it came from is deleted. It is not regenerable.
- `aiya/docs/design.md` is the substance to build on, not a frozen input.

# Rules

How this session works. What aiya *is* lives in `design.md`; what a user sees lives in the plugin's
own artifacts; neither is restated here.

- **Agree the action before a task starts.** State the concrete actions the task will take — what gets
  decided, what gets written, and where — and get the user's agreement before taking them. This is not
  one of the three scheduled gates; it is a per-task alignment on *what will be done*, and no task
  starts without it.
- **A decision the user has not made is not a decision.** Where a task must pick a name, a surface, a
  default or a policy, it is put to the user — never inferred. A string already on disk is not evidence
  that anyone chose it.
- 1 task = 1 commit; commit and push every change; one completion marker per task.
- **UX first, then design, then implementation.** The experience decides the surface; the design answers
  to it; the build implements the design. A lower layer never silently overrides a higher one — a
  contradiction found while building goes back to the higher artifact.
- **Define a term before using it.** No load-bearing term enters an artifact undefined, and a term that
  cannot be defined concretely is replaced rather than kept.
- **Build from the final deliverable.** No intermediate memos or side notes — every task edits the real
  file it is about, and brushes it up there.
- **Curate, never invent.** Anything shipped as a standard or a checklist is drawn from established
  practice and carries its source; nothing is authored from a blank page.
- **The dogfood runs under `.rn/20260813-aiya/dogfood/`.** It is session material, not a plugin: nothing
  it produces ships, and keeping it in the repo is what lets a third party open the run's evidence.

# Tasks

Each task states what it must achieve and the state that means it is done. **Its Steps are agreed with
the user when the task starts** — the review steps below are rn's own process, the work steps are not.

### #1: Decide what using aiya is like

**Purpose**: Settle the human's experience of driving one goal from start to finish — the thing every
later artifact answers to.

**Prerequisites**: none.

**Steps**:

The experience was authored outside this session and confirmed sentence by sentence with the user,
landing as `aiya/README.md` (the experience) and `aiya/docs/design.md`. This task therefore reduces to
the one criterion the delivered set cannot self-certify: that nothing it shows rests on a mechanism
that was not confirmed to exist.

- [x] Extract every platform-dependent claim the delivered set makes — what it asserts Claude Code can do
- [x] Settle each against real evidence: official documentation, the official plugin sources on disk,
      and a headless probe where neither decides it
- [x] Record OK/NG per claim, with its evidence, in `.rn/20260813-aiya/checks/1.md`
- [x] For each NG, propose the fix with its rationale and trade-offs, and take the user's ruling before
      any edit — `README.md` and `design.md` are not touched until then (ruled 2026-08-14: NG-3 → A
      plus a hardening line in Trade-offs; NG-7 → resolved by citation; the rest as proposed)
- [x] ~~QA / Craft / Design expert reviews~~ — not run: they propose wording and structure changes to a
      set the owner already ratified sentence by sentence

**Completion criteria**:

- Someone who has never seen aiya can follow the decided experience end to end and knows, at every
  point where aiya stops for them, what they are shown and what to say back.
- Every user-facing choice it fixes was ratified by the user, and none is left for a later task to
  invent.
- Nothing it shows rests on a mechanism that was not confirmed to exist.

### #2: Complete the design against that experience

**Purpose**: Make the design a complete answer to the decided experience.

**Prerequisites**: #1.

**Steps** (agreed 2026-08-14 — the body is owner-ratified, so this task is cross-checking, not
authoring; NGs are proposed with rationale and ruled on before any edit):

- [x] Term check, exhaustive: every load-bearing term in `design.md` defined before first use, and
      naming aligned with the seven formats in `references/`
- [x] README ↔ design contradiction check: every behavior the README promises (6 gates, two words,
      five commands, 3-strikes escalation, …) is carried by the design
- [x] Ripple check on the seven ruled fixes from #1: the inserted sentences do not collide with their
      surroundings
- [x] Record OK/NG in `.rn/20260813-aiya/checks/2.md`; NGs await the user's ruling (recorded:
      49 OK / 11 NG, all proposals only, `README.md`/`design.md` untouched; coordinator verified every
      cited line)
- [x] Take the user's ruling on the 11 NGs, apply the ruled fixes via the implementation expert, and
      re-check the fix sites against their surroundings (ruled 2026-08-15: all 11 as proposed, NG-9
      design-side, NG-6 at 2,000 bytes, NG-10 covering plan.md:3; applied in 5eddb5e, re-checked)

**Completion criteria**:

- A reader can answer from the design alone what every term in it means and what the plugin is made
  of — nothing left to be inferred, no structural question unanswered.
- Nothing in the design contradicts the decided experience, and every carried-forward decision either
  still stands or its replacement is recorded with the intent behind it.

### #3: Design sign-off

**Purpose**: Take the user's sign-off on the experience and the design together, before anything is
built on them.

**Prerequisites**: #2.

**Steps**:

- [x] Present both to the user on the PR and take the verdict via `/rn:ty` (approve) or `/rn:gm`
      (revise → address the feedback, re-present). Repeat until approved. (approved 2026-08-15 via
      `/rn:ty`)

**Completion criteria**:

- The experience and the design are approved by the user.

### #4: Build the plugin so it runs

**Purpose**: Turn the approved design into a plugin that actually does what it describes.

**Prerequisites**: #3.

**Steps** (agreed 2026-08-15 — the Conductor ships as a Claude-only skill, `user-invocable: false`,
confirmed against the official skills reference; the five command words are thin entries into it;
design §2's part inventory is amended to match, per the user's ruling in-session):

- [x] Skeleton: `aiya/.claude-plugin/plugin.json` (version 0.1.0) and `aiya/CHANGELOG.md`, per
      `.claude/rules/plugin.md` (5b8f4c3)
- [x] Three Turn definitions in `aiya/agents/` — turn-generate / turn-verify / turn-brief (naming
      ruled 2026-08-15) — tools pinned per design §2/§4.4/§5.1: no spawn tool, no user-question
      tool, bounded returns (5b8f4c3)
- [x] Conductor skill (`user-invocable: false`) carrying §4's procedure, plus five thin entry skills
      `on` / `ty` / `gm` / `dn` / `up` (5b8f4c3)
- [x] Amend design §2's part inventory: six skills (five command words + the Claude-only conductor)
      (f1d870f)
- [x] Trace every design contract to where it ships (recorded as evidence in checks/4.md; one patch
      round for §5.4's symptom→remedy table, 2ee0d49)
- [x] Validate: `claude plugin validate aiya --strict` passes; headless probe of one skill
      (both passed; validate re-run by the coordinator, no warnings)
- [x] Rule on escalated default (1) branch/PR mechanics — ruled 2026-08-15, and the discussion grew
      into an architecture ruling: git/PR is not an essential dependency but one backend of two roles
      (durable record / review surface), shipped as three backends (github / gitlab / local); the
      swap point is a Turn — the Turn-definition *count* is not a contract, the Turn common contract
      is; roles regroup into three families (generate / verify / run-keeping = brief + record); a new
      record role (`turn-record-{github|gitlab|local}`) owns all platform operations (branch/PR at
      `on`, wave-settle commit after brief, gate commits and `gm` comment fetch, `dn` sweep); only
      record ever commits, at wave granularity, so every commit is a complete resume point — (1)'s
      branch/PR timing is absorbed into record-github
- [x] Amend `aiya/docs/design.md` to carry those rulings (implementation expert), push, and take the
      user's review on the PR (applied in b1a1237; approved 2026-08-15, "設計改訂はOK")
- [x] Ripple the amended design into the build: conductor skill, agents (add turn-record adapters),
      entry skills, README mode note (implementation expert; applied in 117fe57, validated strict,
      coordinator reviewed every hunk)
- [x] Rule on the remaining escalated defaults — (2) where approved versions (G1-v1) are recorded,
      (3) `disable-model-invocation` on the five entry skills — and apply the rulings (ruled
      2026-08-15: (2) a `version: vN (YYYY-MM-DD HH:MM:SS)` header line written and bumped by
      Turn(generate) — no Conductor ledger, no record stamping — with record-local archiving approved
      editions into `history/` at gate resolution, applied in 21f0b16 + d5586b8; (3) all five entry
      skills keep `disable-model-invocation: true`, contract recorded in design §2 in 58c336c)
- [x] self-check (record OK/NG per criterion in `.rn/20260813-aiya/checks/4.md`) — written by the
      implementation expert, all three criteria OK; review columns await the Verify round
- [x] Review round 1: all four experts ran 2026-08-15 (QA / Craft / Verification / Design) — 15
      mechanical findings triaged Valid and applied (5e56a18); install-instructions finding deferred
      to #5 (its whole purpose); remaining findings resolved into the ruled fix and pending rulings
      below
- [x] Apply the ruled gate-stop fix (implementation expert): ① conductor/on — the Conductor drafts
      the Plan, then dispatches Turn(record) to push it, then stops at the gate (no new machinery;
      Turn ordering only; ruled 2026-08-15 — the history/-universalization and approval-marker
      proposals were rejected: git backends read approval from git, `history/` stays local-only,
      approval needs no dedicated record); ② up — when "at the gate" vs "just approved" cannot be
      told apart from files, re-present the pending gate (safe side, costs one `ty`) (applied in
      ff609f4: conductor §3/§8/§9, on, up, design §4.4/§5.5/§4.5)
- [x] Take the remaining small rulings, one at a time: (i) README wording ×3 (Craft F13–15;
      owner-ratified text, needs approval) — round-1 texts were lost with the conversation, so
      re-derived by a README-scoped Craft scan: 14 findings, ruled 2026-08-15 as 11 apply / 3 reject
      (taste-level rewrites of ratified voice rejected), applied in 69331bc; (ii) whether the
      bare-`gm` comments file joins the Conductor's intake list (Design F5) — ruled 2026-08-15:
      yes, gate feedback (the `gm` line and the fetched comments file) becomes the sixth intake
      item, steering input not work content, applied in 7f09188 (conductor §1/§8, design §2/§5.7);
      (iii) softening the design's "new backend never touches the Conductor's procedure" claim
      (Design F6) — ruled 2026-08-15 as proposed (the loop stays untouched, but a new backend
      registers in the Conductor's detection roster), applied in 64122d2
- [x] Review round 2 (post-(iii); QA / Craft / Verification / Design, all four ran 2026-08-15):
      12 mechanical findings triaged Valid and applied (3b1e7b1); marketplace registration deferred
      to #5 (all four flagged it; it is #5's purpose); three findings escalated and ruled
      2026-08-15: (iv) elicit items are the Conductor's own — Plan items come in two kinds, the
      wall decides who carries each (ccb615a); (v) the no-nest wall is structural for the spawn
      tool, default-and-observable where Bash ships (182869f); (vi) G3's record dispatch is a
      final settle, the PR/MR stays open for the human — aiya never merges — and the dispatch-point
      count is uniformly five (32fc8ad)
- [x] Review round 3 (post-(iv)(v)(vi); all four ran 2026-08-16, all four overall PASS —
      Verification fully clean): 14 mechanical findings triaged Valid and applied (d741e39);
      remaining findings resolved into the two pending rulings below
- [ ] Structural rework, ruled 2026-08-16 (supersedes ruling (vii), which is withdrawn as
      piecemeal patching): the run's lifecycle state becomes a first-class design concept — one
      run-state file written by the Conductor at boundary events (`on`: backend + run branch; each
      gate verdict; `closed` at G3), committed by Turn(record) the same way the Plan is; the
      `backend` file is absorbed as one field of it; the term "backend" itself stays (ruled apt,
      Terraform-backend precedent). Diagnosis agreed with the user: post-sign-off judgments split
      into structure-derived (sound) vs invented-ad-hoc (gate-stop ②, (vi), (vii)) — the ad-hoc
      cluster all patches the same hole, boundary events leaving no record to derive from. Steps:
      (1) amend `design.md` to carry the concept — owner, home, write triggers;
      (2) re-derive **every** post-sign-off judgment from it — full audit: arch ruling (1),
      rulings (2)(3), gate-stop ①②, (i)–(vi), review rounds 1–3 — fixing any whose answer changes;
      (3) present the design revision at the gate for re-approval before rippling into the build
      (progress 2026-08-16: (1) applied in badd0c7; (2) audited — 7 changed answers fixed in
      0764c7e, 5 dispatch points and ruling (vi) unchanged; (3) presented on PR #19 — awaiting
      verdict; after approval the ripple includes up's run discovery via run.yaml, ex-`backend` file)
- [x] Whole-document restructure, ruled 2026-08-17 after the user judged design.md patchwork —
      diagnosis agreed: the spine (2 problems → 2 properties → 2 mechanisms) is sound but buried
      under contract material each review round appended in place, and the argument §1 opens is
      never closed. Six moves applied in a5ffde5, no decision removed: §2 carries the bet only
      (inventory → new §3.5 "What ships"); enforcement-strength consolidated (§2 defines once,
      §5.1 owns the no-nest scope and names its trace); §3.3+§3.4 merged into one table;
      §4.4's two monster paragraphs split by topic; backend/local quarantined to §3.4/§5.5;
      new §6 discharges the two properties. Observability/Trade-offs renumbered §7/§8, all 14
      cross-refs re-resolved. Net +365 words (the estimated −2,000 was wrong — the moves were
      placement, and §6 added 382); density is untouched and is the open question below
- [x] Density ruled 2026-08-19 (user): the document's job is understanding, not coverage — the
      essential thread is drowned by enumerated contracts, diagrams are scarce; "decisions kept"
      is withdrawn as the bar (many restated decisions are themselves the breeding ground for
      duplication and contradiction). New bar: few load-bearing principles stated once, with final
      decisions reading simply from them; contract detail that serves lookup lives in the shipped
      artifacts (checks/4.md's contract trace shows where), not restated in prose. Instrument:
      writ (né techting), alive on PR #15 (`origin/worktree-writ`) — its `/writ:up` build-fresh
      procedure, landing on `aiya/references/design.md`'s own seven-chapter shape (chapters 1–4
      story / 5–7 consulted reference; whole-in-one-diagram, one-diagram-one-claim), which
      design.md is declared the worked example of and currently diverges from
- [x] Rebuild `design.md` by the writ procedure (implementation expert); what-changed note to
      `checks/4-writ-note.md`; coordinator cross-checks the rebuilt document against checks/4.md's
      contract trace — every dropped clause either ships in the build or is named in the note
      (rebuilt in 486a1af: 10,612 → 7,269 words, 3 → 5 diagrams, seven-chapter shape restored;
      coordinator audited old vs new end to end — zero ratified decisions lost, all carried
      claims verified against the shipped files; note completed in 672778c with five added
      dispositions and the §4.3 goal-statement correction, flagged for the gate)
- [x] Refine design.md by the writ-feedback lens (directed in-console 2026-08-20): four findings
      fed back to writ as a PR #15 comment (whom-does-each-sentence-serve; fresh-reader check must
      be independent of the author; axis slots need per-reader justification; weight hierarchy);
      FB1/FB4 applied — 7,269 → 6,239 words, wrong-reader material cut or re-homed, every cut
      grep-verified into a shipped home (dispositions in `checks/4-refine-note.md`); FB2 run as
      designed — a zero-context reader read chapters 1–4 straight through, verdict YES, its four
      stumbles fixed; FB3 (format-side cuts) deferred to a future format ruling (edcf1b4)
- [x] Re-run the writ build-fresh procedure on `design.md` with the FB-updated writ (the PR #15
      feedback is now incorporated upstream) — directed at suspend 2026-08-22; if the document
      changes, the gate object moves to the new commit and the gate is re-presented (run
      2026-08-22: steps 1–10 a fixed point — the edcf1b4 refinement had pre-applied what the
      updated writ codifies, note in `checks/4-writ-rerun-note.md`, ca46a66; the new step-11
      fresh-reader trial then drove three fix rounds — 041413c, a14c010, b2712f2, 6,239 →
      6,448 words — purpose YES on all four trials; loop closed at the 3-iteration cap with
      two residuals flagged for the gate (§4.6 "structural" overclaim, UX/Design docs
      unanchored), 5555337; gate object moves to b2712f2)
- [x] Fix the eight round-4 residuals in the current document before rebuilding — directed by the
      user 2026-08-26 ("先に残課題を現行に反映したら？"), so the rebuild takes its intent from a
      corrected source and the comparison measures the procedure, not known defects. Ruled and
      applied in d7b63f9: R1 §4.6's "structural" overclaim; R2 the product's UX/Design documents
      given a home (§3.3, `docs/ux.md` / `docs/design.md` by default, redirected at the Planning
      Gate — chosen over a ledger row because they are per-product, not per-run); R3–R8 the six
      reader stumbles. Three further rulings taken in the same exchange: §3.3's write-side rule
      ("physical layout exactly once") replaced with `One directory per run:` — it served the
      document's author, not its reader; `run.yaml` → `state.yaml` (the directory already says
      *run*, the document's own term is *run-state*, and Terraform/Airflow/Temporal all use *state*
      for this with *status* as a field inside it); `references/ux.md` gains one line saying a
      screenless product's surface is its API or command vocabulary
- [x] Rebuild `design.md` from a blank page by the writ procedure in a subagent, into a separate
      file, then evaluate current vs. rebuilt from the purpose — directed by the user 2026-08-26,
      the honest re-run of the step-7 deviation disclosed in `checks/4-writ-rerun-note.md`. Done:
      the rebuild ran writ steps 1–10 blank-page into `checks/4-rebuild/design.md` (8,334 words)
      plus `note.md`; step 11 was then run as a **head-to-head** — the same fresh-context reader
      prompt, the ratified reader, neutral filenames — over the current document (d7b63f9, 6,557
      words) and the rebuild, recorded in `checks/4-rebuild/trials.md`
- [x] Write the comparison evaluation from the purpose to `checks/4-rebuild-eval.md`, push, and put
      the adoption question to the user on PR #19. Written and pushed in a3324b2; question posed on
      PR #19. Two things the writing changed from the evidence as summarized: (a) the re-run is
      **not** a clean measurement of the writ procedure — the rebuild's own step-9 disclosure has it
      drafted directly after a full read of the current document (127 shared 8-token spans, reduced
      to a 7.3% identifier-only residue), so it answers "is this document better", not "does
      blank-page writ produce a better document"; (b) `trials.md`'s claim that the +1,777 words are
      contract detail does not survive measurement — per-chapter counts show uniform +17–59% growth
      with §5 taking 23.6% of it against a 24.9% share, so the trade is density-vs-ambiguity, not
      prose-vs-contracts. Recommendation recorded: keep the current document, port P1–P4; ten
      design-level findings (six raised independently by both readers) survive either adoption and
      need their own disposition; R3 and R1 need re-ruling — awaiting the user's verdict
- [ ] Re-run the rebuild once writ is strengthened, then settle adoption on the result — ruled by the
      user 2026-08-30: writ exists to produce the document, so an output that loses is writ's defect,
      not grounds for hand-patching the current document; "keep doc-A and port the wins" is withdrawn
      as the recommendation. Six procedure gaps the head-to-head exposed were fed to the writ session
      as a PR #15 comment (blank-page carryover unmeasured; no status pass over the input, which is
      why the pending run-state design was dropped whole; step 11 patching subject defects as prose,
      which is how R3 backfired; a delivery gate that has never opened; a fill with a drop rule and
      no add rule; the five axes unable to express the ratified article+reference shape). The
      adoption question posed on PR #19 is held open until writ responds; the rebuild is then re-run
      and the result adopted or rejected on its own merits (writ responded 2026-08-30 in 4787745 —
      five findings taken, the length measure declined as D-10; re-run done in 46833b3. **The
      measurement is clean this time**: writ's new step-10 carryover item failed the first render at
      177 spans / 70.87% and forced a rebuild from meaning, ending at 6 spans / 0.64%, so round 1's
      effort-3 win is void — it was measured on a document carrying most of its predecessor's
      phrasing. Round 2 is the first honest comparison and it is a tie: both QUALIFIED, both
      effort 4, the rebuild 43% longer. Recommendation written to `checks/4-rebuild2-eval.md` —
      **adopt neither**, because the single change all four readers across both rounds prescribe,
      "put the discharge at the front", is one neither document may make: `aiya/references/design.md`
      assigns chapter 1 the properties and their discharge to no chapter, and says chapter 5 holds
      format definitions while both documents defer every schema out of it. Two format defects, each
      confirmed by readers on two independently-written documents. Question posed on PR #19: fix the
      format, then rebuild once against it and settle adoption there — awaiting the verdict. Five
      writ findings sent to PR #15). **Superseded in-session 2026-09-01 by the user's ruling**: do not
      fix the format by hand — fix writ, then re-apply. Diagnosis that carried it: writ *detected* the
      heading break in all three trial rounds and could not act, because step 3's slot-by-slot test is
      subtractive only — every verdict it can return is "keep the slot" or "drop it / raise a conflict
      and proceed", with none for "the reader needs a slot this format has not got". Routing the format
      defect through writ rather than a hand edit is what the user's standing principle requires. Two
      further findings recorded: writ's own article axis (question → substance → closing) disagrees
      with its own ceiling ("conclusion first"); the composite's parts were not separable. Consolidated
      round-3 feedback written to `.rn/20260813-aiya/writ-feedback-3.md` (42f3cfe), posted to PR #15,
      and **delivered directly to the writ session** `techting-bb` (worktree `.claude/worktrees/techting`,
      branch `worktree-writ`) 2026-09-01

- [ ] Re-run `/writ:up` on `design.md` once writ has taken the round-3 feedback, and settle adoption on
      that result — same protocol as round 2 (blank page, subagent, separate file, head-to-head against
      the current document with the verbatim prompt now fixed in `checks/4-rebuild2/trials.md`).
      `aiya/docs/design.md` stays at `d7b63f9` until then and is not hand-patched. The targeted
      re-review of the round-2/3 fix sites waits for this too — running it against a document about to
      be rebuilt would be wasted

- [ ] Take the verdict on the design revision — run-state file (badd0c7 + 0764c7e), restructure
      (a5ffde5), the writ rebuild (486a1af), and the noise refinement (edcf1b4) — on PR #19
- [ ] Adopt the grilling interview method (mattpocock/skills, `skills/productivity/grilling`) as
      the elicit-item procedure — ruled 2026-08-22, relentlessness kept deliberately: both AI and
      humans run optimistically past ambiguity, which is exactly what Purpose elicitation must not
      do. Specify in conductor §7 (the "Interview the human at the chat surface" sentence, the
      one unspecified how): design-tree / frontier / rounds, numbered questions each with a
      recommended answer; a frontier question needing a fact becomes an investigation Step on the
      Plan (never the human's homework, never the Conductor's own digging — aiya-native form of
      grilling's sub-agent rule); termination = frontier empty and intent decidable. Delivery ruled
      2026-08-22: curation, not an external-plugin dependency — the method is adapted into
      conductor §7 with attribution (mattpocock/skills, MIT — license confirmed), because aiya
      must stand alone (#4 completion criterion), no plugin-dependency mechanism exists, and the
      sub-agent rule needs the wall-conforming rewrite anyway; design.md carries at most one
      sentence (density bar). Apply after the PR #19 verdict so the pending gate object stays
      stable
- [ ] Take ruling (viii) — README-touching fixes (owner-ratified text, needs approval, not yet
      presented): README:161 "Exactly two things" vs design:462's third local degradation (drafts
      leave no history; mirrors design:148, CHANGELOG:12); README:59 "the PR" used before any
      backend/PR antecedent; README:22-27 mermaid shows five human touchpoints against the text's
      six checkpoints (Delivery Planning Gate missing). Apply on approval
- [ ] Targeted re-review of all fix sites from rounds 2–3, rulings (iv)–(vi), the structural
      rework, and ruling (viii), then fill the review columns in `checks/4.md`

**Completion criteria**:

- Every contract in the approved design is present in what ships, and a third party can trace each one
  back to the design it came from.
- The plugin stands on its own: driving it end to end needs nothing it does not ship.
- No superseded decision survives anywhere in it.

### #5: Make it installable by someone else

**Purpose**: Put aiya where another person can get it and have it work.

**Prerequisites**: #4.

**Steps**:

- [ ] Agree this task's work steps with the user, then replace this line with them.
- [ ] self-check (record OK/NG per criterion in `.rn/20260813-aiya/checks/5.md`)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing)
- [ ] Verification expert review (subagent, fact-check)

**Completion criteria**:

- Both strict validations pass with no warning, on output a third party can re-run.
- Everything that describes aiya to a prospective user describes the plugin that actually ships, and
  every path a reader can follow to it resolves.

### #6: Prove the purpose is reached

**Purpose**: Run aiya on real work and show the four purpose criteria hold. This is the point of the
whole build.

**Prerequisites**: #5.

**Steps**:

- [ ] Agree this task's work steps with the user, then replace this line with them.
- [ ] self-check (record OK/NG per criterion in `.rn/20260813-aiya/checks/6.md`)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing)
- [ ] Verification expert review (subagent, fact-check)

**Completion criteria**:

- Each of the four purpose criteria is backed by evidence from the run that a third party can open and
  re-read.
- The work aiya produced meets its own acceptance criteria, with any shortfall recorded as a delta
  rather than omitted.
- `dogfood/result.md` distinguishes what was measured from what was only asserted, and states what was
  not covered.

### #7: Evaluation sign-off

**Purpose**: Take the user's sign-off on the Acceptance criteria run — the session's closing gate.

**Prerequisites**: #6.

**Steps**:

- [ ] Present the Acceptance criteria run result to the user and take the verdict via `/rn:ty`
      (approve → session closes) or `/rn:gm` (revise → address the feedback, re-present).

**Completion criteria**:

- The Acceptance criteria run is approved by the user.

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**: -
- **Last completed**: -
- **Next**: -
- **Notes**: -
