# Rule inventory — what `rn` states, and what happens when it is broken

**`rn` ships one line of machinery, and it guards one property.** Of the 254 normative statements in
its 8 reference files and 5 skill files, 61 are enforced and 193 are not. The plugin contains no
executable code: `find rn -type f` returns 17 files, sixteen Markdown and one JSON, none of them
executable (`find rn -type f -perm -u+x` returns 0), and there is no hook, no script, no validator
and no CI step anywhere in it. The one exception is a declaration rather than code —
`disable-model-invocation: true`, a line `rn` writes in each skill's own frontmatter, which the
harness acts on (rows 208, 212, 226, 237, 244). It stops the model invoking a command skill, and
nothing else. Every other enforced row borrows its mechanism: a `git` or `gh` command failing, or a
named reader the flow puts in front of the artifact — the user at a scheduled gate, the user meeting
the result of a command they typed, the PR thread's reviewer, or a later `rn` step. Those are set
out with their row ids under "The enforced set" below, and they are the whole of what catches a
breach.

The 193 unenforced rows are this document's product: the definite list task #2 works from, grouped
under "The unenforced set" by *why* nothing catches them, because the groups need different repairs.
The two largest groups hold 68 of the 193 between them. Thirty-five rows produce something a user
can see and give no one an occasion to check it against the rule; twelve of the thirteen rules in
`status-display.md` sit here. Thirty-three more are the review chain's own internals, which live in
prompts that are never written to disk. A tenth group, U10, holds the 27 rows that name a real
reader whose own step is one nothing records having run.

## The verdict vocabulary

Three verdicts. Each has a test, and a row gets the verdict whose test it passes — never the one
whose shape it resembles. They are this session's plan vocabulary made precise: `steering.md` asks
of each rule "visible on breach / stops the flow / neither", and **recognized** is *visible on
breach*, **refuses** is *stops the flow*, **unseen** is *neither*.

- **refuses** — something other than the agent declines to proceed. *Test: if the agent set out to
  break this rule, would something outside it decline anyway?* Only two things ever answer yes: an
  external command exits non-zero or an API rejects the call, and the harness blocking a skill
  invocation. A stop that arrives because the agent asked and then ended its turn does **not** pass:
  that is the agent complying, and a rule cannot be enforced by the agent choosing to obey it.
- **recognized** — a breach reaches a reader who would tell it from compliance. *Test: name three
  things — (1) the reader, a person or a later `rn` step; (2) the artifact the flow **makes** them
  open; (3) what in that artifact differs between compliance and breach, legible without auditing
  against a rule the reader is not holding.* Each of the three is called a **leg** below, cited as
  leg (1), leg (2), leg (3); all three must be nameable, and a row that cannot name one is `unseen`.
  "It is in a message the user can see" fails legs (2) and (3): the user opens the message to answer
  it, not to audit it, and has no copy of the rule to audit it against. Two refinements recur and are
  applied uniformly here. On leg (1), the reader must be someone other than the breaching party —
  an agent reading its own output is not a second reader, which is why row 42 fails on the same
  `git status` it runs itself. And, on leg (2), a message qualifies as the artifact in exactly one
  case: when it answers a command the user has just issued and states what is about to be done in
  their name, so that only they can tell it from a breach (rows 240, 246). A message they merely
  receive in the ordinary flow does not.
- **unseen** — everything else. This is where a rule that is *stated and nothing more* lands, and
  also where two things land that used to look like mechanisms: a stop that needs the agent's
  compliance, and text a reader could in principle audit but has no occasion or standard to audit
  against.

**Enforcement is transitive.** A row is `recognized` only if the reading it names is itself
guaranteed to happen. Where the only reader is an `rn` step this document rates `unseen`, nothing
says the reading occurred, so the row inherits `unseen`. The alternative — a conditional tier,
"enforced *given* step N runs" — was rejected because task #2 needs one list of rules that need a
mechanism, and a rule whose mechanism is a step nobody can tell ran needs one exactly as much as a
rule with no mechanism at all. The chain stops at three anchors, where the reading is done by
someone `rn` does not instruct: the PR thread's reviewer returning to their own thread; the user
meeting the result of a command they themselves typed; and the user at a scheduled gate, which ends
the assistant's turn and hands them an artifact already on the PR. Whether a gate was *placed* is a
separate rule with its own row (12, 14, 15, 93, 94) and is not folded into the rows the gate reads —
folding it in would resolve every verdict here to "nothing forces the agent to run `rn` at all".
Applying this to a fixed point moved 27 rows out of the enforced set; they are listed as **U10**,
where the repair is to make the reader's step leave a trace rather than to find a reader.

Two further words are used throughout in one sense each, and nowhere in the other's:

- **enforced** — the union of `refuses` and `recognized`. The mechanism may sit anywhere; it need
  not belong to `rn`.
- **self-enforced** — enforced by machinery `rn` itself ships. Nothing in `rn` is self-enforced.

## How this was built

Each of the 13 files was read end to end and every line that tells a reader what must, must not,
should, always, or never happen was extracted — table rows, checklist items, and imperative bullets
included. Each rule is cited by `path:line` and quoted or tightly paraphrased. Where a row claims a
mechanism, that mechanism is quoted from the file that implements it, with its own `path:line`;
where no such line could be quoted, the rule is recorded as unenforced. Quotations are verbatim,
with two typographic exceptions applied throughout: a fragment broken across source lines is
rejoined, and a command or identifier the source leaves bare is set in backticks (a `|` inside one
is escaped as `\|` so the table renders).

Rules were also tested against what past sessions actually produced — the eight session directories
under `.rn/`, their `steering.md`, `rn/docs/design.md`, and the 41 `checks/*.md` files they hold —
not only against the rule text. Every "of 40" figure below is over the 40 past check files, this
session's own excluded, since a session still running has not yet had the chance to breach anything.
Several rules that read as enforced turn out to have been broken repeatedly with nothing noticing.

**Counts.** 254 normative statements. By file: 41 in `task-execute-workflow.md` (whose shared span
with `task-verify-workflow.md` is counted once — see that file's table below), 32 more in
`task-verify-workflow.md`, 36 in `planning-workflow.md`, 37 in `steering-template.md`, 13 in
`status-display.md`, 11 in `migration-workflow.md`, 16 in `design-template.md`, 26 in
`pr-feedback-workflow.md`, and 4 / 14 / 11 / 7 / 6 in `on` / `dn` / `up` / `ty` / `gm`. Row ids are
stable identifiers assigned in the order the rules were inventoried; rows 250–254 sit at the end of
their file's table rather than in source-line order; the index under "The unenforced set" gives
every row's `file:line`, so source order is recoverable from there. By verdict: **12 refuse**, **49
are recognized on breach**, **193 are unseen**.

## Per-file inventory

Sources are relative to `rn/references/` in the reference tables and `rn/skills/` in the skill
tables. Verdicts: **refuses** / **recognized** / **unseen**, per the vocabulary above.

### `task-execute-workflow.md` (179 lines)

Lines 6–136 of this file are byte-identical to lines 6–136 of `task-verify-workflow.md` — 131 lines;
`diff <(sed -n '6,136p' rn/references/task-execute-workflow.md) <(sed -n '6,136p'
rn/references/task-verify-workflow.md)` returns no output. Rows 3–26 therefore state the rules of
both files and are not repeated in the next table. Lines 1–5 differ between the two files: row 2's
sentence ("Run one task at a time.") stands verbatim on line 5 of each, but row 1's does not —
`task-verify-workflow.md:5` carries its own wording and has its own row in the next table.

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 1 | "`on` and `up` read both files at task execution, this one first" | :5 | unseen | No step in `on` or `up` records which files it read; a skipped read leaves no trace. `on/SKILL.md:17` and `up/SKILL.md:34` state the same ordering — that is the rule restated, not a check. |
| 2 | "Run one task at a time." | :5 | unseen | Fails at leg (3): two tasks run in the same stretch and both checked off leave the same `steering.md` as two tasks run in sequence. Only the case where the second is built and left unchecked leaves a difference, and its reader is the status block (row 146), which nobody audits. Nothing refuses it. |
| 3 | "Write check files under `{steering_dir}/checks/`." | :7-8 | unseen | No step reads back the path. Two past sessions wrote `checks/task-1.md` instead of `checks/1.md` and nothing surfaced it. |
| 4 | Coordinator "Writes directly **only** `steering.md` and `checks/{task-id}.md`; never edits the deliverable or its git history" | :14-15 | unseen | Git authorship does not distinguish coordinator from subagent, so a coordinator-authored deliverable change is byte-identical to an expert's, and the only reader of the diff is the coordinator itself. The history half would show as a changed SHA against the captured starting commit (`:175`), but that value lives only in the coordinator's context (row 39) and no step compares the two. Row 5 is the mirror-image rule and fails identically. |
| 5 | Implementation expert "Produces, fixes, and commits/pushes the deliverable" | :16-17 | unseen | Nothing records whether a subagent was dispatched. A coordinator that writes the file itself produces an identical commit. |
| 6 | "**QA expert** (every task) — subagent." | :18 | unseen | The check file has a `## QA Expert Review` section — 38 of 40 past files carry one — but nothing reads it, and the tasks whose files omit the one gating field were checked off regardless (row 26). |
| 7 | "**Design expert** (tasks that produce or revise structure/approach)" | :19-20 | unseen | Same as row 6; additionally "produces or revises structure/approach" is a judgment with no recorded answer, so an omission cannot even be identified as one. |
| 8 | "**Craft expert** (per medium: coding / writing / visual)" | :21-22 | unseen | Absent from every session before `20260625-rn-lean`; 29 of 40 check files carry no Craft section. Nothing noticed. |
| 9 | "**Verification expert** (per medium: test / fact-check / dry-run)" | :23-24 | unseen | 35 of 40 check files carry no Verification section; `20260705-improve-design-template` omitted it from all 7 tasks and closed approved. This is the second confirmed instance the session's Assumptions name — not the criteria failure in the Goal (rows 129, 116). |
| 10 | "All deliverable work (produce/fix/commit/push) goes to the implementation expert, every time, any size." | :26 | unseen | Identical to row 5: the commit is the same either way, and nothing records the dispatch. |
| 11 | "Each review expert runs as an independent subagent (Agent tool, no conversation history) and returns a compact summary." | :27-28 | unseen | Nothing records whether the Agent tool was used or whether history was passed. A coordinator role-playing the review produces the same check-file text. |
| 12 | "The user signs off at exactly **three** scheduled gates, never on any other task" | :32 | unseen | An extra gate is a message on the user's screen; a missing one is a task that closes without them. The user is the reader — but only if they notice, and nothing flags it. Fails the recognition test at leg (3): the user has no copy of the three-gate rule, so an extra ask reads as an ordinary question and a missing gate reads as smooth progress. 7 of 8 sessions ran without the Design gate and nobody remarked on it. |
| 13 | "**Plan gate** — the draft-PR plan approval in `on` before any task runs." | :34 | recognized | The gate ends the assistant's turn — but only because the assistant asked, so that is compliance, not a refusal. What is recognized is the breach: if task #1's work lands on the PR before the plan is approved, the user opens the PR at the gate and finds commits they never cleared. Reader: the user; artifact: the PR the ask points them at; difference: work that predates their verdict. `planning-workflow.md:51` states the rule as "**CRITICAL: DO NOT proceed without explicit user approval.**" and states nothing that would decline on its behalf. |
| 14 | "**Design gate** — sign-off on the approach / key decisions before they are built on" | :35-37 | unseen | Realized as a Design sign-off task (`planning-workflow.md:36`) whose absence would show as a gap in `steering.md`'s task list, which `status-display.md:17` re-derives at every stop. Fails at leg (3): the task is absent from 7 of the 8 session directories under `.rn/` — `.rn/20260830-issue-17` (`### #3: Design sign-off`) is the only one that has it — and no user, at any gate, ever asked where it was. Nothing holds the task list up against `planning-workflow.md:36`. |
| 15 | "**Evaluation gate** — the end-of-session run of the `steering.md` Acceptance criteria" | :38-39 | unseen | Backstopped only by `task-verify-workflow.md:219-222` (row 71), which is itself `unseen`: a session that closes without the escalation closes quietly, and nothing records that the backstop ran. It has never been exercised — every session governed by the rule placed the task (row 94). |
| 16 | "the assistant never records a verdict the user did not issue" | :41-42 | recognized | For a sign-off task the record is the `steering.md` check-off (`task-verify-workflow.md:208`). Reader: the user at the next gate; artifact: `steering.md` on the PR, which the gate makes them open; difference: a sign-off task standing checked off against a verdict they know they never issued. For a plan gate there is no record at all (row 241), so that half reaches nothing. |
| 17 | "The per-task boundary is **not** a user gate for ordinary build tasks" | :44-46 | unseen | Stopping anyway puts an unrequested ask on the user's screen. Nothing prevents it. Fails at leg (3) — the same reason as row 12. An unrequested stop is a question the user answers, not a breach they identify. |
| 18 | Escalation is "a separate always-open channel — not a gate; an escalation message opens with the session-status block" | :47-49 | unseen | A *missing* escalation leaves nothing behind — that is the whole failure mode. The status-block half is visible (row 12's reader) only when an escalation is actually sent. |
| 19 | "QA always spawns for a task that builds something; a sign-off task spawns none. Craft and Verification spawn for the task's medium. Design spawns only when the task produces or revises structure/approach." | :53-57 | unseen | See rows 6–9. The per-task judgment is never written down, so neither its result nor its omission is recoverable. |
| 20 | The three build-task instances — Code, Docs, Visual — each run the same chain (paraphrase; the file spells the medium out per instance, e.g. "Self-check → QA → Craft (coding) → Verification (test) → coordinator review → check-off") | :59-64 | unseen | Same as row 19. Empirically the Verification link was simply dropped for a whole session. |
| 21 | "**Sign-off task** (instance): no axes spawn … It skips Phase: Execute and Phase: Verify entirely … take the verdict via `/rn:ty` … or `/rn:gm` … no check-off until later approved" | :65-71 | recognized | The verdict cannot be self-issued as a *command*: the five skills carry `disable-model-invocation: true` (`ty/SKILL.md:4`, `gm/SKILL.md:4`), so the assistant cannot invoke `/rn:ty`. It can still write "approved" in prose — which is why this is recognized rather than refused. Reader: the user; artifact: `steering.md` on the PR and every later status block; difference: a sign-off task checked off against a verdict they never issued. |
| 22 | "Self-check is produced in Execute … reviews run in Verify; the coordinator's independent review then clears the task" | :73-75 | unseen | Ordering is unrecorded; the check file bears no timestamps and nothing compares it to the commit graph. |
| 23 | "the implementation expert writes **only** the Completion Criteria Self-check and Evidence columns (and the Overall Verdict "Self-check" line)" | :79-81 | unseen | The coordinator fills the remaining columns afterwards (`:83-84`) and would find them pre-filled — but that filling is row 63 (`task-verify-workflow.md:191-192`), itself `unseen`: nothing records that the coordinator opened the check file. The only reader is a step nobody can tell ran. |
| 24 | "Column ownership holds across every round, including fix rounds" — the expert writes "never the review-verdict sections (QA / Expert Review / other Overall-Verdict lines and QA columns, which are the coordinator's)" | :79-83 | unseen | Row 23's reader, and row 23's cap. |
| 25 | "The expert does not commit it. The coordinator … commits the file as part of its ledger — on the post-Verify steering check-off commit." | :82-84 | unseen | The expectation is stated — `task-verify-workflow.md:140-143` expects `git status` to show "**only** that tracked check file" — but the step that holds it is row 42, `unseen`: nothing records that the coordinator ran `git status` or read what came back. |
| 26 | The check-file format block — five columns, `## QA Expert Review`, three expert sections, `## Overall Verdict` with five verdict lines and `Ready to check off` | :86-135 | unseen | Looked for a step that opens a check file and compares it to this block: there is none. 39 of 40 past check files carry the `## Overall Verdict` heading, but 24 of 40 omit its `Ready to check off` line, and every one of those tasks was checked off. That line is the only field any other file claims to gate on — see row 162. |
| 27 | The work-order must "include everything it needs and only that, with these 7 elements" | :139-140 | unseen | The work-order is a prompt; it is never written to disk and no artifact records what it contained. |
| 28 | Element 1 Task — "Purpose, Steps, Completion criteria copied from `steering.md`" | :141 | unseen | Same as row 27. A paraphrased or truncated copy is indistinguishable afterwards. |
| 29 | Element 2 Scope — "stay within this task; do not start adjacent tasks; name the files expected in play" | :142 | unseen | Out-of-scope files land in the committed diff, and `task-verify-workflow.md:146` tells the coordinator to "Confirm the change matches the task's scope" — but that confirmation is row 44, `unseen`, and writes nothing. The reader is a step with no trace. |
| 30 | Element 3 Method — "apply the task's Verification method as you build, not only after" (test-first / verify-each-claim-as-drafted / trace-as-built) | :143-147 | unseen | Nothing distinguishes verifying as you write from verifying afterwards, or from not verifying. Element 5 asks the expert to *confirm* it applied — self-report, not evidence. |
| 31 | Element 4 Best practices — Craft always; Design "when the task produces or revises structure/approach" | :148-152 | unseen | Same as row 27. |
| 32 | Element 5 Self-check — verify each completion criterion OK/NG with specific evidence, and confirm the Method was applied (coverage measured / every claim checked / flow traced) | :153-157 | unseen | The written self-check is read by the coordinator, which fills the QA column beside it (`:83-84`) — row 63's act, itself `unseen`. Its quality is unchecked besides: nothing compares Evidence to the artifact. |
| 33 | Element 5 — write to `{steering_dir}/checks/{task-id}.md` filling **only** the self-check columns; "Never write or overwrite the review-verdict sections … on every round, including fix rounds" | :157-161 | unseen | Row 23's reader, and row 23's cap. |
| 34 | Element 5 — "**Do not commit the file.**" | :161 | unseen | Row 25's mechanism, and row 25's cap: `task-verify-workflow.md:140-143` expects the check file to be the one uncommitted change, and row 42 records nothing about whether that expectation was ever held up. |
| 35 | Element 6 — "stage the deliverable paths explicitly (`git add <path>…`); never `git add -A` or `git add .`" | :162-163 | unseen | A stray file would appear in the diff the coordinator is told to read (`task-verify-workflow.md:139`, `:146`) and in the PR — but rows 41 and 44 are `unseen` and no reader is assigned to the PR diff. Nothing detects the *staging command* itself in any case. |
| 36 | Element 6 — plain conventional message; "the message must **not** contain `complete task #`"; push; "**never force-push**" | :163-165 | recognized | Real downstream consumer: `up/SKILL.md:26` — "A commit matches a task when its message contains `complete task #{id}`; check that task off". A breach silently checks off the wrong task. Three commits in this repo's history carry the substring in a body without being markers: `4daf6b2` ("forbid 'complete task #{id}' in a suspend-time commit"), `893de07` ("- Commit type is now conditional ({type}: complete task #{id}); hi matches") and `de0b1ec` ("so this is wip not 'complete task #3'"). The breach is demonstrated and the consumer is demonstrably fooled. Force-pushes surface as events on the PR timeline; nothing in `rn` checks. |
| 37 | Element 6 fallbacks — cannot push → say so and leave the commit, coordinator pushes; cannot commit → say so, coordinator commits mechanically with explicit paths and a plain message, "content stays the expert's" | :166-171 | unseen | Depends entirely on the expert self-reporting the failure. A silent failure leaves the work uncommitted, which the coordinator would meet as an empty diff — visible only in that one case. |
| 38 | Element 7 Return — "a compact summary only … Do not paste full file contents or trial-and-error." | :172-174 | unseen | Fails at legs (2) and (3): the coordinator is handed the summary rather than sent to compare it against a length bar, and no bar is stated. Contrast row 202, where the summary's named fields are what `pr-feedback-workflow.md:128-134` checks the result against; compactness is consumed by nothing. The cost is context, and it is spent before it can be judged. |
| 39 | "**Capture the task's starting commit** — current `HEAD` … Capture it **once**; do **not** re-capture on fix rounds." | :175-176 | unseen | The value lives only in the coordinator's context. A re-captured or lost SHA silently narrows the cumulative diff at `task-verify-workflow.md:144-145`, hiding earlier rounds from review. |
| 40 | "**Dispatch the implementation expert** with the work-order and wait for its summary." | :177 | unseen | See rows 5 and 10. |
| 251 | "Once the expert returns, continue to `task-verify-workflow.md`." | :179 | unseen | The hand-off from Execute to Verify. Nothing records that it was taken: a task whose reviews never ran produces a check file with its review-verdict sections still empty, and nothing reads those sections (row 26). |

### `task-verify-workflow.md` (222 lines)

Lines 6–136 carry rows 3–26 above, and line 5's shared sentence is row 2. Listed here: this file's
own line 5, its Phase: Verify, and its Phase: Complete.

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 41 | "**Read the committed diff yourself.**" | :139 | unseen | The step that group C's coordinator readings all rest on, and nothing records that the coordinator read anything. |
| 42 | "Expect `git status` to show **only** that tracked check file — that is normal, not a deliverable change." | :140-143 | unseen | `git status` is run and its output is on the coordinator's screen, but the coordinator is also the party this expectation binds, so leg (1) has no reader other than the breaching one. Row 41, the adjacent bullet of the same step, fails identically. The same lines do enforce rows 25 and 34, where the breaching party is the expert and the coordinator is a genuine second reader. |
| 43 | "Inspect the committed deliverable: `git show <sha>` … or `git diff <task's starting commit>..HEAD`" | :144-145 | unseen | Depends on row 39's SHA, which lives only in context; a wrong or missing starting commit silently truncates the diff. |
| 44 | "Confirm the change matches the task's scope and Completion criteria before spending review experts." | :146 | unseen | Looked for an artifact this confirmation writes. The check file's columns are the coordinator's only writable surface (`task-execute-workflow.md:79-84`) and none of them records a pre-review scope judgment, so a task where the confirmation happened and one where it did not enter Verify identically. |
| 45 | "**Dispatch the review experts as independent subagents** — QA always; Craft and Verification for the task's medium … Design when the task produces or revises structure/approach. Build each review prompt with 6 elements" | :147-149 | unseen | See rows 6–9 and 19. The empirical record is that whole axes went missing for entire sessions. |
| 46 | Element 1 Role — review "**adversarially** … assume defects exist and try to break the artifact (boundaries, error paths, integration, missed cases)" | :150-152 | unseen | The prompt is never written to disk. A friendly review and an adversarial one return the same shape of summary. |
| 47 | Element 2 Artifact — "the full content or diff under review." | :153 | unseen | Same as row 46. A review given a partial artifact returns a confident verdict about the part it saw. |
| 48 | Element 3 Criteria — "the expert checklist below." | :154 | unseen | Same as row 46. |
| 49 | Element 4 — "the task's Completion criteria copied **verbatim** from `steering.md`" | :155 | unseen | Same as row 46. "Verbatim" is unverifiable after the fact. |
| 50 | Element 5 Output format — "OK/NG per criterion with concrete evidence, plus an overall pass/fail" | :156 | unseen | The returned summary is on the coordinator's screen and is to be transcribed into the check file (`:192`) — row 63, `unseen`. Nothing consumes the summary's *shape*, which is what this rule prescribes. Contrast row 202, whose named fields are what `pr-feedback-workflow.md:128-134` checks the result against. |
| 51 | Element 6 Neutral framing — "**Never** pass the self-check file …, the implementation expert's summary, or any OK/NG verdict; do not defend the choices or hint at the verdict you expect." | :157-159 | unseen | The review-independence rule, and the least observable in the file: a primed review is indistinguishable from an independent one in its output. |
| 52 | QA checklist — "the verification approach is meaningful to the actual objective … no rubber-stamped or purpose-mismatched check" | :162-163 | unseen | Looked for a reader of the reviewer. The check file records the reviewer's verdict (`task-verify-workflow.md:191-192`) but never the checklist it was given, and the review prompt is never written to disk (row 46). A reviewer that ignored the checklist returns a summary of the same shape. |
| 53 | Design checklist — "does the approach/structure fit; separation of concerns; system-wide integrity (interface contracts, API compatibility, cross-doc consistency)" | :164-166 | unseen | Same as row 52 — and the verbatim duplication between this file and `task-execute-workflow.md` survived every Design review that has ever run. |
| 54 | Craft checklist — coding: "naming, error handling, null/thread safety", no duplication, style consistency; writing: "prose clarity and correctness, consistency with the doc's existing voice/terminology"; visual: notation clarity | :167-170 | unseen | Same as row 52. |
| 55 | Verification checklist — test: "meaningful and in GWT (Given/When/Then) format" covering edge cases; fact-check: "every claim/reference verified against its source, no unverified assertion stated as fact, and completeness of claim coverage"; dry-run: trace every step/branch | :171-175 | unseen | Same as row 52 — and this checklist was never run at all in the majority of past tasks. |
| 56 | "**Triage every finding.** Each ends in exactly one of" Valid / Invalid / Escalation | :176 | unseen | Fails at leg (1): the comparison that would catch a dropped finding — the review summary against the check file — is assigned to nobody. `:191-192` says to record the verdicts; no step says to reconcile the record with what came back. |
| 57 | "**Valid** → fix it. Dispatch the implementation expert (fresh subagent) — every deliverable-touching fix, no matter its size, including minor improvements." | :177-178 | unseen | Fails at leg (1), like row 56: an NG that never turned into a commit and an NG that was fixed both leave a check file with an NG in it, and nothing walks from the finding to the diff. |
| 58 | Reuse the original work-order; "point it at the current on-disk state to build on (not regenerate)"; fix commits accumulate, "never force-pushed" | :179-181 | unseen | A regenerated file would show as a wholesale rewrite in the fix commit's diff, but that diff's only assigned reader is row 41, `unseen`. Force-push shows on the PR timeline; no `rn` step reads it. |
| 59 | "re-run the same review expert; if the fix could affect a dimension another expert already cleared, re-run that expert too. Cap at 3 iterations … valid findings still NG after 3 → record them and escalate" | :181-183 | unseen | Iteration count lives only in the coordinator's context. Past check files narrate "Round 3 (final, cap reached)" as prose — a report, not a check. |
| 60 | "**Invalid** → reject it, citing evidence. Invalid **only** when it rests on a factual error or falls outside a scope boundary written in the Completion criteria — cite the specific fact or criterion." | :184-185 | unseen | Fails at leg (2): the rejection is readable only if it was written into the check file's Evidence column, and no step requires that. Nothing then reads it against the Completion criteria the bar cites. |
| 61 | "Escalate **only** when the decision is genuinely the user's … "It's minor, so I'll just ask" is not a reason." | :186-189 | unseen | Fails at leg (3): the user holds no escalation bar, so an over-escalation reads as diligence. Under-escalation is worse — a decision taken silently leaves nothing to read at all. |
| 62 | "Never silently drop, blindly accept, or bounce a finding for lack of a standard." | :191 | unseen | The failure mode is the absence of an artifact. Searched the 40 past check files for any record of a finding that was raised and then dropped: the `## QA Expert Review` and expert sections carry verdicts per aspect, never the findings behind them, so there is no place a dropped one would have been. |
| 63 | "Record the review verdicts into the check file." | :191-192 | unseen | Fails at leg (2): the check file is committed onto the PR (`:83-84`), but no reader is directed to it and no step gates on what it says — row 26's record is the proof. |
| 64 | "**Escalation is an always-open channel, not confined to triage.**  … raised to the user **immediately, wherever it surfaces** … never deferred to a gate … a change to the agreed plan or design cannot ship unseen. Wherever it fires, open the escalation message with the session-status block" | :194-200 | unseen | The failure mode is silence. A change that shipped unseen is by definition not visible; only a later reader of the diff could find it, and no step asks anyone to look. |
| 65 | "There is no per-task user gate for a normal task: once Verify clears … the coordinator checks the task off directly." | :204-206 | unseen | Row 12's reader. Same as rows 12 and 17: the user answers an unexpected ask rather than recognizing it as one. |
| 66 | "**Check off steering.** With Verify cleared … check off the task in `steering.md` directly." | :208-209 | recognized | Real consumer: `task-verify-workflow.md:215` (row 69) begins "the next unchecked task" from this state, and that step answers to the user at the Evaluation gate. An unchecked completed task is re-run; a wrongly checked one is skipped. `status-display.md:17-22` derives its ✅/👉/⬜ block from the same check-offs but nobody audits the block (row 146). Note this step does **not** read `Ready to check off` — see row 26. |
| 67 | Commit the check-off as "`{type}: complete task #{id} — {description}`", then push to the session PR | :210-212 | recognized | Consumed by `up/SKILL.md:26`'s grep. A malformed marker means the task is not re-checked-off on resume. |
| 68 | "This is the one completion marker for the task: deliverable commits carry plain messages; only this check-off commit carries the `complete task #{id}` substring. Keep that exact substring regardless of the prefix." | :212-214 | recognized | Same consumer as row 67 — and demonstrably fooled twice over. The substring test is a prefix test: `git log --all --grep='complete task #1' --oneline \| wc -l` returns 16, of which 7 are other tasks (`#1b`, `#10`, `#11`, `#12`, `#13`, `#14`, `#16`). And three commits carry the substring in a body without being markers (row 36). |
| 69 | "**Advance.** Begin the next unchecked task immediately — a sign-off task goes straight to the gate … any other task begins at Phase: Execute" | :215-217 | recognized | Reader: the user at the Evaluation gate. Artifact: `steering.md` on the PR, which `task-verify-workflow.md:217-219` lets the session close from only when "no unchecked tasks remain". Difference: a session presented for its final sign-off with a task still ⬜. `status-display.md:49-50` renders the same gap at every stop, but nobody audits a status block (row 153), so the gate is what carries it. |
| 70 | "If no unchecked tasks remain and the Evaluation sign-off was approved, the session closes — open that session-close report with the session-status block" | :217-219 | unseen | Row 12's reader. Fails at leg (3): a session that closes without the report closes quietly, and a report that omits the block is still a report. Nothing re-reads a sent message. |
| 71 | "If no unchecked tasks remain and no "Evaluation sign-off" task was ever encountered … that is a planning defect … escalate to the user immediately … do not close the session silently." | :219-222 | unseen | Fails at leg (3): the breach is a session closed silently instead of escalated, and a user receiving a close report holds no copy of this rule to miss the escalation against. It is `rn`'s only cross-rule check and nothing checks it. Untested besides — the rule and `planning-workflow.md:37` both entered on 2026-07-01 (`2ddcafa`), and both sessions since have placed the Evaluation sign-off task, so it has never had an omission to catch. |
| 250 | "`on` and `up` read both files at task execution, this one second." — the counterpart of row 1, and the one line of the shared header that differs between the two files | :4-5 | unseen | Row 1's mechanism, in the other direction. `on/SKILL.md:17` and `up/SKILL.md:34` name the same order ("read `…/task-execute-workflow.md` then `…/task-verify-workflow.md`"), which restates the rule rather than checking it; no step records which file was read when, so reading this file first, or not at all, leaves no trace. |

### `planning-workflow.md` (51 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 72 | "Run once per session." | :6 | refuses | `gh pr create --draft` (`:44`) fails when the branch already has an open pull request, so a second planning run on the same branch is declined by GitHub before it can open a second session PR. The `steering.md` overwrite that precedes it is not declined by anything. |
| 73 | "Treat every user interaction as a proposal: lead with one concrete recommended option in plain language (no internal jargon), and proceed on confirmation." | :10 | unseen | Every such interaction is a message the user reads; a bare question or a jargon-laden one is on their screen. The user is the only reader. Fails at legs (2) and (3): the user reads the message to answer it, not to check its form, and holds no copy of the proposal rule to check it against. |
| 74 | "`AskUserQuestion` is fine when one option is your recommendation." | :10 | unseen | Row 73's reader, and it fails legs (2) and (3) with it. This one is a permission rather than an obligation, so the only breach is using `AskUserQuestion` with no recommendation in it — which reads to the user as an ordinary multiple choice. |
| 75 | "At a stop that instructs opening with the session-status block, the block precedes the proposal." | :10 | unseen | Row 73's reader, and it fails legs (2) and (3) with it. Block-before-proposal is an ordering the user has no reason to notice either way. |
| 76 | "Take it from the user's message or `$ARGUMENTS`; if neither is present, ask for it." | :12 | recognized | Not a stop: nothing declines if the assistant invents a goal instead of asking. Reader: the user at the plan gate; artifact: `steering.md`'s `Goal`, which the gate exists to have them approve; difference: a goal they did not give, legible to them without any rule in hand. |
| 77 | "Restate it as a clear, faithful understanding of what the user wants — capture full intent, never add scope or invent goals." | :12 | recognized | The restatement is put to the user and becomes `steering.md`'s `Goal`, which the user reads on the PR at the plan gate (`:47`). Invented scope surfaces there. |
| 78 | "If ambiguous, propose your restatement and let the user correct it. This restatement becomes `Goal`." | :12 | recognized | Same reader as row 77. |
| 79 | "The session lives at `.rn/{yyyymmdd}-{slug}/steering.md`, where `{yyyymmdd}` is today's date" | :14 | recognized | Reader: the user who typed `/rn:up`. `dn/SKILL.md:14` and `up/SKILL.md:17` discover the file with `git log … -- '*/steering.md'`; a wrong path makes it undiscoverable, so `up/SKILL.md:18-20`'s zero case reports "No steering.md found. Run `/rn:on` to start." to a user who knows a session exists. The date prefix is the weaker half — a wrong one only mis-ranks the candidate list, which reaches rows 214 and 229, both `unseen`. |
| 80 | Slug candidates: the current git branch, an issue reference in `$ARGUMENTS`, a kebab-case name from the goal | :15-17 | unseen | Looked for a consumer of the slug's derivation. `dn/SKILL.md:14` and `up/SKILL.md:17` consume the resulting path (row 79) and `status-display.md:37-38` renders it, but nothing reads which of the three candidate sources it came from. A slug invented outright resolves exactly like one taken from the branch. |
| 81 | "Propose one recommended slug plus the alternatives … When already on a non-default branch, recommend that branch's name as the slug." | :19 | unseen | The proposal is on the user's screen. Fails at legs (2) and (3): a slug proposed without alternatives looks exactly like a slug proposed with the best one first. |
| 82 | "Alongside the slug, decide the session's `design.md` location with the user." | :21 | unseen | Row 81's reader, and it fails legs (2) and (3) with it. A design location decided without the user looks like a design location the user agreed to. |
| 83 | "**Check for an existing design.md first.** … This is a judgment call on scope overlap, not a mechanical file-existence check." | :21-26 | unseen | Looked for an output of the check. `steering.md`'s `Design:` line records the *result* (row 84), never the search; neither `steering-template.md:26-27` nor `planning-workflow.md:21-26` provides a field for which existing `design.md` files were considered. A session that checked and a session that defaulted straight to a new path leave identical files. |
| 84 | "If one covers the area, point this session's `Design:` line at it and treat the work on it as an update — following design-template.md's "Updating an existing design.md" procedure … If none covers the area, default to `.rn/{yyyymmdd}-{slug}/design.md` (lowercase)" | :28-31 | unseen | The `Design:` line is read by `migration-workflow.md:28-29` — row 159, `unseen`, in a workflow that has never run (row 155). A wrong pointer would silently reconcile the wrong file and an absent one silently skip; nothing has ever been in a position to notice either. |
| 85 | "Read `${CLAUDE_PLUGIN_ROOT}/references/steering-template.md` and follow its per-section guidance." | :33 | unseen | Nothing records the read. The guidance it points at is the whole `steering-template.md` table below — rows 105–141 — and 30 of those 37 rows are themselves unenforced. |
| 86 | "Stamp the template's top `Rn version:` line with the currently installed plugin's version — read from … `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` `version` field." | :33 | unseen | 6 of 8 past `steering.md` files have no `Rn version:` line at all. The consumer (`on/SKILL.md:15` and the four siblings) does "a plain string comparison" (`migration-workflow.md:5`) that no file defines for a missing line, so an omission is silently a match. |
| 87 | "Write the chosen design.md path into the template's `Design:` line below it." | :33 | unseen | Row 84's consumer, and row 84's cap. |
| 88 | "Read the doc-division rule … and `…/references/design-template.md`, then **allocate content at planning** per the doc-division" | :33 | unseen | The allocation is a judgment with no recorded output; misallocated content just sits in the wrong file. |
| 89 | "Fill `Goal`, `Acceptance criteria`, `Assumptions`, and `Rules`. Leave `Tasks` and `State` as their placeholders for now." | :33 | recognized | Reader: the user at the plan gate, which `planning-workflow.md:47` sends to the PR to review the plan. Artifact: `steering.md` itself. Difference: an unfilled `Goal`, `Acceptance criteria`, `Assumptions` or `Rules` section is a blank where the thing they came to approve should be. |
| 90 | "**Force no empty `design.md`**: a session with no design to record creates no `design.md` and omits the `Design:` line entirely (no file, no pointer) … never write an empty file and never leave a dangling pointer." | :33 | unseen | A dangling pointer would break row 84's consumer — `migration-workflow.md:28-31` would try to reconcile a file that is not there — but that consumer is row 159, `unseen`, and has never run. Nothing checks the pointer resolves. |
| 91 | "Work backwards from the Acceptance criteria end state" | :35 | unseen | Looked for a trace of the derivation direction. `steering.md`'s `Tasks` section records the tasks and no field in `steering-template.md:55-79` asks how they were reached, so a list worked back from the Acceptance criteria and one written forward from the goal are the same list on disk. |
| 92 | "Define each task following the template's `Tasks` structure, inline `Completion criteria` rules, and `Task definition requirements` table in full." | :35 | unseen | This is the parent of the per-task rules: rows 122–132 (the `Tasks` structure and its inline `Completion criteria` rules) and rows 135–141 (the `Task definition requirements` table). Every one of them is unenforced. The second confirmed instance sits here: `20260705`'s tasks omit the Verification review step the structure mandates (`steering-template.md:70`) and nothing objected. |
| 93 | "**Design sign-off task.** When the session has a `design.md` not settled at plan time, place a **"Design sign-off"** task … at the point where heavy build would otherwise start" | :36 | unseen | No rule checks that the task exists — unlike the Evaluation sign-off, which has row 71's backstop. A missing Design sign-off is invisible. |
| 94 | "**Evaluation sign-off task.** Always place a final **"Evaluation sign-off"** task as the session's last task." | :37 | unseen | Backstopped by `task-verify-workflow.md:219-222` (row 71), itself `unseen`. Untested besides: the rule entered on 2026-07-01 (`2ddcafa`) and both sessions governed by it — `20260705-improve-design-template` (`#7`) and this one — placed the task. |
| 95 | "**Self-check before persisting.** Before persisting (Step 5), confirm the last task in the list is "Evaluation sign-off" — if it is not, add it before persisting." | :38 | unseen | A self-check with no recorded output. `20260625-rn-lean` placed its Evaluation sign-off as `#15`, mid-list before `#6`–`#14`. |
| 96 | "Write the completed `steering.md` to `.rn/{yyyymmdd}-{slug}/steering.md`." | :41 | recognized | Row 79's failure in its most direct form: no file, nothing for the resume to find, and the user who invoked it is told so. |
| 97 | "Commit it: `chore: start session — {slug}`." | :42 | recognized | Two halves, one enforced. Committing at all is: an uncommitted `steering.md` is invisible to `dn`/`up`'s `git log` search, and the resume reports nothing found (row 79). The message *text* reaches nothing — no step reads it — so the `chore: start session — {slug}` wording is unenforced. Consistent in practice all the same (`git log --all --grep='chore: start session' --oneline \| wc -l` returns 11). |
| 98 | "Ensure the work is on a branch — if on the default branch, create `{slug}` first." | :43 | unseen | Not `rn`'s mechanism, and not portable. `gh api repos/lovaizu/ccpm/rules/branches/main` returns a `pull_request` rule with `required_approving_review_count: 1` alongside `non_fast_forward` and `deletion`, so GitHub declines a direct push to `main` **in this repository** — this repository's branch-protection ruleset, not something the plugin ships or requires. `rn` installed on an unprotected repo has no such mechanism, and a verdict for a distributed plugin cannot rest on a fact local to one checkout. (`git push --dry-run origin HEAD:main` reports success, so the dry run is not the test either.) |
| 99 | "Push the branch, then open a draft PR (`gh pr create --draft`) titled from the goal." | :44 | refuses | `gh pr create` errors on a missing branch or an existing PR; the failure is on screen. `:47-48` names the failure branch explicitly: "push or PR creation failed → report it and present the plan in the console instead". |
| 100 | "The PR body is a single link to the steering file and nothing else — do not copy the Goal, tasks, or any plan content into it. Use a branch-ref blob link" | :44 | unseen | Fails at leg (3): the body is on the user's screen at the gate, but a body with the plan pasted into it reads as helpful rather than as a breach. Verified on this session's PR #21 — `gh pr view --json body` returns the single blob link plus a `Closes #17` line added by the user's own workflow. |
| 101 | "Open the plan-gate ask with the session-status block … on both branches: push and PR creation succeeded → report the PR link and ask the user to review the plan on the PR; push or PR creation failed → report it and present the plan in the console instead." | :45-48 | unseen | The message is on the user's screen. Fails at legs (2) and (3), like row 73. |
| 102 | "**Design gate.** … When the design is settled at plan time, fold it into this plan-gate approval (one stop). When it is not, Step 4 placed a **Design sign-off** task" | :49 | unseen | See row 93. Which branch was taken is never recorded, so neither choice can be checked. |
| 103 | "**Take the sign-off via the user's verdict commands** … never infer approval and never record a verdict the user did not issue." | :50 | recognized | The harness stops the assistant from *invoking* `/rn:ty` or `/rn:gm` (`ty/SKILL.md:4`, `gm/SKILL.md:4`), not from writing that a verdict was given. Reader: the user; artifact: the message recording the verdict and the check-off that follows it; difference: they know whether they typed the command. |
| 104 | "**CRITICAL: DO NOT proceed without explicit user approval.**" | :51 | recognized | Row 13's mechanism: the ask ends the turn only if the ask is made, so the recognition is of the breach, not of the rule. Reader: the user at the plan gate; artifact: the PR the gate points them at; difference: commits that predate their verdict. Nothing in `rn` declines on their behalf. |
| 252 | "Use the confirmed slug for the path." | :19 | recognized | The slug becomes the session directory name, which `dn/SKILL.md:14` and `up/SKILL.md:17` discover by `git log … -- '*/steering.md'` and `status-display.md:37-38` renders in every status header ("the session's slug (the steering directory name, date prefix dropped)"). Reader: the user at the plan gate; artifact: the blob link in the PR body (`planning-workflow.md:44`), whose path contains the slug; difference: a slug they did not confirm, against one they chose minutes earlier. Nothing re-derives the path from the confirmation. |
| 253 | "Coverage need not be complete: if an existing design.md covers the core of the work's area, treat it as the update target and record the session's new-but-related content under the sections it belongs to (adding new h3-level content is still "updating," not authoring fresh)." | :26-28 | unseen | The permissive half of row 83's judgment, and unrecorded in the same way: nothing states which existing `design.md` files were considered, how much of the area each covered, or why the threshold was or was not met. A session that skipped the question and a session that asked it and answered "no" produce the same `Design:` line. |
| 254 | The two sign-off tasks' prescribed content — Design sign-off: "Completion criteria: `design.md` is approved. Steps: present `design.md` to the user and take the verdict via `/rn:ty` (approve) or `/rn:gm` (revise → address the feedback, re-present)."; Evaluation sign-off: "Completion criteria: the Acceptance criteria run is approved. Steps: present the Acceptance criteria run result to the user and take the verdict via `/rn:ty` (approve) or `/rn:gm` (revise → address the feedback, re-present)." | :36-37 | unseen | Rows 93 and 94 cover whether the task is *placed*; this covers what planning must *write into* it, and nothing reads the written task against the prescription. Both past Evaluation sign-off tasks depart from it: `.rn/20260625-rn-lean/steering.md:231-252` and `.rn/20260705-improve-design-template/steering.md:239-254` each write their own Purpose, Steps and Completion criteria. `task-verify-workflow.md:219-222`'s backstop tests only that a task by that name was encountered, never what it says. |

### `steering-template.md` (106 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 105 | "Read when creating a new `steering.md`." | :3 | unseen | Looked for any record that the template was opened. `steering.md` carries the template's headings (row 106), which a session could equally reproduce from a previous session's file; there is no version, checksum or provenance line, so a read and a copy-paste are indistinguishable. |
| 106 | "**Copy the template block below verbatim.** Keep every heading. Keep the blank lines between fields" | :7 | unseen | The headings are addressed by name — `dn/SKILL.md:25` (row 217), `up/SKILL.md:24` (row 231), `migration-workflow.md:21-23` (row 158) — but all three of those rows are `unseen`, so a missing heading breaks a consumer nothing records having run. Nothing checks the blank lines. |
| 107 | "**Leave placeholders in unpopulated sections.** `Tasks`, `State` start empty; fill later." | :8 | unseen | Row 106's consumers, and row 106's cap. The other half of the breach — filling `Tasks` or `State` early — reaches nothing at all: premature content reads as content. |
| 108 | "**Fill each section per the rules below.**" | :9 | unseen | Parent of rows 109–141 — every per-section rule in this file. Nothing reads a written `steering.md` against any of them. |
| 109 | Doc-division: "**Requirements & acceptance criteria → `steering.md`**" | :15 | unseen | Looked for a reader that classifies content by kind. `migration-workflow.md:21-23` reconciles steering's *fields* against the template, never their contents against the doc-division, so design rationale written into `steering.md` sits in a legitimate field and reads normally. |
| 110 | "**Structure & decisions (how the parts fit, and why) → `design.md`** … rationale lives only here, at the decision level." | :16 | unseen | Same as row 109. |
| 111 | "**User-facing UX → `README`**" | :17 | unseen | Same as row 109. |
| 112 | "A decision lands in a task, in `design.md`, or in a rule. Deliberation and history live in git + the PR — never in steering." | :19 | unseen | Same absent reader as row 109. Searched the eight past `steering.md` files for a place where deliberation would be flagged: none exists, and `.rn/20260625-rn-lean/steering.md`'s task headings carry per-task narration (`— DONE through QA`, on 15 of 16 tasks) with nothing objecting. |
| 113 | "`Rn version:` … is written once, at creation, from the installed plugin's version — never user-edited afterward" | :21-24 | unseen | Row 86: the line is usually absent, and the comparison that would consume it treats absence as no-mismatch. |
| 114 | "The `Design:` line below it points to the session's `design.md`. A session with no design omits this line entirely" | :26-27 | unseen | Row 84's consumer (`migration-workflow.md:28-29`), and row 84's cap. |
| 115 | `Goal`: "why this is being done and what the user wants to change — the full intent, no added scope" | :37 | recognized | The user reads it at the plan gate; `status-display.md:37-38` compresses it into every status block's header. |
| 116 | `Acceptance criteria`: "the states / conditions by which the goal is judged achieved" | :41 | recognized | Consumed by the Evaluation sign-off task, whose completion criteria are "the Acceptance criteria run is approved" (`planning-workflow.md:37`) — the user reads the run at the last gate. |
| 117 | "two axes: goal alignment + quality" | :42 | unseen | Looked for a check on criterion coverage. QA reviews the artifact *against* the criteria (`task-verify-workflow.md:155`), never the criteria against this rule, so a list of criteria all on one axis passes every step `rn` defines. |
| 118 | "write these exhaustively, never sample — the complete set is what defines scope (in / out)" | :43 | unseen | Completeness of a list against an unstated whole is unverifiable by construction, and nothing tries. |
| 119 | `Assumptions`: "things taken to be true in pursuit of the goal — if one proves false, the plan changes" | :47 | recognized | Read by the user at the plan gate; `migration-workflow.md:21-23` names the field among what it reconciles. |
| 120 | "distinguish facts from assumptions — state explicitly if unverified" | :48 | unseen | Looked for a marker that survives writing. `steering-template.md:47-48` gives facts and assumptions the same bullet shape, so an unverified claim written without the caveat is typographically identical to a verified one, and no later step re-asks. |
| 121 | `Rules` seeds "commit and push every change; one completion marker per task" | :52 | recognized | Two halves. The marker half is consumed by `up/SKILL.md:26`'s grep (row 232), which checks off whatever task the message names. The push half has no consumer: an unpushed branch is absent from the PR, and no step asks anyone to compare the PR against local `HEAD`. |
| 122 | "**Purpose**: what to achieve, 1-2 sentences" | :59 | unseen | Copied into the work-order (`task-execute-workflow.md:141`) and read by the user at the plan gate. Length is unchecked. Fails at leg (2): the work-order that copies `Purpose` is a prompt and never reaches disk, and no reader is sent to measure the sentence count at the gate. |
| 123 | "**Prerequisites**: tasks that must be completed first (or "none")" | :61 | unseen | Nothing reads prerequisites: `task-verify-workflow.md:215` advances to "the next unchecked task" by position, not by dependency. **A stated prerequisite has no consumer at all.** |
| 124 | Steps include "self-check (OK/NG per completion criterion, record in checks/{task-id}.md)" as a `- [ ]` item | :67 | unseen | The step is a checkbox in `steering.md`; `dn/SKILL.md:22-23` checks off completed steps and the file is on the PR. Fails at leg (2) for the step that matters: an unchecked box is a blank only for a step planning actually wrote, and a step never written leaves no blank. Boxes that were written also survived unchecked — 5 in `20260615-experts-do-the-work`, 3 in `20260705-improve-design-template`, 2 in `20260624-rename-cmds-on-dn-up`, 1 each in `20260615-output-rule` and `20260625-rn-lean` — and nothing objected. |
| 125 | Steps include "QA expert review (subagent)" | :68 | unseen | Same checkbox mechanism as row 124, and it fails the same way: a step that planning never wrote cannot be a blank. Every session before `20260625` has QA steps; the review sections behind them are missing from most check files. |
| 126 | Steps include "Craft expert review (subagent, per the task's medium)" | :69 | unseen | Absent from all 5 sessions before `20260625-rn-lean`. Nothing noticed. |
| 127 | Steps include "Verification expert review (subagent, per the task's medium)" | :70 | unseen | The second confirmed instance named in this session's Assumptions. Absent from all 7 tasks of `20260705-improve-design-template` and from every earlier session; present in only 5 of 40 check files. The rule exists, the breach is plain in the output, and nothing in `rn` looks. |
| 128 | Steps include "(tasks that produce or revise structure/approach only) Design expert review (subagent)" | :71 | unseen | Same as row 126, plus the conditional judgment is never recorded. |
| 129 | Completion criterion ①: "is the objective achieved? — the objective met, not that an output was produced (write "the residue no longer keeps the tree dirty", not "DESIGN.md exists")" | :75-76 | unseen | This is the rule this session's Goal names as broken — the specimen proper, distinct from the missing Verification review, which the Assumptions call a second instance of the same mechanism. It binds *Completion* criteria only; `20260705`'s *Acceptance* criteria were written as artifact existence (`:22-49`) and the template says nothing there (row 116). Nothing reads either against this bar. |
| 130 | Criterion ②: "are new problems absent? — name the representative failure modes and require their absence" | :77 | unseen | Same as row 129; most past criteria state no failure modes. |
| 131 | "objectively verifiable by a third party; no vague terms ("appropriate", "correct")" | :78 | unseen | Looked for anything that reads criterion text. `migration-workflow.md:33-38` re-judges Completion criteria against the `Task definition requirements` table, but only for unchecked tasks, only by reasoning, and with no recorded output (row 160). Nothing greps for the two words this rule names. |
| 132 | "state the end-state, never actions/reviews/gates (those belong in Steps); the grounds are recorded at verification … not written into the criterion text" | :79 | unseen | Same as row 129. |
| 133 | `State` placeholder: "`Status` is `paused` while a session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here, so only a genuinely suspended session reads `paused`." | :83-85 | unseen | The named consumers are `dn/SKILL.md:15-16` (row 214) and `up/SKILL.md:19` (row 229), both `unseen` — neither records the ranking it made. The proof is standing: `.rn/20260615-subagent-execution/steering.md:340` still reads `- **Status**: paused` today, a closed session that outranks the live one, and no run of either skill has surfaced it. |
| 134 | `Notes`: "bounded forward pointer … not a re-narration of the session (that lives in `git log`)" | :91 | unseen | Read by `up/SKILL.md:24` and `:28` — rows 231 and 233, both `unseen`. Boundedness, which is the whole of the rule, is measured by nothing. |
| 135 | Granularity: "Purpose expressible in one sentence; split if it grows" | :100 | unseen | Consumed only by `migration-workflow.md:33-38`, which re-applies the same judgment with no recorded output. |
| 136 | Specificity: "Not "implement" but "implement `methodName()` in `ClassName`"" | :101 | unseen | Same as row 135. |
| 137 | Objectivity: "Completion criteria judgeable by a third party" | :102 | unseen | Same as row 135. The third party exists (QA, `task-verify-workflow.md:155`) but reviews *against* the criteria, never *the* criteria. |
| 138 | Prerequisites: "List dependencies explicitly; enables parallel/sequential judgment" | :103 | unseen | Row 123: nothing consumes prerequisites. |
| 139 | Criteria vs steps: criteria answer ① and ② with grounds, "not that an artifact was produced; actions, reviews, and gates go in Steps as `- [ ]` so their status stays trackable. The task-execution references' … Process selection section … is the source of *which* reviews apply — keep the two in sync" | :104 | unseen | "Keep the two in sync" names no mechanism, and the two are demonstrably out of sync: `task-execute-workflow.md:59-64` mandates Verification for every build task, and this template's Steps list has carried it since `0.7.0` — yet planning wrote it into 0 of 7 tasks in the very next session. |
| 140 | Flat tasks: "Number tasks `#1`, `#2`, …; do not group into phases or add phase-level gates … The user signs off only at the three scheduled gates" | :105 | recognized | Two halves. Numbered ids are consumed by `up/SKILL.md:26`'s `complete task #{id}` grep (row 232): a task with no id can never be checked off by a resume. Sequence and flatness are not — non-consecutive ids break neither consumer, and `20260625-rn-lean` ordering `#1–#5, #16, #15, #6–#14` produced a task list whose reading order is not its numeric order, with nothing objecting. |
| 141 | Done annotation: "A task that is done but awaiting an external gate … may carry an explicit done annotation in its heading … such a task counts as completed for the session-status display" | :106 | unseen | Consumed only by `status-display.md:19-22` (row 146), which is `unseen`: the block it produces has no reader but the user and nothing compares the ✅ set to `steering.md`. `20260625-rn-lean` carries the annotation on 15 of its 16 task headings against exactly one `- [x]` in the whole file (`:241`), so that session's ✅ state rests on prose matching that nothing verifies. |

### `status-display.md` (83 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 142 | "The compact session map that opens every message stopping for user input while a session is active … The block comes first in that message — before the ask and anything else." | :3-5 | unseen | Fails at legs (2) and (3): the block is rendered to the user by construction, but nothing in `rn` re-reads a sent message and the user holds no spec to check it against. That applies to every `status-display.md` row below. |
| 143 | "**Emit only while a session is active** — its `steering.md` exists and is identified." with the listed exceptions (planning's pre-persist asks, `/rn:up` before identification, `/rn:gm` or `/rn:ty` with no active session) | :9-12 | unseen | The exception list is the rule's own content: a block emitted at one of the four excluded stops would have to invent task ids for a `steering.md` that is not yet identified. Nothing compares those ids to a file, and the user, mid-planning, has no list to compare them to. |
| 144 | "**Asks and flow-ending reports both count as stops** … on a report the 👉 line states where the session stands and the user's next move instead of an ask." | :13-16 | unseen | The class boundary decides whether a suspend report, an abort, or a session-close message carries a block. A report that omits it is simply a report; no step re-reads a sent message to notice. |
| 145 | "**Derive the block fresh from the active `steering.md` at emit time** — its `Goal`, task list, and check-offs are the only source; never reuse an earlier block." | :17-18 | unseen | A stale block and a fresh one look identical unless the state changed between them, and nothing compares the block to the file. |
| 146 | "**A task counts ✅ when `steering.md` records it complete** — checked off, or carrying an explicit done annotation … Done-but-awaiting … still counts ✅; the pending item goes on the outlook line" | :19-22 | unseen | `steering.md`'s check-offs are a real input here (rows 141, 216), but the block this rule produces has no reader but the user, and no step compares the ✅ set to the file it was derived from. |
| 147 | "**Write the block in the user's conversation language.**" | :23-24 | unseen | A block in the wrong language is legible at a glance, so leg (3) holds — but leg (2) does not: the block arrives inside a message the user opens to answer an ask, not to audit, and no `rn` step re-reads a sent message. The same failure as every other rule in this file. |
| 148 | "**Markers are fixed**: ✅ completed / 👉 current / ⬜ remaining." | :25 | unseen | A substituted marker changes only how the block looks. The user holds no marker table, and nothing in `rn` parses an emitted block. |
| 149 | The format block — header / ✅ / 👉 / ⬜ / outlook, in that order | :29-35 | unseen | Section order is legible only against the format block at `:29-35`, which the user does not have in front of them. A block with the outlook line first is still a readable block. |
| 150 | "**Header** — `── {slug}: {goal one-liner} ──`: the session's slug (the steering directory name, date prefix dropped) and a one-line compression of steering's `Goal`." | :37-38 | unseen | The header compresses steering's `Goal`, and a compression that drops or distorts it has no second reader. The slug half is checkable against the directory name; nothing checks it. Contrast row 252, where the same slug is enforced — there it reaches the user inside the PR body's blob link at the plan gate, an artifact the gate makes them open; here it reaches them inside a status block, which nothing gives them an occasion to audit. |
| 151 | "**✅ completed** … Group consecutive ids into ranges … comma-separate non-consecutive groups … No completed tasks yet → no ✅ lines." | :39-42 | unseen | Range-collapsing is arithmetic over the check-off set. A wrong range and a right one are both plausible strings, and no step recomputes the ranges from `steering.md`. |
| 152 | "**👉 current** — exactly one line … A stop not tied to a numbered task (the plan gate; an escalation that spans tasks) names the gate or moment instead of an id." | :43-48 | unseen | The one-line rule and the report-form substitution are shape constraints on a message nobody re-parses. A block with two 👉 lines would read as an unusually detailed block. |
| 153 | "**⬜ remaining** … **No remaining tasks → omit the ⬜ lines entirely** — never render an empty ⬜ section." | :49-50 | unseen | An empty ⬜ section is exactly the artifact this forbids, and nothing scans for it. `.rn` retains no record of emitted blocks at all, so past breaches cannot even be counted. |
| 154 | "**Outlook** — one closing parenthesized line: what follows this stop" | :51-52 | unseen | Looked for a reader of the outlook line. `:51-52` is the only place it is specified, and no step in `rn` reads an emitted block back, so an omitted outlook withholds information the user never knew was owed to them and a wrong one names a next step nothing compares to `steering.md`'s task list. |

All thirteen rules in this file are `unseen`, and for one reason: the file's entire product is a
block the user receives inside a message they open to answer. No `rn` step ever compares an emitted
block against the `steering.md` it was derived from, and nothing in `rn` re-reads a sent message.
Twelve of the thirteen (142–144, 146–154) sit in U9; row 145 sits in U7, because a block derived
fresh and one reused leave no differing artifact at all.

### `migration-workflow.md` (70 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 155 | "Invoked by a command skill (`on`/`dn`/`up`/`ty`/`gm`) when the active session's `steering.md` `Rn version:` line does not match the installed plugin's version — the skill's own version-check step (a plain string comparison) is what triggers this file … Run once per invocation." | :3-6 | unseen | The trigger is a prose step in five skills (`on/SKILL.md:15` and siblings) with no recorded output. It has never fired in this repo: most sessions carry no `Rn version:` line to compare (row 86), and the two that do were current when written. |
| 156 | "Coordinator only: no implementation expert, and no QA/Design/Craft/Verification review, spawns for this procedure itself … The coordinator reads each artifact, judges drift, and edits it directly." | :8-11 | unseen | Fails at leg (1): the reconciliation commit lands on the PR (`:56`), but no reader is assigned to it, and the property in question — that no expert was spawned — leaves no trace in a commit either way. |
| 157 | "Reconcile the three artifacts below **in this order** — steering, then design, then tasks." | :15-18 | unseen | Looked for a trace of ordering. The three steps' edits are applied and committed together (`migration-workflow.md:56`), so one commit carries all three regardless of the order they were made in; nothing timestamps them and no file records which ran first. |
| 158 | Step 1: "Compare the session's `steering.md` … against the current `steering-template.md`. Judge by reasoning what has drifted … and edit `steering.md` directly to close it." | :20-25 | unseen | An unrecorded judgment. A pass that finds nothing and a pass that never ran produce the same empty diff. |
| 159 | Step 2: "Read the session's `steering.md` `Design:` line; if it is absent … skip this step entirely. If present, follow `design-template.md`'s own "Updating an existing design.md" procedure … do not re-derive reconciliation logic here." | :27-31 | unseen | Fails at leg (1): the `Design:` line is a real input to the branch, but nothing checks that the branch was taken. A read error on a dangling pointer (row 90) is the pointer's failure, not this step's; a step skipped outright errors on nothing. |
| 160 | Step 3: "For every unchecked task … judge its Purpose / Prerequisites / Steps / Completion criteria against each row of that table — Granularity, Specificity, Objectivity, Prerequisites, Criteria vs steps, Flat tasks, Done annotation — and edit the task directly" | :33-38 | unseen | Same as row 158; and the table rows it applies are themselves unenforced (rows 135–141). |
| 161 | "Leave every already-checked-off task untouched — reconciliation targets the forward-looking remainder, not the record of what already happened." | :39-40 | unseen | Fails at leg (1): a touched historical task shows in the reconciliation commit's diff, but `migration-workflow.md` spawns no reviewer (`:8-11`) and passes through no gate (`:56-58`), so no reader is assigned to that diff. |
| 162 | For a task whose Completion criteria changed and that has a `checks/{task-id}.md`: "record in its Overall Verdict a `Ready to check off: No — criteria reconciled, self-check/review must re-run` line" — and if no such file exists, write nothing | :41-52 | unseen | The rule names its own consumer at `:47-48`: "`task-verify-workflow.md`'s Phase: Complete only checks off once Verify has cleared with `Ready to check off` reading Yes". Phase: Complete says something else — `task-verify-workflow.md:208-209` reads "**Check off steering.** With Verify cleared — or, for a sign-off task, once its gate verdict is approved — check off the task in `steering.md` directly", with no mention of the field. So the line this rule writes blocks nothing. What that has cost in practice is recorded under U8. |
| 163 | "Apply the reconciling edits from all three steps and commit them directly. This is not one of the three scheduled gates … and it does not go through per-task QA/Craft/Design review — it is a mechanical, no-gate procedure." | :56-58 | unseen | Fails at leg (1), and deliberately: the commit lands on the PR with no reader assigned, because the rule's own design accepts "an occasional wrong reconciliation … caught via normal PR/git-log review" (`.rn/20260705-improve-design-template/steering.md:58-59`) rather than a live approval step. |
| 164 | "Once the reconciling edits are committed, update the session's `steering.md` `Rn version:` line to the installed plugin's version — the last step, so the stamp only advances once the artifacts it certifies are actually current." | :59-61 | unseen | Nothing checks the ordering, and a stamp advanced without the edits is indistinguishable from one advanced after them. |
| 165 | "Every comparison above asks one question only: does this artifact match what the **currently installed** templates/workflows require, right now. This file never reads `CHANGELOG.md` and never reasons about version ranges or deltas between the session's recorded version and the installed one" | :65-70 | unseen | A prohibition on a reasoning method; nothing observes the method. |

### `design-template.md` (139 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 166 | "Read when creating a session's `design.md` … **Not read at runtime**: it records decisions and how the parts fit" | :3-5 | unseen | The file declares its own product unenforceable: nothing in the flow reads `design.md`. Its only reader is the Design sign-off gate — which exists only when planning placed one (row 93), and 7 of 8 sessions have no such task. |
| 167 | "The h2 sections below are the canonical design-document sections; under each, the h3 headings are the questions that section must answer — a section is done when its questions are answered, not when its heading merely exists." | :7-9 | unseen | Looked for a test of "answered". The file gives its h3 questions no answer marker and `design.md` is not read at runtime (`design-template.md:4`), so a heading with a paragraph under it that answers a different question presents exactly like one that answers this one. |
| 168 | "This is the fresh-authoring path … to update an existing one, skip to "Updating an existing design.md"" | :13-14 | unseen | Looked for a record of the branch. Neither `design.md` nor `steering.md` carries a field saying whether the document was authored fresh or updated; `migration-workflow.md:27-31` routes to the update procedure but records nothing about which path was taken. |
| 169 | "**Copy the template block below verbatim.** Keep every heading, numbering, and section order — the five h2 sections and the h3 questions under them are the contract" | :16-17 | unseen | The shape is checkable — `rn/docs/design.md` does carry all five h2 sections in order (`grep -n '^## ' rn/docs/design.md` returns lines 6, 54, 80, 190, 289) — but checkable is not checked. No step in `rn` opens a `design.md` and compares its headings to the template; `design-template.md:4` states the file is "**Not read at runtime**". |
| 170 | "**Answer every h3 question with a decision and the reasoning behind it** … If a question does not apply, say so **and say why** … Nothing here licenses a section with a question left silently unanswered." | :19-22 | unseen | The core rule of the file, and there is no reader: a missing answer under a present heading looks like prose. |
| 171 | "**In Detailed design, repeat `4.N` once per mechanism or component the design introduces** — not a fixed four" | :23-24 | unseen | Looked for an enumeration to compare against. Nothing in `rn` lists a design's mechanisms independently of the `4.N` subsections themselves, so the subsection count is its own authority — a design with three mechanisms and one subsection reads as a design with one mechanism. |
| 172 | "**Treat the whole document as optional, not any section within it.** … once you are writing one, no section may be skipped for having "nothing to record"" | :25-28 | unseen | Same as row 170. |
| 173 | The template block — five h2 sections with their h3 questions, and the header line "Not read at runtime — for whoever maintains the design" | :32-75 | unseen | Same as row 170. |
| 174 | Per-section guidance, including: every `4.N` "asks the same pair of questions of its mechanism: what does it guarantee, and how is a breach of that guarantee caught?" | :81-96 | unseen | The template asks of every mechanism the exact question this inventory asks of every rule — and nothing checks that the answer is real. `rn/docs/design.md`'s own `4.N` answers are the place this session's gap should have shown. |
| 175 | "Follow this instead of the Steps above when `planning-workflow.md`'s location check (Step 2) points `Design:` at an existing `design.md`" | :100-102 | unseen | Row 168. |
| 176 | "**Read the existing document in full before touching it.** Identify which h3 questions the session's work actually changes" | :104-105 | unseen | Looked for a trace of reading. The update procedure's only output is the revised `design.md`, and a document revised after a full read differs from one revised after a keyword search in quality, not in form. |
| 177 | "**Revise only what changed.** … leave every other section's existing text untouched. Carrying forward unchanged text is correct, not lazy" | :106-108 | unseen | A wholesale rewrite would show in the commit diff, whose only assigned reader is row 41, `unseen`. `design-template.md:4` puts `design.md` outside the runtime flow, so no other step opens it. |
| 178 | "**The decision-plus-reasoning contract from fresh authoring still applies to whatever you touch.**" | :109-111 | unseen | Row 170. |
| 179 | "**If the document predates the five-section shape** … reconcile it toward the current five-section shape as part of this update … relocating content to the section it actually belongs to … not license to rewrite unrelated, still-accurate content." | :112-126 | unseen | Row 177's reader, and row 177's cap. Whether the *right* content moved is unchecked in any case. |
| 180 | "**Give genuinely open content a destination outside `design.md`.** … Session-scoped: put it in that session's `steering.md` Notes field … Canonical/cross-session: track it outside `design.md` instead (e.g. a repo issue)" | :127-137 | unseen | Looked for the destination end. `steering-template.md:91`'s `Notes` field and a repo issue are the two named landing places, and nothing walks from a removed "Open questions" item to either; a question resolved by deletion leaves nothing in the diff but the deletion. |
| 181 | "**Add or drop `4.N` subsections to match what changed** … a new mechanism gets a new subsection, a removed one loses its subsection instead of being left stale." | :138-139 | unseen | Row 171. A stale subsection reads exactly like a current one. |

### `pr-feedback-workflow.md` (153 lines)

This file is the densest cluster of genuinely enforced rules in `rn`, because almost every step is a
`gh` call whose failure is a non-zero exit rather than a prose instruction.

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 182 | "A **coordinator** dispatches one **execution subagent** per review thread, sequentially, and reviews each result before the next." | :3-4 | unseen | Nothing records the dispatch (rows 5, 11). |
| 183 | "Verification is a single coordinator pass — not the QA-expert / multi-round chain" | :4-7 | unseen | A scope statement about what does *not* run; its breach (running experts anyway) leaves no artifact. |
| 184 | "Entered from `/rn:gm` with no argument — the argument/no-argument routing rule lives in `gm/SKILL.md`." | :9-10 | unseen | Not a refusal. The harness gates `/rn:gm` itself (`gm/SKILL.md:4`), but nothing stops the loop being entered from anywhere else, and `gm/SKILL.md:15`'s branch is a rule about which step to take, not a gate on taking it. Entering the loop wrongly leaves no artifact that differs from entering it rightly. |
| 185 | Coordinator "Never resolves a thread." | :14-16 | recognized | Thread resolution is GitHub state the reviewer sees; a thread resolved by the assistant is visibly resolved-by-assistant on the PR. |
| 186 | Execution subagent "Handles exactly one thread, with exactly one of two outcomes (address-and-reply, or reply-with-a-question). Never resolves a thread." | :17-18 | recognized | The reply is posted to a specific thread on the PR; two threads touched by one subagent show as two replies. Row 185's reader. |
| 187 | "**Find the session's PR** for the current branch:" — followed by the fenced command `gh pr view --json number,url` | :22-26 | refuses | Real command with a real failure mode. Verified: run on this branch it returns `{"number":21,"url":"…/pull/21"}` with exit 0; on a branch with no PR it exits non-zero, which is exactly what the next row handles. |
| 188 | "If this exits non-zero or reports "no pull requests found" … **stop and report** — do not fabricate a PR number or proceed into the GraphQL call. Open that report with the session-status block" | :28-31 | refuses | The GraphQL query at `:46` takes `-F pr={number}`; with no number there is nothing to pass and the call fails. The prohibition on fabricating one is only prose, but the fabricated number would return an error from the API. |
| 189 | "Capture `owner` and `repo` as **two separate** values" with the two `gh repo view -q` commands | :33-38 | refuses | A combined value breaks `-f owner=` / `-f repo=` in the GraphQL call, which the API rejects. |
| 190 | "**Fetch all review threads** via GraphQL, **paginating** `reviewThreads` until exhausted … **Repeat** the call while `reviewThreads.pageInfo.hasNextPage` is true … **accumulate** `nodes` across pages." | :42-72 | recognized | A skipped page drops threads from the queue and nothing counts what should have been there — but a dropped thread stays unresolved on the PR, and `pr-feedback-workflow.md:142-148` makes the unresolved state the queue, so the next run re-collects it (row 206). Reader: the thread's reviewer, on their own thread; artifact: the thread; difference: it is still unanswered. A page-skipped thread and row 191's wrongly-dropped thread produce the identical artifact and take the identical verdict. |
| 191 | "Keep a thread **only** when both hold: … `isResolved == false`, AND … the **last** comment's author … equals the **first** comment's author" | :74-78 | recognized | Wrongly kept threads produce a duplicate reply on the PR, which the reviewer sees; wrongly dropped ones leave the thread unanswered, which the reviewer also sees. The reviewer is a real second reader here. |
| 192 | "Drop every other thread … For each kept thread record: the **first** comment's `databaseId`, `path` and `line` … and the comment bodies" | :80-82 | refuses | The reply endpoint at `:109` is keyed on `first_comment_databaseId`; a wrong or missing id is rejected by the API. |
| 193 | "Process the queue **one thread at a time**. Never dispatch two threads in parallel" | :86-87 | unseen | Looked for a trace of concurrency. The loop's only outputs are the replies on the PR and the commits behind them, both order-independent; nothing records dispatch times, and `pr-feedback-workflow.md:130-134`'s between-item review inspects a result, never when it arrived. |
| 194 | Work-order contents: Thread (`path`, `line`, full bodies, `databaseId`) and Task ("produce exactly one of the two outcomes") | :89-92 | unseen | Row 27: the prompt is never written down. |
| 195 | Outcome (a): "Make the change. … Stage the touched paths **explicitly** … Never `git add -A` or `git add .`." | :94-95 | recognized | The PR diff, read by the reviewer whose thread this is. Row 35's limits apply. |
| 196 | Outcome (a): "Commit with a plain conventional message … The message must **not** contain `complete task #`." | :96-97 | recognized | Row 36's consumer (`up/SKILL.md:26`). A PR-feedback commit carrying the substring would check off an unrelated task on the next resume. |
| 197 | Outcome (a): "Push to the session PR. Never force-push." | :98 | recognized | Not a refusal in either half. A skipped push leaves the commit local, and the Done reply at `:105-111` then carries a permalink to a commit GitHub does not have — reader: the thread's reviewer, who `:144-145` expects to resolve it after reading the reply; artifact: their own thread; difference: the commit link 404s. A force-push is not declined by anything and shows only on the PR timeline, which nothing asks anyone to read. |
| 198 | "**If the commit or push fails, do not post a Done reply** (its permalink would point at an unpushed, dead commit). Return the failure in the summary … post the reply only once the commit is confirmed pushed." | :99-102 | recognized | The obvious mechanism is not there: `gh browse <sha> -n` builds a URL locally and never asks GitHub whether the commit exists — run here on an all-zero sha it printed `https://github.com/lovaizu/ccpm/issues/0000000000000000000000000000000000000000` and exited 0. Nothing prevents a Done reply for an unpushed commit. What remains is recognition: reader — the thread's reviewer; artifact — their thread; difference — a dead commit link. |
| 199 | "Once the commit is pushed, get its permalink: `gh browse <sha> -n`" | :103-104 | recognized | Same reader as row 198. Skipping the permalink step yields a Done reply with no commit link, which the reviewer reads on their own thread. The command itself refuses nothing (see row 198). |
| 200 | "**Reply to the thread** with a short summary of what was done plus the commit link, in-reply-to the thread's first comment — **only after the commit is pushed**" | :105-111 | recognized | The reply is on the PR; a missing one leaves the reviewer's thread unanswered, and the loop's own queue filter (row 191) re-picks it up on the next run. That re-pick is a genuine self-correcting mechanism. |
| 201 | "**Outcome (b) — needs a decision / is unclear:** make **no** code change. Reply to the thread with the question" | :113-119 | recognized | Same reader as row 200; a code change made anyway shows in the PR diff. |
| 202 | "**Return** — a compact summary: which outcome, what changed (files), the commit SHA and that it was pushed … or the question asked" | :121-122 | recognized | Read by the coordinator at `:130` — `pr-feedback-workflow.md:128-134`, row 204, itself `recognized`, so this is not a reading nobody can tell happened. The fields the rule names (outcome, files, SHA, pushed) are exactly what that check needs. Contrast row 50, whose consumer is `unseen`. |
| 203 | "**Never resolve the thread.** Resolution is the author's act on GitHub" | :124 | recognized | Row 185. |
| 204 | "**Check the result.** … **OK → dispatch the next thread.** … **Problem → re-instruct the same subagent on the same thread.** Do not advance until it is right." | :128-134 | recognized | The coordinator reads the summary and the PR; a wrong result shows as a reply that does not match its thread. |
| 205 | "When the queue is empty, the loop is done — report the loop result … opening that report with the session-status block" | :136-138 | unseen | The loop-completion report reaches the user, but nothing in `rn` re-reads it, and the thread state it summarizes lives on GitHub, where the user would have to go and count for themselves. |
| 206 | "The loop **never** resolves a thread. Neither the coordinator nor the subagent calls `resolveReviewThread` … The loop treats GitHub's unresolved state as its **queue**." | :142-148 | recognized | State lives in GitHub rather than in the assistant's memory, so a missed thread is re-collected on the next run (row 200). Quoted in full because the guarantee is real: it is the only rule in `rn` that repairs its own omission. |
| 207 | "One coordinator pass per item … is the whole of verification. No QA expert, no Design / Craft / Verification experts, no multi-round iteration cap." | :152-153 | unseen | Row 183. |

### `on/SKILL.md` (17 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 208 | "`disable-model-invocation: true`" / "Has side effects (writes files, commits, pushes, opens a PR) — run only on explicit `/rn:on`." | `on/SKILL.md:3-4` | refuses | The harness refuses model invocation of the skill. The only machine-enforced rule in the plugin. |
| 209 | "**Plan the session.** Read `${CLAUDE_PLUGIN_ROOT}/references/planning-workflow.md` and run it in sequence." | `on/SKILL.md:13` | recognized | The workflow's own outputs are the artifacts: `steering.md` (row 96), the `chore: start session` commit (row 97) and the draft PR (row 99, whose command refuses on failure). Their absence leaves the user who typed `/rn:on` with no PR link and no plan to approve. Skipping a *step* inside the workflow shows only if that step had an artifact. |
| 210 | "**Check version.** … on a mismatch, run `…/references/migration-workflow.md` first — on a match, do nothing. Since step 1 just stamped that line from this same installed version, this branch can never actually fire here — it's kept only so `on`'s step matches `dn`/`up`/`ty`/`gm`'s" | `on/SKILL.md:15` | unseen | The file states outright that the branch is unreachable. It is a consistency-of-appearance rule, not a check. |
| 211 | "**Begin task #1.** After approval, read `…/references/task-execute-workflow.md` then `…/references/task-verify-workflow.md` and execute task #1 following them in sequence." | `on/SKILL.md:17` | recognized | "After approval" is row 104's recognition, with the same reader and artifact. The read-both-files-in-order half is row 1: nothing records which file was read, or whether either was. |

### `dn/SKILL.md` (59 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 212 | "`disable-model-invocation: true`" / "run only on explicit `/rn:dn`" | `dn/SKILL.md:3-4` | refuses | Row 208's harness mechanism. |
| 213 | "Records resume state and hands off. Does not execute tasks." | `dn/SKILL.md:9` | unseen | Fails at leg (1): a deliverable commit made during suspend rides along in the suspend push and lands on the PR, but no step and no scheduled reader opens that push to ask what was in it. |
| 214 | "**Locate steering.md.** Use the path known from this session. If unknown: run `git log --diff-filter=AM --name-only --pretty=format: -- '*/steering.md' \| head -5`, keep the paths that exist on disk, and take the one whose `State` shows `Status: paused`, else the most recent." | `dn/SKILL.md:13-16` | unseen | Not a refusal: the command runs, and nothing declines when its output is ignored or the wrong candidate is taken. Nothing downstream re-derives the choice either — `dn` writes `State` into whichever file it picked, and the next `/rn:up` starts from whatever it finds. The known data defect stands: `.rn/20260615-subagent-execution/steering.md:340` still reads `- **Status**: paused`, so a closed session outranks the live one. |
| 215 | "**Check version.** Compare `steering.md`'s `Rn version:` line to the installed plugin's version … on a mismatch, run `…/references/migration-workflow.md` first — on a match, do nothing." | `dn/SKILL.md:18-20` | unseen | Row 86: the line is usually absent, and no file defines the missing-line case. |
| 216 | "**Check off progress.** In steering.md, check off completed task steps and add any tasks discovered during the work." | `dn/SKILL.md:22-23` | recognized | The check-offs are consumed by `task-verify-workflow.md:215`'s "next unchecked task" (row 69). `status-display.md:19-22` reads them too, but that reader is `unseen` (row 146). |
| 217 | "**Write the `State` section** per `steering-template.md`'s State placeholder: `Status: paused`, `Date`, `Last completed`, `Next`, `Notes` — cap `Notes` to the bounded forward pointer" | `dn/SKILL.md:25-27` | unseen | The named readers are `up/SKILL.md:19` (row 229) and `:24` (row 231), both `unseen`: nothing records which candidate `up` ranked or whether it read `State` at all. A missing or wrong `State` sends the resume to the wrong session, and the resume looks the same either way. The `Notes` cap is unchecked. |
| 218 | "**Commit the work.**" — "Tree clean → skip this commit. … Current task's steps all checked → commit normally. … Some steps unchecked → commit with a `wip:` prefix." | `dn/SKILL.md:29-32` | unseen | Fails at leg (3): `git status` picks the branch, but nothing compares the chosen prefix to the checkbox state, so a `wip:` on a finished task and a plain message on an unfinished one both read as ordinary commits. |
| 219 | "The message must not contain `complete task #`." | `dn/SKILL.md:33` | recognized | Row 36's consumer — and the historical breach `4daf6b2` is precisely a suspend-time bookkeeping commit that quoted this rule in its own body. |
| 220 | "**Resolve untracked residue.** Run `git status --porcelain` … Regenerable test/build artifact … → append a matching rule to the repo-root `.gitignore` (create it if absent). Any doubt → handle as the next item instead." | `dn/SKILL.md:35-39` | unseen | Step 8 (`dn/SKILL.md:50-54`) re-runs `git status --porcelain` against step 6's own effect and writes each leftover into `State → Notes`. That is a post-condition in shape, but it is row 224, `unseen` — nothing records that step 8 ran — and the record it writes is read by `up/SKILL.md:24`, row 231, also `unseen`. Both links are steps nobody can tell happened. |
| 221 | "Anything else → ask the user how to handle it … opening the message with the session-status block … For any path the user does not resolve, append its exact `git status --porcelain` string to `State → Notes`." | `dn/SKILL.md:40-43` | unseen | Row 220's chain, and row 220's cap. The ask itself ends the turn, which is compliance, not a mechanism. The one breach nothing reaches at all is deleting the path (row 222). |
| 222 | "Never delete a file yourself." | `dn/SKILL.md:44` | unseen | A deleted untracked file leaves no trace anywhere — not in git, not in `git status`. Its breach is undetectable in principle, not merely unobserved. |
| 223 | "**Commit and push.** Commit the `State` changes and any `.gitignore` edit together in one commit, then `git push`. If push fails, continue and record that it failed (for step 9). Never amend, never force-push." | `dn/SKILL.md:46-48` | refuses | `git push` reports its own failure and the rule handles it. The amend half is a genuine refusal: an amended commit that has already been pushed is rejected as a non-fast-forward on the next push, and the rule forbids the force-push that would clear it. |
| 224 | "**Verify clean.** Run `git status --porcelain` … Non-empty → for each remaining (non-gitignored) untracked path, if its exact … string is not already recorded in `State → Notes` … record it there as user-deferred; then go to step 9. Never loop back to step 6. Never delete a file." | `dn/SKILL.md:50-54` | unseen | The re-run is a real post-condition on step 6 — which is why row 220 is recognized — but nothing checks that step 8 itself ran. A `dn` that skips it and a `dn` that runs it and finds an empty tree produce the same report and the same commit. |
| 225 | "**Report.** Open the report with the session-status block … then output the branch name. If the last push did not succeed, state that the commits are local-only and must be pushed. Name any user-deferred paths" | `dn/SKILL.md:56-59` | unseen | Fails at leg (3): the report is on the user's screen, and its one checkable claim — that the commits are local-only — would have to be checked against the PR by someone who has no reason to look. |

### `up/SKILL.md` (34 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 226 | "`disable-model-invocation: true`" / "run only on explicit `/rn:up`" | `up/SKILL.md:3-4` | refuses | Row 208's harness mechanism. |
| 227 | "**Handle a dirty tree.** … Tree dirty → run step 2's discovery first, read-only … then propose a `wip:` commit or a discard, opening the message with the session-status block … and wait for confirmation before touching the working tree." | `up/SKILL.md:13-15` | unseen | The dirty-tree branch is read from `git status`, but nothing declines a tree touched without confirmation, and the load-bearing half leaves no residue: a discarded working tree is gone from git, from `git status`, and from the report. The `wip:` half would at least land as a commit on the PR. |
| 228 | "**Find steering.md.** Run `git log --diff-filter=AM --name-only --pretty=format: -- '*/steering.md' \| head -5` and keep the paths that exist on disk." | `up/SKILL.md:17` | unseen | A real command, but running it is not the rule anything checks — nothing re-derives the candidate list or compares it to what was used. `head -5` also truncates silently once a repo has more than five session directories; this repo already has eight `steering.md` files. |
| 229 | "One result → use it. … Multiple → rank by `State` showing `Status: paused`, then most recent commit, and propose the top candidate. … Zero → tell the user "No steering.md found. Run `/rn:on` to start." and stop." | `up/SKILL.md:18-20` | unseen | Nothing declines a wrong branch: the zero case ends the turn only if the assistant takes it, and the ranking is a judgment fed by row 133's stale `paused`. A wrongly ranked candidate produces a resume that looks entirely normal. |
| 230 | "From step 3 on, any message stopping for user input opens with the session-status block" | `up/SKILL.md:22` | unseen | A blanket instruction covering every later stop in `up`. It inherits row 142's problem exactly: the block goes into a message the user answers rather than audits. |
| 231 | "**Read State.** Read the `State` section: last completed task, next task, and notes." | `up/SKILL.md:24` | unseen | Nothing declines a resume that skipped `State`. The step's output lives only in the agent's context; a session resumed from a guess and a session resumed from the file produce the same next commit. |
| 232 | "**Sync tasks.** Cross-check `git log` against the unchecked tasks. A commit matches a task when its message contains `complete task #{id}`; check that task off" | `up/SKILL.md:26` | recognized | Reader: `task-verify-workflow.md:215` (row 69), which begins "the next unchecked task" from what this step writes. Artifact: `steering.md`'s unchecked-task list. Difference: a task finished in a past session is re-entered as though it were not. `status-display.md:19-22` renders the same list but nobody audits it (row 146). Nothing refuses. The step's own defect — a substring match that also fires on other task ids and on prose — is recorded as a finding under group D. |
| 233 | "**Check blockers.** If `State` notes mention a blocker, investigate and find an alternative approach before removing any task." | `up/SKILL.md:28` | unseen | A removed task disappears from `steering.md`, which the user sees in every subsequent status block. Fails at leg (3): a removed task simply disappears from the ⬜ line, and the user holds no earlier copy of the list to miss it from. |
| 234 | "**Clean up State.** Replace the `State` section with its template placeholder and commit the reconciliation." | `up/SKILL.md:30` | unseen | The commit lands on the PR with no reader assigned, and the reset's consumers are rows 214 and 229, both `unseen`. The standing breach proves it: `.rn/20260615-subagent-execution/steering.md:340` still reads `paused` and still mis-ranks discovery. |
| 235 | "**Check version.** … on a mismatch, run `…/references/migration-workflow.md` first — on a match, do nothing." | `up/SKILL.md:32` | unseen | Row 86. |
| 236 | "**Begin the next task.** Read `…/references/task-execute-workflow.md` then `…/references/task-verify-workflow.md` and execute the next unchecked task following them in sequence." | `up/SKILL.md:34` | recognized | Reader: the user who typed `/rn:up` and gets back a resume that started somewhere else, or nowhere. The next-unchecked half is read from `steering.md`; the ordering half is row 1 (`unseen`). |

### `ty/SKILL.md` (26 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 237 | "`disable-model-invocation: true`" / "is user-invoked — run only on explicit `/rn:ty`" | `ty/SKILL.md:3-4` | refuses | Row 208's harness mechanism — and it is what makes rows 16 and 103 meaningful: an approval cannot be self-issued. |
| 238 | "Approves the pending rn confirmation and advances the flow. Performs no revision." | `ty/SKILL.md:9` | unseen | A revision made under `/rn:ty` lands as a commit on the PR, but no step and no scheduled reader opens that commit to ask whether an approval should have produced one. Row 213 (`dn/SKILL.md:9`, "Does not execute tasks") is the same rule in the same shape and fails the same way. |
| 239 | "**Check version.**" | `ty/SKILL.md:13` | unseen | Row 86. |
| 240 | "**Identify the pending approval.** … Exclude weigh-in / escalation questions … State the identified target back. Proceed only if it is unambiguous; if more than one approval is plausibly pending … ask the user which before recording approval" | `ty/SKILL.md:15` | recognized | Reader: the user who just typed `/rn:ty`. Artifact: the stated-back identification, which the rule requires be put in front of them before anything is recorded. Difference: a target they did not mean — and they are the only party who knows what they meant, so it is legible to them with no rule in hand. The rule supplies its own reader, which nothing else in `rn` does. |
| 241 | "**Record it as approved.** Register the pending confirmation as accepted." | `ty/SKILL.md:17` | recognized | For a task gate, the record is the `steering.md` check-off (`task-verify-workflow.md:208`), which is committed and read downstream. For a plan gate there is no artifact at all. |
| 242 | "**Advance the workflow.** … a plan or design gate passes — execution proceeds to the next task; … an evaluation gate passes — the session can close; … a reviewed item is accepted … When the advance ends the flow … open that closing report with the session-status block" | `ty/SKILL.md:19-24` | unseen | The advance itself is recognized where it lands in an artifact (row 241); the closing report's block is not, for row 142's reason. |
| 243 | "**Nothing pending.** If nothing is actually awaiting approval, open the reply with the session-status block …, say so, and do nothing else." | `ty/SKILL.md:26` | unseen | The nothing-pending reply is a message and nothing else. No artifact differs between a compliant reply and a breaching one, so even the trace available to row 241 is absent here. |

### `gm/SKILL.md` (21 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 244 | "`disable-model-invocation: true`" / "run only on explicit `/rn:gm`" | `gm/SKILL.md:3-4` | refuses | Row 208's harness mechanism. |
| 245 | "**Check version.**" | `gm/SKILL.md:13` | unseen | Row 86. |
| 246 | "**Branch on the argument.** Trim `$ARGUMENTS` of surrounding whitespace first; treat a blank/whitespace-only value as empty. If non-empty after trimming, it is the feedback — go to step 3. If empty … go to step 4." | `gm/SKILL.md:15` | recognized | Not a refusal — nothing declines the wrong branch — but the wrong branch is recognized at once. Reader: the user who typed `/rn:gm <text>`; artifact: the report they get back; difference: their feedback was never acted on and the PR's threads were answered instead. The predicate itself is the only fully specified conditional in the plugin. |
| 247 | "**With feedback (`$ARGUMENTS` present).** Treat `$ARGUMENTS` as a revise verdict on the pending item … If there is no pending item, treat `$ARGUMENTS` as a direct instruction and act on it … do not stall on a missing target. Apply the revision … then report, opening the report with the session-status block … Do not enter the PR-feedback loop." | `gm/SKILL.md:17` | unseen | Fails at leg (3): the revision's commits are on the PR and the report is on the user's screen, but whether they address the feedback is a judgment nobody is asked to make. |
| 248 | "**From the PR (no argument).** Read `…/references/pr-feedback-workflow.md` and run that loop against the current PR's review comments." | `gm/SKILL.md:19` | recognized | Reader: the user who typed `/rn:gm` with no argument; artifact: the report they get back; difference: the PR's threads are still unanswered. Not entering the loop and not addressing a thread leave the same artifact, which is why this takes row 249's verdict rather than a weaker one. The loop's own `gh` calls (rows 187–192) refuse a *malformed* call once it is running; they say nothing about whether it was entered. |
| 249 | "**Either way, this is a revise verdict** … It drops nothing: every piece of feedback is acted on." | `gm/SKILL.md:21` | recognized | For PR feedback: real — an unaddressed thread stays unresolved and is re-collected on the next run (`pr-feedback-workflow.md:146-148`). For `$ARGUMENTS` feedback: nothing at all, since the feedback exists only in the conversation. |

---

## The enforced set

**61 rows — 12 `refuses` and 49 `recognized`.** They are a partition: every row appears in exactly
one of the four groups below, and 5 + 7 + 39 + 10 = 61. Listed by mechanism so task #2 can see what
it has to work with — a rebuilt rule has to attach to one of these four, or invent a fifth.

### A. The harness refuses the action — 5 rows

Rows **208, 212, 226, 237, 244.** `disable-model-invocation: true` in each skill's frontmatter — the
one line of machinery `rn` ships. The model cannot invoke the skill; only the user typing `/rn:on`
can. It guards exactly one property: that the five commands are user-initiated. It does **not** make
the three gates self-executing — it stops the assistant issuing `/rn:ty`, not writing "approved" in
prose, which is why rows 21 and 103 are `recognized` rather than `refuses`.

### B. An external command fails — 7 rows

Rows **72, 99, 187, 188, 189, 192, 223.** `gh pr create` on a branch that already has a PR (72, 99);
`gh pr view` exiting non-zero and the GraphQL and reply calls rejecting a missing PR number, a
combined `owner`/`repo` value, or a bad comment id (187, 188, 189, 192); a non-fast-forward push
after an amend (223). Every one sits in `planning-workflow.md`, `pr-feedback-workflow.md` or `dn` —
the only files that actually run commands.

Four shapes that look like this group are not in it. Rows 197, 198 and 199 turn on `gh browse <sha>
-n`, which builds its URL locally and never asks GitHub whether the commit exists (row 198), so
nothing declines a Done reply for an unpushed commit. Rows 214, 224, 228, 229 have the agent run a
command and then act on its output — a command the agent interprets is not a mechanism that refuses
it. Row 98's push to a protected `main` is declined by GitHub in *this* repository only, and a
distributed plugin cannot carry an enforced verdict on one checkout's branch-protection settings, so
it sits in U8. Rows 220 and 232 are real consumers, but they recognize rather than refuse — and 220
is capped at `unseen` besides, because the consumer is a step nothing records.

### C. A named reader is made to look — 39 rows

Three readers, none of them an `rn` step, each with an artifact the flow puts in front of them.

- **The user at a scheduled gate, reading what the gate presents** — the plan on the PR, the
  Acceptance criteria run, and the verdict recorded against their name. Rows **13, 16, 21, 69, 76,
  77, 78, 89, 103, 104, 115, 116, 119, 211, 240, 241, 246, 252** (18). This is the narrow sense of
  "the user reads it": the gate exists to make them read that artifact and answer for it, and their
  own next message is what the flow waits on. A message they merely receive is not this, and lands
  in U9. Rows 240 and 246 are the leg-(2) carve-out — a message that answers a command they just
  typed and states what is about to be done in their name.
- **The PR thread's reviewer, returning to their own thread** — `pr-feedback-workflow.md:144-145`:
  "the reviewer who opened the thread resolves it after reading the reply", and `:142-148` makes
  GitHub's unresolved state the loop's queue, so a thread that goes unanswered comes back. Rows
  **185, 186, 190, 191, 195, 197, 198, 199, 200, 201, 202, 203, 204, 206, 248, 249** (16). Row 202
  reaches the reviewer one step removed, through the coordinator's own between-item check (row 204).
- **The user meeting the result of a command they typed** — `/rn:on` returning no PR link, `/rn:up`
  reporting "No steering.md found", a resume that starts on the wrong task. Rows **79, 96, 97, 209,
  236** (5).

The coordinator is **not** a reader in this group any more. `task-verify-workflow.md:139-146` — "Read
the committed diff yourself … Confirm the change matches the task's scope and Completion criteria" —
is rows 41–44, all `unseen`: nothing records that the coordinator read anything, so its reading
cannot be what makes another rule's breach visible. The thirteen rows that used to rest on it (23,
24, 25, 29, 32, 33, 34, 35, 50, 58, 177, 179, and the check-file transcription at row 63) are in
U10.

### D. A later `rn` step consumes the artifact — 10 rows

Rows **36, 66, 67, 68, 121, 140, 196, 216, 219, 232.** Two consumers carry all ten, and each is
itself enforced, so the chain terminates:

| Consumer | Quoted at | What it makes enforceable |
|---|---|---|
| `up/SKILL.md:26` — "A commit matches a task when its message contains `complete task #{id}`" (row 232, itself read by row 69) | rows 36, 67, 68, 121, 140, 196, 219 | the completion marker, numbered task ids, and the prohibition on the substring elsewhere |
| `task-verify-workflow.md:215` — "Begin the next unchecked task" (row 69, answering to the user at the Evaluation gate) | rows 66, 216, 232 | check-off state |

Six consumers this document used to credit are gone, because each is a step nothing records having
run: `status-display.md:19-22` (row 146), `up/SKILL.md:19` and `:24` (rows 229, 231),
`dn/SKILL.md:14` and `up/SKILL.md:17` (rows 214, 228), `migration-workflow.md:28-29` (row 159, in a
workflow that has never run), `dn/SKILL.md:50-54` (row 224), and `task-verify-workflow.md:219-222`
(row 71). The rows that rested on them are in U10.

The one surviving consumer is demonstrably defective and should be treated as a finding, not an
asset: **`up/SKILL.md:26`'s grep is a prefix test and matches prose.** `git log --all --grep='complete
task #1' --oneline | wc -l` returns 16 in this repo, and 7 of those 16 are other tasks (`#1b`,
`#10`, `#11`, `#12`, `#13`, `#14`, `#16`) matched on the prefix. One commit, `de0b1ec` ("so this is
wip not 'complete task #3'"), carries a real task's substring in a body without being a marker. In
the other direction it can also find nothing: `git log --grep='complete task #1'` without `--all`
returns 0 from this worktree's `HEAD`, past markers having been squash-merged.

A second asserted consumer does not exist at all: **`migration-workflow.md:47-48`** claims Phase:
Complete gates on `Ready to check off` reading Yes, and `task-verify-workflow.md:208-209` contains no
such condition. Row 162 is enforced only in the text that asserts it.

---

## The unenforced set — the list task #2 works from

**193 rows** where a breach reaches nothing that would tell it from compliance. The ten groups
below are a partition — every `unseen` row appears in exactly one group, and
33+15+10+14+14+10+27+8+35+27 = 193 — and they are grouped by *why* nothing catches them, because the
groups need different repairs. Each group lists its rows with the `file:line` they live at and what
they say, so a worker can start on one group without searching the per-file tables above; the full
statement, the verdict and the grounds stay in those tables under the same id. Because the source
citations travel with the ids here, the five rows appended out of numeric order (250–254) are
locatable in their files from this list alone.

### U1. The review chain's internals — 33 rows

| # | Source | Rule |
|---|---|---|
| 4 | `task-execute-workflow.md:14-15` | Coordinator "Writes directly **only** `steering.md` and `checks/{task-id}.md`; never edits the deliverable or its git history" |
| 5 | `task-execute-workflow.md:16-17` | Implementation expert "Produces, fixes, and commits/pushes the deliverable" |
| 10 | `task-execute-workflow.md:26` | "All deliverable work (produce/fix/commit/push) goes to the implementation expert, every time, any size." |
| 11 | `task-execute-workflow.md:27-28` | "Each review expert runs as an independent subagent (Agent tool, no conversation history) and returns a compact summary." |
| 22 | `task-execute-workflow.md:73-75` | "Self-check is produced in Execute … reviews run in Verify; the coordinator's independent review then clears the task" |
| 27 | `task-execute-workflow.md:139-140` | The work-order must "include everything it needs and only that, with these 7 elements" |
| 28 | `task-execute-workflow.md:141` | Element 1 Task — "Purpose, Steps, Completion criteria copied from `steering.md`" |
| 30 | `task-execute-workflow.md:143-147` | Element 3 Method — "apply the task's Verification method as you build, not only after" (test-first / verify-each-claim-as-drafted / trace-as-built) |
| 31 | `task-execute-workflow.md:148-152` | Element 4 Best practices — Craft always; Design "when the task produces or revises structure/approach" |
| 37 | `task-execute-workflow.md:166-171` | Element 6 fallbacks — cannot push → say so and leave the commit, coordinator pushes; cannot commit → say so, coordinator commits mechanically with … |
| 38 | `task-execute-workflow.md:172-174` | Element 7 Return — "a compact summary only … Do not paste full file contents or trial-and-error." |
| 40 | `task-execute-workflow.md:177` | "**Dispatch the implementation expert** with the work-order and wait for its summary." |
| 46 | `task-verify-workflow.md:150-152` | Element 1 Role — review "**adversarially** … assume defects exist and try to break the artifact (boundaries, error paths, integration, missed cases)" |
| 47 | `task-verify-workflow.md:153` | Element 2 Artifact — "the full content or diff under review." |
| 48 | `task-verify-workflow.md:154` | Element 3 Criteria — "the expert checklist below." |
| 49 | `task-verify-workflow.md:155` | Element 4 — "the task's Completion criteria copied **verbatim** from `steering.md`" |
| 51 | `task-verify-workflow.md:157-159` | Element 6 Neutral framing — "**Never** pass the self-check file …, the implementation expert's summary, or any OK/NG verdict; do not defend the …" |
| 52 | `task-verify-workflow.md:162-163` | QA checklist — "the verification approach is meaningful to the actual objective … no rubber-stamped or purpose-mismatched check" |
| 53 | `task-verify-workflow.md:164-166` | Design checklist — "does the approach/structure fit; separation of concerns; system-wide integrity (interface contracts, API compatibility, cross-doc …" |
| 54 | `task-verify-workflow.md:167-170` | Craft checklist — coding: "naming, error handling, null/thread safety", no duplication, style consistency; writing: "prose clarity and correctness …" |
| 55 | `task-verify-workflow.md:171-175` | Verification checklist — test: "meaningful and in GWT (Given/When/Then) format" covering edge cases; fact-check: "every claim/reference verified …" |
| 56 | `task-verify-workflow.md:176` | "**Triage every finding.** Each ends in exactly one of" Valid / Invalid / Escalation |
| 57 | `task-verify-workflow.md:177-178` | "**Valid** → fix it. Dispatch the implementation expert (fresh subagent) — every deliverable-touching fix, no matter its size, including minor …" |
| 59 | `task-verify-workflow.md:181-183` | "re-run the same review expert; if the fix could affect a dimension another expert already cleared, re-run that expert too. Cap at 3 iterations … …" |
| 60 | `task-verify-workflow.md:184-185` | "**Invalid** → reject it, citing evidence. Invalid **only** when it rests on a factual error or falls outside a scope boundary written in the …" |
| 61 | `task-verify-workflow.md:186-189` | "Escalate **only** when the decision is genuinely the user's … "It's minor, so I'll just ask" is not a reason." |
| 62 | `task-verify-workflow.md:191` | "Never silently drop, blindly accept, or bounce a finding for lack of a standard." |
| 63 | `task-verify-workflow.md:191-192` | "Record the review verdicts into the check file." |
| 182 | `pr-feedback-workflow.md:3-4` | "A **coordinator** dispatches one **execution subagent** per review thread, sequentially, and reviews each result before the next." |
| 183 | `pr-feedback-workflow.md:4-7` | "Verification is a single coordinator pass — not the QA-expert / multi-round chain" |
| 193 | `pr-feedback-workflow.md:86-87` | "Process the queue **one thread at a time**. Never dispatch two threads in parallel" |
| 194 | `pr-feedback-workflow.md:89-92` | Work-order contents: Thread (`path`, `line`, full bodies, `databaseId`) and Task ("produce exactly one of the two outcomes") |
| 207 | `pr-feedback-workflow.md:152-153` | "One coordinator pass per item … is the whole of verification. No QA expert, no Design / Craft / Verification experts, no multi-round iteration cap." |

Every rule about *how* a review or a dispatch is produced: that the work went to a subagent rather
than to the coordinator's own hand (rows 4 and 5, the two halves of the authorship boundary), that
it carried no conversation history, that it was told to be adversarial, that it got the full
artifact, that the completion criteria were copied verbatim, that it was **not** shown the
self-check or any prior verdict (`task-verify-workflow.md:157-159` — the review-independence rule),
that each expert checklist was applied, that findings were triaged rather than dropped, that the
3-iteration cap held. All of it lives in prompts that are never written to disk, so a review that
never ran, a review that ran primed, and a good review produce the same artifact.

It is the second-largest group after U9, and it holds every rule protecting the integrity of the
mechanism that is supposed to protect everything else.

### U2. The per-task reviews and their placement — 15 rows

| # | Source | Rule |
|---|---|---|
| 6 | `task-execute-workflow.md:18` | "**QA expert** (every task) — subagent." |
| 7 | `task-execute-workflow.md:19-20` | "**Design expert** (tasks that produce or revise structure/approach)" |
| 8 | `task-execute-workflow.md:21-22` | "**Craft expert** (per medium: coding / writing / visual)" |
| 9 | `task-execute-workflow.md:23-24` | "**Verification expert** (per medium: test / fact-check / dry-run)" |
| 19 | `task-execute-workflow.md:53-57` | "QA always spawns for a task that builds something; a sign-off task spawns none. Craft and Verification spawn for the task's medium. Design spawns …" |
| 20 | `task-execute-workflow.md:59-64` | The three build-task instances — Code, Docs, Visual — each run the same chain (paraphrase; the file spells the medium out per instance, e.g. … |
| 45 | `task-verify-workflow.md:147-149` | "**Dispatch the review experts as independent subagents** — QA always; Craft and Verification for the task's medium … Design when the task produces …" |
| 92 | `planning-workflow.md:35` | "Define each task following the template's `Tasks` structure, inline `Completion criteria` rules, and `Task definition requirements` table in full." |
| 124 | `steering-template.md:67` | Steps include "self-check (OK/NG per completion criterion, record in checks/{task-id}.md)" as a `- [ ]` item |
| 125 | `steering-template.md:68` | Steps include "QA expert review (subagent)" |
| 126 | `steering-template.md:69` | Steps include "Craft expert review (subagent, per the task's medium)" |
| 127 | `steering-template.md:70` | Steps include "Verification expert review (subagent, per the task's medium)" |
| 128 | `steering-template.md:71` | Steps include "(tasks that produce or revise structure/approach only) Design expert review (subagent)" |
| 139 | `steering-template.md:104` | Criteria vs steps: criteria answer ① and ② with grounds, "not that an artifact was produced; actions, reviews, and gates go in Steps as `- [ ]` so …" |
| 251 | `task-execute-workflow.md:179` | "Once the expert returns, continue to `task-verify-workflow.md`." |

The mandated per-task reviews and the rules that place them. Empirically the least-observed rules in
the plugin: a Verification section appears in 5 of the 40 past check files and Craft in 11. The two
axes fail differently. Craft was simply never adopted before `20260625-rn-lean` (0 of 20 check files
in the five sessions before it), then adopted wholesale — 5 of 14 in `rn-lean`, 6 of 6 in
`20260705-improve-design-template`, which also writes a Craft step into 6 of its 7 tasks.
Verification appears in 5 of `rn-lean`'s 14 files and nowhere else at all:
`20260705-improve-design-template` writes the step into none of its 7 tasks and closed approved.
`steering-template.md:67-71`'s Steps checklist would be a mechanism — an unchecked box is a visible
blank — but only for a step planning actually wrote. The failure is at authoring time, not execution
time, and `planning-workflow.md:38`'s pre-persist self-check covers only the Evaluation sign-off
task. Row 139's "keep the two in sync" names no mechanism and the two are provably out of sync.

### U3. The shape of task criteria — 10 rows

| # | Source | Rule |
|---|---|---|
| 117 | `steering-template.md:42` | "two axes: goal alignment + quality" |
| 118 | `steering-template.md:43` | "write these exhaustively, never sample — the complete set is what defines scope (in / out)" |
| 122 | `steering-template.md:59` | "**Purpose**: what to achieve, 1-2 sentences" |
| 129 | `steering-template.md:75-76` | Completion criterion ①: "is the objective achieved? — the objective met, not that an output was produced (write "the residue no longer keeps the tree … |
| 130 | `steering-template.md:77` | Criterion ②: "are new problems absent? — name the representative failure modes and require their absence" |
| 131 | `steering-template.md:78` | "objectively verifiable by a third party; no vague terms ("appropriate", "correct")" |
| 132 | `steering-template.md:79` | "state the end-state, never actions/reviews/gates (those belong in Steps); the grounds are recorded at verification … not written into the criterion …" |
| 135 | `steering-template.md:100` | Granularity: "Purpose expressible in one sentence; split if it grows" |
| 136 | `steering-template.md:101` | Specificity: "Not "implement" but "implement `methodName()` in `ClassName`"" |
| 137 | `steering-template.md:102` | Objectivity: "Completion criteria judgeable by a third party" |

The ①/② phrasing, "the objective met, not that an output was produced", "no vague terms",
exhaustiveness, and the Granularity / Specificity / Objectivity rows of the `Task definition
requirements` table. This is the group the session's Goal names — the specimen proper: the rule was
correct, sat in the template, and was broken in the very next session. The missing Verification
review (U2) is the second instance of the same mechanism, not the same failure. One asymmetry to fix
while rebuilding: `steering-template.md:75-79` states the bar for **Completion** criteria only;
`:41-43` states nothing of the kind for **Acceptance** criteria — and the breach landed on the
Acceptance criteria (`.rn/20260705-improve-design-template/steering.md:22-49`, 9 of 10 written as
artifact existence).

### U4. The whole of `design.md` — 14 rows

| # | Source | Rule |
|---|---|---|
| 166 | `design-template.md:3-5` | "Read when creating a session's `design.md` … **Not read at runtime**: it records decisions and how the parts fit" |
| 167 | `design-template.md:7-9` | "The h2 sections below are the canonical design-document sections; under each, the h3 headings are the questions that section must answer — a section …" |
| 168 | `design-template.md:13-14` | "This is the fresh-authoring path … to update an existing one, skip to "Updating an existing design.md"" |
| 169 | `design-template.md:16-17` | "**Copy the template block below verbatim.** Keep every heading, numbering, and section order — the five h2 sections and the h3 questions under them …" |
| 170 | `design-template.md:19-22` | "**Answer every h3 question with a decision and the reasoning behind it** … If a question does not apply, say so **and say why** … Nothing here …" |
| 171 | `design-template.md:23-24` | "**In Detailed design, repeat `4.N` once per mechanism or component the design introduces** — not a fixed four" |
| 172 | `design-template.md:25-28` | "**Treat the whole document as optional, not any section within it.** … once you are writing one, no section may be skipped for having "nothing to … |
| 173 | `design-template.md:32-75` | The template block — five h2 sections with their h3 questions, and the header line "Not read at runtime — for whoever maintains the design" |
| 174 | `design-template.md:81-96` | Per-section guidance, including: every `4.N` "asks the same pair of questions of its mechanism: what does it guarantee, and how is a breach of that …" |
| 175 | `design-template.md:100-102` | "Follow this instead of the Steps above when `planning-workflow.md`'s location check (Step 2) points `Design:` at an existing `design.md`" |
| 176 | `design-template.md:104-105` | "**Read the existing document in full before touching it.** Identify which h3 questions the session's work actually changes" |
| 178 | `design-template.md:109-111` | "**The decision-plus-reasoning contract from fresh authoring still applies to whatever you touch.**" |
| 180 | `design-template.md:127-137` | "**Give genuinely open content a destination outside `design.md`.** … Session-scoped: put it in that session's `steering.md` Notes field … …" |
| 181 | `design-template.md:138-139` | "**Add or drop `4.N` subsections to match what changed** … a new mechanism gets a new subsection, a removed one loses its subsection instead of being …" |

`design-template.md:4` says outright "**Not read at runtime**". The document has no consumer in the
flow: only a Design sign-off gate presents it, and that task exists only if planning placed one (row
93, itself unenforced and absent from 7 of 8 sessions). The template's own contract — "What does
<mechanism> guarantee, and how is a breach caught?" (`design-template.md:68`) — is exactly the
question this inventory asks, and nothing checks that a `4.N` answers it truthfully.

### U5. Content allocation, doc division, and the migration judgments — 14 rows

| # | Source | Rule |
|---|---|---|
| 88 | `planning-workflow.md:33` | "Read the doc-division rule … and `…/references/design-template.md`, then **allocate content at planning** per the doc-division" |
| 109 | `steering-template.md:15` | Doc-division: "**Requirements & acceptance criteria → `steering.md`**" |
| 110 | `steering-template.md:16` | "**Structure & decisions (how the parts fit, and why) → `design.md`** … rationale lives only here, at the decision level." |
| 111 | `steering-template.md:17` | "**User-facing UX → `README`**" |
| 112 | `steering-template.md:19` | "A decision lands in a task, in `design.md`, or in a rule. Deliberation and history live in git + the PR — never in steering." |
| 120 | `steering-template.md:48` | "distinguish facts from assumptions — state explicitly if unverified" |
| 123 | `steering-template.md:61` | "**Prerequisites**: tasks that must be completed first (or "none")" |
| 138 | `steering-template.md:103` | Prerequisites: "List dependencies explicitly; enables parallel/sequential judgment" |
| 157 | `migration-workflow.md:15-18` | "Reconcile the three artifacts below **in this order** — steering, then design, then tasks." |
| 158 | `migration-workflow.md:20-25` | Step 1: "Compare the session's `steering.md` … against the current `steering-template.md`. Judge by reasoning what has drifted … and edit …" |
| 159 | `migration-workflow.md:27-31` | Step 2: "Read the session's `steering.md` `Design:` line; if it is absent … skip this step entirely. If present, follow `design-template.md`'s own …" |
| 160 | `migration-workflow.md:33-38` | Step 3: "For every unchecked task … judge its Purpose / Prerequisites / Steps / Completion criteria against each row of that table — Granularity …" |
| 161 | `migration-workflow.md:39-40` | "Leave every already-checked-off task untouched — reconciliation targets the forward-looking remainder, not the record of what already happened." |
| 163 | `migration-workflow.md:56-58` | "Apply the reconciling edits from all three steps and commit them directly. This is not one of the three scheduled gates … and it does not go through …" |

Which file a piece of content belongs in; that assumptions are separated from facts; that
prerequisites are listed; the reconciliation judgments in `migration-workflow.md`'s three steps.
Misallocated content simply sits in the wrong place and reads normally. **Rows 123 and 138 are the
extreme case: nothing consumes `Prerequisites` at all** — `task-verify-workflow.md:215` advances to
"the next unchecked task" by position, never by dependency — so a declared prerequisite has no
effect on anything in the system.

### U6. Version stamping and migration triggering — 10 rows

| # | Source | Rule |
|---|---|---|
| 86 | `planning-workflow.md:33` | "Stamp the template's top `Rn version:` line with the currently installed plugin's version — read from … …" |
| 113 | `steering-template.md:21-24` | "`Rn version:` … is written once, at creation, from the installed plugin's version — never user-edited afterward" |
| 155 | `migration-workflow.md:3-6` | "Invoked by a command skill (`on`/`dn`/`up`/`ty`/`gm`) when the active session's `steering.md` `Rn version:` line does not match the installed …" |
| 164 | `migration-workflow.md:59-61` | "Once the reconciling edits are committed, update the session's `steering.md` `Rn version:` line to the installed plugin's version — the last step …" |
| 165 | `migration-workflow.md:65-70` | "Every comparison above asks one question only: does this artifact match what the **currently installed** templates/workflows require, right now. …" |
| 210 | `on/SKILL.md:15` | "**Check version.** … on a mismatch, run `…/references/migration-workflow.md` first — on a match, do nothing. Since step 1 just stamped that line …" |
| 215 | `dn/SKILL.md:18-20` | "**Check version.** Compare `steering.md`'s `Rn version:` line to the installed plugin's version … on a mismatch, run …" |
| 235 | `up/SKILL.md:32` | "**Check version.** … on a mismatch, run `…/references/migration-workflow.md` first — on a match, do nothing." |
| 239 | `ty/SKILL.md:13` | "**Check version.**" |
| 245 | `gm/SKILL.md:13` | "**Check version.**" |

The `Rn version:` stamp is absent from 6 of 8 past sessions, and its consumer is "a plain string
comparison" (`migration-workflow.md:5`) that no file defines for a missing line — so an un-stamped
session silently reads as up to date, forever. `on/SKILL.md:15` documents that its own copy of the
check says "this branch can never actually fire here". The reconciliation the trigger guards (rows
157, 158, 160, 164, 165) is itself an unrecorded judgment.

### U7. Breaches with no possible trace — 27 rows

| # | Source | Rule |
|---|---|---|
| 1 | `task-execute-workflow.md:5` | "`on` and `up` read both files at task execution, this one first" |
| 2 | `task-execute-workflow.md:5` | "Run one task at a time." |
| 3 | `task-execute-workflow.md:7-8` | "Write check files under `{steering_dir}/checks/`." |
| 18 | `task-execute-workflow.md:47-49` | Escalation is "a separate always-open channel — not a gate; an escalation message opens with the session-status block" |
| 39 | `task-execute-workflow.md:175-176` | "**Capture the task's starting commit** — current `HEAD` … Capture it **once**; do **not** re-capture on fix rounds." |
| 41 | `task-verify-workflow.md:139` | "**Read the committed diff yourself.**" |
| 42 | `task-verify-workflow.md:140-143` | "Expect `git status` to show **only** that tracked check file — that is normal, not a deliverable change." |
| 43 | `task-verify-workflow.md:144-145` | "Inspect the committed deliverable: `git show <sha>` … or `git diff <task's starting commit>..HEAD`" |
| 44 | `task-verify-workflow.md:146` | "Confirm the change matches the task's scope and Completion criteria before spending review experts." |
| 64 | `task-verify-workflow.md:194-200` | "**Escalation is an always-open channel, not confined to triage.**  … raised to the user **immediately, wherever it surfaces** … never deferred to a …" |
| 71 | `task-verify-workflow.md:219-222` | "If no unchecked tasks remain and no "Evaluation sign-off" task was ever encountered … that is a planning defect … escalate to the user immediately … …" |
| 83 | `planning-workflow.md:21-26` | "**Check for an existing design.md first.** … This is a judgment call on scope overlap, not a mechanical file-existence check." |
| 85 | `planning-workflow.md:33` | "Read `${CLAUDE_PLUGIN_ROOT}/references/steering-template.md` and follow its per-section guidance." |
| 91 | `planning-workflow.md:35` | "Work backwards from the Acceptance criteria end state" |
| 95 | `planning-workflow.md:38` | "**Self-check before persisting.** Before persisting (Step 5), confirm the last task in the list is "Evaluation sign-off" — if it is not, add it …" |
| 105 | `steering-template.md:3` | "Read when creating a new `steering.md`." |
| 145 | `status-display.md:17-18` | "**Derive the block fresh from the active `steering.md` at emit time** — its `Goal`, task list, and check-offs are the only source; never reuse an …" |
| 184 | `pr-feedback-workflow.md:9-10` | "Entered from `/rn:gm` with no argument — the argument/no-argument routing rule lives in `gm/SKILL.md`." |
| 214 | `dn/SKILL.md:13-16` | "**Locate steering.md.** Use the path known from this session. If unknown: run …" |
| 222 | `dn/SKILL.md:44` | "Never delete a file yourself." |
| 224 | `dn/SKILL.md:50-54` | "**Verify clean.** Run `git status --porcelain` … Non-empty → for each remaining (non-gitignored) untracked path, if its exact … string is not …" |
| 227 | `up/SKILL.md:13-15` | "**Handle a dirty tree.** … Tree dirty → run step 2's discovery first, read-only … then propose a `wip:` commit or a discard, opening the message …" |
| 228 | `up/SKILL.md:17` | "**Find steering.md.** Run `git log --diff-filter=AM --name-only --pretty=format: -- '*/steering.md' \| head -5` and keep the paths that exist on …" |
| 229 | `up/SKILL.md:18-20` | "One result → use it. … Multiple → rank by `State` showing `Status: paused`, then most recent commit, and propose the top candidate. … Zero → tell …" |
| 231 | `up/SKILL.md:24` | "**Read State.** Read the `State` section: last completed task, next task, and notes." |
| 250 | `task-verify-workflow.md:4-5` | "`on` and `up` read both files at task execution, this one second." — the counterpart of row 1, and the one line of the shared header that differs … |
| 253 | `planning-workflow.md:26-28` | "Coverage need not be complete: if an existing design.md covers the core of the work's area, treat it as the update target and record the session's …" |

The breach here leaves nothing to look at: that a file was read (1, 85, 105), that a judgment was
made (44, 83, 91, 95), that an escalation *should* have fired and did not (18, 64, 71), that a
status block was derived fresh rather than reused (145), that a starting SHA was captured once and
not re-captured (39, 43), that the coordinator's own `git status` and diff-read happened at all (41,
42), that two tasks ran in sequence rather than together (2), and `dn/SKILL.md:44`'s "Never delete a
file yourself" (222) — a deleted untracked file leaves no residue in git, in `git status`, or
anywhere else. Seven of them (184, 214, 224, 227, 228, 229, 231) are the same shape one step further
out: they instruct the agent to run a command, read a file, or take a branch, and the only evidence
the step happened is that the agent proceeded as though it had. **Adding a reader cannot fix these;
the rule has to be restated as something that produces an artifact, or dropped.**

Rows **41–44, 63, 71, 214, 229 and 231** carry a second load beyond their own: they are the reader
steps the 27 rows of U10 rest on. Fixing them is worth 34 rows, not 8.

### U8. Single cases — 8 rows


| # | Source | Rule |
|---|---|---|
| 26 | `task-execute-workflow.md:86-135` | The check-file format block — five columns, `## QA Expert Review`, three expert sections, `## Overall Verdict` with five verdict lines and … |
| 80 | `planning-workflow.md:15-17` | Slug candidates: the current git branch, an issue reference in `$ARGUMENTS`, a kebab-case name from the goal |
| 93 | `planning-workflow.md:36` | "**Design sign-off task.** When the session has a `design.md` not settled at plan time, place a **"Design sign-off"** task … at the point where heavy …" |
| 98 | `planning-workflow.md:43` | "Ensure the work is on a branch — if on the default branch, create `{slug}` first." |
| 102 | `planning-workflow.md:49` | "**Design gate.** … When the design is settled at plan time, fold it into this plan-gate approval (one stop). When it is not, Step 4 placed a …" |
| 108 | `steering-template.md:9` | "**Fill each section per the rules below.**" |
| 162 | `migration-workflow.md:41-52` | For a task whose Completion criteria changed and that has a `checks/{task-id}.md`: "record in its Overall Verdict a …" |
| 254 | `planning-workflow.md:36-37` | The two sign-off tasks' prescribed content — Design sign-off: "Completion criteria: `design.md` is approved. Steps: present `design.md` to the user …" |

Three worth naming:

- **Rows 26 and 162** — the check file's `## Overall Verdict` block, and
  `migration-workflow.md:47-48`'s claim that Phase: Complete gates on `Ready to check off` reading
  Yes. It does not: `task-verify-workflow.md:208-209` contains no such condition, and row 26 records
  what that cost. This is an enforcement asserted in prose that does not exist in the file it cites.
  Row 258 is the second of the pair: `task-execute-workflow.md:46-47` says per-task quality "is
  caught by self-check + QA/expert review + the coordinator's independent review", and rows 6–9,
  32–33 and 41–45 say none of those three catches anything.
- **Row 93** — the Design sign-off task has no equivalent of the Evaluation sign-off's backstop
  (`task-verify-workflow.md:219-222`), so its absence is invisible. The Evaluation sign-off's
  backstop is row 71, itself `unseen` and never exercised, so the asymmetry buys less than it looks.
- **Row 98** — "Ensure the work is on a branch". GitHub declines a direct push to `main` in this
  repository, under a branch-protection ruleset the plugin neither ships nor requires. Installed on
  an unprotected repo, `rn` has nothing here at all — which is why the verdict is `unseen` rather
  than `refuses`.

### U9. Output on the user's screen with no auditor — 35 rows

| # | Source | Rule |
|---|---|---|
| 12 | `task-execute-workflow.md:32` | "The user signs off at exactly **three** scheduled gates, never on any other task" |
| 14 | `task-execute-workflow.md:35-37` | "**Design gate** — sign-off on the approach / key decisions before they are built on" |
| 17 | `task-execute-workflow.md:44-46` | "The per-task boundary is **not** a user gate for ordinary build tasks" |
| 65 | `task-verify-workflow.md:204-206` | "There is no per-task user gate for a normal task: once Verify clears … the coordinator checks the task off directly." |
| 70 | `task-verify-workflow.md:217-219` | "If no unchecked tasks remain and the Evaluation sign-off was approved, the session closes — open that session-close report with the session-status …" |
| 73 | `planning-workflow.md:10` | "Treat every user interaction as a proposal: lead with one concrete recommended option in plain language (no internal jargon), and proceed on …" |
| 74 | `planning-workflow.md:10` | "`AskUserQuestion` is fine when one option is your recommendation." |
| 75 | `planning-workflow.md:10` | "At a stop that instructs opening with the session-status block, the block precedes the proposal." |
| 81 | `planning-workflow.md:19` | "Propose one recommended slug plus the alternatives … When already on a non-default branch, recommend that branch's name as the slug." |
| 82 | `planning-workflow.md:21` | "Alongside the slug, decide the session's `design.md` location with the user." |
| 100 | `planning-workflow.md:44` | "The PR body is a single link to the steering file and nothing else — do not copy the Goal, tasks, or any plan content into it. Use a branch-ref blob …" |
| 101 | `planning-workflow.md:45-48` | "Open the plan-gate ask with the session-status block … on both branches: push and PR creation succeeded → report the PR link and ask the user to …" |
| 142 | `status-display.md:3-5` | "The compact session map that opens every message stopping for user input while a session is active … The block comes first in that message — before …" |
| 143 | `status-display.md:9-12` | "**Emit only while a session is active** — its `steering.md` exists and is identified." with the listed exceptions (planning's pre-persist asks … |
| 144 | `status-display.md:13-16` | "**Asks and flow-ending reports both count as stops** … on a report the 👉 line states where the session stands and the user's next move instead of an …" |
| 146 | `status-display.md:19-22` | "**A task counts ✅ when `steering.md` records it complete** — checked off, or carrying an explicit done annotation … Done-but-awaiting … still counts …" |
| 147 | `status-display.md:23-24` | "**Write the block in the user's conversation language.**" |
| 148 | `status-display.md:25` | "**Markers are fixed**: ✅ completed / 👉 current / ⬜ remaining." |
| 149 | `status-display.md:29-35` | The format block — header / ✅ / 👉 / ⬜ / outlook, in that order |
| 150 | `status-display.md:37-38` | "**Header** — `── {slug}: {goal one-liner} ──`: the session's slug (the steering directory name, date prefix dropped) and a one-line compression of …" |
| 151 | `status-display.md:39-42` | "**✅ completed** … Group consecutive ids into ranges … comma-separate non-consecutive groups … No completed tasks yet → no ✅ lines." |
| 152 | `status-display.md:43-48` | "**👉 current** — exactly one line … A stop not tied to a numbered task (the plan gate; an escalation that spans tasks) names the gate or moment …" |
| 153 | `status-display.md:49-50` | "**⬜ remaining** … **No remaining tasks → omit the ⬜ lines entirely** — never render an empty ⬜ section." |
| 154 | `status-display.md:51-52` | "**Outlook** — one closing parenthesized line: what follows this stop" |
| 156 | `migration-workflow.md:8-11` | "Coordinator only: no implementation expert, and no QA/Design/Craft/Verification review, spawns for this procedure itself … The coordinator reads …" |
| 205 | `pr-feedback-workflow.md:136-138` | "When the queue is empty, the loop is done — report the loop result … opening that report with the session-status block" |
| 213 | `dn/SKILL.md:9` | "Records resume state and hands off. Does not execute tasks." |
| 218 | `dn/SKILL.md:29-32` | "**Commit the work.**" — "Tree clean → skip this commit. … Current task's steps all checked → commit normally. … Some steps unchecked → commit with a …" |
| 225 | `dn/SKILL.md:56-59` | "**Report.** Open the report with the session-status block … then output the branch name. If the last push did not succeed, state that the commits …" |
| 230 | `up/SKILL.md:22` | "From step 3 on, any message stopping for user input opens with the session-status block" |
| 233 | `up/SKILL.md:28` | "**Check blockers.** If `State` notes mention a blocker, investigate and find an alternative approach before removing any task." |
| 238 | `ty/SKILL.md:9` | "Approves the pending rn confirmation and advances the flow. Performs no revision." |
| 242 | `ty/SKILL.md:19-24` | "**Advance the workflow.** … a plan or design gate passes — execution proceeds to the next task; … an evaluation gate passes — the session can close …" |
| 243 | `ty/SKILL.md:26` | "**Nothing pending.** If nothing is actually awaiting approval, open the reply with the session-status block …, say so, and do nothing else." |
| 247 | `gm/SKILL.md:17` | "**With feedback (`$ARGUMENTS` present).** Treat `$ARGUMENTS` as a revise verdict on the pending item … If there is no pending item, treat …" |

This group is what the tightened `recognized` test created, and it is the largest of the ten. Every one of these rules produces something the user could in principle see — a
status block, a proposal, a report, a PR body, a commit on the branch — and none of them produces a
reader who is looking at it *against the rule*. Twelve of them are `status-display.md`'s output
contract (142–144, 146–154): the file's own product is a block the user reads, and no `rn` step ever
compares an emitted block to the `steering.md` it was supposed to be derived from. That file's
thirteenth rule (145) is unenforced too — it sits in U7, since a block derived fresh and one reused
differ in nothing. Six more are planning's proposal rules (73–75, 81, 82, 101), where a proposal
made without alternatives is indistinguishable from one made with them.

The repair these need is different from every other group's. Where U1–U8 lack an artifact, U9 has
the artifact and lacks the occasion to read it. A rule here becomes enforceable by naming a moment
at which someone is required to hold the output up against the rule — which is what the gates
already do for `Goal`, `Acceptance criteria` and `Assumptions` (group C), and what nothing does for
the block, the proposals, or the reports.

### U10. Enforced only if a step nothing records actually runs — 27 rows

| # | Source | Rule |
|---|---|---|
| 15 | `task-execute-workflow.md:38-39` | "**Evaluation gate** — the end-of-session run of the `steering.md` Acceptance criteria" |
| 23 | `task-execute-workflow.md:79-81` | "the implementation expert writes **only** the Completion Criteria Self-check and Evidence columns (and the Overall Verdict "Self-check" line)" |
| 24 | `task-execute-workflow.md:79-83` | "Column ownership holds across every round, including fix rounds" — the expert writes "never the review-verdict sections (QA / Expert Review / other …" |
| 25 | `task-execute-workflow.md:82-84` | "The expert does not commit it. The coordinator … commits the file as part of its ledger — on the post-Verify steering check-off commit." |
| 29 | `task-execute-workflow.md:142` | Element 2 Scope — "stay within this task; do not start adjacent tasks; name the files expected in play" |
| 32 | `task-execute-workflow.md:153-157` | Element 5 Self-check — verify each completion criterion OK/NG with specific evidence, and confirm the Method was applied (coverage measured / every … |
| 33 | `task-execute-workflow.md:157-161` | Element 5 — write to `{steering_dir}/checks/{task-id}.md` filling **only** the self-check columns; "Never write or overwrite the review-verdict …" |
| 34 | `task-execute-workflow.md:161` | Element 5 — "**Do not commit the file.**" |
| 35 | `task-execute-workflow.md:162-163` | Element 6 — "stage the deliverable paths explicitly (`git add <path>…`); never `git add -A` or `git add .`" |
| 50 | `task-verify-workflow.md:156` | Element 5 Output format — "OK/NG per criterion with concrete evidence, plus an overall pass/fail" |
| 58 | `task-verify-workflow.md:179-181` | Reuse the original work-order; "point it at the current on-disk state to build on (not regenerate)"; fix commits accumulate, "never force-pushed" |
| 84 | `planning-workflow.md:28-31` | "If one covers the area, point this session's `Design:` line at it and treat the work on it as an update — following design-template.md's "Updating … |
| 87 | `planning-workflow.md:33` | "Write the chosen design.md path into the template's `Design:` line below it." |
| 90 | `planning-workflow.md:33` | "**Force no empty `design.md`**: a session with no design to record creates no `design.md` and omits the `Design:` line entirely (no file, no …" |
| 94 | `planning-workflow.md:37` | "**Evaluation sign-off task.** Always place a final **"Evaluation sign-off"** task as the session's last task." |
| 106 | `steering-template.md:7` | "**Copy the template block below verbatim.** Keep every heading. Keep the blank lines between fields" |
| 107 | `steering-template.md:8` | "**Leave placeholders in unpopulated sections.** `Tasks`, `State` start empty; fill later." |
| 114 | `steering-template.md:26-27` | "The `Design:` line below it points to the session's `design.md`. A session with no design omits this line entirely" |
| 133 | `steering-template.md:83-85` | `State` placeholder: "`Status` is `paused` while a session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` …" |
| 134 | `steering-template.md:91` | `Notes`: "bounded forward pointer … not a re-narration of the session (that lives in `git log`)" |
| 141 | `steering-template.md:106` | Done annotation: "A task that is done but awaiting an external gate … may carry an explicit done annotation in its heading … such a task counts as …" |
| 177 | `design-template.md:106-108` | "**Revise only what changed.** … leave every other section's existing text untouched. Carrying forward unchanged text is correct, not lazy" |
| 179 | `design-template.md:112-126` | "**If the document predates the five-section shape** … reconcile it toward the current five-section shape as part of this update … relocating content …" |
| 217 | `dn/SKILL.md:25-27` | "**Write the `State` section** per `steering-template.md`'s State placeholder: `Status: paused`, `Date`, `Last completed`, `Next`, `Notes` — cap …" |
| 220 | `dn/SKILL.md:35-39` | "**Resolve untracked residue.** Run `git status --porcelain` … Regenerable test/build artifact … → append a matching rule to the repo-root …" |
| 221 | `dn/SKILL.md:40-43` | "Anything else → ask the user how to handle it … opening the message with the session-status block … For any path the user does not resolve, append …" |
| 234 | `up/SKILL.md:30` | "**Clean up State.** Replace the `State` section with its template placeholder and commit the reconciliation." |

Every row here names a real reader and a real artifact. What it cannot name is anything that says the
reading happened. Five reader steps carry all 27:

| The reader | Its own row | Rows that rested on it |
|---|---|---|
| The coordinator's diff read and `git status` — `task-verify-workflow.md:139-146` | 41, 42, 43, 44 | 25, 29, 34, 35, 58, 177, 179 |
| The coordinator transcribing verdicts into the check file — `task-verify-workflow.md:191-192` | 63 | 23, 24, 32, 33, 50 |
| The `Design:` read in `migration-workflow.md:27-31`, in a workflow that has never run | 159, 155 | 84, 87, 90, 114 |
| `up`'s candidate ranking and `State` read — `up/SKILL.md:19`, `:24`; `dn/SKILL.md:15-16` | 214, 229, 231 | 106, 107, 133, 134, 217, 220, 221, 234 |
| The Evaluation-sign-off backstop — `task-verify-workflow.md:219-222`, itself `unseen` | 71 | 15, 94 |
| The status block's ✅-membership rule — `status-display.md:19-22`, read by no one but the user | 146 | 141 |

The repair is the opposite of U9's. U9 has the artifact and lacks the occasion to read it; U10 has
the occasion, named and mandated, and lacks any trace that it was taken. Making one of these five
steps write a line — which file was read, what the diff showed, which candidate was ranked first —
would move most of the 27 back across the boundary at once, and none of them needs a new reader.
Two of the five have standing proof they went untaken: `.rn/20260615-subagent-execution/steering.md:340`
still reads `- **Status**: paused` today, and `migration-workflow.md`'s reconciliation has never
fired at all (row 155).

### Outside the 193: the rule that was never written

The 131 lines the two task-workflow files share verbatim carry **no rule anywhere requiring they
stay in sync**, and no mechanism if there were one. This is deliberately not one of the 193 and not
one of the 254: the 254 are statements `rn` makes, and this is a statement `rn` does not make, so it
has no `file:line` to be cited at and no breach to judge. It is recorded here so task #2 does not
lose it — it is a rule to write, where every row in the nine groups above is a rule to rebuild.
The Design expert on the task that created it did flag it (`.rn/20260625-rn-lean/checks/12.md`: "a
standing drift risk against the repo's own anti-duplication principle — noted, not actioned"), and
the finding was closed as an accepted tradeoff. The review worked; nothing turned its outcome into a
rule, so the drift risk it named is now unguarded and invisible.

---

## What each unconditionally mandated step catches

**What counts.** A step is unconditionally mandated when `rn` runs it on every instance of its kind
with no discretion about the *size* of the change. Several carry a dimension condition instead — the
task's medium, whether the task touches structure/approach, whether `/rn:gm` was given an argument —
and those stay in scope, because a dimension is not a size: `rn` states no rule permitting any of
them to be skipped for a small change, which is the question this section asks. The few steps that
fire only on a state a session may never reach are marked conditional where they appear.

**What is inventoried.** Sixty-one steps, in five tables: fifteen bind every build task (four
reviews plus eleven others), eight are planning's, twenty-four belong to the five command skills,
twelve are the PR-feedback loop's, and two run across everything. Each carries the row ids that
state it, so the set can be checked against the per-file tables above rather than taken on trust.
For each: what it catches that nothing else in the structure would, and whether it earns that on a
small change.

### Of the four per-task reviews, only QA earns its place regardless of the change

| Step | Mandated at | Rows | What only this catches | Earns its cost on a small task? |
|---|---|---|---|---|
| **QA** (every build task) | `task-execute-workflow.md:18`, `:55`; `task-verify-workflow.md:147` | 6, 19, 45 | Not the verbatim criteria — element 4 of the review prompt hands those to **every** expert (`task-verify-workflow.md:155`, built per `:147-149`). What is QA's alone is the bar it applies to them: whether the verification approach is meaningful to the objective, "not just 'it ran'/'it passed'" (`:162-163`), and `task-execute-workflow.md:103`'s designation of QA as "the per-criterion gate" while the other three "assess the aspects below, not each completion criterion". Execute element 5 also reads criterion against artifact (`task-execute-workflow.md:153-161`), but it is written by the agent that built the artifact; QA is the only *independent* per-criterion read. | **Yes, at any size.** It is the only adversarial read of the criteria, and the criteria are the contract. Cheapest of the four to justify. |
| **Craft** (per medium) | `task-execute-workflow.md:21-22`; `task-verify-workflow.md:167-170` | 8, 19, 45 | The only reviewer looking at *how* the artifact is written rather than whether it is right: naming, error handling, duplication; prose clarity and "consistency with the doc's existing voice/terminology". Nothing else in the structure ever mentions style, and voice drift accumulates silently across a plugin whose entire product is prose. | **Not always.** On a rename, a version bump, or a one-line correction it returns wording nits — the past record bears this out ("round 1 found 2 valid Craft findings", `.rn/20260625-rn-lean/checks/12.md`). It earns its place on any task producing prose a user will read, and not on a mechanical edit. `rn` offers no way to say so. |
| **Verification** (per medium) | `task-execute-workflow.md:23-24`; `task-verify-workflow.md:171-175` | 9, 19, 45 | The distinction from QA is real and is this session's subject: **QA judges the approach, Verification judges the doing.** It is the only step asking whether every claim was actually checked against its source, whether tests are in GWT form and cover boundary/error/empty/max cases, whether the flow was traced step by step. A self-check can assert "verified"; only this step re-derives it. | **Yes on any claim-bearing or behavior-bearing artifact; near-worthless on a change already proven by a grep or a green test the coordinator can see in the diff.** It was dropped from 35 of 40 past tasks. Most of those were of the second kind, where its absence cost nothing — which is also why its absence from tasks of the first kind went unremarked. |
| **Design** (conditional, structure/approach only) | `task-execute-workflow.md:19-20`, `:56-57`; `task-verify-workflow.md:164-166` | 7, 19, 45 | The only reviewer with a whole-system remit: "separation of concerns; system-wide integrity (interface contracts, API compatibility, cross-doc consistency)". Everything else in `rn` reviews one artifact against one task. It is the axis with the clearest recorded catch: when `task-execute-workflow.md` and `task-verify-workflow.md` were split apart, Design flagged the duplication on the spot — the Design review of that split is the finding recorded at the end of the unenforced set, and no other axis mentioned it. | **Already conditional, and correctly so.** The gap that case exposes is not the review but the *disposition*: the finding was accepted as a tradeoff, and that acceptance lives only in a check file nothing reads. 131 lines are still duplicated with no sync rule anywhere. **A review only earns its cost if the disposition of its findings lands somewhere durable** — which is U1's problem, not Design's. |

**The shared problem.** All four are dispatched as fresh subagents that must read the artifact from
scratch, so on a one-line change four subagents are the entire cost of the task. `rn`'s only
conditionality is medium and structure/approach; it has no notion of size, and no rule permitting a
reviewer to be skipped. The result in practice was not proportionality but silent omission —
planning simply stopped writing the steps. The lesson for task #2 is that the fix for an
over-mandated step is a stated condition, not a firmer instruction.

### The other eleven per-task steps carry the task's boundary, its record and its state

| Step | Mandated at | Rows | What only this catches | Worth its cost? |
|---|---|---|---|---|
| Scope in the work-order | `task-execute-workflow.md:142` | 29 | The only place the task's boundary is stated to the agent that will cross it — "stay within this task; do not start adjacent tasks; name the files expected in play". It is what makes `task-verify-workflow.md:146`'s scope confirmation answerable: without it the coordinator has no boundary to hold the diff against. | Yes, and it is one sentence. On a small task it is the difference between a one-file diff and an opportunistic tidy-up nobody asked for. |
| Method in the work-order | `task-execute-workflow.md:143-147` | 30 | The only instruction to verify *while building* rather than after — test-first for code, claim-by-claim for writing, trace-as-built for a diagram. Every other verification step in `rn` runs after the artifact exists, when a wrong claim is already written down. | Yes on any task with claims or behavior in it. It is also the least checkable step in the loop: element 5 asks the expert to confirm it applied the Method, which is self-report, not evidence (row 30). |
| Self-check | `task-execute-workflow.md:153-161` | 32, 33, 34 | The only per-criterion evidence written by whoever built the thing, and the only record of *how* the Method was applied (coverage figures, which claims were checked, where the flow was traced). | Yes as a **record**; weak as a **check** — it is written by the same agent that built the artifact, and past files were left without a `Ready to check off` verdict with no consequence (row 26). Its value is entirely contingent on QA reading it, which `task-verify-workflow.md:157-159` forbids passing to the reviewer. |
| Coordinator reads the committed diff | `task-verify-workflow.md:139-146` | 41, 42, 43, 44 | The only step that reads the actual artifact independently of anyone's account of it. Catches scope creep, stray staged files, a summary that does not match the diff, a regenerated file. It is the reader behind all 16 rows of group C's coordinator list. | Yes, always. It is one `git show`, and 13 rows of group C rest on it. |
| Dispatch all deliverable work to the implementation expert | `task-execute-workflow.md:26` | 10, 40 | Keeps the coordinator's context clear of build trial-and-error — a resource property, not a quality one. | Yes for context economy; it catches nothing, and nothing records whether it happened. |
| Capture the task's starting commit | `task-execute-workflow.md:175-176` | 39 | The only way `task-verify-workflow.md:144-145`'s cumulative diff spans multiple fix rounds. Without it, review sees the last round only. | Yes — free, and its loss silently narrows the one step that always earns its place. |
| Triage every finding to Valid/Invalid/Escalation | `task-verify-workflow.md:176-189` | 56, 57, 60, 61 | The only step forcing a finding to a decision instead of a judgment call about whether to bother. The Invalid bar ("Invalid **only** when it rests on a factual error or falls outside a scope boundary written in the Completion criteria") is what stops findings being waved off. | Yes — it is the rule that makes the reviews consequential rather than advisory. |
| Record review verdicts into the check file | `task-verify-workflow.md:191-192` | 62, 63 | The only durable trace that a review happened at all. Everything else about the review chain is prompt-only. | Yes — it is the one artifact that could make U1's 33 unenforced rows visible, and it already exists. |
| Escalation, always open | `task-verify-workflow.md:194-200` | 18, 64 | The only route by which a discovery that changes the agreed plan or design reaches the user between gates — "raised to the user **immediately, wherever it surfaces** … never deferred to a gate". Nothing else in the loop can interrupt it. | Yes, and it costs nothing when it does not fire. Its failure mode is silence: an escalation that should have fired and did not leaves no artifact anywhere (row 64), which is why it sits in U7 rather than in the enforced set. |
| Check off steering + the single completion marker | `task-verify-workflow.md:208-214` | 66, 67, 68 | The session's actual state. Feeds `up`'s resume, the status block, and "the next unchecked task". | Yes — this is `rn`'s state machine; without it a resumed session redoes or skips work. |
| Advance immediately, no per-task gate | `task-verify-workflow.md:215-217` | 69, 17, 65 | Keeps the user out of per-task decisions, which is the plugin's whole premise. | Yes; it costs nothing and is what the three-gate design buys. |

### Planning's eight steps fix everything the session is later judged against

| Step | Mandated at | Rows | What only this catches | Worth its cost? |
|---|---|---|---|---|
| **1. Understand the goal** | `planning-workflow.md:12` | 76, 77, 78 | The only point at which what the user asked for is written down in a form they can correct. `Goal` is the root every later artifact derives from — the tasks, the criteria, the Evaluation run — and nothing downstream ever re-checks it against the request. | Yes on any session. It is one exchange, and it is the only place invented scope is still cheap to remove. |
| **2. Propose the location** | `:14-31` | 79, 80, 81, 82, 83, 252, 253 | Two things: where the session's record lives, and whether an existing `design.md` already covers the area. A wrong path makes the session undiscoverable to `dn`/`up`'s `git log` search; a missed existing design starts a second document over the same ground. | The path half yes — it is what makes the session resumable at all. The overlap judgment is unrecorded (rows 83, 253), so its cost is paid and nothing is bought back. |
| **3. Create steering.md** | `:33` | 85, 86, 87, 88, 89, 90 | The only step that puts the template's contract into the session: the headings later steps address by name, the `Rn version:` stamp, the `Design:` pointer, and the planning-time allocation of content across steering / design / README. | Yes for the headings and the pointer, which have named consumers (rows 106, 114). No for the version stamp as built — see the version check below. |
| **3a. Design sign-off task** (conditional: a `design.md` not settled at plan time) | `:36` | 93, 254 | That an unsettled design is approved before heavy build is spent on it. | Yes, and it is the one sign-off with no backstop: 7 of 8 sessions never placed the task and nothing escalated. |
| **4. Decompose tasks** | `:35` | 91, 92 | The only place the work is cut into units, and the parent of every per-task rule in `steering-template.md` — the `Tasks` structure, the inline criteria rules, and the `Task definition requirements` table. | Yes; it is the plan. It is also where the Goal's specimen failure happened, and every criteria-shape rule it invokes sits in U3. |
| Evaluation sign-off always last | `planning-workflow.md:37` | 94, 254 | That the goal is confirmed met before the session closes — the only step that checks the Acceptance criteria at all. | Yes, and it is the one planning rule with a real backstop (`task-verify-workflow.md:219-222`). |
| Pre-persist self-check that the last task is Evaluation sign-off | `planning-workflow.md:38` | 95 | Would catch the omission at authoring time rather than at session end. | Yes in principle; unenforced in fact (row 95), and it covers only this one task — the Design sign-off, the review steps, and the criteria phrasing get no equivalent. **The cheapest generalization available to task #2 is to widen this step, since it is already the right shape: a check at authoring time on the artifact planning just wrote.** |
| **5. Persist and open a draft PR — the plan gate** | `planning-workflow.md:40-51` | 99, 100 | Puts the plan in front of the user in rendered form and creates the session's one review surface, on which group C's user depends entirely. | Yes — every `recognized` verdict in this inventory that names the user ultimately resolves to this PR. |

### The command skills' twenty-four steps are what survives a suspend

| Step | Mandated at | Rows | What only this catches | Worth its cost? |
|---|---|---|---|---|
| Version check in all five skills | `on/SKILL.md:15`, `dn/SKILL.md:18`, `up/SKILL.md:32`, `ty/SKILL.md:13`, `gm/SKILL.md:13` | 210, 215, 235, 239, 245 | In principle, drift between a session and the installed plugin. | **No, as built.** It has never fired: most sessions carry no stamp to compare (row 86), `on`'s copy is documented as unreachable, and the missing-line case is undefined. It is four lines of ceremony in five files. |
| `on` **1. Plan the session** | `on/SKILL.md:13` | 209 | The only invocation of `planning-workflow.md`. Without it a session has no `steering.md`, no PR and no gate. | Yes, and it is a one-line delegation. |
| `on` **3. Begin task #1** | `on/SKILL.md:17` | 1, 211 | The handoff from the plan gate into the execution loop, and the only place `on` names the two workflow files and their reading order. | Yes, and free. The ordering half buys nothing: nothing records which file was read, or whether either was (row 1). |
| `dn` **1. Locate steering.md** | `dn/SKILL.md:13-16` | 214 | The only step that finds the file the rest of `dn` writes to, when the path is not already known. | Yes when the path is unknown; the cost is one `git log`. The `Status: paused` ranking is worth less than it looks — `20260615-subagent-execution/steering.md` is a closed session still reading `paused` today, and it outranks the live one. |
| `dn` **3. Check off progress** | `:22-23` | 216 | The only place a suspend records what was actually finished. `status-display.md:19-22` and `task-verify-workflow.md:215` read nothing else, so a suspend that skips it makes the resumed session redo work it already did. | Yes — it is the state the resume runs on. |
| `dn` **4. Write the `State` section** | `:25-27` | 217 | The only forward pointer between two sessions: last completed, next, notes. `up/SKILL.md:19` and `:24` have no other source. | Yes. Without it a resume has to reconstruct its position from `git log`, which is exactly what `up` step 4 does badly. |
| `dn` **5. Commit the work** | `:29-33` | 218, 219 | Two things: whether in-flight work is committed as finished or as `wip:`, and that a suspend-time bookkeeping message keeps `complete task #` out of it. | The marker prohibition yes — row 219's breach would have checked off a task nobody finished. The `wip:` prefix rule buys nothing: no step compares the prefix to the checkbox state (row 218). |
| `dn` resolves untracked residue | `dn/SKILL.md:35-39` | 220, 221, 222 | The only step in `rn` that looks at what the work left behind rather than at what it produced. A regenerable artifact gets a `.gitignore` rule; anything else goes to the user. Nothing else ever runs `git status --porcelain` for its own sake. | Yes — it is the reason a suspend hands back a clean tree rather than a dirty one, and the classification is cheap. The one breach it cannot reach is deleting a file (row 222). |
| `dn` **7. Commit and push** | `:46-48` | 223 | The only step that gets the suspend's own bookkeeping off the machine, and the only place `rn` forbids an amend. | Yes — and the amend prohibition is one of the plugin's thirteen real refusals: an amended commit that was already pushed is rejected non-fast-forward, and the rule bars the force-push that would clear it. |
| `dn` verifies the tree is clean | `dn/SKILL.md:50-54` | 224 | The only post-condition check in the plugin: it re-runs `git status --porcelain` against step 6's own effect and records whatever step 6 failed to resolve. Every other step in `rn` asserts its outcome rather than re-reading it. | Yes, and it is the shape task #2 should copy: a step that re-reads the artifact its predecessor wrote costs one command. That nothing checks *this* step ran (row 224) is the limit, not the design. |
| `dn` **9. Report** | `:56-59` | 225 | The only statement of whether the commits actually reached the PR, and the only list of paths the user deferred. | Worth writing; worth little as a check. Its one checkable claim — that commits are local-only — would have to be checked against the PR by someone with no reason to look (row 225). |
| `up` **1. Handle a dirty tree** | `up/SKILL.md:13-15` | 227 | The only thing standing between a resume and an uncommitted working tree, and the only place `rn` requires confirmation before touching one. | Yes — this is the one moment `rn` can destroy work, and the destructive half leaves no residue in git, in `git status`, or in the report (row 227). It has to be right the first time. |
| `up` **2. Find steering.md** | `:17-20` | 228, 229 | The same discovery as `dn` 1 from the resume end, plus the zero-result case that sends the user to `/rn:on`. | Yes, with a known defect: `head -5` truncates the candidate list silently, and this repo already holds eight `steering.md` files. |
| `up` **3. Read State** | `:24` | 231 | The only read of the pointer `dn` 4 wrote. | Yes, and free. Nothing records that it happened: a session resumed from a guess and one resumed from the file produce the same next commit (row 231). |
| `up` **4. Sync tasks** | `:26` | 36, 67, 68, 232 | The only reconciliation between what `git log` says was finished and what `steering.md` says is unchecked — and `rn`'s only consumer of the `complete task #{id}` marker, which is what makes seven rows elsewhere in this inventory enforced at all. | **Yes in principle, defective as built, and it runs on every resume.** The match is a substring test: `complete task #1` also matches `#1b` and `#10`–`#16` (`git log --all --grep='complete task #1' --oneline` returns 16 here, 7 of them other tasks), and three commits carry the substring in prose without being markers. Every wrong match checks off a task nobody finished. Making this one grep exact is the cheapest repair available in the plugin. |
| `up` **5. Check blockers** | `:28` | 233 | The only bar on removing a task: an alternative approach has to be found before the task goes. | Yes when `State` names a blocker, and it fires on nothing otherwise. Its breach is invisible — a removed task simply stops appearing, and the user holds no earlier copy of the list (row 233). |
| `up` **6. Clean up State** | `:30` | 234 | The only reset of `Status: paused`. Skipping it leaves a closed session outranking a live one in both discovery searches. | Yes — `20260615-subagent-execution/steering.md` is the standing proof that it was skipped once and still costs something. |
| `up` **8. Begin the next task** | `:34` | 1, 236 | The resume's handoff into the execution loop, reading "the next unchecked task" from `steering.md`. | Yes, free, and it is the payoff for steps 3, 4 and 6. Ordering half unenforced, as in `on` 3. |
| `ty` **2. Identify the pending approval** | `ty/SKILL.md:15` | 240 | The only step in `rn` that manufactures its own reader: it states the target back to the user before anything is recorded, so a misidentified approval is caught by the one party who knows what they meant. | Yes, always. It is a sentence, and it is the shape the rest of the plugin is missing. |
| `ty` **3. Record it as approved** | `:17` | 241 | The act the gate exists for. | Yes for a task gate, where the record is a committed check-off read downstream. For a plan gate it writes nothing at all, so the approval survives only in the conversation. |
| `ty` **4. Advance the workflow** | `:19-24` | 242 | The only mapping from which gate was approved to what happens next — plan/design to the next task, evaluation to session close, a reviewed item to accepted. | Yes; it is one branch table. Where the advance lands in an artifact it is recognized (row 241); where it ends in a closing report it is not. |
| `ty` **5. Nothing pending** | `:26` | 243 | The guard against `/rn:ty` approving something that was never pending. | Yes — it costs a sentence and it is the negative case of step 2. It catches nothing after the fact: a compliant reply and a breaching one differ in no artifact (row 243). |
| `gm` **2. Branch on the argument** | `gm/SKILL.md:15` | 246 | The plugin's one fully specified predicate — trim, treat blank as empty, non-empty to step 3, empty to step 4. Every other conditional in `rn` is a judgment. | Yes, and the wrong branch is recognized at once by the user who typed the command. Steps 3 and 4 are its two arms; their condition is the argument, not the size of the work. |
| `gm` **5. Either way, this is a revise verdict** | `:21` | 249 | The rule that no piece of feedback is dropped, whichever arm ran. | Real for PR feedback, where an unaddressed thread stays unresolved and is re-collected on the next run (rows 200, 206). Nothing at all for `$ARGUMENTS` feedback, which exists only in the conversation. |

### The PR-feedback loop's twelve steps keep their state in GitHub, not in memory

| Step | Mandated at | Rows | What only this catches | Worth its cost? |
|---|---|---|---|---|
| **Find the session's PR**, and capture `owner`/`repo` separately | `pr-feedback-workflow.md:22-38` | 187, 188, 189 | The only place the loop learns which PR it is working on, and the one branch that stops rather than fabricating a number. | Yes, and it is one of the few steps that genuinely refuses: `gh pr view` exits non-zero with no PR, and the GraphQL call has nothing to take. |
| **Fetch all review threads**, paginating until exhausted | `:42-72` | 190 | The only enumeration of what the loop has to answer. | Yes — and it is the one step in this file that fails silently. A skipped page shrinks the queue and nothing counts what should have been in it. |
| **Build the queue** — unresolved, last comment by the thread's author | `:74-82` | 191, 192 | The only filter separating threads awaiting a reply from threads already answered or resolved, and the step that records the `databaseId` every later call is keyed on. | Yes; the reviewer is a real reader of both errors — a wrongly kept thread gets a duplicate reply, a wrongly dropped one stays unanswered — and a bad id is rejected by the API. |
| Work-order element **Thread** | `:91` | 194 | The only context the subagent gets: `path`, `line`, the full comment bodies, the first comment's id. | Yes, and it is four fields. It is never written to disk, so a truncated one is unrecoverable afterwards. |
| Work-order element **Task** — exactly one of two outcomes | `:92` | 194 | The only thing forcing a thread to end in either a change or a question rather than in silence. | Yes; it is the loop's entire contract with the subagent, in one sentence. |
| **Outcome (a) — address it** | `:93-111` | 195, 196, 197, 198, 199, 200 | The only path that changes anything, and the only place `rn` ties a reply to a commit that is confirmed pushed. | Yes. Its no-reply-before-push rule is the right shape resting on nothing — `gh browse <sha> -n` builds the URL locally without asking GitHub (row 198) — so what actually catches the breach is the reviewer finding a dead link on their own thread. |
| **Outcome (b) — needs a decision** | `:113-119` | 201 | The only route by which a thread the subagent should not decide reaches the person who should. | Yes; it costs one reply and prevents a change nobody authorized. |
| **Return** a compact summary | `:121-122` | 202 | The coordinator's only account of what happened before it dispatches the next thread. | Yes, and cheap — the coordinator reads it at `:130` and can compare it to the PR. |
| **Never resolve the thread** — resolution is the author's act | `:124`, `:142-148` | 203, 206 | The loop's state lives in GitHub's unresolved flag rather than in the assistant's memory, so a missed thread is re-collected on the next run instead of being lost. | Yes, unconditionally. It is the only mechanism in `rn` that repairs its own omissions, and it costs nothing to obey. |
| **Check the result** before advancing | `:130-132` | 204 | The only inspection between two threads; without it the loop advances on the subagent's word. | Yes — it is the loop's per-item review, and it is one read of the reply against its thread. |
| **OK → dispatch the next thread** | `:133` | 193 | The sequencing that keeps two subagents off the same PR at once. | Yes for context economy and for reply ordering. Nothing records whether it held: the replies and commits are order-independent (row 193). |
| **Problem → re-instruct the same subagent** | `:134` | 204 | The only correction path inside the loop, and the only rule forbidding advance on a wrong result. | Yes; re-instructing the subagent that already holds the thread is cheaper than a fresh one. |

### Two steps span the whole session, and one of them has never run

| Step | Mandated at | Rows | What only this catches | Worth its cost? |
|---|---|---|---|---|
| Session-status block at every user stop | `status-display.md:3-5` | 142 | The only thing that tells the user where the session stands without opening `steering.md`. | Yes on a stop; it is the user's only continuous view, and the user is one of group C's three readers. |
| `migration` reconciles steering, then design, then tasks | `migration-workflow.md:20-25`, `:27-31`, `:33-38` | 157, 158, 159, 160, 161, 162 | The only path by which a session authored under an older `rn` is brought to current convention — and the only step that re-reads a *past* artifact against a current template rather than a new artifact against its own task. | **Not as built.** It has never run: its trigger is a `Rn version:` comparison that usually has no left operand (row 86), and all three reconciliations are unrecorded judgments whose output is indistinguishable from not having run (rows 158, 160). The shape is right; nothing starts it and nothing records it. |

### Thirteen of the sixty-one do not earn their place as written

Collected from the cost column above, so the set is in one place rather than scattered across six
tables. Each is a step `rn` runs anyway.

- **Craft on a mechanical edit** — a rename or a version bump returns wording nits. It earns its
  place on any task producing prose a user will read; `rn` offers no way to say which task that is.
- **Verification on a change already proven in the diff** — a grep or a green test the coordinator
  can already see makes the re-derivation redundant. It was dropped from 35 of 40 past tasks, most
  of them of exactly this kind, which is why its absence from the other kind went unremarked.
- **Dispatching all deliverable work to the implementation expert** — a context-economy rule in a
  quality rule's position. It catches nothing, and nothing records whether it happened (rows 10,
  40).
- **The self-check as a check** — it is written by the agent that built the artifact. As a record it
  is the only per-criterion evidence there is; as a check it verifies nothing (rows 32, 33).
- **The version check in all five skills** — it has never fired, `on`'s copy is documented as
  unreachable, and no file defines the missing-line case (rows 86, 210).
- **`migration`'s three reconciliations** — never run, and all three produce judgments whose output
  is indistinguishable from not having run (rows 158, 160).
- **Planning step 2's design-overlap judgment** — the cost is paid at plan time and nothing records
  the answer, so a session that asked and one that did not leave identical files (rows 83, 253).
- **`dn` 5's `wip:` prefix rule** — nothing compares the prefix to the checkbox state it is supposed
  to reflect (row 218).
- **`dn` 9's report as a check** — its one checkable claim, that the commits are local-only, has no
  reader with a reason to check it (row 225).
- **`ty` 3 at a plan gate** — for a task gate it writes a committed check-off; for a plan gate it
  writes nothing at all, so the approval survives only in the conversation (row 241).
- **`ty` 5's nothing-pending reply** — a compliant reply and a breaching one differ in no artifact
  (row 243).
- **`gm` 5 for `$ARGUMENTS` feedback** — real for PR feedback, where the thread is the queue;
  nothing at all for feedback that exists only in the conversation (row 249).
- **`up` 4 as built** — the right step on the wrong predicate: a substring match that fires on six
  other task ids and on three prose commits (rows 36, 232).

### What the cost column adds up to

The steps that earn their place unconditionally are the cheap ones that write or read an artifact —
one `git show`, one check-off, one `git status --porcelain` re-run, one target stated back to the
user. The thirteen above are of two kinds: steps whose cost is a fresh subagent that must read the
artifact from scratch, and steps whose only output is a judgment nobody records. `rn` has no way to
say "not on this change" about either kind, and the record shows what follows — not proportionality
but silent omission. Task #2 inherits both halves: 165 rules with no mechanism, and thirteen steps
whose mechanism costs more than it returns.
