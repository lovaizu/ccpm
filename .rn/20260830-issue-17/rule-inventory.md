# Rule inventory — what `rn` states, and what happens when it is broken

**Nothing in `rn` enforces anything.** Of the 254 normative statements in its 8 reference files and 5
skill files, 93 are enforced and 161 are not — and not one of the 93 is enforced by machinery `rn`
itself ships. The plugin contains no executable code at all: `find rn -type f` returns 17 files,
sixteen Markdown and one JSON, none of them executable (`find rn -type f -perm -u+x` returns 0), and
there is no hook, no script, no validator and no CI step anywhere in it. Every enforced row borrows a
mechanism from somewhere else — the harness refusing a skill invocation, a `git` or `gh` command
failing, a user at a scheduled gate, or a later `rn` step that reads a written artifact. Those four
are set out with their row ids under "The enforced set" below, and they are the whole of what catches
a breach.

The 161 unenforced rows are this document's product: the definite list task #2 works from, grouped
under "The unenforced set" by *why* nothing catches them, because the groups need different repairs.
Two of the nine groups hold more than half of them, and neither is the one `rn`'s own prose would
suggest. Thirty-three rows produce something a user can see and give no one an occasion to check it
against the rule — the whole of `status-display.md`'s output contract sits here. Thirty-two more are
the review chain's own internals: every rule protecting the integrity of the mechanism that is
supposed to protect everything else lives in prompts that are never written to disk.

## The verdict vocabulary

Three verdicts. Each has a test, and a row gets the verdict whose test it passes — never the one whose
shape it resembles.

- **refuses** — something other than the agent declines to proceed. *Test: if the agent set out to
  break this rule, would something outside it decline anyway?* Only two things ever answer yes: an
  external command exits non-zero or an API rejects the call, and the harness blocking a skill
  invocation. A stop that arrives because the agent asked and then ended its turn does **not** pass:
  that is the agent complying, and a rule cannot be enforced by the agent choosing to obey it.
- **recognised** — a breach reaches a reader who would tell it from compliance. *Test: name three
  things — (1) the reader, a person or a later `rn` step; (2) the artifact the flow **makes** them
  open; (3) what in that artifact differs between compliance and breach, legible without auditing
  against a rule the reader is not holding.* All three must be nameable. "It is in a message the user
  can see" fails (2) and (3): the user opens the message to answer it, not to audit it, and has no
  copy of the rule to audit it against.
- **unseen** — everything else. This is where a rule that is *stated and nothing more* lands, and also
  where two things land that used to look like mechanisms: a stop that needs the agent's compliance,
  and text a reader could in principle audit but has no occasion or standard to audit against.

Two further words are used throughout in one sense each, and nowhere in the other's:

- **enforced** — the union of `refuses` and `recognised`. The mechanism may sit anywhere; it need not
  belong to `rn`.
- **self-enforced** — enforced by machinery `rn` itself ships. Nothing in `rn` is self-enforced.

The change from the first pass of this inventory was in the boundary, not the evidence: `stops` used
to absorb rules that only stop when the agent obeys them, and `visible` used to absorb rules whose
only reader is a user glancing at a message. Applying the tests above moved 52 rows out of the
enforced set.

## How this was built

Each of the 13 files was read end to end and every line that tells a reader what must, must not,
should, always, or never happen was extracted — table rows, checklist items, and imperative bullets
included. Each rule is cited by `path:line` and quoted or tightly paraphrased. Where a row claims a
mechanism, that mechanism is quoted from the file that implements it, with its own `path:line`; where
no such line could be quoted, the rule is recorded as unenforced.

Rules were also tested against what past sessions actually produced — the eight session directories
under `.rn/`, their `steering.md`, `rn/docs/design.md`, and 40 `checks/*.md` files — not only against
the rule text. Several rules that read as enforced turn out to have been broken repeatedly with
nothing noticing.

**Counts.** 254 normative statements. By file: 41 in `task-execute-workflow.md` (whose lines 6–136 are
byte-identical to `task-verify-workflow.md`'s — 131 lines — so rows 3–26 state the rules of both and
are counted once), 32 more in `task-verify-workflow.md`, 36 in `planning-workflow.md`, 37 in
`steering-template.md`, 13 in `status-display.md`, 11 in `migration-workflow.md`, 16 in
`design-template.md`, 26 in `pr-feedback-workflow.md`, and 4 / 14 / 11 / 7 / 6 in `on` / `dn` / `up` /
`ty` / `gm`. Row ids are stable identifiers assigned in the order the rules were inventoried; rows
250–254 were added in a later pass and sit at the end of their file's table rather than in line order.
By verdict: **13 refuse**, **80 are recognised on breach**, **161 are unseen**.

## Breaches observed in past sessions

These are recorded here because they are the evidence for several `unseen` verdicts below: the rule
was stated, it was broken, and nothing surfaced it.

| Rule | Where it was broken | What noticed |
|---|---|---|
| `Verification expert review (subagent, per the task's medium)` is a mandated Step (`steering-template.md:70`) | 35 of 40 past `checks/*.md` have no `### Verification Expert` section; `20260705-improve-design-template/steering.md` never lists the step in any of its 7 tasks | Nothing. The session closed and was approved. |
| `Craft expert review` mandated (`steering-template.md:69`) | absent from all 5 sessions before `20260625-rn-lean`; 29 of 40 check files have no Craft section | Nothing. |
| Check-file format's `## Overall Verdict` block (`task-execute-workflow.md:127-134`) | 24 of 40 past check files carry no `Ready to check off` line — the block's last field and the only one another file claims to read; 39 of 40 do carry the `## Overall Verdict` heading, the exception being `.rn/20260615-experts-do-the-work/checks/1.md` | Nothing; every one of those tasks was still checked off. |
| A deliverable commit's message "must **not** contain `complete task #`" (`task-execute-workflow.md:164`) | three commits carry it in prose: `4daf6b2` ("forbid 'complete task #{id}' in a suspend-time commit"), `893de07` ("{type}: complete task #{id}; hi matches"), `de0b1ec` ("so this is wip not 'complete task #3'") | Nothing at the time. `/rn:up`'s sync (`up/SKILL.md:26`) would have checked off the wrong tasks. |
| A criterion must state the objective met, "not that an output was produced" — `steering-template.md:76`, which binds **Completion** criteria; `:41-43` sets no such bar for **Acceptance** criteria | `.rn/20260705-improve-design-template/steering.md:22-49` — 9 of 10 Acceptance criteria are artifact-existence ("A new `migration-workflow.md` reference exists") | Nothing. This is the specimen named in this session's Goal, and the gap is twofold: the bar was never stated for Acceptance criteria, and nothing reads either kind against it. |
| `Rn version:` stamped at creation (`planning-workflow.md:33`) | absent from 6 of 8 `steering.md` files | Nothing — and the absence is silent by construction, since the version check is "a plain string comparison" (`migration-workflow.md:5`) with no left operand. |
| `Evaluation sign-off` always the last task (`planning-workflow.md:37`) | 5 of 8 sessions have no such task; `20260625-rn-lean` has it as `#15`, placed mid-list before `#6`–`#14` | Nothing; the backstop at `task-verify-workflow.md:219-222` only fires if a session reaches "no unchecked tasks remain" inside a live `rn` flow. |
| Check file path `checks/{task-id}.md` (`task-execute-workflow.md:79`) | two sessions wrote `checks/task-1.md`; `20260625-rn-lean` is missing `2.md` and `15.md` for tasks that exist | Nothing. |
| The 131 lines shared by `task-execute-workflow.md` and `task-verify-workflow.md` are duplicated verbatim with no sync rule stated anywhere | `diff <(sed -n '6,136p' rn/references/task-execute-workflow.md) <(sed -n '6,136p' rn/references/task-verify-workflow.md)` returns no output | The Design expert on the splitting task did flag it — `.rn/20260625-rn-lean/checks/12.md`: "a standing drift risk against the repo's own anti-duplication principle — noted, not actioned" — and it was accepted as a tradeoff. No rule was written from that finding, so nothing guards it now. |

---

# Per-file inventory

Sources are relative to `rn/references/` in the reference tables and `rn/skills/` in the skill tables.
Verdicts: **refuses** / **recognised** / **unseen**, per the vocabulary above.

## `task-execute-workflow.md` (179 lines)

Lines 6–136 of this file are byte-identical to lines 6–136 of `task-verify-workflow.md` — 131 lines;
`diff <(sed -n '6,136p' rn/references/task-execute-workflow.md) <(sed -n '6,136p'
rn/references/task-verify-workflow.md)` returns no output. Rows 3–26 therefore state the rules of both
files and are not repeated in the next table. Lines 1–5 differ between the two files: row 2's sentence
("Run one task at a time.") stands verbatim on line 5 of each, but row 1's does not —
`task-verify-workflow.md:5` carries its own wording and has its own row in the next table.

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 1 | "`on` and `up` read both files at task execution, this one first" | :5 | unseen | No step in `on` or `up` records which files it read; a skipped read leaves no trace. `on/SKILL.md:17` and `up/SKILL.md:34` state the same ordering — that is the rule restated, not a check. |
| 2 | "Run one task at a time." | :5 | recognised | The coordinator checks off one task per commit (`task-verify-workflow.md:210`) and "Begin the next unchecked task" is singular (`:215`); two tasks run together would produce two deliverables under one check-off, showing in the PR the user reviews. Nothing refuses it. |
| 3 | "Write check files under `{steering_dir}/checks/`." | :7-8 | unseen | No step reads back the path. Two past sessions wrote `checks/task-1.md` instead of `checks/1.md` and nothing surfaced it. |
| 4 | Coordinator "Writes directly **only** `steering.md` and `checks/{task-id}.md`; never edits the deliverable or its git history" | :14-15 | recognised | Git authorship does not distinguish coordinator from subagent, but a coordinator-authored deliverable change lands in the same PR diff the user reads and the coordinator itself re-reads (`task-verify-workflow.md:139`). History rewriting would show as a changed SHA against the captured starting commit (`:175`). Weak: nothing compares them. |
| 5 | Implementation expert "Produces, fixes, and commits/pushes the deliverable" | :16-17 | unseen | Nothing records whether a subagent was dispatched. A coordinator that writes the file itself produces an identical commit. |
| 6 | "**QA expert** (every task) — subagent." | :18 | unseen | The check file has a `## QA Expert Review` section — 38 of 40 past files carry one — but nothing reads it: 24 of 40 leave the `Ready to check off` line out of the Overall Verdict block, and every one of those tasks was still checked off. |
| 7 | "**Design expert** (tasks that produce or revise structure/approach)" | :19-20 | unseen | Same as row 6; additionally "produces or revises structure/approach" is a judgement with no recorded answer, so an omission cannot even be identified as one. |
| 8 | "**Craft expert** (per medium: coding / writing / visual)" | :21-22 | unseen | Absent from every session before `20260625-rn-lean`; 29 of 40 check files carry no Craft section. Nothing noticed. |
| 9 | "**Verification expert** (per medium: test / fact-check / dry-run)" | :23-24 | unseen | 35 of 40 check files carry no Verification section; `20260705-improve-design-template` omitted it from all 7 tasks and closed approved. This is the specimen breach for this session. |
| 10 | "All deliverable work (produce/fix/commit/push) goes to the implementation expert, every time, any size." | :26 | unseen | Identical to row 5: the commit is the same either way, and nothing records the dispatch. |
| 11 | "Each review expert runs as an independent subagent (Agent tool, no conversation history) and returns a compact summary." | :27-28 | unseen | Nothing records whether the Agent tool was used or whether history was passed. A coordinator role-playing the review produces the same check-file text. |
| 12 | "The user signs off at exactly **three** scheduled gates, never on any other task" | :32 | unseen | An extra gate is a message on the user's screen; a missing one is a task that closes without them. The user is the reader — but only if they notice, and nothing flags it. Fails the recognition test at leg (3): the user has no copy of the three-gate rule, so an extra ask reads as an ordinary question and a missing gate reads as smooth progress. 7 of 8 sessions ran without the Design gate and nobody remarked on it. |
| 13 | "**Plan gate** — the draft-PR plan approval in `on` before any task runs." | :34 | recognised | The gate ends the assistant's turn — but only because the assistant asked, so that is compliance, not a refusal. What is recognised is the breach: if task #1's work lands on the PR before the plan is approved, the user opens the PR at the gate and finds commits they never cleared. Reader: the user; artifact: the PR the ask points them at; difference: work that predates their verdict. `planning-workflow.md:51` states the rule as "**CRITICAL: DO NOT proceed without explicit user approval.**" and states nothing that would decline on its behalf. |
| 14 | "**Design gate** — sign-off on the approach / key decisions before they are built on" | :35-37 | unseen | Realized as a Design sign-off task (`planning-workflow.md:36`) whose absence is visible in `steering.md`'s task list, which `status-display.md:17` re-derives at every stop. If planning never places the task, nothing catches it — 7 of the 8 session directories under `.rn/` have no such task; `.rn/20260830-issue-17` (`### #3: Design sign-off`) is the only one that does. Fails at leg (3), and the record proves it: the Design sign-off task is absent from 7 of 8 sessions and no user, at any gate, ever asked where it was. Nothing holds the task list up against `planning-workflow.md:36`. |
| 15 | "**Evaluation gate** — the end-of-session run of the `steering.md` Acceptance criteria" | :38-39 | recognised | Backstopped by `task-verify-workflow.md:219-222`: "If no unchecked tasks remain and no "Evaluation sign-off" task was ever encountered … escalate to the user immediately". That is a real consumer, quoted; it fires only inside a live flow that reaches the end of the task list. |
| 16 | "the assistant never records a verdict the user did not issue" | :41-42 | recognised | The fabricated verdict appears in the message the user reads next. The user is the reader; nothing else checks. |
| 17 | "The per-task boundary is **not** a user gate for ordinary build tasks" | :44-46 | unseen | Stopping anyway puts an unrequested ask on the user's screen. Nothing prevents it. Fails at leg (3) — the same reason as row 12. An unrequested stop is a question the user answers, not a breach they identify. |
| 18 | Escalation is "a separate always-open channel — not a gate; an escalation message opens with the session-status block" | :47-49 | unseen | A *missing* escalation leaves nothing behind — that is the whole failure mode. The status-block half is visible (row 12's reader) only when an escalation is actually sent. |
| 19 | "QA always spawns for a task that builds something; a sign-off task spawns none. Craft and Verification spawn for the task's medium. Design spawns only when the task produces or revises structure/approach." | :53-57 | unseen | See rows 6–9. The per-task judgement is never written down, so neither its result nor its omission is recoverable. |
| 20 | The three build-task instances — Code, Docs, Visual — each run the same chain (paraphrase; the file spells the medium out per instance, e.g. "Self-check → QA → Craft (coding) → Verification (test) → coordinator review → check-off") | :59-64 | unseen | Same as row 19. Empirically the Verification link was simply dropped for a whole session. |
| 21 | "**Sign-off task** (instance): no axes spawn … It skips Phase: Execute and Phase: Verify entirely … take the verdict via `/rn:ty` … or `/rn:gm` … no check-off until later approved" | :65-71 | recognised | The verdict cannot be self-issued as a *command*: the five skills carry `disable-model-invocation: true` (`ty/SKILL.md:4`, `gm/SKILL.md:4`), so the assistant cannot invoke `/rn:ty`. It can still write "approved" in prose — which is why this is recognised rather than refused. Reader: the user; artifact: `steering.md` on the PR and every later status block; difference: a sign-off task checked off against a verdict they never issued. |
| 22 | "Self-check is produced in Execute … reviews run in Verify; the coordinator's independent review then clears the task" | :73-75 | unseen | Ordering is unrecorded; the check file bears no timestamps and nothing compares it to the commit graph. |
| 23 | "the implementation expert writes **only** the Completion Criteria Self-check and Evidence columns (and the Overall Verdict "Self-check" line)" | :79-81 | recognised | The coordinator fills the remaining columns afterwards (`:83-84`) and would find them pre-filled. That is a real second reader, but it is the only one. |
| 24 | "Column ownership holds across every round, including fix rounds" — the expert writes "never the review-verdict sections (QA / Expert Review / other Overall-Verdict lines and QA columns, which are the coordinator's)" | :79-83 | recognised | Same reader as row 23. |
| 25 | "The expert does not commit it. The coordinator … commits the file as part of its ledger — on the post-Verify steering check-off commit." | :82-84 | recognised | An expert-committed check file appears in the deliverable commit, which the coordinator reads (`task-verify-workflow.md:140-143` expects `git status` to show "**only** that tracked check file"). That expectation is stated and would be violated visibly. |
| 26 | The check-file format block — five columns, `## QA Expert Review`, three expert sections, `## Overall Verdict` with five verdict lines and `Ready to check off` | :86-135 | unseen | Looked for a step that opens a check file and compares it to this block: there is none. 39 of 40 past check files carry the `## Overall Verdict` heading, but 24 of 40 omit its `Ready to check off` line, and every one of those tasks was checked off. That line is the only field any other file claims to gate on — see row 162. |
| 27 | The work-order must "include everything it needs and only that, with these 7 elements" | :139-140 | unseen | The work-order is a prompt; it is never written to disk and no artifact records what it contained. |
| 28 | Element 1 Task — "Purpose, Steps, Completion criteria copied from `steering.md`" | :141 | unseen | Same as row 27. A paraphrased or truncated copy is indistinguishable afterwards. |
| 29 | Element 2 Scope — "stay within this task; do not start adjacent tasks; name the files expected in play" | :142 | recognised | Out-of-scope files land in the committed diff, which the coordinator reads and is told to "Confirm the change matches the task's scope" (`task-verify-workflow.md:146`). |
| 30 | Element 3 Method — "apply the task's Verification method as you build, not only after" (test-first / verify-each-claim-as-drafted / trace-as-built) | :143-147 | unseen | Nothing distinguishes verifying as you write from verifying afterwards, or from not verifying. Element 5 asks the expert to *confirm* it applied — self-report, not evidence. |
| 31 | Element 4 Best practices — Craft always; Design "when the task produces or revises structure/approach" | :148-152 | unseen | Same as row 27. |
| 32 | Element 5 Self-check — verify each completion criterion OK/NG with specific evidence, and confirm the Method was applied (coverage measured / every claim checked / flow traced) | :153-157 | recognised | The written self-check is read by the coordinator, which fills the QA column beside it (`:83-84`). Its quality is unchecked: nothing compares Evidence to the artifact. |
| 33 | Element 5 — write to `{steering_dir}/checks/{task-id}.md` filling **only** the self-check columns; "Never write or overwrite the review-verdict sections … on every round, including fix rounds" | :157-161 | recognised | Same reader as row 23. |
| 34 | Element 5 — "**Do not commit the file.**" | :161 | recognised | Row 25's mechanism: `task-verify-workflow.md:140-143` expects the check file to be the one uncommitted change. |
| 35 | Element 6 — "stage the deliverable paths explicitly (`git add <path>…`); never `git add -A` or `git add .`" | :162-163 | recognised | A stray file appears in the diff the coordinator reads (`task-verify-workflow.md:139`, `:146`) and in the PR. Nothing detects the *staging command* itself — only its consequences, and only when there was a stray file to catch. |
| 36 | Element 6 — plain conventional message; "the message must **not** contain `complete task #`"; push; "**never force-push**" | :163-165 | recognised | Real downstream consumer: `up/SKILL.md:26` — "A commit matches a task when its message contains `complete task #{id}`; check that task off". A breach silently checks off the wrong task. Three commits in this repo's history carry the substring in prose (`4daf6b2`, `893de07`, `de0b1ec`), so the breach is demonstrated and the consumer is demonstrably fooled. Force-pushes surface as events on the PR timeline; nothing in `rn` checks. |
| 37 | Element 6 fallbacks — cannot push → say so and leave the commit, coordinator pushes; cannot commit → say so, coordinator commits mechanically with explicit paths and a plain message, "content stays the expert's" | :166-171 | unseen | Depends entirely on the expert self-reporting the failure. A silent failure leaves the work uncommitted, which the coordinator would meet as an empty diff — visible only in that one case. |
| 38 | Element 7 Return — "a compact summary only … Do not paste full file contents or trial-and-error." | :172-174 | unseen | The coordinator reads the summary; a bloated one is on its screen. Nothing enforces brevity, and the cost (context) is paid before it is seen. Fails at leg (2) and (3): the coordinator does read the summary, but it is handed one, not sent to compare it against a length bar, and no bar is stated. The cost is context, and it is spent before it can be judged. |
| 39 | "**Capture the task's starting commit** — current `HEAD` … Capture it **once**; do **not** re-capture on fix rounds." | :175-176 | unseen | The value lives only in the coordinator's context. A re-captured or lost SHA silently narrows the cumulative diff at `task-verify-workflow.md:144-145`, hiding earlier rounds from review. |
| 40 | "**Dispatch the implementation expert** with the work-order and wait for its summary." | :177 | unseen | See rows 5 and 10. |
| 251 | "Once the expert returns, continue to `task-verify-workflow.md`." | :179 | unseen | The hand-off from Execute to Verify. Nothing records that it was taken: a task whose reviews never ran produces a check file with its review-verdict sections still empty, and nothing reads those sections — 24 of 40 past check files carry no `Ready to check off` line and every one of those tasks was checked off. |

## `task-verify-workflow.md` (222 lines)

Lines 6–136 carry rows 3–26 above, and line 5's shared sentence is row 2. Listed here: this file's own
line 5, its Phase: Verify, and its Phase: Complete.

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 41 | "**Read the committed diff yourself.**" | :139 | unseen | This *is* `rn`'s strongest mechanism — and nothing enforces the mechanism itself. Nothing records that the coordinator read anything. |
| 42 | "Expect `git status` to show **only** that tracked check file — that is normal, not a deliverable change." | :140-143 | recognised | `git status` is run and its output is on the coordinator's screen; a second uncommitted file shows there. |
| 43 | "Inspect the committed deliverable: `git show <sha>` … or `git diff <task's starting commit>..HEAD`" | :144-145 | unseen | Depends on row 39's SHA, which lives only in context; a wrong or missing starting commit silently truncates the diff. |
| 44 | "Confirm the change matches the task's scope and Completion criteria before spending review experts." | :146 | unseen | Looked for an artifact this confirmation writes. The check file's columns are the coordinator's only writable surface (`task-execute-workflow.md:79-84`) and none of them records a pre-review scope judgement, so a task where the confirmation happened and one where it did not enter Verify identically. |
| 45 | "**Dispatch the review experts as independent subagents** — QA always; Craft and Verification for the task's medium … Design when the task produces or revises structure/approach. Build each review prompt with 6 elements" | :147-149 | unseen | See rows 6–9 and 19. The empirical record is that whole axes went missing for entire sessions. |
| 46 | Element 1 Role — review "**adversarially** … assume defects exist and try to break the artifact (boundaries, error paths, integration, missed cases)" | :150-152 | unseen | The prompt is never written to disk. A friendly review and an adversarial one return the same shape of summary. |
| 47 | Element 2 Artifact — "the full content or diff under review." | :153 | unseen | Same as row 46. A review given a partial artifact returns a confident verdict about the part it saw. |
| 48 | Element 3 Criteria — "the expert checklist below." | :154 | unseen | Same as row 46. |
| 49 | Element 4 — "the task's Completion criteria copied **verbatim** from `steering.md`" | :155 | unseen | Same as row 46. "Verbatim" is unverifiable after the fact. |
| 50 | Element 5 Output format — "OK/NG per criterion with concrete evidence, plus an overall pass/fail" | :156 | recognised | The returned summary is on the coordinator's screen and is transcribed into the check file (`:192`). A summary in the wrong shape shows immediately. |
| 51 | Element 6 Neutral framing — "**Never** pass the self-check file …, the implementation expert's summary, or any OK/NG verdict; do not defend the choices or hint at the verdict you expect." | :157-159 | unseen | The single most consequential rule in the file for review independence, and the single least observable: a primed review is indistinguishable from an independent one in its output. |
| 52 | QA checklist — "the verification approach is meaningful to the actual objective … no rubber-stamped or purpose-mismatched check" | :162-163 | unseen | Looked for a reader of the reviewer. The check file records the reviewer's verdict (`task-verify-workflow.md:191-192`) but never the checklist it was given, and the review prompt is never written to disk (row 46). A reviewer that ignored the checklist returns a summary of the same shape. |
| 53 | Design checklist — "does the approach/structure fit; separation of concerns; system-wide integrity (interface contracts, API compatibility, cross-doc consistency)" | :164-166 | unseen | Same as row 52. Note the 132-line verbatim duplication between this file and `task-execute-workflow.md` survived every Design review that has ever run. |
| 54 | Craft checklist — coding: "naming, error handling, null/thread safety", no duplication, style consistency; writing: "prose clarity and correctness, consistency with the doc's existing voice/terminology"; visual: notation clarity | :167-170 | unseen | Same as row 52. |
| 55 | Verification checklist — test: "meaningful and in GWT (Given/When/Then) format" covering edge cases; fact-check: "every claim/reference verified against its source, no unverified assertion stated as fact, and completeness of claim coverage"; dry-run: trace every step/branch | :171-175 | unseen | Same as row 52 — and this checklist was never run at all in the majority of past tasks. |
| 56 | "**Triage every finding.** Each ends in exactly one of" Valid / Invalid / Escalation | :176 | unseen | Findings arrive in the review summary the coordinator reads; the check file records verdicts (`:191-192`). A dropped finding is visible only to whoever compares the summary against the file — and nobody does. Fails at leg (1): the comparison that would catch a dropped finding — review summary against check file — is assigned to nobody. `:191-192` says to record the verdicts; no step says to reconcile the record with what came back. |
| 57 | "**Valid** → fix it. Dispatch the implementation expert (fresh subagent) — every deliverable-touching fix, no matter its size, including minor improvements." | :177-178 | unseen | The fix lands as a further commit in the PR; its absence shows as an NG that never turned into a diff. Nothing compares them. Fails at leg (1) for the same reason. An NG that never turned into a commit and an NG that was fixed both leave a check file with an NG in it; nothing walks from the finding to the diff. |
| 58 | Reuse the original work-order; "point it at the current on-disk state to build on (not regenerate)"; fix commits accumulate, "never force-pushed" | :179-181 | recognised | A regenerated file shows as a wholesale rewrite in the fix commit's diff, which the coordinator reads (`:139`). Force-push shows on the PR timeline; no `rn` check. |
| 59 | "re-run the same review expert; if the fix could affect a dimension another expert already cleared, re-run that expert too. Cap at 3 iterations … valid findings still NG after 3 → record them and escalate" | :181-183 | unseen | Iteration count lives only in the coordinator's context. Past check files narrate "round 3 (final, cap reached)" as prose — a report, not a check. |
| 60 | "**Invalid** → reject it, citing evidence. Invalid **only** when it rests on a factual error or falls outside a scope boundary written in the Completion criteria — cite the specific fact or criterion." | :184-185 | unseen | If the rejection is written into the check file's Evidence column it is readable; nothing requires that, and no reader compares it to the criteria. Fails at leg (2): the rejection is only readable if it was written into the check file's Evidence column, and no step requires that. Nothing then reads it against the Completion criteria the bar cites. |
| 61 | "Escalate **only** when the decision is genuinely the user's … "It's minor, so I'll just ask" is not a reason." | :186-189 | unseen | An over-escalation is a message on the user's screen. Under-escalation leaves nothing. Fails at leg (3): the user has no escalation bar, so an over-escalation reads as diligence. Under-escalation is worse — a decision taken silently leaves nothing to read at all. |
| 62 | "Never silently drop, blindly accept, or bounce a finding for lack of a standard." | :191 | unseen | The failure mode is the absence of an artifact. Searched the 40 past check files for any record of a finding that was raised and then dropped: the `## QA Expert Review` and expert sections carry verdicts per aspect, never the findings behind them, so there is no place a dropped one would have been. |
| 63 | "Record the review verdicts into the check file." | :191-192 | unseen | The check file is committed with the check-off (`:83-84`) and lands in the PR. Empirically weak: 24 of 40 past files record no `Ready to check off` verdict and nothing objected. Fails at leg (2): the check file is committed onto the PR, but no reader is directed to it and no step gates on what it says. 24 of 40 past files record no `Ready to check off` verdict and none of those tasks was held up. |
| 64 | "**Escalation is an always-open channel, not confined to triage.**  … raised to the user **immediately, wherever it surfaces** … never deferred to a gate … a change to the agreed plan or design cannot ship unseen. Wherever it fires, open the escalation message with the session-status block" | :194-200 | unseen | The failure mode is silence. A change that shipped unseen is by definition not visible; only a later reader of the diff could find it, and no step asks anyone to look. |
| 65 | "There is no per-task user gate for a normal task: once Verify clears … the coordinator checks the task off directly." | :204-206 | unseen | Row 12's reader. Same as rows 12 and 17: the user answers an unexpected ask rather than recognising it as one. |
| 66 | "**Check off steering.** With Verify cleared … check off the task in `steering.md` directly." | :208-209 | recognised | Real consumers: `status-display.md:17-22` derives the ✅/👉/⬜ block from these check-offs at every stop, and `:215` begins "the next unchecked task". An unchecked completed task is re-run; a wrongly checked one is skipped. Note this step does **not** read `Ready to check off` — see row 26. |
| 67 | Commit the check-off as "`{type}: complete task #{id} — {description}`", then push to the session PR | :210-212 | recognised | Consumed by `up/SKILL.md:26`'s grep. A malformed marker means the task is not re-checked-off on resume. |
| 68 | "This is the one completion marker for the task: deliverable commits carry plain messages; only this check-off commit carries the `complete task #{id}` substring. Keep that exact substring regardless of the prefix." | :212-214 | recognised | Same consumer as row 67 — and demonstrably fooled twice over. The substring test is a prefix test: `git log --all --grep='complete task #1' --oneline \| wc -l` returns 16, of which 7 are other tasks (`#1b`, `#10`, `#11`, `#12`, `#13`, `#14`, `#16`). And three commits (`4daf6b2`, `893de07`, `de0b1ec`) carry the substring in a body without being markers. |
| 69 | "**Advance.** Begin the next unchecked task immediately — a sign-off task goes straight to the gate … any other task begins at Phase: Execute" | :215-217 | recognised | The unchecked-task list in `steering.md` is the state; skipping one leaves it unchecked and it reappears in every subsequent status block (`status-display.md:49-50`). |
| 70 | "If no unchecked tasks remain and the Evaluation sign-off was approved, the session closes — open that session-close report with the session-status block" | :217-219 | unseen | Row 12's reader. Fails at leg (3): a session that closes without the report closes quietly, and a report that omits the block is still a report. Nothing re-reads a sent message. |
| 71 | "If no unchecked tasks remain and no "Evaluation sign-off" task was ever encountered … that is a planning defect … escalate to the user immediately … do not close the session silently." | :219-222 | recognised | A genuine backstop, quoted in full here, and the only rule in `rn` that checks another rule's output (`planning-workflow.md:37`). It fires only if the flow reaches the end of the task list inside a live session — 5 of 8 past sessions have no Evaluation sign-off task and none of them escalated. |
| 250 | "`on` and `up` read both files at task execution, this one second." — the counterpart of row 1, and the one line of the shared header that differs between the two files | :4-5 | unseen | Row 1's mechanism, in the other direction. `on/SKILL.md:17` and `up/SKILL.md:34` name the same order ("read `…/task-execute-workflow.md` then `…/task-verify-workflow.md`"), which restates the rule rather than checking it; no step records which file was read when, so reading this file first, or not at all, leaves no trace. |

## `planning-workflow.md` (51 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 72 | "Run once per session." | :6 | refuses | `gh pr create --draft` (`:44`) fails when the branch already has an open pull request, so a second planning run on the same branch is declined by GitHub before it can open a second session PR. The `steering.md` overwrite that precedes it is not declined by anything. |
| 73 | "Treat every user interaction as a proposal: lead with one concrete recommended option in plain language (no internal jargon), and proceed on confirmation." | :10 | unseen | Every such interaction is a message the user reads; a bare question or a jargon-laden one is on their screen. The user is the only reader. Fails at legs (2) and (3): the user reads the message to answer it, not to check its form, and holds no copy of the proposal rule to check it against. |
| 74 | "`AskUserQuestion` is fine when one option is your recommendation." | :10 | unseen | Same reader as row 73 — a permission, not an obligation, so a breach is only using it without a recommendation. Same as row 73 — and this is a permission rather than an obligation, so the only breach is using `AskUserQuestion` with no recommendation in it, which reads to the user as an ordinary multiple choice. |
| 75 | "At a stop that instructs opening with the session-status block, the block precedes the proposal." | :10 | unseen | Same reader as row 73. Same as row 73. Block-before-proposal is an ordering the user has no reason to notice either way. |
| 76 | "Take it from the user's message or `$ARGUMENTS`; if neither is present, ask for it." | :12 | recognised | Not a stop: nothing declines if the assistant invents a goal instead of asking. Reader: the user at the plan gate; artifact: `steering.md`'s `Goal`, which the gate exists to have them approve; difference: a goal they did not give, legible to them without any rule in hand. |
| 77 | "Restate it as a clear, faithful understanding of what the user wants — capture full intent, never add scope or invent goals." | :12 | recognised | The restatement is put to the user and becomes `steering.md`'s `Goal`, which the user reads on the PR at the plan gate (`:47`). Invented scope surfaces there. |
| 78 | "If ambiguous, propose your restatement and let the user correct it. This restatement becomes `Goal`." | :12 | recognised | Same reader as row 77. |
| 79 | "The session lives at `.rn/{yyyymmdd}-{slug}/steering.md`, where `{yyyymmdd}` is today's date" | :14 | recognised | Real consumers: `dn/SKILL.md:14` and `up/SKILL.md:17` both discover the file with `git log … -- '*/steering.md'` and rank "most recent". A wrong date prefix mis-ranks the candidate list; a wrong path makes the file undiscoverable. |
| 80 | Slug candidates: the current git branch, an issue reference in `$ARGUMENTS`, a kebab-case name from the goal | :15-17 | unseen | Looked for a consumer of the slug's derivation. `dn/SKILL.md:14` and `up/SKILL.md:17` consume the resulting path (row 79) and `status-display.md:37-38` renders it, but nothing reads which of the three candidate sources it came from. A slug invented outright resolves exactly like one taken from the branch. |
| 81 | "Propose one recommended slug plus the alternatives … When already on a non-default branch, recommend that branch's name as the slug." | :19 | unseen | The proposal is on the user's screen. Fails at legs (2) and (3): a slug proposed without alternatives looks exactly like a slug proposed with the best one first. |
| 82 | "Alongside the slug, decide the session's `design.md` location with the user." | :21 | unseen | Same reader as row 81. Same as row 81. A design location decided without the user looks like a design location the user agreed to. |
| 83 | "**Check for an existing design.md first.** … This is a judgment call on scope overlap, not a mechanical file-existence check." | :21-26 | unseen | Looked for an output of the check. `steering.md`'s `Design:` line records the *result* (row 84), never the search; neither `steering-template.md:26-27` nor `planning-workflow.md:21-26` provides a field for which existing `design.md` files were considered. A session that checked and a session that defaulted straight to a new path leave identical files. |
| 84 | "If one covers the area, point this session's `Design:` line at it and treat the work on it as an update — following design-template.md's "Updating an existing design.md" procedure … If none covers the area, default to `.rn/{yyyymmdd}-{slug}/design.md` (lowercase)" | :28-31 | recognised | The `Design:` line is read by `migration-workflow.md:28-29` ("Read the session's `steering.md` `Design:` line; if it is absent, the session has no `design.md` — skip this step entirely"). A wrong pointer silently reconciles the wrong file; an absent one silently skips. |
| 85 | "Read `${CLAUDE_PLUGIN_ROOT}/references/steering-template.md` and follow its per-section guidance." | :33 | unseen | Nothing records the read. The guidance it points at is the whole `steering-template.md` table below — rows 105–141 — and 30 of those 37 rows are themselves unenforced. |
| 86 | "Stamp the template's top `Rn version:` line with the currently installed plugin's version — read from … `.claude-plugin/plugin.json` `version` field." | :33 | unseen | 6 of 8 past `steering.md` files have no `Rn version:` line at all. The consumer (`on/SKILL.md:15` and the four siblings) does "a plain string comparison" (`migration-workflow.md:5`) that no file defines for a missing line, so an omission is silently a match. |
| 87 | "Write the chosen design.md path into the template's `Design:` line below it." | :33 | recognised | Row 84's consumer. |
| 88 | "Read the doc-division rule … and `…/references/design-template.md`, then **allocate content at planning** per the doc-division" | :33 | unseen | The allocation is a judgement with no recorded output; misallocated content just sits in the wrong file. |
| 89 | "Fill `Goal`, `Acceptance criteria`, `Assumptions`, and `Rules`. Leave `Tasks` and `State` as their placeholders for now." | :33 | recognised | An empty section is a visible blank in the file the user reads at the plan gate. |
| 90 | "**Force no empty `design.md`**: a session with no design to record creates no `design.md` and omits the `Design:` line entirely (no file, no pointer) … never write an empty file and never leave a dangling pointer." | :33 | recognised | A dangling pointer breaks row 84's consumer — `migration-workflow.md:28-31` would try to reconcile a file that is not there. Nothing checks the pointer resolves. |
| 91 | "Work backwards from the Acceptance criteria end state" | :35 | unseen | Looked for a trace of the derivation direction. `steering.md`'s `Tasks` section records the tasks and no field in `steering-template.md:55-79` asks how they were reached, so a list worked back from the Acceptance criteria and one written forward from the goal are the same list on disk. |
| 92 | "Define each task following the template's `Tasks` structure, inline `Completion criteria` rules, and `Task definition requirements` table in full." | :35 | unseen | This is the parent of the per-task rules: rows 122–132 (the `Tasks` structure and its inline `Completion criteria` rules) and rows 135–141 (the `Task definition requirements` table). Every one of them is unenforced. The specimen: `20260705`'s tasks omit the Verification review step the structure mandates (`steering-template.md:70`) and nothing objected. |
| 93 | "**Design sign-off task.** When the session has a `design.md` not settled at plan time, place a **"Design sign-off"** task … at the point where heavy build would otherwise start" | :36 | unseen | No rule checks that the task exists — unlike the Evaluation sign-off, which has row 71's backstop. A missing Design sign-off is invisible. |
| 94 | "**Evaluation sign-off task.** Always place a final **"Evaluation sign-off"** task as the session's last task." | :37 | recognised | Backstopped by `task-verify-workflow.md:219-222` — the only planning rule with a downstream check. It fires late (at end of session) and only inside a live flow; 5 of 8 past sessions have no such task and none escalated. |
| 95 | "**Self-check before persisting.** Before persisting (Step 5), confirm the last task in the list is "Evaluation sign-off" — if it is not, add it before persisting." | :38 | unseen | A self-check with no recorded output. `20260625-rn-lean` placed its Evaluation sign-off as `#15`, mid-list before `#6`–`#14`. |
| 96 | "Write the completed `steering.md` to `.rn/{yyyymmdd}-{slug}/steering.md`." | :41 | recognised | Row 79's consumers. |
| 97 | "Commit it: `chore: start session — {slug}`." | :42 | recognised | Confirmed used consistently in this repo (`git log --all --grep='chore: start session' --oneline \| wc -l` returns 11). Nothing reads the message, but its absence would leave the file uncommitted and therefore undiscoverable by `dn`/`up`'s `git log` search. |
| 98 | "Ensure the work is on a branch — if on the default branch, create `{slug}` first." | :43 | refuses | External and real, but not `rn`'s: `.claude/rules/plugin.md:37` records that in this repo "`main` is protected and only the user holds the privileges to clear its required" review, so a push from the default branch is refused by GitHub. (Stated on the repo's own written policy — `gh api repos/lovaizu/ccpm/branches/main/protection` returns 403 with this token, so it was not confirmed by command here.) |
| 99 | "Push the branch, then open a draft PR (`gh pr create --draft`) titled from the goal." | :44 | refuses | `gh pr create` errors on a missing branch or an existing PR; the failure is on screen. `:47-48` names the failure branch explicitly: "push or PR creation failed → report it and present the plan in the console instead". |
| 100 | "The PR body is a single link to the steering file and nothing else — do not copy the Goal, tasks, or any plan content into it. Use a branch-ref blob link" | :44 | unseen | The PR body is what the user opens at the plan gate. Verified on this session's PR #21: the body is the single blob link (plus a `Closes #17` line added by the user's own workflow). Fails at leg (3): the body is on the user's screen at the gate, but a body with the plan pasted into it reads as helpful rather than as a breach. Verified on this session's PR #21: `gh pr view --json body` returns the single blob link plus a `Closes #17` line added by the user's own workflow. |
| 101 | "Open the plan-gate ask with the session-status block … on both branches: push and PR creation succeeded → report the PR link and ask the user to review the plan on the PR; push or PR creation failed → report it and present the plan in the console instead." | :45-48 | unseen | The message is on the user's screen. Fails at legs (2) and (3), like row 73. |
| 102 | "**Design gate.** … When the design is settled at plan time, fold it into this plan-gate approval (one stop). When it is not, Step 4 placed a **Design sign-off** task" | :49 | unseen | See row 93. Which branch was taken is never recorded, so neither choice can be checked. |
| 103 | "**Take the sign-off via the user's verdict commands** … never infer approval and never record a verdict the user did not issue." | :50 | recognised | The harness stops the assistant from *invoking* `/rn:ty` or `/rn:gm` (`ty/SKILL.md:4`, `gm/SKILL.md:4`), not from writing that a verdict was given. Reader: the user; artifact: the message recording the verdict and the check-off that follows it; difference: they know whether they typed the command. |
| 104 | "**CRITICAL: DO NOT proceed without explicit user approval.**" | :51 | recognised | The ask ends the turn only if the ask is made. Reader: the user; artifact: the next message they receive; difference: the flow has advanced past a gate they never cleared. Nothing in `rn` declines on their behalf. |
| 252 | "Use the confirmed slug for the path." | :19 | recognised | The slug becomes the session directory name, which `dn/SKILL.md:14` and `up/SKILL.md:17` discover by `git log … -- '*/steering.md'` and `status-display.md:37-38` renders in every status header ("the session's slug (the steering directory name, date prefix dropped)"). A path built from a slug the user did not confirm is on their screen at the plan gate and in every later block. Nothing compares the path to what was confirmed. |
| 253 | "Coverage need not be complete: if an existing design.md covers the core of the work's area, treat it as the update target and record the session's new-but-related content under the sections it belongs to (adding new h3-level content is still "updating," not authoring fresh)." | :26-28 | unseen | The permissive half of row 83's judgement, and unrecorded in the same way: nothing states which existing `design.md` files were considered, how much of the area each covered, or why the threshold was or was not met. A session that skipped the question and a session that asked it and answered "no" produce the same `Design:` line. |
| 254 | The two sign-off tasks' prescribed content — Design sign-off: "Completion criteria: `design.md` is approved. Steps: present `design.md` to the user and take the verdict via `/rn:ty` (approve) or `/rn:gm` (revise → address the feedback, re-present)."; Evaluation sign-off: "Completion criteria: the Acceptance criteria run is approved. Steps: present the Acceptance criteria run result to the user and take the verdict via `/rn:ty` (approve) or `/rn:gm` (revise → address the feedback, re-present)." | :36-37 | unseen | Rows 93 and 94 cover whether the task is *placed*; this covers what planning must *write into* it, and nothing reads the written task against the prescription. Both past Evaluation sign-off tasks depart from it: `.rn/20260625-rn-lean/steering.md:231-252` and `.rn/20260705-improve-design-template/steering.md:239-254` each write their own Purpose, Steps and Completion criteria. `task-verify-workflow.md:219-222`'s backstop tests only that a task by that name was encountered, never what it says. |

## `steering-template.md` (106 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 105 | "Read when creating a new `steering.md`." | :3 | unseen | Looked for any record that the template was opened. `steering.md` carries the template's headings (row 106), which a session could equally reproduce from a previous session's file; there is no version, checksum or provenance line, so a read and a copy-paste are indistinguishable. |
| 106 | "**Copy the template block below verbatim.** Keep every heading. Keep the blank lines between fields" | :7 | recognised | The headings are consumed: `dn/SKILL.md:25` writes "the `State` section", `up/SKILL.md:24` reads it, `migration-workflow.md:21-23` compares "its `Goal` / `Acceptance criteria` / `Assumptions` / `Rules` / `Tasks` / `State` fields". A missing heading breaks a named consumer. Nothing checks the blank lines. |
| 107 | "**Leave placeholders in unpopulated sections.** `Tasks`, `State` start empty; fill later." | :8 | recognised | An empty section is a blank the user reads at the plan gate. |
| 108 | "**Fill each section per the rules below.**" | :9 | unseen | Parent of rows 109–141 — every per-section rule in this file. Nothing reads a written `steering.md` against any of them. |
| 109 | Doc-division: "**Requirements & acceptance criteria → `steering.md`**" | :15 | unseen | Looked for a reader that classifies content by kind. `migration-workflow.md:21-23` reconciles steering's *fields* against the template, never their contents against the doc-division, so design rationale written into `steering.md` sits in a legitimate field and reads normally. |
| 110 | "**Structure & decisions (how the parts fit, and why) → `design.md`** … rationale lives only here, at the decision level." | :16 | unseen | Same as row 109. |
| 111 | "**User-facing UX → `README`**" | :17 | unseen | Same as row 109. |
| 112 | "A decision lands in a task, in `design.md`, or in a rule. Deliberation and history live in git + the PR — never in steering." | :19 | unseen | Same absent reader as row 109. Searched the eight past `steering.md` files for a place where deliberation would be flagged: none exists, and `.rn/20260625-rn-lean/steering.md`'s task headings carry per-task narration (`— DONE through QA`, on 15 of 16 tasks) with nothing objecting. |
| 113 | "`Rn version:` … is written once, at creation, from the installed plugin's version — never user-edited afterward" | :21-24 | unseen | See row 86: absent from 6 of 8 sessions, and the comparison that would consume it treats absence as no-mismatch. |
| 114 | "The `Design:` line below it points to the session's `design.md`. A session with no design omits this line entirely" | :26-27 | recognised | Row 84's consumer (`migration-workflow.md:28-29`). |
| 115 | `Goal`: "why this is being done and what the user wants to change — the full intent, no added scope" | :37 | recognised | The user reads it at the plan gate; `status-display.md:37-38` compresses it into every status block's header. |
| 116 | `Acceptance criteria`: "the states / conditions by which the goal is judged achieved" | :41 | recognised | Consumed by the Evaluation sign-off task, whose completion criteria are "the Acceptance criteria run is approved" (`planning-workflow.md:37`) — the user reads the run at the last gate. |
| 117 | "two axes: goal alignment + quality" | :42 | unseen | Looked for a check on criterion coverage. QA reviews the artifact *against* the criteria (`task-verify-workflow.md:155`), never the criteria against this rule, so a list of criteria all on one axis passes every step `rn` defines. |
| 118 | "write these exhaustively, never sample — the complete set is what defines scope (in / out)" | :43 | unseen | Completeness of a list against an unstated whole is unverifiable by construction, and nothing tries. |
| 119 | `Assumptions`: "things taken to be true in pursuit of the goal — if one proves false, the plan changes" | :47 | recognised | Read by the user at the plan gate; `migration-workflow.md:21-23` names the field among what it reconciles. |
| 120 | "distinguish facts from assumptions — state explicitly if unverified" | :48 | unseen | Looked for a marker that survives writing. `steering-template.md:47-48` gives facts and assumptions the same bullet shape, so an unverified claim written without the caveat is typographically identical to a verified one, and no later step re-asks. |
| 121 | `Rules` seeds "commit and push every change; one completion marker per task" | :52 | recognised | The marker half is consumed by `up/SKILL.md:26`; the push half is visible as an unpushed branch on the PR. |
| 122 | "**Purpose**: what to achieve, 1-2 sentences" | :59 | unseen | Copied into the work-order (`task-execute-workflow.md:141`) and read by the user at the plan gate. Length is unchecked. Fails at leg (2): the work-order that copies `Purpose` is a prompt and never reaches disk, and no reader is sent to measure the sentence count at the gate. |
| 123 | "**Prerequisites**: tasks that must be completed first (or "none")" | :61 | unseen | Nothing reads prerequisites: `task-verify-workflow.md:215` advances to "the next unchecked task" by position, not by dependency. **A stated prerequisite has no consumer at all.** |
| 124 | Steps include "self-check (OK/NG per completion criterion, record in checks/{task-id}.md)" as a `- [ ]` item | :67 | unseen | The step is a checkbox in `steering.md`; `dn/SKILL.md:22-23` checks off completed steps and the file is on the PR. An unchecked box is a visible blank — but past sessions closed with unchecked boxes left behind (3 in `20260705`, 2 in `20260624`) and nothing objected. Fails at leg (2) for the step that matters: an unchecked box is a blank only for a step planning actually wrote, and a step never written leaves no blank. Past sessions closed with unchecked boxes still standing — 3 in `20260705-improve-design-template`, 2 in `20260624-rename-cmds-on-dn-up` — and nothing objected. |
| 125 | Steps include "QA expert review (subagent)" | :68 | unseen | Same checkbox mechanism as row 124, and it fails the same way: a step that planning never wrote cannot be a blank. Every session before `20260625` has QA steps; the review sections behind them are missing from most check files. |
| 126 | Steps include "Craft expert review (subagent, per the task's medium)" | :69 | unseen | Absent from all 5 sessions before `20260625-rn-lean`. Nothing noticed. |
| 127 | Steps include "Verification expert review (subagent, per the task's medium)" | :70 | unseen | **The specimen.** Absent from all 7 tasks of `20260705-improve-design-template` and from every earlier session; present in only 5 of 40 check files. The rule exists, the breach is plain in the output, and nothing in `rn` looks. |
| 128 | Steps include "(tasks that produce or revise structure/approach only) Design expert review (subagent)" | :71 | unseen | Same as row 126, plus the conditional judgement is never recorded. |
| 129 | Completion criterion ①: "is the objective achieved? — the objective met, not that an output was produced (write "the residue no longer keeps the tree dirty", not "DESIGN.md exists")" | :75-76 | unseen | This is the rule this session's Goal names as broken. It binds *Completion* criteria only; `20260705`'s *Acceptance* criteria were written as artifact existence (`:22-49`) and the template says nothing there (row 116). Nothing reads either against this bar. |
| 130 | Criterion ②: "are new problems absent? — name the representative failure modes and require their absence" | :77 | unseen | Same as row 129; most past criteria state no failure modes. |
| 131 | "objectively verifiable by a third party; no vague terms ("appropriate", "correct")" | :78 | unseen | Looked for anything that reads criterion text. `migration-workflow.md:33-38` re-judges Completion criteria against the `Task definition requirements` table, but only for unchecked tasks, only by reasoning, and with no recorded output (row 160). Nothing greps for the two words this rule names. |
| 132 | "state the end-state, never actions/reviews/gates (those belong in Steps); the grounds are recorded at verification … not written into the criterion text" | :79 | unseen | Same as row 129. |
| 133 | `State` placeholder: "`Status` is `paused` while a session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here, so only a genuinely suspended session reads `paused`." | :83-85 | recognised | Real consumers: `dn/SKILL.md:15-16` and `up/SKILL.md:19` both rank candidates by "`State` showing `Status: paused`". A stale `paused` mis-ranks discovery — and `20260615-subagent-execution/steering.md` still reads `Status: paused` today, a closed session that would win that ranking. |
| 134 | `Notes`: "bounded forward pointer … not a re-narration of the session (that lives in `git log`)" | :91 | recognised | Read by `up/SKILL.md:24` and `:28`. Boundedness is unchecked. |
| 135 | Granularity: "Purpose expressible in one sentence; split if it grows" | :100 | unseen | Consumed only by `migration-workflow.md:33-38`, which re-applies the same judgement with no recorded output. |
| 136 | Specificity: "Not "implement" but "implement `methodName()` in `ClassName`"" | :101 | unseen | Same as row 135. |
| 137 | Objectivity: "Completion criteria judgeable by a third party" | :102 | unseen | Same as row 135. The third party exists (QA, `task-verify-workflow.md:155`) but reviews *against* the criteria, never *the* criteria. |
| 138 | Prerequisites: "List dependencies explicitly; enables parallel/sequential judgment" | :103 | unseen | Row 123: nothing consumes prerequisites. |
| 139 | Criteria vs steps: criteria answer ① and ② with grounds, "not that an artifact was produced; actions, reviews, and gates go in Steps as `- [ ]` so their status stays trackable. The task-execution references' … Process selection section … is the source of *which* reviews apply — keep the two in sync" | :104 | unseen | "Keep the two in sync" names no mechanism, and the two are demonstrably out of sync: `task-execute-workflow.md:59-64` mandates Verification for every build task, and this template's Steps list has carried it since `0.7.0` — yet planning wrote it into 0 of 7 tasks in the very next session. |
| 140 | Flat tasks: "Number tasks `#1`, `#2`, …; do not group into phases or add phase-level gates … The user signs off only at the three scheduled gates" | :105 | recognised | Numbering is consumed by `up/SKILL.md:26`'s `complete task #{id}` grep and by `status-display.md:39-50`'s ranges. Non-sequential ids break neither, but `20260625-rn-lean` ordering `#1–#5, #16, #15, #6–#14` produced a task list whose reading order is not its numeric order. |
| 141 | Done annotation: "A task that is done but awaiting an external gate … may carry an explicit done annotation in its heading … such a task counts as completed for the session-status display" | :106 | recognised | Consumed by `status-display.md:19-22`: "A task counts ✅ when `steering.md` records it complete — checked off, or carrying an explicit done annotation". Both files agree; `20260625-rn-lean` used the annotation on 14 tasks with no `[x]` check-offs at all, so the whole session's ✅ state rests on prose matching. |

## `status-display.md` (83 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 142 | "The compact session map that opens every message stopping for user input while a session is active … The block comes first in that message — before the ask and anything else." | :3-5 | unseen | The block is rendered to the user by construction; its absence is a gap on their screen. Nothing flags it, and nothing in `rn` re-reads a sent message. Fails at legs (2) and (3): the block is rendered to the user, but nothing in `rn` re-reads a sent message and the user holds no spec to check it against. This concession applies to every `status-display.md` row below. |
| 143 | "**Emit only while a session is active** — its `steering.md` exists and is identified." with the listed exceptions (planning's pre-persist asks, `/rn:up` before identification, `/rn:gm` or `/rn:ty` with no active session) | :9-12 | unseen | The exception list is the rule's own content: a block emitted at one of the four excluded stops would have to invent task ids for a `steering.md` that is not yet identified. Nothing compares those ids to a file, and the user, mid-planning, has no list to compare them to. |
| 144 | "**Asks and flow-ending reports both count as stops** … on a report the 👉 line states where the session stands and the user's next move instead of an ask." | :13-16 | unseen | The class boundary decides whether a suspend report, an abort, or a session-close message carries a block. A report that omits it is simply a report; no step re-reads a sent message to notice. |
| 145 | "**Derive the block fresh from the active `steering.md` at emit time** — its `Goal`, task list, and check-offs are the only source; never reuse an earlier block." | :17-18 | unseen | A stale block and a fresh one look identical unless the state changed between them, and nothing compares the block to the file. |
| 146 | "**A task counts ✅ when `steering.md` records it complete** — checked off, or carrying an explicit done annotation … Done-but-awaiting … still counts ✅; the pending item goes on the outlook line" | :19-22 | unseen | `steering.md`'s check-offs are a real input here (rows 141, 216), but the block this rule produces has no reader but the user, and no step compares the ✅ set to the file it was derived from. |
| 147 | "**Write the block in the user's conversation language.**" | :23-24 | recognised | Immediately obvious to the user. |
| 148 | "**Markers are fixed**: ✅ completed / 👉 current / ⬜ remaining." | :25 | unseen | A substituted marker changes only how the block looks. The user holds no marker table, and nothing in `rn` parses an emitted block. |
| 149 | The format block — header / ✅ / 👉 / ⬜ / outlook, in that order | :29-35 | unseen | Section order is legible only against the format block at `:29-35`, which the user does not have in front of them. A block with the outlook line first is still a readable block. |
| 150 | "**Header** — `── {slug}: {goal one-liner} ──`: the session's slug (the steering directory name, date prefix dropped) and a one-line compression of steering's `Goal`." | :37-38 | unseen | The header compresses steering's `Goal` (`:37-38`), and a compression that drops or distorts it has no second reader. The slug half is checkable against the directory name; nothing checks it. |
| 151 | "**✅ completed** … Group consecutive ids into ranges … comma-separate non-consecutive groups … No completed tasks yet → no ✅ lines." | :39-42 | unseen | Range-collapsing is arithmetic over the check-off set. A wrong range and a right one are both plausible strings, and no step recomputes the ranges from `steering.md`. |
| 152 | "**👉 current** — exactly one line … A stop not tied to a numbered task (the plan gate; an escalation that spans tasks) names the gate or moment instead of an id." | :43-48 | unseen | The one-line rule and the report-form substitution are shape constraints on a message nobody re-parses. A block with two 👉 lines would read as an unusually detailed block. |
| 153 | "**⬜ remaining** … **No remaining tasks → omit the ⬜ lines entirely** — never render an empty ⬜ section." | :49-50 | unseen | An empty ⬜ section is exactly the artifact this forbids, and nothing scans for it. `.rn` retains no record of emitted blocks at all, so past breaches cannot even be counted. |
| 154 | "**Outlook** — one closing parenthesized line: what follows this stop" | :51-52 | unseen | One closing parenthesized line saying what follows. Its absence removes information the user never had, and nothing supplies it from elsewhere. |

`status-display.md` is the file where the tightened boundary bites hardest. Every one of its rules used
to read as enforced, because its entire product is a block the user sees; on the recognition test all
thirteen fall to `unseen` except row 147 (a block in the wrong language is legible to the user with no
rule in hand). The user is the only checker, no `rn` step ever compares an emitted block against the
`steering.md` it was derived from, and nothing in `rn` re-reads a sent message. Rows 142–144, 146,
148–154 are group U9's core.

## `migration-workflow.md` (70 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 155 | "Invoked by a command skill (`on`/`dn`/`up`/`ty`/`gm`) when the active session's `steering.md` `Rn version:` line does not match the installed plugin's version — the skill's own version-check step (a plain string comparison) is what triggers this file … Run once per invocation." | :3-6 | unseen | The trigger is a prose step in five skills (`on/SKILL.md:15` and siblings) with no recorded output. It has never fired in this repo: 6 of 8 sessions carry no `Rn version:` line, and the two that do were current when written. |
| 156 | "Coordinator only: no implementation expert, and no QA/Design/Craft/Verification review, spawns for this procedure itself … The coordinator reads each artifact, judges drift, and edits it directly." | :8-11 | unseen | The edits land as a commit on the PR (`:56`), which the user reads. Nothing checks that no expert was spawned. Fails at leg (1): the reconciliation commit lands on the PR, but no reader is assigned to it and the property in question — that no expert was spawned — leaves no trace in a commit either way. |
| 157 | "Reconcile the three artifacts below **in this order** — steering, then design, then tasks." | :15-18 | unseen | Looked for a trace of ordering. The three steps' edits are applied and committed together (`migration-workflow.md:56`), so one commit carries all three regardless of the order they were made in; nothing timestamps them and no file records which ran first. |
| 158 | Step 1: "Compare the session's `steering.md` … against the current `steering-template.md`. Judge by reasoning what has drifted … and edit `steering.md` directly to close it." | :20-25 | unseen | An unrecorded judgement. A pass that finds nothing and a pass that never ran produce the same empty diff. |
| 159 | Step 2: "Read the session's `steering.md` `Design:` line; if it is absent … skip this step entirely. If present, follow `design-template.md`'s own "Updating an existing design.md" procedure … do not re-derive reconciliation logic here." | :27-31 | unseen | The `Design:` line is a real input that determines a branch; a dangling pointer (row 90) sends this step at a missing file, which errors on read. Fails at leg (1): the `Design:` line is a real input to the branch, but nothing checks that the branch was taken. A read error on a dangling pointer (row 90) is the pointer's failure, not this step's; a step skipped outright errors on nothing. |
| 160 | Step 3: "For every unchecked task … judge its Purpose / Prerequisites / Steps / Completion criteria against each row of that table — Granularity, Specificity, Objectivity, Prerequisites, Criteria vs steps, Flat tasks, Done annotation — and edit the task directly" | :33-38 | unseen | Same as row 158; and the table rows it applies are themselves unenforced (rows 135–141). |
| 161 | "Leave every already-checked-off task untouched — reconciliation targets the forward-looking remainder, not the record of what already happened." | :39-40 | unseen | A touched historical task shows in the reconciliation commit's diff on the PR. Fails at leg (1): a touched historical task shows in the reconciliation commit's diff, and `migration-workflow.md` spawns no reviewer (`:8-11`) and passes through no gate (`:56-58`), so no reader is assigned to that diff. |
| 162 | For a task whose Completion criteria changed and that has a `checks/{task-id}.md`: "record in its Overall Verdict a `Ready to check off: No — criteria reconciled, self-check/review must re-run` line" — and if no such file exists, write nothing | :41-52 | unseen | The rule names its own consumer at `:47-48`: "`task-verify-workflow.md`'s Phase: Complete only checks off once Verify has cleared with `Ready to check off` reading Yes". Phase: Complete says something else — `task-verify-workflow.md:208-209` reads "**Check off steering.** With Verify cleared — or, for a sign-off task, once its gate verdict is approved — check off the task in `steering.md` directly", with no mention of the field. So the line this rule writes blocks nothing. What that has cost in practice is recorded under U8. |
| 163 | "Apply the reconciling edits from all three steps and commit them directly. This is not one of the three scheduled gates … and it does not go through per-task QA/Craft/Design review — it is a mechanical, no-gate procedure." | :56-58 | unseen | The commit is on the PR the user reads. This is deliberate: the rule's own design accepts "an occasional wrong reconciliation … caught via normal PR/git-log review" (`.rn/20260705-improve-design-template/steering.md:58-59`). Fails at leg (1) for the same reason, and deliberately: the rule's own design accepts "an occasional wrong reconciliation … caught via normal PR/git-log review" (`.rn/20260705-improve-design-template/steering.md:58-59`) rather than a live approval step. |
| 164 | "Once the reconciling edits are committed, update the session's `steering.md` `Rn version:` line to the installed plugin's version — the last step, so the stamp only advances once the artifacts it certifies are actually current." | :59-61 | unseen | Nothing checks the ordering, and a stamp advanced without the edits is indistinguishable from one advanced after them. |
| 165 | "Every comparison above asks one question only: does this artifact match what the **currently installed** templates/workflows require, right now. This file never reads `CHANGELOG.md` and never reasons about version ranges or deltas between the session's recorded version and the installed one" | :65-70 | unseen | A prohibition on a reasoning method; nothing observes the method. |

## `design-template.md` (139 lines)

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
| 177 | "**Revise only what changed.** … leave every other section's existing text untouched. Carrying forward unchanged text is correct, not lazy" | :106-108 | recognised | A wholesale rewrite shows in the commit diff the coordinator reads (`task-verify-workflow.md:139`) and on the PR. |
| 178 | "**The decision-plus-reasoning contract from fresh authoring still applies to whatever you touch.**" | :109-111 | unseen | Row 170. |
| 179 | "**If the document predates the five-section shape** … reconcile it toward the current five-section shape as part of this update … relocating content to the section it actually belongs to … not license to rewrite unrelated, still-accurate content." | :112-126 | recognised | The relocation shows in the diff (row 177's reader). Whether the *right* content moved is unchecked. |
| 180 | "**Give genuinely open content a destination outside `design.md`.** … Session-scoped: put it in that session's `steering.md` Notes field … Canonical/cross-session: track it outside `design.md` instead (e.g. a repo issue)" | :127-137 | unseen | Looked for the destination end. `steering-template.md:91`'s `Notes` field and a repo issue are the two named landing places, and nothing walks from a removed "Open questions" item to either; a question resolved by deletion leaves nothing in the diff but the deletion. |
| 181 | "**Add or drop `4.N` subsections to match what changed** … a new mechanism gets a new subsection, a removed one loses its subsection instead of being left stale." | :138-139 | unseen | Row 171. A stale subsection reads exactly like a current one. |

## `pr-feedback-workflow.md` (153 lines)

This file is the densest cluster of genuinely enforced rules in `rn`, because almost every step is a
`gh` call whose failure is a non-zero exit rather than a prose instruction.

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 182 | "A **coordinator** dispatches one **execution subagent** per review thread, sequentially, and reviews each result before the next." | :3-4 | unseen | Nothing records the dispatch (rows 5, 11). |
| 183 | "Verification is a single coordinator pass — not the QA-expert / multi-round chain" | :4-7 | unseen | A scope statement about what does *not* run; its breach (running experts anyway) leaves no artifact. |
| 184 | "Entered from `/rn:gm` with no argument — the argument/no-argument routing rule lives in `gm/SKILL.md`." | :9-10 | unseen | Not a refusal. The harness gates `/rn:gm` itself (`gm/SKILL.md:4`), but nothing stops the loop being entered from anywhere else, and `gm/SKILL.md:15`'s branch is a rule about which step to take, not a gate on taking it. Entering the loop wrongly leaves no artifact that differs from entering it rightly. |
| 185 | Coordinator "Never resolves a thread." | :14-16 | recognised | Thread resolution is GitHub state the reviewer sees; a thread resolved by the assistant is visibly resolved-by-assistant on the PR. |
| 186 | Execution subagent "Handles exactly one thread, with exactly one of two outcomes (address-and-reply, or reply-with-a-question). Never resolves a thread." | :17-18 | recognised | The reply is posted to a specific thread on the PR; two threads touched by one subagent show as two replies. Row 185's reader. |
| 187 | "**Find the session's PR** for the current branch:" — followed by the fenced command `gh pr view --json number,url` | :22-26 | refuses | Real command with a real failure mode. Verified: run on this branch it returns `{"number":21,"url":"…/pull/21"}` with exit 0; on a branch with no PR it exits non-zero, which is exactly what the next row handles. |
| 188 | "If this exits non-zero or reports "no pull requests found" … **stop and report** — do not fabricate a PR number or proceed into the GraphQL call. Open that report with the session-status block" | :28-31 | refuses | The GraphQL query at `:46` takes `-F pr={number}`; with no number there is nothing to pass and the call fails. The prohibition on fabricating one is only prose, but the fabricated number would return an error from the API. |
| 189 | "Capture `owner` and `repo` as **two separate** values" with the two `gh repo view -q` commands | :33-38 | refuses | A combined value breaks `-f owner=` / `-f repo=` in the GraphQL call, which the API rejects. |
| 190 | "**Fetch all review threads** via GraphQL, **paginating** `reviewThreads` until exhausted … **Repeat** the call while `reviewThreads.pageInfo.hasNextPage` is true … **accumulate** `nodes` across pages." | :42-72 | unseen | A skipped page silently drops threads: the loop's queue is smaller, and nothing counts what should have been there. This is the one step in the file whose breach is invisible. |
| 191 | "Keep a thread **only** when both hold: … `isResolved == false`, AND … the **last** comment's author … equals the **first** comment's author" | :74-78 | recognised | Wrongly kept threads produce a duplicate reply on the PR, which the reviewer sees; wrongly dropped ones leave the thread unanswered, which the reviewer also sees. The reviewer is a real second reader here. |
| 192 | "Drop every other thread … For each kept thread record: the **first** comment's `databaseId`, `path` and `line` … and the comment bodies" | :80-82 | refuses | The reply endpoint at `:109` is keyed on `first_comment_databaseId`; a wrong or missing id is rejected by the API. |
| 193 | "Process the queue **one thread at a time**. Never dispatch two threads in parallel" | :86-87 | unseen | Looked for a trace of concurrency. The loop's only outputs are the replies on the PR and the commits behind them, both order-independent; nothing records dispatch times, and `pr-feedback-workflow.md:130-134`'s between-item review inspects a result, never when it arrived. |
| 194 | Work-order contents: Thread (`path`, `line`, full bodies, `databaseId`) and Task ("produce exactly one of the two outcomes") | :89-92 | unseen | Row 27: the prompt is never written down. |
| 195 | Outcome (a): "Make the change. … Stage the touched paths **explicitly** … Never `git add -A` or `git add .`." | :94-95 | recognised | The PR diff, read by the reviewer whose thread this is. Row 35's limits apply. |
| 196 | Outcome (a): "Commit with a plain conventional message … The message must **not** contain `complete task #`." | :96-97 | recognised | Row 36's consumer (`up/SKILL.md:26`). A PR-feedback commit carrying the substring would check off an unrelated task on the next resume. |
| 197 | Outcome (a): "Push to the session PR. Never force-push." | :98 | recognised | Not a refusal in either half. A skipped push leaves the commit local, and the Done reply at `:105-111` then carries a permalink to a commit GitHub does not have — reader: the thread's reviewer, who `:144-145` expects to "resolve it after reading the reply"; artifact: their own thread; difference: the commit link 404s. A force-push is not declined by anything and shows only on the PR timeline, which nothing asks anyone to read. |
| 198 | "**If the commit or push fails, do not post a Done reply** (its permalink would point at an unpushed, dead commit). Return the failure in the summary … post the reply only once the commit is confirmed pushed." | :99-102 | recognised | **The mechanism this row used to claim does not exist.** `gh browse <sha> -n` builds a URL locally and never asks GitHub whether the commit is there — run here on an all-zero sha it printed `https://github.com/lovaizu/ccpm/issues/0000000000000000000000000000000000000000` and exited 0. So nothing prevents a Done reply for an unpushed commit. What remains is recognition: reader — the thread's reviewer; artifact — their thread; difference — a dead commit link. |
| 199 | "Once the commit is pushed, get its permalink: `gh browse <sha> -n`" | :103-104 | recognised | Same reader as row 198. Skipping the permalink step yields a Done reply with no commit link, which the reviewer reads on their own thread. The command itself refuses nothing (see row 198). |
| 200 | "**Reply to the thread** with a short summary of what was done plus the commit link, in-reply-to the thread's first comment — **only after the commit is pushed**" | :105-111 | recognised | The reply is on the PR; a missing one leaves the reviewer's thread unanswered, and the loop's own queue filter (row 191) re-picks it up on the next run. That re-pick is a genuine self-correcting mechanism. |
| 201 | "**Outcome (b) — needs a decision / is unclear:** make **no** code change. Reply to the thread with the question" | :113-119 | recognised | Same reader as row 200; a code change made anyway shows in the PR diff. |
| 202 | "**Return** — a compact summary: which outcome, what changed (files), the commit SHA and that it was pushed … or the question asked" | :121-122 | recognised | Read by the coordinator at `:130`. |
| 203 | "**Never resolve the thread.** Resolution is the author's act on GitHub" | :124 | recognised | Row 185. |
| 204 | "**Check the result.** … **OK → dispatch the next thread.** … **Problem → re-instruct the same subagent on the same thread.** Do not advance until it is right." | :128-134 | recognised | The coordinator reads the summary and the PR; a wrong result shows as a reply that does not match its thread. |
| 205 | "When the queue is empty, the loop is done — report the loop result … opening that report with the session-status block" | :136-138 | unseen | The loop-completion report reaches the user, but nothing in `rn` re-reads it, and the thread state it summarises lives on GitHub, where the user would have to go and count for themselves. |
| 206 | "The loop **never** resolves a thread. Neither the coordinator nor the subagent calls `resolveReviewThread` … The loop treats GitHub's unresolved state as its **queue**." | :142-148 | recognised | This is `rn`'s single best-designed mechanism: state lives in GitHub, not in the assistant's memory, so a missed thread is re-collected on the next run (row 200). Quoted in full because the guarantee is real. |
| 207 | "One coordinator pass per item … is the whole of verification. No QA expert, no Design / Craft / Verification experts, no multi-round iteration cap." | :152-153 | unseen | Row 183. |

## `on/SKILL.md` (17 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 208 | "`disable-model-invocation: true`" / "Has side effects (writes files, commits, pushes, opens a PR) — run only on explicit `/rn:on`." | `on/SKILL.md:3-4` | refuses | The harness refuses model invocation of the skill. The only machine-enforced rule in the plugin. |
| 209 | "**Plan the session.** Read `${CLAUDE_PLUGIN_ROOT}/references/planning-workflow.md` and run it in sequence." | `on/SKILL.md:13` | recognised | The workflow's own outputs (`steering.md`, the `chore: start session` commit, the draft PR) are artifacts whose absence shows. Skipping a *step* inside it shows only if that step had an artifact. |
| 210 | "**Check version.** … on a mismatch, run `…/references/migration-workflow.md` first — on a match, do nothing. Since step 1 just stamped that line from this same installed version, this branch can never actually fire here — it's kept only so `on`'s step matches `dn`/`up`/`ty`/`gm`'s" | `on/SKILL.md:15` | unseen | The file states outright that the branch is unreachable. It is a consistency-of-appearance rule, not a check. |
| 211 | "**Begin task #1.** After approval, read `…/references/task-execute-workflow.md` then `…/references/task-verify-workflow.md` and execute task #1 following them in sequence." | `on/SKILL.md:17` | recognised | "After approval" is row 104's recognition, with the same reader and artifact. The read-both-files-in-order half is row 1: nothing records which file was read, or whether either was. |

## `dn/SKILL.md` (59 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 212 | "`disable-model-invocation: true`" / "run only on explicit `/rn:dn`" | `dn/SKILL.md:3-4` | refuses | Row 208's harness mechanism. |
| 213 | "Records resume state and hands off. Does not execute tasks." | `dn/SKILL.md:9` | unseen | A task executed during suspend would land as a deliverable commit in the suspend push, visible on the PR. Fails at leg (1): a deliverable commit made during suspend rides along in the suspend push and lands on the PR, but no step and no scheduled reader opens that push to ask what was in it. |
| 214 | "**Locate steering.md.** Use the path known from this session. If unknown: run `git log --diff-filter=AM --name-only --pretty=format: -- '*/steering.md' \| head -5`, keep the paths that exist on disk, and take the one whose `State` shows `Status: paused`, else the most recent." | `dn/SKILL.md:13-16` | unseen | Not a refusal: the command runs, and nothing declines when its output is ignored or the wrong candidate is taken. Nothing downstream re-derives the choice either — `dn` writes `State` into whichever file it picked, and the next `/rn:up` starts from whatever it finds. The known data defect stands: `.rn/20260615-subagent-execution/steering.md:340` still reads `- **Status**: paused`, so a closed session outranks the live one. |
| 215 | "**Check version.** Compare `steering.md`'s `Rn version:` line to the installed plugin's version … on a mismatch, run `…/references/migration-workflow.md` first — on a match, do nothing." | `dn/SKILL.md:18-20` | unseen | Row 86: 6 of 8 sessions have no such line, and no file defines the missing-line case. |
| 216 | "**Check off progress.** In steering.md, check off completed task steps and add any tasks discovered during the work." | `dn/SKILL.md:22-23` | recognised | The check-offs are consumed by `status-display.md:19-22` and by `task-verify-workflow.md:215`'s "next unchecked task". |
| 217 | "**Write the `State` section** per `steering-template.md`'s State placeholder: `Status: paused`, `Date`, `Last completed`, `Next`, `Notes` — cap `Notes` to the bounded forward pointer" | `dn/SKILL.md:25-27` | recognised | Reader: `up`, at `up/SKILL.md:19` ("rank by `State` showing `Status: paused`, then most recent commit") and `:24` ("Read the `State` section: last completed task, next task, and notes"). Artifact: the `State` section itself. Difference: a missing or wrong `State` sends resume to the wrong session or leaves it with no next task. The `Notes` cap is unchecked. |
| 218 | "**Commit the work.**" — "Tree clean → skip this commit. … Current task's steps all checked → commit normally. … Some steps unchecked → commit with a `wip:` prefix." | `dn/SKILL.md:29-32` | unseen | `git status` output is on screen and drives the branch; the resulting message is on the PR. Nothing verifies the prefix matches the checkbox state. Fails at leg (3): `git status` picks the branch, but nothing compares the chosen prefix to the checkbox state, so a `wip:` on a finished task and a plain message on an unfinished one both read as ordinary commits. |
| 219 | "The message must not contain `complete task #`." | `dn/SKILL.md:33` | recognised | Row 36's consumer — and the historical breach `4daf6b2` is precisely a suspend-time bookkeeping commit that quoted this rule in its own body. |
| 220 | "**Resolve untracked residue.** Run `git status --porcelain` … Regenerable test/build artifact … → append a matching rule to the repo-root `.gitignore` (create it if absent). Any doubt → handle as the next item instead." | `dn/SKILL.md:35-39` | recognised | Reader: step 8 of the same procedure (`dn/SKILL.md:50-54`), which re-runs `git status --porcelain` and behaves differently on a non-empty result — recording each leftover into `State → Notes`. That is a genuine post-condition on step 6, and the only one in the plugin. It is not a refusal: nothing declines a wrong `.gitignore` rule, only the residue it fails to clear. |
| 221 | "Anything else → ask the user how to handle it … opening the message with the session-status block … For any path the user does not resolve, append its exact `git status --porcelain` string to `State → Notes`." | `dn/SKILL.md:40-43` | recognised | Reader: step 8 again (`dn/SKILL.md:50-54`) — a path the user was never asked about is still untracked when step 8 re-runs `git status --porcelain`, and gets recorded as user-deferred. The ask itself ends the turn, which is compliance, not a mechanism. The one breach nothing reaches is deleting the path (row 222). |
| 222 | "Never delete a file yourself." | `dn/SKILL.md:44` | unseen | A deleted untracked file leaves no trace anywhere — not in git, not in `git status`. This is the clearest example in `rn` of a rule whose breach is undetectable in principle. |
| 223 | "**Commit and push.** Commit the `State` changes and any `.gitignore` edit together in one commit, then `git push`. If push fails, continue and record that it failed (for step 9). Never amend, never force-push." | `dn/SKILL.md:46-48` | refuses | `git push` reports its own failure and the rule handles it. The amend half is a genuine refusal: an amended commit that has already been pushed is rejected as a non-fast-forward on the next push, and the rule forbids the force-push that would clear it. |
| 224 | "**Verify clean.** Run `git status --porcelain` … Non-empty → for each remaining (non-gitignored) untracked path, if its exact … string is not already recorded in `State → Notes` … record it there as user-deferred; then go to step 9. Never loop back to step 6. Never delete a file." | `dn/SKILL.md:50-54` | unseen | The re-run is a real post-condition on step 6 — which is why row 220 is recognised — but nothing checks that step 8 itself ran. A `dn` that skips it and a `dn` that runs it and finds an empty tree produce the same report and the same commit. |
| 225 | "**Report.** Open the report with the session-status block … then output the branch name. If the last push did not succeed, state that the commits are local-only and must be pushed. Name any user-deferred paths" | `dn/SKILL.md:56-59` | unseen | The report is on the user's screen; the "local-only" claim is checkable against the PR. Fails at leg (3): the report is on the user's screen, and its one checkable claim — that commits are local-only — would have to be checked against the PR by someone who has no reason to. |

## `up/SKILL.md` (34 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 226 | "`disable-model-invocation: true`" / "run only on explicit `/rn:up`" | `up/SKILL.md:3-4` | refuses | Row 208. |
| 227 | "**Handle a dirty tree.** … Tree dirty → run step 2's discovery first, read-only … then propose a `wip:` commit or a discard, opening the message with the session-status block … and wait for confirmation before touching the working tree." | `up/SKILL.md:13-15` | unseen | The dirty-tree branch is read from `git status`, but nothing declines a tree touched without confirmation, and the load-bearing half leaves no residue: a discarded working tree is gone from git, from `git status`, and from the report. The `wip:` half would at least land as a commit on the PR. |
| 228 | "**Find steering.md.** Run `git log --diff-filter=AM --name-only --pretty=format: -- '*/steering.md' \| head -5` and keep the paths that exist on disk." | `up/SKILL.md:17` | unseen | A real command, but running it is not the rule anything checks — nothing re-derives the candidate list or compares it to what was used. `head -5` also truncates silently once a repo has more than five session directories; this repo already has eight `steering.md` files. |
| 229 | "One result → use it. … Multiple → rank by `State` showing `Status: paused`, then most recent commit, and propose the top candidate. … Zero → tell the user "No steering.md found. Run `/rn:on` to start." and stop." | `up/SKILL.md:18-20` | unseen | Nothing declines a wrong branch: the zero case ends the turn only if the assistant takes it, and the ranking is a judgement fed by row 133's stale `paused`. A wrongly ranked candidate produces a resume that looks entirely normal. |
| 230 | "From step 3 on, any message stopping for user input opens with the session-status block" | `up/SKILL.md:22` | unseen | A blanket instruction covering every later stop in `up`. It inherits row 142's problem exactly: the block goes into a message the user answers rather than audits. |
| 231 | "**Read State.** Read the `State` section: last completed task, next task, and notes." | `up/SKILL.md:24` | unseen | Nothing declines a resume that skipped `State`. The step's output lives only in the agent's context; a session resumed from a guess and a session resumed from the file produce the same next commit. |
| 232 | "**Sync tasks.** Cross-check `git log` against the unchecked tasks. A commit matches a task when its message contains `complete task #{id}`; check that task off" | `up/SKILL.md:26` | recognised | Reader: this rule *is* a downstream consumer, and skipping it leaves tasks unchecked in `steering.md`, which `task-verify-workflow.md:215` and `status-display.md:19-22` then read — the session re-runs work already done. Nothing refuses. The mechanism also produces wrong answers on its own terms: `complete task #{id}` is a substring test, so `complete task #1` is a prefix of `complete task #1b`, `#10`–`#14` and `#16`; `git log --all --grep='complete task #1' --oneline \\| wc -l` returns 16 here, 7 of them other tasks, and three commits (`4daf6b2`, `893de07`, `de0b1ec`) carry the substring in a body without being markers. |
| 233 | "**Check blockers.** If `State` notes mention a blocker, investigate and find an alternative approach before removing any task." | `up/SKILL.md:28` | unseen | A removed task disappears from `steering.md`, which the user sees in every subsequent status block. Fails at leg (3): a removed task simply disappears from the ⬜ line, and the user holds no earlier copy of the list to miss it from. |
| 234 | "**Clean up State.** Replace the `State` section with its template placeholder and commit the reconciliation." | `up/SKILL.md:30` | recognised | The commit is on the PR. Skipping it leaves `Status: paused` behind — exactly the residue in `20260615-subagent-execution/steering.md` that still mis-ranks discovery today. |
| 235 | "**Check version.** … on a mismatch, run `…/references/migration-workflow.md` first — on a match, do nothing." | `up/SKILL.md:32` | unseen | Row 86. |
| 236 | "**Begin the next task.** Read `…/references/task-execute-workflow.md` then `…/references/task-verify-workflow.md` and execute the next unchecked task following them in sequence." | `up/SKILL.md:34` | recognised | "Next unchecked" is read from `steering.md`; the ordering half is row 1 (`unseen`). |

## `ty/SKILL.md` (26 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 237 | "`disable-model-invocation: true`" / "is user-invoked — run only on explicit `/rn:ty`" | `ty/SKILL.md:3-4` | refuses | Row 208 — and this is what makes rows 16 and 103 meaningful: an approval cannot be self-issued. |
| 238 | "Approves the pending rn confirmation and advances the flow. Performs no revision." | `ty/SKILL.md:9` | recognised | A revision made under `/rn:ty` lands as a commit the user did not ask for, on the PR. |
| 239 | "**Check version.**" | `ty/SKILL.md:13` | unseen | Row 86. |
| 240 | "**Identify the pending approval.** … Exclude weigh-in / escalation questions … State the identified target back. Proceed only if it is unambiguous; if more than one approval is plausibly pending … ask the user which before recording approval" | `ty/SKILL.md:15` | recognised | "State the identified target back" puts the identification on the user's screen before it is acted on — a deliberate, real, and rare design: the rule creates its own reader. |
| 241 | "**Record it as approved.** Register the pending confirmation as accepted." | `ty/SKILL.md:17` | recognised | For a task gate, the record is the `steering.md` check-off (`task-verify-workflow.md:208`), which is committed and read downstream. For a plan gate there is no artifact at all. |
| 242 | "**Advance the workflow.** … a plan or design gate passes — execution proceeds to the next task; … an evaluation gate passes — the session can close; … a reviewed item is accepted … When the advance ends the flow … open that closing report with the session-status block" | `ty/SKILL.md:19-24` | unseen | The advance itself is recognised where it lands in an artifact (row 241); the closing report's block is not, for row 142's reason. |
| 243 | "**Nothing pending.** If nothing is actually awaiting approval, open the reply with the session-status block …, say so, and do nothing else." | `ty/SKILL.md:26` | unseen | The nothing-pending reply is a message and nothing else. No artifact differs between a compliant reply and a breaching one, so even the trace available to row 241 is absent here. |

## `gm/SKILL.md` (21 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 244 | "`disable-model-invocation: true`" / "run only on explicit `/rn:gm`" | `gm/SKILL.md:3-4` | refuses | Row 208. |
| 245 | "**Check version.**" | `gm/SKILL.md:13` | unseen | Row 86. |
| 246 | "**Branch on the argument.** Trim `$ARGUMENTS` of surrounding whitespace first; treat a blank/whitespace-only value as empty. If non-empty after trimming, it is the feedback — go to step 3. If empty … go to step 4." | `gm/SKILL.md:15` | recognised | Not a refusal — nothing declines the wrong branch — but the wrong branch is recognised at once. Reader: the user who typed `/rn:gm <text>`; artifact: the report they get back; difference: their feedback was never acted on and the PR's threads were answered instead. The predicate itself is the only fully specified conditional in the plugin. |
| 247 | "**With feedback (`$ARGUMENTS` present).** Treat `$ARGUMENTS` as a revise verdict on the pending item … If there is no pending item, treat `$ARGUMENTS` as a direct instruction and act on it … do not stall on a missing target. Apply the revision … then report, opening the report with the session-status block … Do not enter the PR-feedback loop." | `gm/SKILL.md:17` | unseen | The revision lands as commits on the PR and the report is on the user's screen. Whether it addressed the feedback is unchecked. Fails at leg (3): the revision's commits are on the PR and the report is on the user's screen, but whether they address the feedback is a judgement nobody is asked to make. |
| 248 | "**From the PR (no argument).** Read `…/references/pr-feedback-workflow.md` and run that loop against the current PR's review comments." | `gm/SKILL.md:19` | unseen | Nothing declines this. The loop's own `gh` calls (rows 187–192) refuse a *malformed* call once the loop is running; they say nothing about whether the loop was entered at all. |
| 249 | "**Either way, this is a revise verdict** … It drops nothing: every piece of feedback is acted on." | `gm/SKILL.md:21` | recognised | For PR feedback: real — an unaddressed thread stays unresolved and is re-collected on the next run (`pr-feedback-workflow.md:146-148`). For `$ARGUMENTS` feedback: nothing at all, since the feedback exists only in the conversation. |

---

# The enforced set

**93 rows — 13 `refuses` and 80 `recognised`.** They are a partition: every row appears in exactly one
of the four groups below, and 5 + 8 + 49 + 31 = 93. Listed by mechanism so task #2 can see what it has
to work with — a rebuilt rule has to attach to one of these four, or invent a fifth.

## A. The harness refuses the action — 5 rows

Rows **208, 212, 226, 237, 244.** `disable-model-invocation: true` in each skill's frontmatter. The
model cannot invoke the skill; only the user typing `/rn:on` can. This is the only place in the plugin
where something other than the model decides, and it guards exactly one property: that the five
commands are user-initiated. It does **not** make the three gates self-executing — it stops the
assistant issuing `/rn:ty`, not writing "approved" in prose, which is why rows 21 and 103 are
`recognised` rather than `refuses`.

## B. An external command fails — 8 rows

Rows **72, 98, 99, 187, 188, 189, 192, 223.** `gh pr create` on a branch that already has a PR (72,
99); a push to a protected `main` (98); `gh pr view` exiting non-zero and the GraphQL and reply calls
rejecting a missing PR number, a combined `owner`/`repo` value, or a bad comment id (187, 188, 189,
192); a non-fast-forward push after an amend (223). Every one sits in `planning-workflow.md`,
`pr-feedback-workflow.md` or `dn` — the only files that actually run commands.

Nine rows that the first pass counted here have been removed: 197, 198, 199 (nothing declines an
unpushed commit — `gh browse <sha> -n` builds its URL locally, see row 198), 214, 224, 228, 229, 231,
248 (a command the agent runs and interprets is not a mechanism that refuses it), and 220, 232 (real
consumers, but they recognise rather than refuse).

## C. A named reader is made to look — 49 rows

Three readers, each with an artifact the flow puts in front of them.

- **The coordinator, reading the committed diff and the check file** — mandated at
  `task-verify-workflow.md:139-146` ("Read the committed diff yourself … Confirm the change matches
  the task's scope and Completion criteria") and `:83-84`. Rows **2, 4, 23, 24, 25, 29, 32, 33, 34,
  35, 42, 50, 58, 177, 179, 202** (16).
- **The user at a scheduled gate, reading what the gate presents** — the plan on the PR, the design,
  the Acceptance criteria run, and the verdict recorded against their name. Rows **13, 16, 21, 76,
  77, 78, 89, 103, 104, 107, 115, 116, 119, 147, 211, 238, 240, 241, 246, 252** (20). This is the
  narrow sense of "the user reads it": the gate exists to make them read that artifact and answer for
  it. A message they merely receive is not this, and lands in U9.
- **The PR thread's reviewer, returning to their own thread** — `pr-feedback-workflow.md:144-145`:
  "the reviewer who opened the thread resolves it after reading the reply." Rows **185, 186, 191, 195,
  197, 198, 199, 200, 201, 203, 204, 206, 249** (13).

## D. A later `rn` step consumes the artifact — 31 rows

Rows **15, 36, 66, 67, 68, 69, 71, 79, 84, 87, 90, 94, 96, 97, 106, 114, 121, 133, 134, 140, 141, 196,
209, 216, 217, 219, 220, 221, 232, 234, 236.** The consumers, each quoted at its row:

| Consumer | Quoted at | What it makes enforceable |
|---|---|---|
| `up/SKILL.md:26` — "A commit matches a task when its message contains `complete task #{id}`" | rows 36, 67, 68, 121, 196, 219, 232 | the completion marker and the prohibition on the substring elsewhere |
| `status-display.md:19-22` — "A task counts ✅ when `steering.md` records it complete" | rows 66, 140, 141, 216 | steering's check-offs, task ids, done annotations |
| `task-verify-workflow.md:215` — "Begin the next unchecked task" | rows 69, 236 | check-off state |
| `task-verify-workflow.md:219-222` — the "no 'Evaluation sign-off' task was ever encountered … escalate" backstop | rows 15, 94 | the Evaluation sign-off task's existence |
| `up/SKILL.md:19` — "rank by `State` showing `Status: paused`, then most recent commit"; `up/SKILL.md:24` — "Read the `State` section" | rows 133, 134, 217, 234 | the `State` section's shape and reset |
| `dn/SKILL.md:14` and `up/SKILL.md:17` — `git log --diff-filter=AM --name-only --pretty=format: -- '*/steering.md'` | rows 79, 96, 97, 106 | the session path, the start-session commit, the template's headings |
| `migration-workflow.md:28-29` — "Read the session's `steering.md` `Design:` line; if it is absent … skip this step entirely" | rows 84, 87, 90, 114 | the `Design:` pointer |
| `dn/SKILL.md:50-54` — step 8 re-runs `git status --porcelain` on step 6's own effect | rows 220, 221 | untracked residue actually being resolved |
| `planning-workflow.md:37`'s Evaluation sign-off, run at the last gate | row 116 | the Acceptance criteria being answerable |
| `task-execute-workflow.md:141` / the plan-gate task list | row 209 | planning's own outputs existing at all |

Two of these consumers are demonstrably defective and should be treated as findings, not assets:

- **`up/SKILL.md:26`'s grep is a prefix test and matches prose.** `git log --all --grep='complete task
  #1' --oneline | wc -l` returns 16 in this repo, and 7 of those 16 are other tasks (`#1b`, `#10`,
  `#11`, `#12`, `#13`, `#14`, `#16`) matched on the prefix. Three commits (`4daf6b2`, `893de07`,
  `de0b1ec`) carry the substring in a body without being markers. The mechanism exists and produces
  wrong answers. In the other direction it can also find nothing: `git log --grep='complete task #1'`
  without `--all` returns 0 from this worktree's `HEAD`, past markers having been squash-merged.
- **`migration-workflow.md:47-48` names a consumer that does not exist.** It claims Phase: Complete
  gates on `Ready to check off` reading Yes; `task-verify-workflow.md:208-209` contains no such
  condition. Row 162 is enforced only in the text that asserts it.

---

# The unenforced set — the list task #2 works from

**161 rows** where a breach reaches nothing that would tell it from compliance. The nine groups below
are a partition — every `unseen` row appears in exactly one group, and
32+15+10+14+14+10+25+8+33 = 161 — and they are grouped by *why* nothing catches them, because the
groups need different repairs.

The set grew by 52 rows when the verdict tests were tightened (see "The verdict vocabulary"). The
reviews that prompted the tightening estimated the shortfall at roughly 35; the derived figure is 52,
and the difference is almost all of U9 — the `status-display.md` block and the plan-time proposal
rules, which had been counted enforced on the strength of the user seeing a message.

## U1. The review chain's internals — 32 rows

Rows **5, 10, 11, 22, 27, 28, 30, 31, 37, 38, 40, 46, 47, 48, 49, 51, 52, 53, 54, 55, 56, 57, 59, 60,
61, 62, 63, 182, 183, 193, 194, 207.**

Every rule about *how* a review or a dispatch is produced: that a subagent was spawned at all, that it
carried no conversation history, that it was told to be adversarial, that it got the full artifact,
that the completion criteria were copied verbatim, that it was **not** shown the self-check or any
prior verdict (`task-verify-workflow.md:157-159` — the review-independence rule), that each expert
checklist was applied, that findings were triaged rather than dropped, that the 3-iteration cap held.
All of it lives in prompts that are never written to disk, so a review that never ran, a review that
ran primed, and a good review produce the same artifact.

This is the second-largest group after U9, and the most consequential: it holds every rule protecting
the integrity of the mechanism that is supposed to protect everything else.

## U2. Which reviews run at all — 15 rows

Rows **6, 7, 8, 9, 19, 20, 45, 92, 124, 125, 126, 127, 128, 139, 251.**

The mandated per-task reviews and the rules that place them. Empirically the worst-performing rules in
the plugin: a Verification section appears in 5 of 40 check files, Craft in 11, and
`20260705-improve-design-template` ran neither in any of its 7 tasks while closing approved.
`steering-template.md:67-71`'s Steps checklist would be a mechanism — an unchecked box is a visible
blank — but only for a step planning actually wrote, and **a step never written cannot be a blank.**
The failure is at authoring time, not execution time, and `planning-workflow.md:38`'s pre-persist
self-check covers only the Evaluation sign-off task. Row 139's "keep the two in sync" names no
mechanism and the two are provably out of sync.

## U3. How criteria are written — 10 rows

Rows **117, 118, 122, 129, 130, 131, 132, 135, 136, 137.**

The ①/② phrasing, "the objective met, not that an output was produced", "no vague terms",
exhaustiveness, and the Granularity / Specificity / Objectivity rows of the `Task definition
requirements` table. This is the group this session's Goal names: the rule was correct, sat in the
template, and was broken in the very next session. One asymmetry to fix while rebuilding:
`steering-template.md:75-79` states the bar for **Completion** criteria only; `:41-43` states nothing
of the kind for **Acceptance** criteria — and the breach landed on the Acceptance criteria
(`.rn/20260705-improve-design-template/steering.md:22-49`, 9 of 10 written as artifact existence).

## U4. Everything about `design.md` — 14 rows

Rows **166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 178, 180, 181.**

`design-template.md:4` says outright "**Not read at runtime**". The document has no consumer in the
flow: only a Design sign-off gate presents it, and that task exists only if planning placed one
(row 93, itself unenforced and absent from 7 of 8 sessions). The template's own contract —
"What does <mechanism> guarantee, and how is a breach caught?" (`design-template.md:68`) — is exactly
the question this inventory asks, and nothing checks that a `4.N` answers it truthfully.

## U5. Content allocation, doc division, and the migration judgement — 14 rows

Rows **88, 109, 110, 111, 112, 120, 123, 138, 157, 158, 159, 160, 161, 163.**

Which file a piece of content belongs in; that assumptions are separated from facts; that
prerequisites are listed; the reconciliation judgements in `migration-workflow.md`'s three steps.
Misallocated content simply sits in the wrong place and reads normally. **Rows 123 and 138 are the
sharpest case: nothing consumes `Prerequisites` at all** — `task-verify-workflow.md:215` advances to
"the next unchecked task" by position, never by dependency — so a declared prerequisite has no effect
on anything in the system.

## U6. Version stamping and migration triggering — 10 rows

Rows **86, 113, 155, 164, 165, 210, 215, 235, 239, 245.**

The `Rn version:` stamp is absent from 6 of 8 past sessions, and its consumer is "a plain string
comparison" (`migration-workflow.md:5`) that no file defines for a missing line — so an un-stamped
session silently reads as up to date, forever. `on/SKILL.md:15` documents that its own copy of the
check "can never actually fire." The reconciliation the trigger guards (rows 157, 158, 160, 164, 165)
is itself an unrecorded judgement.

## U7. Undetectable in principle — 25 rows

Rows **1, 3, 18, 39, 41, 43, 44, 64, 83, 85, 91, 95, 105, 145, 184, 214, 222, 224, 227, 228, 229, 231,
248, 250, 253.**

Not "nothing looks" but "there is nothing to look at": that a file was read (1, 85, 105), that a
judgement was made (44, 83, 91, 95), that an escalation *should* have fired and did not (18, 64), that
a status block was derived fresh rather than reused (145), that a starting SHA was captured once and
not re-captured (39, 43), and `dn/SKILL.md:44`'s "Never delete a file yourself" (222) — a deleted
untracked file leaves no residue in git, in `git status`, or anywhere else. The eight rows added here
in the second pass (184, 214, 224, 227, 228, 229, 231, 248) are the same shape one step further out:
they instruct the agent to run a command, read a file, or take a branch, and the only evidence the
step happened is that the agent proceeded as though it had. **Adding a reader cannot fix these; the
rule has to be restated as something that produces an artifact, or dropped.**

Row **41** belongs here and deserves naming: "Read the committed diff yourself"
(`task-verify-workflow.md:139`) is `rn`'s strongest mechanism — it backs the 16 rows of group C's
coordinator list — and there is no trace of whether it happened.

## U8. Single cases — 8 rows

Rows **26, 80, 93, 102, 108, 162, 190, 254.** Three worth naming:

- **Rows 26 and 162** — the check file's `## Overall Verdict` block, and `migration-workflow.md:47-48`'s
  claim that Phase: Complete gates on `Ready to check off` reading Yes. It does not:
  `task-verify-workflow.md:208-209` contains no such condition. 24 of 40 past check files carry no
  `Ready to check off` line at all and every one of those tasks was checked off. **This is a mechanism
  asserted in prose that does not exist in the file it cites** — the one row in this inventory where
  `rn` documents an enforcement it never built.
- **Row 93** — the Design sign-off task has no equivalent of the Evaluation sign-off's backstop
  (`task-verify-workflow.md:219-222`), so its absence is invisible. Adding the symmetric backstop is a
  cheap, mechanism-shaped fix.
- **Row 190** — GraphQL pagination (`pr-feedback-workflow.md:42-72`). A skipped page silently shrinks
  the queue: the one file whose steps otherwise fail loudly has a single step that fails silently.

## U9. On the user's screen, but nobody is auditing — 33 rows

Rows **12, 14, 17, 65, 70, 73, 74, 75, 81, 82, 100, 101, 142, 143, 144, 146, 148, 149, 150, 151, 152,
153, 154, 156, 205, 213, 218, 225, 230, 233, 242, 243, 247.**

This group is what the tightened `recognised` test created, and it is the largest single correction in
this inventory. Every one of these rules produces something the user could in principle see — a status
block, a proposal, a report, a PR body, a commit on the branch — and none of them produces a reader
who is looking at it *against the rule*. Twelve are the whole of `status-display.md`'s output contract
(142–144, 146, 148–154): the file's own product is a block the user reads, and no `rn` step ever
compares an emitted block to the `steering.md` it was supposed to be derived from. Six more are
planning's proposal rules (73–75, 81, 82, 101), where a proposal made without alternatives is
indistinguishable from one made with them.

The repair these need is different from every other group's. U1–U8 are missing an artifact; U9 has the
artifact and is missing the occasion. A rule here becomes enforceable by naming a moment at which
someone is required to hold the output up against the rule — which is what the gates already do for
`Goal`, `Acceptance criteria` and `Assumptions` (group C), and what nothing does for the block, the
proposals, or the reports.

## Not in any group, but unenforced and worth a row of its own

`task-execute-workflow.md` lines 6–136 and `task-verify-workflow.md` lines 6–136 are byte-identical —
131 duplicated lines with **no rule anywhere requiring they stay in sync**, and no mechanism if there
were one. It is not a broken rule; it is a missing one. The Design expert on the task that created it
did flag it (`.rn/20260625-rn-lean/checks/12.md`: "a standing drift risk against the repo's own
anti-duplication principle — noted, not actioned"), and the finding was closed as an accepted tradeoff.
The review worked; nothing turned its outcome into a rule, so the drift risk it named is now
unguarded and invisible.

---

# What each unconditionally mandated step catches

A step counts as unconditionally mandated when `rn` runs it on every task or every session of its
kind, with no condition but the task's medium and whether the task touches structure/approach —
**never its size**. Twenty-three such steps are inventoried below: **fifteen bind every build task**
(fourteen in the Execute → Verify → Complete loop, plus the always-open escalation channel that can
fire inside it) and **eight run outside that loop** — once per session, or per invocation of the skill that carries them.
Each carries the row ids that state it, so the set can be checked against the per-file tables above
rather than taken on trust. For each: what it catches that nothing else in the structure would, and
whether it earns that on a small task.

## The four per-task reviews

| Step | Mandated at | Rows | What only this catches | Earns its cost on a small task? |
|---|---|---|---|---|
| **QA** (every build task) | `task-execute-workflow.md:18`, `:55`; `task-verify-workflow.md:147` | 6, 19, 45 | Not the verbatim criteria — element 4 of the review prompt hands those to **every** expert (`task-verify-workflow.md:155`, built per `:147-149`). What is QA's alone is the bar it applies to them: whether the verification approach is meaningful to the objective, "not just 'it ran'/'it passed'" (`:162-163`), and `task-execute-workflow.md:103`'s designation of QA as "the per-criterion gate" while the other three "assess the aspects below, not each completion criterion". Execute element 5 also reads criterion against artifact (`task-execute-workflow.md:153-161`), but it is written by the agent that built the artifact; QA is the only *independent* per-criterion read. | **Yes, at any size.** It is the only adversarial read of the criteria, and the criteria are the contract. Cheapest of the four to justify. |
| **Craft** (per medium) | `task-execute-workflow.md:21-22`; `task-verify-workflow.md:167-170` | 8, 19, 45 | The only reviewer looking at *how* the artifact is written rather than whether it is right: naming, error handling, duplication; prose clarity and "consistency with the doc's existing voice/terminology". Nothing else in the structure ever mentions style, and voice drift accumulates silently across a plugin whose entire product is prose. | **Not always.** On a rename, a version bump, or a one-line correction it returns wording nits — the past record bears this out ("round 1 found 2 valid Craft findings", `.rn/20260625-rn-lean/checks/12.md`). It earns its place on any task producing prose a user will read, and not on a mechanical edit. `rn` offers no way to say so. |
| **Verification** (per medium) | `task-execute-workflow.md:23-24`; `task-verify-workflow.md:171-175` | 9, 19, 45 | The distinction from QA is real and is this session's subject: **QA judges the approach, Verification judges the doing.** It is the only step asking whether every claim was actually checked against its source, whether tests are in GWT form and cover boundary/error/empty/max cases, whether the flow was traced step by step. A self-check can assert "verified"; only this step re-derives it. | **Yes on any claim-bearing or behavior-bearing artifact; near-worthless on a change already proven by a grep or a green test the coordinator can see in the diff.** It was dropped from 35 of 40 past tasks. Most of those were of the second kind, where its absence cost nothing — which is also why its absence from tasks of the first kind went unremarked. |
| **Design** (conditional, structure/approach only) | `task-execute-workflow.md:19-20`, `:56-57`; `task-verify-workflow.md:164-166` | 7, 19, 45 | The only reviewer with a whole-system remit: "separation of concerns; system-wide integrity (interface contracts, API compatibility, cross-doc consistency)". Everything else in `rn` reviews one artifact against one task. **Its record is the best of the four**: when `task-execute-workflow.md` and `task-verify-workflow.md` were split apart, Design caught the duplication on the spot — `.rn/20260625-rn-lean/checks/12.md` records "Flagged the ~110-line shared-header duplication as a standing drift risk against the repo's own anti-duplication principle — noted, not actioned … an already-decided tradeoff". No other axis mentioned it. | **Already conditional, and correctly so.** The gap that case exposes is not the review but the *disposition*: the finding was accepted as a tradeoff, and that acceptance lives only in a check file nothing reads. 131 lines are still duplicated with no sync rule anywhere. **A review only earns its cost if the disposition of its findings lands somewhere durable** — which is U1's problem, not Design's. |

**The shared problem.** All four are dispatched as fresh subagents that must read the artifact from
scratch, so on a one-line change four subagents are the entire cost of the task. `rn`'s only
conditionality is medium and structure/approach; it has no notion of size, and no rule permitting a
reviewer to be skipped. The result in practice was not proportionality but silent omission — planning
simply stopped writing the steps. **A rule that cannot be skipped legitimately gets skipped
illegitimately**, and that is the mechanism-shaped lesson for task #2: the fix for an over-mandated step is
a stated condition, not a firmer instruction.

## The other eleven that bind every build task

| Step | Mandated at | Rows | What only this catches | Worth its cost? |
|---|---|---|---|---|
| Scope in the work-order | `task-execute-workflow.md:142` | 29 | The only place the task's boundary is stated to the agent that will cross it — "stay within this task; do not start adjacent tasks; name the files expected in play". It is what makes `task-verify-workflow.md:146`'s scope confirmation answerable: without it the coordinator has no boundary to hold the diff against. | Yes, and it is one sentence. On a small task it is the difference between a one-file diff and an opportunistic tidy-up nobody asked for. |
| Method in the work-order | `task-execute-workflow.md:143-147` | 30 | The only instruction to verify *while building* rather than after — test-first for code, claim-by-claim for writing, trace-as-built for a diagram. Every other verification step in `rn` runs after the artifact exists, when a wrong claim is already written down. | Yes on any task with claims or behavior in it. It is also the least checkable step in the loop: element 5 asks the expert to confirm it applied the Method, which is self-report, not evidence (row 30). |
| Self-check | `task-execute-workflow.md:153-161` | 32, 33, 34 | The only per-criterion evidence written by whoever built the thing, and the only record of *how* the Method was applied (coverage figures, which claims were checked, where the flow was traced). | Yes as a **record**; weak as a **check** — it is written by the same agent that built the artifact, and 24 of 40 past files were left without a `Ready to check off` verdict with no consequence. Its value is entirely contingent on QA reading it, which `task-verify-workflow.md:157-159` forbids passing to the reviewer. |
| Coordinator reads the committed diff | `task-verify-workflow.md:139-146` | 41, 42, 43, 44 | The only step that reads the actual artifact independently of anyone's account of it. Catches scope creep, stray staged files, a summary that does not match the diff, a regenerated file. It is the reader behind all 16 rows of group C's coordinator list. | **Yes, always.** It is one `git show`, the cheapest step in the loop, and the most load-bearing. |
| Dispatch all deliverable work to the implementation expert | `task-execute-workflow.md:26` | 10, 40 | Keeps the coordinator's context clear of build trial-and-error — a resource property, not a quality one. | Yes for context economy; it catches nothing, and nothing records whether it happened. |
| Capture the task's starting commit | `task-execute-workflow.md:175-176` | 39 | The only way `task-verify-workflow.md:144-145`'s cumulative diff spans multiple fix rounds. Without it, review sees the last round only. | Yes — free, and its loss silently narrows the one step that always earns its place. |
| Triage every finding to Valid/Invalid/Escalation | `task-verify-workflow.md:176-189` | 56, 57, 60, 61 | The only step forcing a finding to a decision instead of a judgement call about whether to bother. The Invalid bar ("only when it rests on a factual error or falls outside a scope boundary written in the Completion criteria") is what stops findings being waved off. | Yes — it is the rule that makes the reviews consequential rather than advisory. |
| Record review verdicts into the check file | `task-verify-workflow.md:191-192` | 62, 63 | The only durable trace that a review happened at all. Everything else about the review chain is prompt-only. | **Yes, and it is currently the weakest link that could most cheaply become the strongest** — it is the one artifact that could make U1's 32 unenforced rows visible. |
| Escalation, always open | `task-verify-workflow.md:194-200` | 18, 64 | The only route by which a discovery that changes the agreed plan or design reaches the user between gates — "raised to the user **immediately, wherever it surfaces** … never deferred to a gate". Nothing else in the loop can interrupt it. | Yes, and it costs nothing when it does not fire. Its failure mode is silence: an escalation that should have fired and did not leaves no artifact anywhere (row 64), which is why it sits in U7 rather than in the enforced set. |
| Check off steering + the single completion marker | `task-verify-workflow.md:208-214` | 66, 67, 68 | The session's actual state. Feeds `up`'s resume, the status block, and "the next unchecked task". | Yes — this is `rn`'s state machine; without it a resumed session redoes or skips work. |
| Advance immediately, no per-task gate | `task-verify-workflow.md:215-217` | 69, 17, 65 | Keeps the user out of per-task decisions, which is the plugin's whole premise. | Yes; it costs nothing and is what the three-gate design buys. |

## The eight that run outside the per-task loop

| Step | Mandated at | Rows | What only this catches | Worth its cost? |
|---|---|---|---|---|
| Session-status block at every user stop | `status-display.md:3-5` | 142 | The only thing that tells the user where the session stands without opening `steering.md`. | Yes on a stop; it is the user's only continuous view, and the user is mechanism C. |
| Version check in all five skills | `on/SKILL.md:15` and siblings | 210, 215, 235, 239, 245 | In principle, drift between a session and the installed plugin. | **No, as built.** It has never fired: 6 of 8 sessions carry no stamp to compare, `on`'s copy is documented as unreachable, and the missing-line case is undefined. It is four lines of ceremony in five files. |
| Evaluation sign-off always last | `planning-workflow.md:37` | 94, 254 | That the goal is confirmed met before the session closes — the only step that checks the Acceptance criteria at all. | Yes, and it is the one planning rule with a real backstop (`task-verify-workflow.md:219-222`). |
| Pre-persist self-check that the last task is Evaluation sign-off | `planning-workflow.md:38` | 95 | Would catch the omission at authoring time rather than at session end. | Yes in principle; unenforced in fact (row 95), and it covers only this one task — the Design sign-off, the review steps, and the criteria phrasing get no equivalent. **The cheapest generalization available to task #2 is to widen this step, since it is already the right shape: a check at authoring time on the artifact planning just wrote.** |
| Draft PR with a single-link body | `planning-workflow.md:44` | 99, 100 | Puts the plan in front of the user in rendered form and creates the session's one review surface, on which group C's user depends entirely. | Yes — every `recognised` verdict in this inventory that names the user ultimately resolves to this PR. |
| `dn` resolves untracked residue | `dn/SKILL.md:35-39` | 220, 221, 222 | The only step in `rn` that looks at what the work left behind rather than at what it produced. A regenerable artifact gets a `.gitignore` rule; anything else goes to the user. Nothing else ever runs `git status --porcelain` for its own sake. | Yes — it is the reason a suspend hands back a clean tree rather than a dirty one, and the classification is cheap. The one breach it cannot reach is deleting a file (row 222). |
| `dn` verifies the tree is clean | `dn/SKILL.md:50-54` | 224 | The only post-condition check in the plugin: it re-runs `git status --porcelain` against step 6's own effect and records whatever step 6 failed to resolve. Every other step in `rn` asserts its outcome rather than re-reading it. | Yes, and it is the shape task #2 should copy — a step that re-reads the artifact its predecessor wrote is the cheapest mechanism in the plugin. That nothing checks *this* step ran (row 224) is the limit, not the design. |
| `migration` reconciles steering, then design, then tasks | `migration-workflow.md:20-25`, `:27-31`, `:33-38` | 157, 158, 159, 160, 161, 162 | The only path by which a session authored under an older `rn` is brought to current convention — and the only step that re-reads a *past* artifact against a current template rather than a new artifact against its own task. | **Not as built.** It has never run: its trigger is a `Rn version:` comparison with no left operand in 6 of 8 sessions (row 86), and all three reconciliations are unrecorded judgements whose output is indistinguishable from not having run (rows 158, 160). The shape is right; nothing starts it and nothing records it. |
