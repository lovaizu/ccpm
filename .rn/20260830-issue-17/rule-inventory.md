# Rule inventory — what `rn` states, and what happens when it is broken

Every normative statement in `rn`'s 8 reference files and 5 skill files, with a judgement of what
happens on a breach. This is the ground for task #2: the **Unenforced set** below is the definite
list of rules that need rebuilding.

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

**Counts.** 249 normative statements. By file: 40 in `task-execute-workflow.md` (whose lines 6–136 are
byte-identical to `task-verify-workflow.md`'s — 131 lines — so rows 3–26 state the rules of
both and are counted once), 31 more in `task-verify-workflow.md`, 33 in `planning-workflow.md`, 37 in
`steering-template.md`, 13 in `status-display.md`, 11 in `migration-workflow.md`, 16 in
`design-template.md`, 26 in `pr-feedback-workflow.md`, and 4 / 14 / 11 / 7 / 6 in `on` / `dn` / `up` /
`ty` / `gm`.

By verdict: **34 stop the flow**, **111 are visible on breach**, **104 are neither**. Every one of the
34 stops rests on something outside `rn`'s prose: a `git` or `gh` command that fails (17 rows — 98, 99,
187–189, 192, 197–199, 214, 220, 223, 224, 228, 229, 232, 248), the harness refusing to let the model
invoke a skill (`disable-model-invocation: true` — 208, 212, 226, 237, 244), the assistant's turn ending
so only a user message can resume (13, 21, 76, 103, 104, 184, 211, 221, 227, 246), or a later step
simply having no input to run on (217, 231). **Not one rule in `rn` is enforced by `rn`.**

## The verdict vocabulary

- **stops** — something refuses to proceed independently of whether the agent complies: an external
  command errors out, or the harness itself blocks the action.
- **visible** — the breach lands in an artifact a named party demonstrably reads: the user (at a gate,
  or in the message on their screen), the coordinator reading the committed diff, or a later `rn` step
  that consumes the artifact and behaves differently. The reader is named in every such row.
- **neither** — the rule is stated and nothing more. An instruction to the coordinator is the rule,
  not its enforcement, and lands here.

## The one structural fact behind every judgement

`rn` ships no executable code. `find rn -type f` returns 17 files — 8 references, 5 `SKILL.md`,
`README.md`, `CHANGELOG.md`, `docs/design.md`, and `plugin.json`: sixteen Markdown files and one JSON
file, none of them executable (`find rn -type f -perm -u+x` returns 0). There is no hook, no script,
no validator, no CI step anywhere in the plugin. So **no rule in `rn` is enforced by `rn`**. Only four things can catch a
breach, and every "visible"/"stops" row below rests on one of them:

1. **The harness** — `disable-model-invocation: true` in each skill's frontmatter. The model cannot
   invoke the skill; only the user typing `/rn:on` can. This is the only true machine gate in the
   plugin, and it guards exactly one property: that the five commands are user-initiated.
2. **External tools** — `git` and `gh` returning errors (`gh pr view` exiting non-zero,
   `gh api …/replies` rejecting a bad id, `git push` failing).
3. **The user** — present at exactly three scheduled gates and on the PR. Anything on the user's
   screen or in the PR diff is visible; anything behind the coordinator is not.
4. **A downstream `rn` step that reads a written artifact** — `/rn:up`'s marker grep
   (`up/SKILL.md:26`), `status-display.md`'s read of steering's check-offs (`status-display.md:17`),
   `task-verify-workflow.md`'s "begin the next **unchecked** task" (`task-verify-workflow.md:215`),
   and the coordinator's own read of the committed diff (`task-verify-workflow.md:139`).

Everything else — the entire review chain's internals, every template's shape, every "never" addressed
to the coordinator — has no reader and no consumer.

## Breaches observed in past sessions

These are recorded here because they are the evidence for several "neither" verdicts below: the rule
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
Verdicts: **stops** / **visible** / **neither**, per the vocabulary above.

## `task-execute-workflow.md` (lines 1–179)

Lines 6–136 of this file are byte-identical to lines 6–136 of `task-verify-workflow.md` — 131 lines;
`diff <(sed -n '6,136p' rn/references/task-execute-workflow.md) <(sed -n '6,136p'
rn/references/task-verify-workflow.md)` returns no output. Rows 3–26 therefore state the rules of both
files and are not repeated in the next table. Lines 1–5 differ between the two files: row 2's sentence
("Run one task at a time.") stands verbatim on line 5 of each, but row 1's does not —
`task-verify-workflow.md:5` carries its own wording and has its own row in the next table.

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 1 | "`on` and `up` read both files at task execution, this one first" | :5 | neither | No step in `on` or `up` records which files it read; a skipped read leaves no trace. `on/SKILL.md:17` and `up/SKILL.md:34` state the same ordering — that is the rule restated, not a check. |
| 2 | "Run one task at a time." | :5 | visible | The coordinator checks off one task per commit (`task-verify-workflow.md:210`) and "Begin the next unchecked task" is singular (`:215`); two tasks run together would produce two deliverables under one check-off, showing in the PR the user reviews. Nothing refuses it. |
| 3 | "Write check files under `{steering_dir}/checks/`." | :7-8 | neither | No step reads back the path. Two past sessions wrote `checks/task-1.md` instead of `checks/1.md` and nothing surfaced it. |
| 4 | Coordinator "Writes directly **only** `steering.md` and `checks/{task-id}.md`; never edits the deliverable or its git history" | :14-15 | visible | Git authorship does not distinguish coordinator from subagent, but a coordinator-authored deliverable change lands in the same PR diff the user reads and the coordinator itself re-reads (`task-verify-workflow.md:139`). History rewriting would show as a changed SHA against the captured starting commit (`:175`). Weak: nothing compares them. |
| 5 | Implementation expert "Produces, fixes, and commits/pushes the deliverable" | :16-17 | neither | Nothing records whether a subagent was dispatched. A coordinator that writes the file itself produces an identical commit. |
| 6 | "**QA expert** (every task) — subagent." | :18 | neither | The check file has a `## QA Expert Review` section — 38 of 40 past files carry one — but nothing reads it: 24 of 40 leave the `Ready to check off` line out of the Overall Verdict block, and every one of those tasks was still checked off. |
| 7 | "**Design expert** (tasks that produce or revise structure/approach)" | :19-20 | neither | Same as row 6; additionally "produces or revises structure/approach" is a judgement with no recorded answer, so an omission cannot even be identified as one. |
| 8 | "**Craft expert** (per medium: coding / writing / visual)" | :21-22 | neither | Absent from every session before `20260625-rn-lean`; 29 of 40 check files carry no Craft section. Nothing noticed. |
| 9 | "**Verification expert** (per medium: test / fact-check / dry-run)" | :23-24 | neither | 35 of 40 check files carry no Verification section; `20260705-improve-design-template` omitted it from all 7 tasks and closed approved. This is the specimen breach for this session. |
| 10 | "All deliverable work (produce/fix/commit/push) goes to the implementation expert, every time, any size." | :26 | neither | Identical to row 5: the commit is the same either way, and nothing records the dispatch. |
| 11 | "Each review expert runs as an independent subagent (Agent tool, no conversation history) and returns a compact summary." | :27-28 | neither | Nothing records whether the Agent tool was used or whether history was passed. A coordinator role-playing the review produces the same check-file text. |
| 12 | "The user signs off at exactly **three** scheduled gates, never on any other task" | :32 | visible | An extra gate is a message on the user's screen; a missing one is a task that closes without them. The user is the reader — but only if they notice, and nothing flags it. |
| 13 | "**Plan gate** — the draft-PR plan approval in `on` before any task runs." | :34 | stops | The gate ends the assistant's turn; the conversation cannot advance without a user message. `planning-workflow.md:51` states it as "**CRITICAL: DO NOT proceed without explicit user approval.**" The stop is structural once the ask is made; the obligation to make it is not enforced. |
| 14 | "**Design gate** — sign-off on the approach / key decisions before they are built on" | :35-37 | visible | Realized as a Design sign-off task (`planning-workflow.md:36`) whose absence is visible in `steering.md`'s task list, which `status-display.md:17` re-derives at every stop. If planning never places the task, nothing catches it — 7 of the 8 session directories under `.rn/` have no such task; `.rn/20260830-issue-17` (`### #3: Design sign-off`) is the only one that does. |
| 15 | "**Evaluation gate** — the end-of-session run of the `steering.md` Acceptance criteria" | :38-39 | visible | Backstopped by `task-verify-workflow.md:219-222`: "If no unchecked tasks remain and no 'Evaluation sign-off' task was ever encountered … escalate to the user immediately". That is a real consumer, quoted; it fires only inside a live flow that reaches the end of the task list. |
| 16 | "the assistant never records a verdict the user did not issue" | :41-42 | visible | The fabricated verdict appears in the message the user reads next. The user is the reader; nothing else checks. |
| 17 | "The per-task boundary is **not** a user gate for ordinary build tasks" | :44-46 | visible | Stopping anyway puts an unrequested ask on the user's screen. Nothing prevents it. |
| 18 | Escalation is "a separate always-open channel — not a gate; an escalation message opens with the session-status block" | :47-49 | neither | A *missing* escalation leaves nothing behind — that is the whole failure mode. The status-block half is visible (row 12's reader) only when an escalation is actually sent. |
| 19 | "QA always spawns for a task that builds something; a sign-off task spawns none. Craft and Verification spawn for the task's medium. Design spawns only when the task produces or revises structure/approach." | :53-57 | neither | See rows 6–9. The per-task judgement is never written down, so neither its result nor its omission is recoverable. |
| 20 | The three build-task instances: Code / Docs / Visual each run "Self-check → QA → Craft → Verification → coordinator review → check-off" | :59-64 | neither | Same as row 19. Empirically the Verification link was simply dropped for a whole session. |
| 21 | "**Sign-off task**: no axes spawn … It skips Phase: Execute and Phase: Verify entirely … take the verdict via `/rn:ty` … or `/rn:gm` … no check-off until later approved" | :65-71 | stops | The verdict can only arrive as a user message: the five skills carry `disable-model-invocation: true` (`ty/SKILL.md:4`, `gm/SKILL.md:4`), so the assistant cannot invoke them. The flow genuinely cannot self-approve. The "no check-off until approved" half is only visible (row 12's reader). |
| 22 | "Self-check is produced in Execute … reviews run in Verify; the coordinator's independent review then clears the task" | :73-75 | neither | Ordering is unrecorded; the check file bears no timestamps and nothing compares it to the commit graph. |
| 23 | "the implementation expert writes **only** the Completion Criteria Self-check and Evidence columns (and the Overall Verdict 'Self-check' line)" | :79-81 | visible | The coordinator fills the remaining columns afterwards (`:83-84`) and would find them pre-filled. That is a real second reader, but it is the only one. |
| 24 | The expert "never [writes] the review-verdict sections … on every round, including fix rounds" | :81-83 | visible | Same reader as row 23. |
| 25 | "The expert does not commit it. The coordinator … commits the file as part of its ledger — on the post-Verify steering check-off commit." | :83-84 | visible | An expert-committed check file appears in the deliverable commit, which the coordinator reads (`task-verify-workflow.md:140-143` expects `git status` to show "**only** that tracked check file"). That expectation is stated and would be violated visibly. |
| 26 | The check-file format block — five columns, `## QA Expert Review`, three expert sections, `## Overall Verdict` with five verdict lines and `Ready to check off` | :86-135 | neither | Nothing reads the file's shape. 39 of 40 past check files carry the `## Overall Verdict` heading, but 24 of 40 omit its `Ready to check off` line — the one field another file claims to gate on. `migration-workflow.md:46-48` asserts that "`task-verify-workflow.md`'s Phase: Complete only checks off once Verify has cleared with `Ready to check off` reading Yes" — but Phase: Complete (`task-verify-workflow.md:208-209`) never mentions the field. **The mechanism that file names does not exist.** |
| 27 | The work-order "include[s] everything it needs and only that, with these 7 elements" | :139-140 | neither | The work-order is a prompt; it is never written to disk and no artifact records what it contained. |
| 28 | Element 1 Task — "Purpose, Steps, Completion criteria copied from `steering.md`" | :141 | neither | Same as row 27. A paraphrased or truncated copy is indistinguishable afterwards. |
| 29 | Element 2 Scope — "stay within this task; do not start adjacent tasks; name the files expected in play" | :142 | visible | Out-of-scope files land in the committed diff, which the coordinator reads and is told to "Confirm the change matches the task's scope" (`task-verify-workflow.md:146`). |
| 30 | Element 3 Method — "apply the task's Verification method as you build, not only after" (test-first / verify-each-claim-as-drafted / trace-as-built) | :143-147 | neither | Nothing distinguishes verifying as you write from verifying afterwards, or from not verifying. Element 5 asks the expert to *confirm* it applied — self-report, not evidence. |
| 31 | Element 4 Best practices — Craft always; Design "when the task produces or revises structure/approach" | :148-152 | neither | Same as row 27. |
| 32 | Element 5 Self-check — verify each completion criterion OK/NG with specific evidence, and confirm the Method was applied (coverage measured / every claim checked / flow traced) | :153-157 | visible | The written self-check is read by the coordinator, which fills the QA column beside it (`:83-84`). Its quality is unchecked: nothing compares Evidence to the artifact. |
| 33 | Element 5 — write to `{steering_dir}/checks/{task-id}.md` filling **only** the self-check columns; "Never write or overwrite the review-verdict sections … on every round, including fix rounds" | :157-161 | visible | Same reader as row 23. |
| 34 | Element 5 — "**Do not commit the file.**" | :161 | visible | Row 25's mechanism: `task-verify-workflow.md:140-143` expects the check file to be the one uncommitted change. |
| 35 | Element 6 — "stage the deliverable paths explicitly (`git add <path>…`); never `git add -A` or `git add .`" | :162-163 | visible | A stray file appears in the diff the coordinator reads (`task-verify-workflow.md:139`, `:146`) and in the PR. Nothing detects the *staging command* itself — only its consequences, and only when there was a stray file to catch. |
| 36 | Element 6 — plain conventional message; "the message must **not** contain `complete task #`"; push; "**never force-push**" | :163-165 | visible | Real downstream consumer: `up/SKILL.md:26` — "A commit matches a task when its message contains `complete task #{id}`; check that task off". A breach silently checks off the wrong task. Three commits in this repo's history carry the substring in prose (`4daf6b2`, `893de07`, `de0b1ec`), so the breach is demonstrated and the consumer is demonstrably fooled. Force-pushes surface as events on the PR timeline; nothing in `rn` checks. |
| 37 | Element 6 fallbacks — cannot push → say so and leave the commit, coordinator pushes; cannot commit → say so, coordinator commits mechanically with explicit paths and a plain message, "content stays the expert's" | :166-171 | neither | Depends entirely on the expert self-reporting the failure. A silent failure leaves the work uncommitted, which the coordinator would meet as an empty diff — visible only in that one case. |
| 38 | Element 7 Return — "a compact summary only … Do not paste full file contents or trial-and-error." | :172-174 | visible | The coordinator reads the summary; a bloated one is on its screen. Nothing enforces brevity, and the cost (context) is paid before it is seen. |
| 39 | "**Capture the task's starting commit** — current `HEAD` … Capture it **once**; do **not** re-capture on fix rounds." | :175-176 | neither | The value lives only in the coordinator's context. A re-captured or lost SHA silently narrows the cumulative diff at `task-verify-workflow.md:144-145`, hiding earlier rounds from review. |
| 40 | "**Dispatch the implementation expert** with the work-order and wait for its summary." | :177 | neither | See rows 5 and 10. |

## `task-verify-workflow.md` (lines 137–222)

Lines 6–136 carry rows 3–26 above, and line 5's shared sentence is row 2. Listed here: this file's own
line 5, its Phase: Verify, and its Phase: Complete.

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 41 | "**Read the committed diff yourself.**" | :139 | neither | This *is* `rn`'s strongest mechanism — and nothing enforces the mechanism itself. Nothing records that the coordinator read anything. |
| 42 | "Expect `git status` to show **only** that tracked check file — that is normal, not a deliverable change." | :140-143 | visible | `git status` is run and its output is on the coordinator's screen; a second uncommitted file shows there. |
| 43 | "Inspect the committed deliverable: `git show <sha>` … or `git diff <task's starting commit>..HEAD`" | :144-145 | neither | Depends on row 39's SHA, which lives only in context; a wrong or missing starting commit silently truncates the diff. |
| 44 | "Confirm the change matches the task's scope and Completion criteria before spending review experts." | :146 | neither | A private judgement with no recorded output. |
| 45 | "**Dispatch the review experts as independent subagents** — QA always; Craft and Verification for the task's medium … Design when the task produces or revises structure/approach. Build each review prompt with 6 elements" | :147-149 | neither | See rows 6–9 and 19. The empirical record is that whole axes went missing for entire sessions. |
| 46 | Element 1 Role — review "**adversarially** … assume defects exist and try to break the artifact (boundaries, error paths, integration, missed cases)" | :150-152 | neither | The prompt is never written to disk. A friendly review and an adversarial one return the same shape of summary. |
| 47 | Element 2 Artifact — "The full content or diff under review." | :153 | neither | Same as row 46. A review given a partial artifact returns a confident verdict about the part it saw. |
| 48 | Element 3 Criteria — "The expert checklist below." | :154 | neither | Same as row 46. |
| 49 | Element 4 — "the task's Completion criteria copied **verbatim** from `steering.md`" | :155 | neither | Same as row 46. "Verbatim" is unverifiable after the fact. |
| 50 | Element 5 Output format — "OK/NG per criterion with concrete evidence, plus an overall pass/fail" | :156 | visible | The returned summary is on the coordinator's screen and is transcribed into the check file (`:192`). A summary in the wrong shape shows immediately. |
| 51 | Element 6 Neutral framing — "**Never** pass the self-check file …, the implementation expert's summary, or any OK/NG verdict; do not defend the choices or hint at the verdict you expect." | :157-159 | neither | The single most consequential rule in the file for review independence, and the single least observable: a primed review is indistinguishable from an independent one in its output. |
| 52 | QA checklist — "the verification approach is meaningful to the actual objective … no rubber-stamped or purpose-mismatched check" | :162-163 | neither | Nothing checks the reviewer against its checklist. |
| 53 | Design checklist — "does the approach/structure fit; separation of concerns; system-wide integrity (interface contracts, API compatibility, cross-doc consistency)" | :164-166 | neither | Same as row 52. Note the 132-line verbatim duplication between this file and `task-execute-workflow.md` survived every Design review that has ever run. |
| 54 | Craft checklist — coding: "naming, error handling, null/thread safety", no duplication, style consistency; writing: "prose clarity and correctness, consistency with the doc's existing voice/terminology"; visual: notation clarity | :167-170 | neither | Same as row 52. |
| 55 | Verification checklist — test: "meaningful and in GWT (Given/When/Then) format" covering edge cases; fact-check: "every claim/reference verified against its source, no unverified assertion stated as fact, and completeness of claim coverage"; dry-run: trace every step/branch | :171-175 | neither | Same as row 52 — and this checklist was never run at all in the majority of past tasks. |
| 56 | "**Triage every finding.** Each ends in exactly one of" Valid / Invalid / Escalation | :176 | visible | Findings arrive in the review summary the coordinator reads; the check file records verdicts (`:192`). A dropped finding is visible only to whoever compares the summary against the file — and nobody does. |
| 57 | "**Valid** → fix it. Dispatch the implementation expert (fresh subagent) — every deliverable-touching fix, no matter its size, including minor improvements." | :177-180 | visible | The fix lands as a further commit in the PR; its absence shows as an NG that never turned into a diff. Nothing compares them. |
| 58 | Reuse the original work-order; "point it at the current on-disk state to build on (not regenerate)"; fix commits accumulate, "never force-pushed" | :179-181 | visible | A regenerated file shows as a wholesale rewrite in the fix commit's diff, which the coordinator reads (`:139`). Force-push shows on the PR timeline; no `rn` check. |
| 59 | "re-run the same review expert; if the fix could affect a dimension another expert already cleared, re-run that expert too. Cap at 3 iterations … valid findings still NG after 3 → record them and escalate" | :181-183 | neither | Iteration count lives only in the coordinator's context. Past check files narrate "round 3 (final, cap reached)" as prose — a report, not a check. |
| 60 | "**Invalid** → reject it, citing evidence. Invalid **only** when it rests on a factual error or falls outside a scope boundary written in the Completion criteria — cite the specific fact or criterion." | :184-186 | visible | If the rejection is written into the check file's Evidence column it is readable; nothing requires that, and no reader compares it to the criteria. |
| 61 | "Escalate **only** when the decision is genuinely the user's … 'It's minor, so I'll just ask' is not a reason." | :186-189 | visible | An over-escalation is a message on the user's screen. Under-escalation leaves nothing. |
| 62 | "Never silently drop, blindly accept, or bounce a finding for lack of a standard." | :191 | neither | By construction: a silently dropped finding leaves no artifact. |
| 63 | "Record the review verdicts into the check file." | :191-192 | visible | The check file is committed with the check-off (`:83-84`) and lands in the PR. Empirically weak: 24 of 40 past files record no `Ready to check off` verdict and nothing objected. |
| 64 | "**Escalation is an always-open channel** … raised to the user **immediately, wherever it surfaces** … never deferred to a gate … a change to the agreed plan or design cannot ship unseen. Wherever it fires, open the escalation message with the session-status block" | :194-200 | neither | The failure mode is silence. A change that shipped unseen is by definition not visible; only a later reader of the diff could find it, and no step asks anyone to look. |
| 65 | "There is no per-task user gate for a normal task: once Verify clears … the coordinator checks the task off directly." | :204-206 | visible | Row 12's reader. |
| 66 | "**Check off steering.** With Verify cleared … check off the task in `steering.md` directly." | :208-209 | visible | Real consumers: `status-display.md:17-22` derives the ✅/👉/⬜ block from these check-offs at every stop, and `:215` begins "the next **unchecked** task". An unchecked completed task is re-run; a wrongly checked one is skipped. Note this step does **not** read `Ready to check off` — see row 26. |
| 67 | Commit the check-off as "`{type}: complete task #{id} — {description}`", then push to the session PR | :210-212 | visible | Consumed by `up/SKILL.md:26`'s grep. A malformed marker means the task is not re-checked-off on resume. |
| 68 | "This is the one completion marker for the task: deliverable commits carry plain messages; only this check-off commit carries the `complete task #{id}` substring. Keep that exact substring regardless of the prefix." | :212-214 | visible | Same consumer as row 67 — and demonstrably fooled twice over. The substring test is a prefix test: `git log --all --grep='complete task #1' --oneline \| wc -l` returns 16, of which 7 are other tasks (`#1b`, `#10`, `#11`, `#12`, `#13`, `#14`, `#16`). And three commits (`4daf6b2`, `893de07`, `de0b1ec`) carry the substring in a body without being markers. |
| 69 | "**Advance.** Begin the next unchecked task immediately — a sign-off task goes straight to the gate … any other task begins at Phase: Execute" | :215-217 | visible | The unchecked-task list in `steering.md` is the state; skipping one leaves it unchecked and it reappears in every subsequent status block (`status-display.md:49-50`). |
| 70 | "If no unchecked tasks remain and the Evaluation sign-off was approved, the session closes — open that session-close report with the session-status block" | :217-219 | visible | Row 12's reader. |
| 71 | "If no unchecked tasks remain and no 'Evaluation sign-off' task was ever encountered … that is a planning defect … escalate to the user immediately … do not close the session silently." | :219-222 | visible | A genuine backstop, quoted in full here, and the only rule in `rn` that checks another rule's output (`planning-workflow.md:37`). It fires only if the flow reaches the end of the task list inside a live session — 5 of 8 past sessions have no Evaluation sign-off task and none of them escalated. |

## `planning-workflow.md` (51 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 72 | "Run once per session." | :6 | visible | A second run would overwrite `steering.md` and open a second draft PR; both show in git and on GitHub. Nothing prevents it. |
| 73 | "Treat every user interaction as a proposal: lead with one concrete recommended option in plain language (no internal jargon), and proceed on confirmation." | :10 | visible | Every such interaction is a message the user reads; a bare question or a jargon-laden one is on their screen. The user is the only reader. |
| 74 | "`AskUserQuestion` is fine when one option is your recommendation." | :10 | visible | Same reader as row 73 — a permission, not an obligation, so a breach is only using it without a recommendation. |
| 75 | "At a stop that instructs opening with the session-status block, the block precedes the proposal." | :10 | visible | Same reader as row 73. |
| 76 | "Take it from the user's message or `$ARGUMENTS`; if neither is present, ask for it." | :12 | stops | With no goal there is nothing to restate; the flow cannot produce a `Goal` section without a user turn. |
| 77 | "Restate it as a clear, faithful understanding of what the user wants — capture full intent, never add scope or invent goals." | :12 | visible | The restatement is put to the user and becomes `steering.md`'s `Goal`, which the user reads on the PR at the plan gate (`:47`). Invented scope surfaces there. |
| 78 | "If ambiguous, propose your restatement and let the user correct it. This restatement becomes `Goal`." | :12 | visible | Same reader as row 77. |
| 79 | "The session lives at `.rn/{yyyymmdd}-{slug}/steering.md`, where `{yyyymmdd}` is today's date" | :14 | visible | Real consumers: `dn/SKILL.md:14` and `up/SKILL.md:17` both discover the file with `git log … -- '*/steering.md'` and rank "most recent". A wrong date prefix mis-ranks the candidate list; a wrong path makes the file undiscoverable. |
| 80 | Slug candidates: the current git branch, an issue reference in `$ARGUMENTS`, a kebab-case name from the goal | :15-18 | neither | Nothing reads the slug back. |
| 81 | "Propose one recommended slug plus the alternatives … When already on a non-default branch, recommend that branch's name as the slug." | :19 | visible | The proposal is on the user's screen. |
| 82 | "Alongside the slug, decide the session's `design.md` location with the user." | :21 | visible | Same reader as row 81. |
| 83 | "**Check for an existing design.md first.** … This is a judgment call on scope overlap, not a mechanical file-existence check." | :21-27 | neither | No artifact records that the check happened or what it concluded. |
| 84 | "If one covers the area, point this session's `Design:` line at it and treat the work on it as an update — following design-template.md's 'Updating an existing design.md' procedure … If none covers the area, default to `.rn/{yyyymmdd}-{slug}/design.md` (lowercase)" | :28-31 | visible | The `Design:` line is read by `migration-workflow.md:28-29` ("Read the session's `steering.md` `Design:` line; if it is absent, the session has no `design.md` — skip this step entirely"). A wrong pointer silently reconciles the wrong file; an absent one silently skips. |
| 85 | "Read `${CLAUDE_PLUGIN_ROOT}/references/steering-template.md` and follow its per-section guidance." | :33 | neither | Nothing records the read. Rows 106–134 below are the guidance, and most of it is itself unenforced. |
| 86 | "Stamp the template's top `Rn version:` line with the currently installed plugin's version — read from … `plugin.json`'s `version` field." | :33 | neither | 6 of 8 past `steering.md` files have no `Rn version:` line at all. The consumer (`on/SKILL.md:15` and the four siblings) does "a plain string comparison" (`migration-workflow.md:5`) that no file defines for a missing line, so an omission is silently a match. |
| 87 | "Write the chosen design.md path into the template's `Design:` line below it." | :33 | visible | Row 84's consumer. |
| 88 | "Read the doc-division rule … and `design-template.md`, then **allocate content at planning** per the doc-division" | :33 | neither | The allocation is a judgement with no recorded output; misallocated content just sits in the wrong file. |
| 89 | "Fill `Goal`, `Acceptance criteria`, `Assumptions`, and `Rules`. Leave `Tasks` and `State` as their placeholders for now." | :33 | visible | An empty section is a visible blank in the file the user reads at the plan gate. |
| 90 | "**Force no empty `design.md`**: a session with no design to record creates no `design.md` and omits the `Design:` line entirely (no file, no pointer) … never write an empty file and never leave a dangling pointer." | :33 | visible | A dangling pointer breaks row 84's consumer — `migration-workflow.md:28-31` would try to reconcile a file that is not there. Nothing checks the pointer resolves. |
| 91 | "Work backwards from the Acceptance criteria end state" | :35 | neither | An unrecorded reasoning method; the task list looks the same either way. |
| 92 | "Define each task following the template's `Tasks` structure, inline `Completion criteria` rules, and `Task definition requirements` table in full." | :35 | neither | This is the parent of rows 118–134, all of which are unenforced. The specimen: `20260705`'s tasks omit the Verification review step the structure mandates (`steering-template.md:70`) and nothing objected. |
| 93 | "**Design sign-off task.** When the session has a `design.md` not settled at plan time, place a 'Design sign-off' task … at the point where heavy build would otherwise start" | :36 | neither | No rule checks that the task exists — unlike the Evaluation sign-off, which has row 71's backstop. A missing Design sign-off is invisible. |
| 94 | "**Evaluation sign-off task.** Always place a final 'Evaluation sign-off' task as the session's last task." | :37 | visible | Backstopped by `task-verify-workflow.md:219-222` — the only planning rule with a downstream check. It fires late (at end of session) and only inside a live flow; 5 of 8 past sessions have no such task and none escalated. |
| 95 | "**Self-check before persisting.** Before persisting (Step 5), confirm the last task in the list is 'Evaluation sign-off' — if it is not, add it before persisting." | :38 | neither | A self-check with no recorded output. `20260625-rn-lean` placed its Evaluation sign-off as `#15`, mid-list before `#6`–`#14`. |
| 96 | "Write the completed `steering.md` to `.rn/{yyyymmdd}-{slug}/steering.md`." | :41 | visible | Row 79's consumers. |
| 97 | "Commit it: `chore: start session — {slug}`." | :42 | visible | Confirmed used consistently in this repo (`git log --all --grep='chore: start session' --oneline | wc -l` returns 11). Nothing reads the message, but its absence would leave the file uncommitted and therefore undiscoverable by `dn`/`up`'s `git log` search. |
| 98 | "Ensure the work is on a branch — if on the default branch, create `{slug}` first." | :43 | stops | `main` is protected in this repo: a push to it is refused by GitHub. This is external and real, not an `rn` mechanism. |
| 99 | "Push the branch, then open a draft PR (`gh pr create --draft`) titled from the goal." | :44 | stops | `gh pr create` errors on a missing branch or an existing PR; the failure is on screen. `:47-48` names the failure branch explicitly: "push or PR creation failed → report it and present the plan in the console instead". |
| 100 | "The PR body is a single link to the steering file and nothing else — do not copy the Goal, tasks, or any plan content into it. Use a branch-ref blob link" | :44 | visible | The PR body is what the user opens at the plan gate. Verified on this session's PR #21: the body is the single blob link (plus a `Closes #17` line added by the user's own workflow). |
| 101 | "Open the plan-gate ask with the session-status block … on both branches: push and PR creation succeeded → report the PR link and ask the user to review the plan on the PR; push or PR creation failed → report it and present the plan in the console instead." | :45-48 | visible | The message is on the user's screen. |
| 102 | "**Design gate.** … When the design is settled at plan time, fold it into this plan-gate approval (one stop). When it is not, Step 4 placed a **Design sign-off** task" | :49 | neither | See row 93. Which branch was taken is never recorded, so neither choice can be checked. |
| 103 | "**Take the sign-off via the user's verdict commands** … never infer approval and never record a verdict the user did not issue." | :50 | stops | `/rn:ty` and `/rn:gm` carry `disable-model-invocation: true` (`ty/SKILL.md:4`, `gm/SKILL.md:4`) — the assistant cannot invoke them, so a genuine verdict can only come from the user. Fabricating one in prose is only *visible* (row 16). |
| 104 | "**CRITICAL: DO NOT proceed without explicit user approval.**" | :51 | stops | Row 13's mechanism: the ask ends the turn and the conversation needs a user message to continue. |

## `steering-template.md` (106 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 105 | "Read when creating a new `steering.md`." | :3 | neither | Nothing records the read. |
| 106 | "**Copy the template block below verbatim.** Keep every heading. Keep the blank lines between fields" | :7 | visible | The headings are consumed: `dn/SKILL.md:25` writes "the `State` section", `up/SKILL.md:24` reads it, `migration-workflow.md:21-23` compares "its `Goal` / `Acceptance criteria` / `Assumptions` / `Rules` / `Tasks` / `State` fields". A missing heading breaks a named consumer. Nothing checks the blank lines. |
| 107 | "**Leave placeholders in unpopulated sections.** `Tasks`, `State` start empty; fill later." | :8 | visible | An empty section is a blank the user reads at the plan gate. |
| 108 | "**Fill each section per the rules below.**" | :9 | neither | Parent of rows 109–141; almost all of them are unenforced. |
| 109 | Doc-division: "**Requirements & acceptance criteria → `steering.md`**" | :15 | neither | No reader checks what kind of content sits in which file. |
| 110 | "**Structure & decisions (how the parts fit, and why) → `design.md`** … rationale lives only here, at the decision level." | :16 | neither | Same as row 109. |
| 111 | "**User-facing UX → `README`**" | :17 | neither | Same as row 109. |
| 112 | "A decision lands in a task, in `design.md`, or in a rule. Deliberation and history live in git + the PR — never in steering." | :19 | neither | Nothing measures steering's content against this. |
| 113 | "`Rn version:` … is written once, at creation, from the installed plugin's version — never user-edited afterward" | :21-24 | neither | See row 86: absent from 6 of 8 sessions, and the comparison that would consume it treats absence as no-mismatch. |
| 114 | "The `Design:` line below it points to the session's `design.md`. A session with no design omits this line entirely" | :26-27 | visible | Row 84's consumer (`migration-workflow.md:28-29`). |
| 115 | `Goal`: "why this is being done and what the user wants to change — the full intent, no added scope" | :37 | visible | The user reads it at the plan gate; `status-display.md:37-38` compresses it into every status block's header. |
| 116 | `Acceptance criteria`: "the states / conditions by which the goal is judged achieved" | :41 | visible | Consumed by the Evaluation sign-off task, whose completion criteria are "the Acceptance criteria run is approved" (`planning-workflow.md:37`) — the user reads the run at the last gate. |
| 117 | "two axes: goal alignment + quality" | :42 | neither | Nothing checks that both axes are present. |
| 118 | "write these exhaustively, never sample — the complete set is what defines scope (in / out)" | :43 | neither | Completeness of a list against an unstated whole is unverifiable by construction, and nothing tries. |
| 119 | `Assumptions`: "things taken to be true in pursuit of the goal — if one proves false, the plan changes" | :47 | visible | Read by the user at the plan gate; `migration-workflow.md:21-23` names the field among what it reconciles. |
| 120 | "distinguish facts from assumptions — state explicitly if unverified" | :48 | neither | Nothing separates the two after the fact. |
| 121 | `Rules` seeds "commit and push every change; one completion marker per task" | :52 | visible | The marker half is consumed by `up/SKILL.md:26`; the push half is visible as an unpushed branch on the PR. |
| 122 | "**Purpose**: what to achieve, 1-2 sentences" | :59 | visible | Copied into the work-order (`task-execute-workflow.md:141`) and read by the user at the plan gate. Length is unchecked. |
| 123 | "**Prerequisites**: tasks that must be completed first (or 'none')" | :61 | neither | Nothing reads prerequisites: `task-verify-workflow.md:215` advances to "the next unchecked task" by position, not by dependency. **A stated prerequisite has no consumer at all.** |
| 124 | Steps include "self-check (OK/NG per completion criterion, record in checks/{task-id}.md)" as a `- [ ]` item | :67 | visible | The step is a checkbox in `steering.md`; `dn/SKILL.md:22-23` checks off completed steps and the file is on the PR. An unchecked box is a visible blank — but past sessions closed with unchecked boxes left behind (3 in `20260705`, 2 in `20260624`) and nothing objected. |
| 125 | Steps include "QA expert review (subagent)" | :68 | neither | Same checkbox mechanism as row 124, and it fails the same way: a step that planning never wrote cannot be a blank. Every session before `20260625` has QA steps; the review sections behind them are missing from most check files. |
| 126 | Steps include "Craft expert review (subagent, per the task's medium)" | :69 | neither | Absent from all 5 sessions before `20260625-rn-lean`. Nothing noticed. |
| 127 | Steps include "Verification expert review (subagent, per the task's medium)" | :70 | neither | **The specimen.** Absent from all 7 tasks of `20260705-improve-design-template` and from every earlier session; present in only 5 of 40 check files. The rule exists, the breach is plain in the output, and nothing in `rn` looks. |
| 128 | Steps include "(tasks that produce or revise structure/approach only) Design expert review (subagent)" | :71 | neither | Same as row 126, plus the conditional judgement is never recorded. |
| 129 | Completion criterion ①: "is the objective achieved? — the objective met, not that an output was produced (write 'the residue no longer keeps the tree dirty', not 'DESIGN.md exists')" | :75-76 | neither | This is the rule this session's Goal names as broken. It binds *Completion* criteria only; `20260705`'s *Acceptance* criteria were written as artifact existence (`:22-49`) and the template says nothing there (row 116). Nothing reads either against this bar. |
| 130 | Criterion ②: "are new problems absent? — name the representative failure modes and require their absence" | :77 | neither | Same as row 129; most past criteria state no failure modes. |
| 131 | "objectively verifiable by a third party; no vague terms ('appropriate', 'correct')" | :78 | neither | Nothing scans for the vague terms it names. |
| 132 | "state the end-state, never actions/reviews/gates (those belong in Steps); the grounds are recorded at verification … not written into the criterion text" | :79 | neither | Same as row 129. |
| 133 | `State` placeholder: "`Status` is `paused` while a session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here, so only a genuinely suspended session reads `paused`." | :83-85 | visible | Real consumers: `dn/SKILL.md:15-16` and `up/SKILL.md:19` both rank candidates by "`State` showing `Status: paused`". A stale `paused` mis-ranks discovery — and `20260615-subagent-execution/steering.md` still reads `Status: paused` today, a closed session that would win that ranking. |
| 134 | `Notes`: "bounded forward pointer … not a re-narration of the session (that lives in `git log`)" | :91 | visible | Read by `up/SKILL.md:24` and `:28`. Boundedness is unchecked. |
| 135 | Granularity: "Purpose expressible in one sentence; split if it grows" | :100 | neither | Consumed only by `migration-workflow.md:33-38`, which re-applies the same judgement with no recorded output. |
| 136 | Specificity: "Not 'implement' but 'implement `methodName()` in `ClassName`'" | :101 | neither | Same as row 135. |
| 137 | Objectivity: "Completion criteria judgeable by a third party" | :102 | neither | Same as row 135. The third party exists (QA, `task-verify-workflow.md:154-155`) but reviews *against* the criteria, never *the* criteria. |
| 138 | Prerequisites: "List dependencies explicitly; enables parallel/sequential judgment" | :103 | neither | Row 123: nothing consumes prerequisites. |
| 139 | Criteria vs steps: criteria answer ① and ② with grounds, "not that an artifact was produced; actions, reviews, and gates go in Steps as `- [ ]` so their status stays trackable. The task-execution references' … Process selection section … is the source of *which* reviews apply — keep the two in sync" | :104 | neither | "Keep the two in sync" names no mechanism, and the two are demonstrably out of sync: `task-execute-workflow.md:59-64` mandates Verification for every build task, and this template's Steps list has carried it since `0.7.0` — yet planning wrote it into 0 of 7 tasks in the very next session. |
| 140 | Flat tasks: "Number tasks `#1`, `#2`, …; do not group into phases or add phase-level gates … The user signs off only at the three scheduled gates" | :105 | visible | Numbering is consumed by `up/SKILL.md:26`'s `complete task #{id}` grep and by `status-display.md:39-50`'s ranges. Non-sequential ids break neither, but `20260625-rn-lean` ordering `#1–#5, #16, #15, #6–#14` produced a task list whose reading order is not its numeric order. |
| 141 | Done annotation: "A task that is done but awaiting an external gate … may carry an explicit done annotation in its heading … such a task counts as completed for the session-status display" | :106 | visible | Consumed by `status-display.md:19-22`: "A task counts ✅ when `steering.md` records it complete — checked off, or carrying an explicit done annotation". Both files agree; `20260625-rn-lean` used the annotation on 14 tasks with no `[x]` check-offs at all, so the whole session's ✅ state rests on prose matching. |

## `status-display.md` (83 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 142 | "The compact session map that opens every message stopping for user input while a session is active … The block comes first in that message — before the ask and anything else." | :3-5 | visible | The block is rendered to the user by construction; its absence is a gap on their screen. Nothing flags it, and nothing in `rn` re-reads a sent message. |
| 143 | "**Emit only while a session is active** — its `steering.md` exists and is identified." with the listed exceptions (planning's pre-persist asks, `/rn:up` before identification, `/rn:gm` or `/rn:ty` with no active session) | :9-12 | visible | Same reader as row 142. A block emitted with no session would have to be invented, which shows as fabricated task ids. |
| 144 | "**Asks and flow-ending reports both count as stops** … on a report the 👉 line states where the session stands and the user's next move instead of an ask." | :13-16 | visible | Same reader as row 142. |
| 145 | "**Derive the block fresh from the active `steering.md` at emit time** — its `Goal`, task list, and check-offs are the only source; never reuse an earlier block." | :17-18 | neither | A stale block and a fresh one look identical unless the state changed between them, and nothing compares the block to the file. |
| 146 | "**A task counts ✅ when `steering.md` records it complete** — checked off, or carrying an explicit done annotation … Done-but-awaiting … still counts ✅; the pending item goes on the outlook line" | :19-22 | visible | Row 141's paired rule. The user reads the block against the PR. |
| 147 | "**Write the block in the user's conversation language.**" | :23-24 | visible | Immediately obvious to the user. |
| 148 | "**Markers are fixed**: ✅ completed / 👉 current / ⬜ remaining." | :25 | visible | Same reader as row 142. |
| 149 | The format block — header / ✅ / 👉 / ⬜ / outlook, in that order | :29-35 | visible | Same reader as row 142. |
| 150 | "**Header** — `── {slug}: {goal one-liner} ──`: the session's slug (the steering directory name, date prefix dropped) and a one-line compression of steering's `Goal`." | :37-38 | visible | Same reader as row 142. |
| 151 | "**✅ completed** … Group consecutive ids into ranges … comma-separate non-consecutive groups … No completed tasks yet → no ✅ lines." | :39-42 | visible | Same reader as row 142. |
| 152 | "**👉 current** — exactly one line … A stop not tied to a numbered task (the plan gate; an escalation that spans tasks) names the gate or moment instead of an id." | :43-48 | visible | Same reader as row 142. |
| 153 | "**⬜ remaining** … **No remaining tasks → omit the ⬜ lines entirely** — never render an empty ⬜ section." | :49-50 | visible | Same reader as row 142. |
| 154 | "**Outlook** — one closing parenthesized line: what follows this stop" | :51-52 | visible | Same reader as row 142. |

`status-display.md` is the one file whose every rule lands "visible": its entire product is a block the
user reads. That is also its ceiling — the user is the only checker, and no `rn` step ever compares an
emitted block against `steering.md`.

## `migration-workflow.md` (70 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 155 | "Invoked by a command skill (`on`/`dn`/`up`/`ty`/`gm`) when the active session's `steering.md` `Rn version:` line does not match the installed plugin's version — the skill's own version-check step (a plain string comparison) is what triggers this file … Run once per invocation." | :3-5 | neither | The trigger is a prose step in five skills (`on/SKILL.md:15` and siblings) with no recorded output. It has never fired in this repo: 6 of 8 sessions carry no `Rn version:` line, and the two that do were current when written. |
| 156 | "Coordinator only: no implementation expert, and no QA/Design/Craft/Verification review, spawns for this procedure itself … The coordinator reads each artifact, judges drift, and edits it directly." | :8-12 | visible | The edits land as a commit on the PR (`:56`), which the user reads. Nothing checks that no expert was spawned. |
| 157 | "Reconcile the three artifacts below **in this order** — steering, then design, then tasks." | :15-18 | neither | Order leaves no trace in the resulting commit. |
| 158 | Step 1: "Compare the session's `steering.md` … against the current `steering-template.md`. Judge by reasoning what has drifted … and edit `steering.md` directly to close it." | :20-25 | neither | An unrecorded judgement. A pass that finds nothing and a pass that never ran produce the same empty diff. |
| 159 | Step 2: "Read the session's `steering.md` `Design:` line; if it is absent … skip this step entirely. If present, follow `design-template.md`'s own 'Updating an existing design.md' procedure … do not re-derive reconciliation logic here." | :27-31 | visible | The `Design:` line is a real input that determines a branch; a dangling pointer (row 90) sends this step at a missing file, which errors on read. |
| 160 | Step 3: "For every unchecked task … judge its Purpose / Prerequisites / Steps / Completion criteria against each row of that table — Granularity, Specificity, Objectivity, Prerequisites, Criteria vs steps, Flat tasks, Done annotation — and edit the task directly" | :33-38 | neither | Same as row 158; and the table rows it applies are themselves unenforced (rows 135–141). |
| 161 | "Leave every already-checked-off task untouched — reconciliation targets the forward-looking remainder, not the record of what already happened." | :39-40 | visible | A touched historical task shows in the reconciliation commit's diff on the PR. |
| 162 | For a task whose Completion criteria changed and that has a `checks/{task-id}.md`: "record in its Overall Verdict a `Ready to check off: No — criteria reconciled, self-check/review must re-run` line" — and if no such file exists, write nothing | :41-52 | neither | **This row's own stated mechanism does not exist.** `:46-48` claims "`task-verify-workflow.md`'s Phase: Complete only checks off once Verify has cleared with `Ready to check off` reading Yes", but Phase: Complete (`task-verify-workflow.md:208-209`) never mentions the field: it says only "With Verify cleared … check off the task in `steering.md` directly." Empirically, 24 of 40 past check files carry no `Ready to check off` line at all and every one of those tasks was checked off anyway. |
| 163 | "Apply the reconciling edits from all three steps and commit them directly. This is not one of the three scheduled gates … and it does not go through per-task QA/Craft/Design review — it is a mechanical, no-gate procedure." | :56-58 | visible | The commit is on the PR the user reads. This is deliberate: the rule's own design accepts "an occasional wrong reconciliation … caught via normal PR/git-log review" (`.rn/20260705-improve-design-template/steering.md:57-59`). |
| 164 | "Once the reconciling edits are committed, update the session's `steering.md` `Rn version:` line to the installed plugin's version — the last step, so the stamp only advances once the artifacts it certifies are actually current." | :59-61 | neither | Nothing checks the ordering, and a stamp advanced without the edits is indistinguishable from one advanced after them. |
| 165 | "This file never reads `CHANGELOG.md` and never reasons about version ranges or deltas … Every comparison above asks one question only: does this artifact match what the **currently installed** templates/workflows require, right now." | :63-70 | neither | A prohibition on a reasoning method; nothing observes the method. |

## `design-template.md` (139 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 166 | "Read when creating a session's `design.md` … **Not read at runtime**: it records decisions and how the parts fit" | :3-5 | neither | The file declares its own product unenforceable: nothing in the flow reads `design.md`. Its only reader is the Design sign-off gate — which exists only when planning placed one (row 93), and 7 of 8 sessions have no such task. |
| 167 | "The h2 sections below are the canonical design-document sections; under each, the h3 headings are the questions that section must answer — a section is done when its questions are answered, not when its heading merely exists." | :7-9 | neither | Nothing distinguishes an answered h3 from a heading with prose under it. |
| 168 | "This is the fresh-authoring path … to update an existing one, skip to 'Updating an existing design.md'" | :13-14 | neither | Which path was taken is never recorded. |
| 169 | "**Copy the template block below verbatim.** Keep every heading, numbering, and section order — the five h2 sections and the h3 questions under them are the contract" | :16-17 | visible | Verifiable by reading the file, and `rn/docs/design.md` does carry all five h2 sections in order (verified: lines 6, 54, 80, 190, 289). Nobody is asked to check. |
| 170 | "**Answer every h3 question with a decision and the reasoning behind it** … If a question does not apply, say so **and say why** … Nothing here licenses a section with a question left silently unanswered." | :19-22 | neither | The core rule of the file, and there is no reader: a missing answer under a present heading looks like prose. |
| 171 | "**In Detailed design, repeat `4.N` once per mechanism or component the design introduces** — not a fixed four" | :23-24 | neither | Nothing enumerates the design's mechanisms to compare against the subsection count. |
| 172 | "**Treat the whole document as optional, not any section within it.** … once you are writing one, no section may be skipped for having 'nothing to record'" | :25-28 | neither | Same as row 170. |
| 173 | The template block — five h2 sections with their h3 questions, and the header line "Not read at runtime — for whoever maintains the design" | :32-75 | neither | Same as row 170. |
| 174 | Per-section guidance, including: every `4.N` "asks the same pair of questions of its mechanism: what does it guarantee, and how is a breach of that guarantee caught?" | :81-96 | neither | The template asks of every mechanism the exact question this inventory asks of every rule — and nothing checks that the answer is real. `rn/docs/design.md`'s own `4.N` answers are the place this session's gap should have shown. |
| 175 | "Follow this instead of the Steps above when `planning-workflow.md`'s location check (Step 2) points `Design:` at an existing `design.md`" | :100-102 | neither | Row 168. |
| 176 | "**Read the existing document in full before touching it.** Identify which h3 questions the session's work actually changes" | :104-105 | neither | Reading leaves no trace. |
| 177 | "**Revise only what changed.** … leave every other section's existing text untouched. Carrying forward unchanged text is correct, not lazy" | :106-108 | visible | A wholesale rewrite shows in the commit diff the coordinator reads (`task-verify-workflow.md:139`) and on the PR. |
| 178 | "**The decision-plus-reasoning contract from fresh authoring still applies to whatever you touch.**" | :109-111 | neither | Row 170. |
| 179 | "**If the document predates the five-section shape** … reconcile it toward the current five-section shape as part of this update … relocating content to the section it actually belongs to … not license to rewrite unrelated, still-accurate content." | :112-126 | visible | The relocation shows in the diff (row 177's reader). Whether the *right* content moved is unchecked. |
| 180 | "**Give genuinely open content a destination outside `design.md`.** … Session-scoped: put it in that session's `steering.md` Notes field … Canonical/cross-session: track it outside `design.md` instead (e.g. a repo issue)" | :127-137 | neither | Nothing follows an open question to its destination; a dropped one leaves no residue. |
| 181 | "**Add or drop `4.N` subsections to match what changed** — a new mechanism gets a new subsection, a removed one loses its subsection instead of being left stale." | :138-139 | neither | Row 171. A stale subsection reads exactly like a current one. |

## `pr-feedback-workflow.md` (153 lines)

This file is the densest cluster of genuinely enforced rules in `rn`, because almost every step is a
`gh` call whose failure is a non-zero exit rather than a prose instruction.

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 182 | "A **coordinator** dispatches one **execution subagent** per review thread, sequentially, and reviews each result before the next." | :3-5 | neither | Nothing records the dispatch (rows 5, 11). |
| 183 | "Verification is a single coordinator pass — not the QA-expert / multi-round chain" | :5-7 | neither | A scope statement about what does *not* run; its breach (running experts anyway) leaves no artifact. |
| 184 | "Entered from `/rn:gm` with no argument — the argument/no-argument routing rule lives in `gm/SKILL.md`." | :9-10 | stops | `gm/SKILL.md:15` is a deterministic branch on a trimmed `$ARGUMENTS`, and `gm` itself carries `disable-model-invocation: true` (`gm/SKILL.md:4`) so it can only be user-invoked. |
| 185 | Coordinator "Never resolves a thread." | :16-17 | visible | Thread resolution is GitHub state the reviewer sees; a thread resolved by the assistant is visibly resolved-by-assistant on the PR. |
| 186 | Execution subagent "Handles exactly one thread, with exactly one of two outcomes (address-and-reply, or reply-with-a-question). Never resolves a thread." | :18-19 | visible | The reply is posted to a specific thread on the PR; two threads touched by one subagent show as two replies. Row 185's reader. |
| 187 | "**Find the session's PR** for the current branch: `gh pr view --json number,url`" | :22-26 | stops | Real command with a real failure mode. Verified: run on this branch it returns `{"number":21,"url":"…/pull/21"}` with exit 0; on a branch with no PR it exits non-zero, which is exactly what the next row handles. |
| 188 | "If this exits non-zero or reports 'no pull requests found' … **stop and report** — do not fabricate a PR number or proceed into the GraphQL call. Open that report with the session-status block" | :28-31 | stops | The GraphQL query at `:46` takes `-F pr={number}`; with no number there is nothing to pass and the call fails. The prohibition on fabricating one is only prose, but the fabricated number would return an error from the API. |
| 189 | "Capture `owner` and `repo` as **two separate** values" with the two `gh repo view -q` commands | :33-38 | stops | A combined value breaks `-f owner=` / `-f repo=` in the GraphQL call, which the API rejects. |
| 190 | "**Fetch all review threads** via GraphQL, **paginating** `reviewThreads` until exhausted … **Repeat** the call while `pageInfo.hasNextPage` is true … **accumulate** `nodes` across pages." | :42-72 | neither | A skipped page silently drops threads: the loop's queue is smaller, and nothing counts what should have been there. This is the one step in the file whose breach is invisible. |
| 191 | "Keep a thread **only** when both hold: `isResolved == false`, AND the **last** comment's author … equals the **first** comment's author" | :74-79 | visible | Wrongly kept threads produce a duplicate reply on the PR, which the reviewer sees; wrongly dropped ones leave the thread unanswered, which the reviewer also sees. The reviewer is a real second reader here. |
| 192 | "Drop every other thread … For each kept thread record: the **first** comment's `databaseId`, `path` and `line` … and the comment bodies" | :80-82 | stops | The reply endpoint at `:109` is keyed on `first_comment_databaseId`; a wrong or missing id is rejected by the API. |
| 193 | "Process the queue **one thread at a time**. Never dispatch two threads in parallel" | :86-87 | neither | Parallel dispatch produces the same replies in a different order; nothing records timing. |
| 194 | Work-order contents: Thread (`path`, `line`, full bodies, `databaseId`) and Task ("produce exactly one of the two outcomes") | :89-92 | neither | Row 27: the prompt is never written down. |
| 195 | Outcome (a): "Make the change. Stage the touched paths **explicitly** … Never `git add -A` or `git add .`." | :94-95 | visible | The PR diff, read by the reviewer whose thread this is. Row 35's limits apply. |
| 196 | Outcome (a): "Commit with a plain conventional message … The message must **not** contain `complete task #`." | :96-97 | visible | Row 36's consumer (`up/SKILL.md:26`). A PR-feedback commit carrying the substring would check off an unrelated task on the next resume. |
| 197 | Outcome (a): "Push to the session PR. Never force-push." | :98 | stops | `git push` fails on a rejected non-fast-forward, and the failure is handled explicitly by the next row. |
| 198 | "**If the commit or push fails, do not post a Done reply** (its permalink would point at an unpushed, dead commit). Return the failure in the summary … post the reply only once the commit is confirmed pushed." | :99-102 | stops | `gh browse <sha> -n` at `:103` cannot produce a URL for a commit GitHub does not have, so the reply body cannot be built. |
| 199 | "Once the commit is pushed, get its permalink: `gh browse <sha> -n`" | :103-104 | stops | Same as row 198 — a real command with a real failure. |
| 200 | "**Reply to the thread** with a short summary of what was done plus the commit link, in-reply-to the thread's first comment — **only after the commit is pushed**" | :105-111 | visible | The reply is on the PR; a missing one leaves the reviewer's thread unanswered, and the loop's own queue filter (row 191) re-picks it up on the next run. That re-pick is a genuine self-correcting mechanism. |
| 201 | "**Outcome (b) — needs a decision / is unclear:** make **no** code change. Reply to the thread with the question" | :113-119 | visible | Same reader as row 200; a code change made anyway shows in the PR diff. |
| 202 | "**Return** — a compact summary: which outcome, what changed (files), the commit SHA and that it was pushed … or the question asked" | :121-122 | visible | Read by the coordinator at `:130`. |
| 203 | "**Never resolve the thread.** Resolution is the author's act on GitHub" | :124 | visible | Row 185. |
| 204 | "**Check the result.** … **OK → dispatch the next thread.** … **Problem → re-instruct the same subagent on the same thread.** Do not advance until it is right." | :128-134 | visible | The coordinator reads the summary and the PR; a wrong result shows as a reply that does not match its thread. |
| 205 | "When the queue is empty, the loop is done — report the loop result … opening that report with the session-status block" | :136-138 | visible | Row 142's reader. |
| 206 | "The loop **never** resolves a thread. Neither the coordinator nor the subagent calls `resolveReviewThread` … The loop treats GitHub's unresolved state as its **queue**." | :142-148 | visible | This is `rn`'s single best-designed mechanism: state lives in GitHub, not in the assistant's memory, so a missed thread is re-collected on the next run (row 200). Quoted in full because the guarantee is real. |
| 207 | "One coordinator pass per item … is the whole of verification. No QA expert, no Design / Craft / Verification experts, no multi-round iteration cap." | :150-153 | neither | Row 183. |

## `on/SKILL.md` (17 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 208 | "`disable-model-invocation: true`" / "Has side effects (writes files, commits, pushes, opens a PR) — run only on explicit `/rn:on`." | `on/SKILL.md:3-4` | stops | The harness refuses model invocation of the skill. The only machine-enforced rule in the plugin. |
| 209 | "**Plan the session.** Read `${CLAUDE_PLUGIN_ROOT}/references/planning-workflow.md` and run it in sequence." | `on/SKILL.md:13` | visible | The workflow's own outputs (`steering.md`, the `chore: start session` commit, the draft PR) are artifacts whose absence shows. Skipping a *step* inside it shows only if that step had an artifact. |
| 210 | "**Check version.** … on a mismatch, run `migration-workflow.md` first — on a match, do nothing. Since step 1 just stamped that line from this same installed version, this branch can never actually fire here — it's kept only so `on`'s step matches `dn`/`up`/`ty`/`gm`'s" | `on/SKILL.md:15` | neither | The file states outright that the branch is unreachable. It is a consistency-of-appearance rule, not a check. |
| 211 | "**Begin task #1.** After approval, read `task-execute-workflow.md` then `task-verify-workflow.md` and execute task #1 following them in sequence." | `on/SKILL.md:17` | stops | "After approval" is row 104's stop; the ordering half is row 1 (neither). |

## `dn/SKILL.md` (59 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 212 | "`disable-model-invocation: true`" / "run only on explicit `/rn:dn`" | `dn/SKILL.md:3-4` | stops | Row 208's harness mechanism. |
| 213 | "Records resume state and hands off. Does not execute tasks." | `dn/SKILL.md:9` | visible | A task executed during suspend would land as a deliverable commit in the suspend push, visible on the PR. |
| 214 | "**Locate steering.md.** Use the path known from this session. If unknown: run `git log --diff-filter=AM --name-only --pretty=format: -- '*/steering.md' \| head -5`, keep the paths that exist on disk, and take the one whose `State` shows `Status: paused`, else the most recent." | `dn/SKILL.md:13-16` | stops | A real command whose output determines the branch. Its weakness is data, not enforcement: `20260615-subagent-execution/steering.md` still reads `Status: paused`, so a closed session outranks the live one. |
| 215 | "**Check version.** Compare `steering.md`'s `Rn version:` line to the installed plugin's version; on a mismatch, run `migration-workflow.md` first" | `dn/SKILL.md:18-20` | neither | Row 86: 6 of 8 sessions have no such line, and no file defines the missing-line case. |
| 216 | "**Check off progress.** In steering.md, check off completed task steps and add any tasks discovered during the work." | `dn/SKILL.md:22-23` | visible | The check-offs are consumed by `status-display.md:19-22` and by `task-verify-workflow.md:215`'s "next unchecked task". |
| 217 | "**Write the `State` section** per `steering-template.md`'s State placeholder: `Status: paused`, `Date`, `Last completed`, `Next`, `Notes` — cap `Notes` to the bounded forward pointer" | `dn/SKILL.md:25-27` | stops | `up/SKILL.md:19` ranks candidates by `Status: paused` and `:24` reads the section: without it, resume picks the wrong session or has no next task. The `Notes` cap itself is unchecked. |
| 218 | "**Commit the work.** Tree clean → skip. Current task's steps all checked → commit normally. Some steps unchecked → commit with a `wip:` prefix." | `dn/SKILL.md:29-32` | visible | `git status` output is on screen and drives the branch; the resulting message is on the PR. Nothing verifies the prefix matches the checkbox state. |
| 219 | "The message must not contain `complete task #`." | `dn/SKILL.md:33` | visible | Row 36's consumer — and the historical breach `4daf6b2` is precisely a suspend-time bookkeeping commit that quoted this rule in its own body. |
| 220 | "**Resolve untracked residue.** Run `git status --porcelain` … Regenerable test/build artifact … → append a matching rule to the repo-root `.gitignore` (create it if absent). Any doubt → handle as the next item instead." | `dn/SKILL.md:35-39` | stops | `git status --porcelain` is run and its output is the input; step 8 (`:50-54`) re-runs it as a check. This is one of only two places in `rn` where a step verifies its own effect. |
| 221 | "Anything else → ask the user how to handle it … opening the message with the session-status block … For any path the user does not resolve, append its exact `git status --porcelain` string to `State → Notes`." | `dn/SKILL.md:40-43` | stops | The ask ends the turn (row 13's mechanism), and step 8's re-run catches anything left. |
| 222 | "Never delete a file yourself." | `dn/SKILL.md:44` | neither | A deleted untracked file leaves no trace anywhere — not in git, not in `git status`. This is the clearest example in `rn` of a rule whose breach is undetectable in principle. |
| 223 | "**Commit and push.** Commit the `State` changes and any `.gitignore` edit together in one commit, then `git push`. If push fails, continue and record that it failed (for step 9). Never amend, never force-push." | `dn/SKILL.md:46-48` | stops | `git push` reports its own failure and the rule handles it; the resulting commit is on the PR. An amend would rewrite a pushed commit and be rejected without a force-push. |
| 224 | "**Verify clean.** Run `git status --porcelain` … Non-empty → for each remaining (non-gitignored) untracked path, if its exact string is not already recorded in `State → Notes` … record it there as user-deferred; then go to step 9. Never loop back to step 6. Never delete a file." | `dn/SKILL.md:50-54` | stops | The re-run is a genuine post-condition check on step 6 — the only self-verifying step in the plugin. |
| 225 | "**Report.** Open the report with the session-status block … then output the branch name. If the last push did not succeed, state that the commits are local-only and must be pushed. Name any user-deferred paths" | `dn/SKILL.md:56-59` | visible | The report is on the user's screen; the "local-only" claim is checkable against the PR. |

## `up/SKILL.md` (34 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 226 | "`disable-model-invocation: true`" / "run only on explicit `/rn:up`" | `up/SKILL.md:3-4` | stops | Row 208. |
| 227 | "**Handle a dirty tree.** Tree dirty → run step 2's discovery first, read-only … then propose a `wip:` commit or a discard, opening the message with the session-status block … and wait for confirmation before touching the working tree." | `up/SKILL.md:13-15` | stops | `git status` drives the branch and the proposal ends the turn. Discarding without confirmation would be irreversible and undetectable — that half is unenforced. |
| 228 | "**Find steering.md.** Run `git log --diff-filter=AM --name-only --pretty=format: -- '*/steering.md' \| head -5` and keep the paths that exist on disk." | `up/SKILL.md:17` | stops | Real command; `head -5` silently truncates once a repo has more than five session directories — this repo already has eight `steering.md` files. |
| 229 | "One result → use it. Multiple → rank by `State` showing `Status: paused`, then most recent commit, and propose the top candidate. Zero → tell the user 'No steering.md found. Run `/rn:on` to start.' and stop." | `up/SKILL.md:18-20` | stops | The zero branch genuinely stops. The ranking is fed by row 133's stale `paused`. |
| 230 | "From step 3 on, any message stopping for user input opens with the session-status block" | `up/SKILL.md:22` | visible | Row 142's reader. |
| 231 | "**Read State.** Read the `State` section: last completed task, next task, and notes." | `up/SKILL.md:24` | stops | Without it there is no "next task" to resume; the flow has nothing to do. |
| 232 | "**Sync tasks.** Cross-check `git log` against the unchecked tasks. A commit matches a task when its message contains `complete task #{id}`; check that task off" | `up/SKILL.md:26` | stops | A real grep against real commits — the single most consequential consumer in `rn`. The mechanism exists and is wrong on its own terms: `complete task #{id}` is a substring test, so `complete task #1` is a prefix of `complete task #1b`, `#10`–`#14` and `#16`. `git log --all --grep='complete task #1' --oneline \| wc -l` returns 16 in this repo; 7 of those 16 are those other tasks. Three further commits (`4daf6b2`, `893de07`, `de0b1ec`) carry the substring in a body without being markers. Scoping is a second defect in the other direction: `git log --grep='complete task #1'` without `--all` returns 0 from this worktree's `HEAD`, because past sessions' marker commits were squash-merged into `main` and no longer exist as individual commits in this history. |
| 233 | "**Check blockers.** If `State` notes mention a blocker, investigate and find an alternative approach before removing any task." | `up/SKILL.md:28` | visible | A removed task disappears from `steering.md`, which the user sees in every subsequent status block. |
| 234 | "**Clean up State.** Replace the `State` section with its template placeholder and commit the reconciliation." | `up/SKILL.md:30` | visible | The commit is on the PR. Skipping it leaves `Status: paused` behind — exactly the residue in `20260615-subagent-execution/steering.md` that still mis-ranks discovery today. |
| 235 | "**Check version.** … on a mismatch, run `migration-workflow.md` first" | `up/SKILL.md:32` | neither | Row 86. |
| 236 | "**Begin the next task.** Read `task-execute-workflow.md` then `task-verify-workflow.md` and execute the next unchecked task following them in sequence." | `up/SKILL.md:34` | visible | "Next unchecked" is read from `steering.md`; the ordering half is row 1 (neither). |

## `ty/SKILL.md` (26 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 237 | "`disable-model-invocation: true`" / "is user-invoked — run only on explicit `/rn:ty`" | `ty/SKILL.md:3-4` | stops | Row 208 — and this is what makes rows 16 and 103 meaningful: an approval cannot be self-issued. |
| 238 | "Approves the pending rn confirmation and advances the flow. Performs no revision." | `ty/SKILL.md:9` | visible | A revision made under `/rn:ty` lands as a commit the user did not ask for, on the PR. |
| 239 | "**Check version.**" | `ty/SKILL.md:13` | neither | Row 86. |
| 240 | "**Identify the pending approval.** … Exclude weigh-in / escalation questions … State the identified target back. Proceed only if it is unambiguous; if more than one approval is plausibly pending … ask the user which before recording approval" | `ty/SKILL.md:15` | visible | "State the identified target back" puts the identification on the user's screen before it is acted on — a deliberate, real, and rare design: the rule creates its own reader. |
| 241 | "**Record it as approved.** Register the pending confirmation as accepted." | `ty/SKILL.md:17` | visible | For a task gate, the record is the `steering.md` check-off (`task-verify-workflow.md:208`), which is committed and read downstream. For a plan gate there is no artifact at all. |
| 242 | "**Advance the workflow.** … a plan or design gate passes — execution proceeds to the next task; an evaluation gate passes — the session can close; a reviewed item is accepted … When the advance ends the flow … open that closing report with the session-status block" | `ty/SKILL.md:19-24` | visible | Row 142's reader. |
| 243 | "**Nothing pending.** If nothing is actually awaiting approval, open the reply with the session-status block …, say so, and do nothing else." | `ty/SKILL.md:26` | visible | Row 142's reader. |

## `gm/SKILL.md` (21 lines)

| # | Rule | Source | Verdict | Mechanism, or why nothing catches it |
|---|---|---|---|---|
| 244 | "`disable-model-invocation: true`" / "run only on explicit `/rn:gm`" | `gm/SKILL.md:3-4` | stops | Row 208. |
| 245 | "**Check version.**" | `gm/SKILL.md:13` | neither | Row 86. |
| 246 | "**Branch on the argument.** Trim `$ARGUMENTS` of surrounding whitespace first; treat a blank/whitespace-only value as empty. If non-empty after trimming, it is the feedback — go to step 3. If empty … go to step 4." | `gm/SKILL.md:15` | stops | A deterministic predicate on a real value, with both branches defined — the only fully specified conditional in the plugin. |
| 247 | "**With feedback.** Treat `$ARGUMENTS` as a revise verdict on the pending item … If there is no pending item, treat `$ARGUMENTS` as a direct instruction and act on it … do not stall on a missing target. Apply the revision … then report, opening the report with the session-status block … Do not enter the PR-feedback loop." | `gm/SKILL.md:17` | visible | The revision lands as commits on the PR and the report is on the user's screen. Whether it addressed the feedback is unchecked. |
| 248 | "**From the PR (no argument).** Read `pr-feedback-workflow.md` and run that loop against the current PR's review comments." | `gm/SKILL.md:19` | stops | The loop's own `gh` calls (rows 187–192) fail loudly if it is entered wrongly. |
| 249 | "**Either way, this is a revise verdict** … It drops nothing: every piece of feedback is acted on." | `gm/SKILL.md:21` | visible | For PR feedback: real — an unaddressed thread stays unresolved and is re-collected on the next run (`pr-feedback-workflow.md:146-148`). For `$ARGUMENTS` feedback: nothing at all, since the feedback exists only in the conversation. |

---

# The enforced set

145 rows (34 stops + 111 visible). They rest on four mechanisms and nothing else. Listed here by
mechanism so #2 can see what it has to work with — a rebuilt rule has to attach to one of these, or
invent a fifth. Groups A and B are exact and disjoint; C and D overlap, since many rows are read both
by the user on the PR and by a later `rn` step, so their sizes are given as the rows that cite them
rather than as a partition.

## A. The harness refuses the action (5 rows)

`disable-model-invocation: true` in each skill's frontmatter — rows 208, 212, 226, 237, 244. This is
the only place in the plugin where something other than the model decides. It is what makes the three
gates real: the assistant cannot issue `/rn:ty` or `/rn:gm` for the user (rows 21, 103).

## B. An external command fails (17 rows)

Rows 98, 99, 187, 188, 189, 192, 197, 198, 199, 214, 220, 223, 224, 228, 229, 232, 248. They sit almost
entirely in `pr-feedback-workflow.md` (7), `dn` (4) and `up` (3), with 2 in `planning-workflow.md` and
1 in `gm` — because those are the only files that actually run commands. `dn/SKILL.md:50-54` is the plugin's one self-verifying step: it re-runs
`git status --porcelain` to check step 6's own effect.

## C. The user reads it — a gate, or a message on their screen

Every `status-display.md` rule (142–154), every plan-gate and proposal rule (73–75, 77, 78, 81, 82, 101,
104), the verdict-integrity rules (12, 16, 17), the report rules (225, 242, 243, 247), and every rule
whose product is `steering.md` content the user reads on the PR (89, 100, 107, 115, 116, 119, 122).
Strength: the user is a genuinely independent reader. Limit: they see only what is put in front of
them, which is the plan, the design (if a gate exists), the acceptance run, and the PR diff.

## D. A later `rn` step consumes the artifact

The real consumers, each quoted at its row:

| Consumer | Quoted at | What it makes enforceable |
|---|---|---|
| `up/SKILL.md:26` — "A commit matches a task when its message contains `complete task #{id}`" | rows 36, 67, 68, 121, 196, 219, 232 | the completion marker and the prohibition on the substring elsewhere |
| `status-display.md:17-22` — "Derive the block fresh from the active `steering.md` … A task counts ✅ when `steering.md` records it complete" | rows 66, 69, 115, 140, 141, 146, 216, 233 | steering's check-offs, task ids, `Goal`, done annotations |
| `task-verify-workflow.md:139-146` — "Read the committed diff yourself … Confirm the change matches the task's scope" | rows 4, 29, 35, 38, 57, 58, 177, 179, 195 | anything that shows in a diff: scope, stray staged files, wholesale rewrites |
| `task-verify-workflow.md:215` — "Begin the next unchecked task" | rows 2, 66, 69, 236 | check-off state |
| `task-verify-workflow.md:219-222` — the "no Evaluation sign-off task was ever encountered … escalate" backstop | rows 15, 94 | the Evaluation sign-off task's existence |
| `dn/SKILL.md:15-16` and `up/SKILL.md:19` — rank by "`State` showing `Status: paused`" | rows 133, 134, 217, 234 | the `State` section's shape and reset |
| `migration-workflow.md:28-29` — "Read the session's `steering.md` `Design:` line; if it is absent … skip this step entirely" | rows 84, 87, 90, 114, 159 | the `Design:` pointer |
| `task-verify-workflow.md:83-84` / `:140-143` — the coordinator fills the review columns and expects only the check file uncommitted | rows 23, 24, 25, 32, 33, 34 | check-file column ownership |
| `pr-feedback-workflow.md:146-148` — "The loop treats GitHub's unresolved state as its **queue**" | rows 185, 186, 191, 200, 201, 203, 206, 249 | every PR-thread obligation; the only self-healing mechanism in `rn` |

Two of these consumers are demonstrably defective and should be treated as findings, not assets:

- **`up/SKILL.md:26`'s grep is a prefix test and matches prose.** `git log --all --grep='complete task
  #1' --oneline | wc -l` returns 16 in this repo, and 7 of those 16 are other tasks (`#1b`, `#10`,
  `#11`, `#12`, `#13`, `#14`, `#16`) matched on the prefix. Three commits (`4daf6b2`, `893de07`,
  `de0b1ec`) carry the substring in a body without being markers. The mechanism exists and produces
  wrong answers. In the other direction it can also find nothing: `git log --grep='complete task #1'`
  without `--all` returns 0 from this worktree's `HEAD`, past markers having been squash-merged.
- **`migration-workflow.md:46-48` names a consumer that does not exist.** It claims Phase: Complete
  gates on `Ready to check off` reading Yes; `task-verify-workflow.md:208-209` contains no such
  condition. Row 162 is enforced only in the text that asserts it.

---

# The unenforced set — the list #2 works from

**104 rows** where a breach leaves no trace anyone or anything reads. The eight groups below are a
partition — every "neither" row appears in exactly one group, and 26+13+9+13+11+10+15+7 = 104. They are
grouped by *why* nothing catches them, because the groups need different repairs.

## U1. The review chain's internals — 26 rows

Rows **5, 10, 11, 22, 27, 28, 30, 31, 37, 40, 46, 47, 48, 49, 51, 52, 53, 54, 55, 59, 62, 182, 183,
193, 194, 207.**

Every rule about *how* a review or a dispatch is produced: that a subagent was spawned at all, that it
carried no conversation history, that it was told to be adversarial, that it got the full artifact,
that the completion criteria were copied verbatim, that it was **not** shown the self-check or any
prior verdict (`task-verify-workflow.md:156-159` — the review-independence rule), that each expert
checklist was applied, that findings were triaged rather than dropped, that the 3-iteration cap held.
All of it lives in prompts that are never written to disk, so a review that never ran, a review that
ran primed, and a good review produce the same artifact.

This is the largest group and the most consequential: it contains every rule protecting the integrity
of the mechanism that is supposed to protect everything else.

## U2. Which reviews run at all — 13 rows

Rows **6, 7, 8, 9, 19, 20, 45, 92, 125, 126, 127, 128, 139.**

The mandated per-task reviews and the rules that place them. Empirically the worst-performing rules in
the plugin: a Verification section appears in 5 of 40 check files, Craft in 11, and
`20260705-improve-design-template` ran neither in any of its 7 tasks while closing approved.
`steering-template.md:67-71`'s Steps checklist would be a mechanism — an unchecked box is a visible
blank — but only for a step planning actually wrote, and **a step never written cannot be a blank.**
The failure is at authoring time, not execution time, and `planning-workflow.md:38`'s pre-persist
self-check covers only the Evaluation sign-off task. Row 139's "keep the two in sync" names no
mechanism and the two are provably out of sync.

## U3. How criteria are written — 9 rows

Rows **117, 118, 129, 130, 131, 132, 135, 136, 137.**

The ①/② phrasing, "the objective met, not that an output was produced", "no vague terms",
exhaustiveness, and the Granularity / Specificity / Objectivity rows of the `Task definition
requirements` table. This is the group this session's Goal names: the rule was correct, sat in the
template, and was broken in the very next session. One asymmetry to fix while rebuilding:
`steering-template.md:75-79` states the bar for **Completion** criteria only; `:41-43` states nothing
of the kind for **Acceptance** criteria — and the breach landed on the Acceptance criteria
(`.rn/20260705-improve-design-template/steering.md:22-49`, 9 of 10 written as artifact existence).

## U4. Everything about `design.md` — 13 rows

Rows **166, 167, 168, 170, 171, 172, 173, 174, 175, 176, 178, 180, 181.**

`design-template.md:4` says outright "**Not read at runtime**". The document has no consumer in the
flow: only a Design sign-off gate presents it, and that task exists only if planning placed one
(row 93, itself unenforced and absent from 7 of 8 sessions). The template's own contract —
"what does <mechanism> guarantee, and how is a breach caught?" (`design-template.md:68`) — is exactly
the question this inventory asks, and nothing checks that a `4.N` answers it truthfully.

## U5. Content allocation, doc division, and the migration judgement — 11 rows

Rows **88, 109, 110, 111, 112, 120, 123, 138, 157, 158, 160.**

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

## U7. Undetectable in principle — 15 rows

Rows **1, 3, 18, 39, 41, 43, 44, 64, 83, 85, 91, 95, 105, 145, 222.**

Not "nothing looks" but "there is nothing to look at": that a file was read (1, 85, 105), that a
judgement was made (44, 83, 91, 95), that an escalation *should* have fired and did not (18, 64), that
a status block was derived fresh rather than reused (145), that a starting SHA was captured once and
not re-captured (39, 43), and `dn/SKILL.md:44`'s "Never delete a file yourself" (222) — a deleted
untracked file leaves no residue in git, in `git status`, or anywhere else. **Adding a reader cannot
fix these; the rule has to be restated as something that produces an artifact, or dropped.**

Row **41** belongs here and deserves naming: "Read the committed diff yourself"
(`task-verify-workflow.md:139`) is `rn`'s single strongest mechanism — it backs nine rows in the
enforced set — and there is no trace of whether it happened.

## U8. Single cases — 7 rows

Rows **26, 80, 93, 102, 108, 162, 190.** Three worth naming:

- **Rows 26 and 162** — the check file's `## Overall Verdict` block, and `migration-workflow.md:46-48`'s
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

`rn` mandates thirteen steps per build task and five more per session, with no conditionality except
the task's medium and whether it touches structure/approach — **never its size**. For each: what it
catches that nothing else in the structure would, and whether it earns that on a small task.

## The four per-task reviews

| Step | Mandated at | What only this catches | Earns its cost on a small task? |
|---|---|---|---|
| **QA** (every build task) | `task-execute-workflow.md:18`, `:55`; `task-verify-workflow.md:147` | The only reviewer handed the task's Completion criteria verbatim (`task-verify-workflow.md:154-155`) and the only one judging whether the verification *approach* is meaningful rather than whether it passed — "no rubber-stamped or purpose-mismatched check" (`:162-163`). `task-execute-workflow.md:103` names it "the per-criterion gate": nothing else in `rn` reads criterion against artifact. | **Yes, at any size.** It is the only adversarial read of the criteria, and the criteria are the contract. Cheapest of the four to justify. |
| **Craft** (per medium) | `task-execute-workflow.md:21-22`; `task-verify-workflow.md:167-170` | The only reviewer looking at *how* the artifact is written rather than whether it is right: naming, error handling, duplication; prose clarity and "consistency with the doc's existing voice/terminology". Nothing else in the structure ever mentions style, and voice drift accumulates silently across a plugin whose entire product is prose. | **Not always.** On a rename, a version bump, or a one-line correction it returns wording nits — the past record bears this out ("round 1 found 2 valid Craft findings", `.rn/20260625-rn-lean/checks/12.md`). It earns its place on any task producing prose a user will read, and not on a mechanical edit. `rn` offers no way to say so. |
| **Verification** (per medium) | `task-execute-workflow.md:23-24`; `task-verify-workflow.md:171-175` | The distinction from QA is real and is this session's subject: **QA judges the approach, Verification judges the doing.** It is the only step asking whether every claim was actually checked against its source, whether tests are in GWT form and cover boundary/error/empty/max cases, whether the flow was traced step by step. A self-check can assert "verified"; only this step re-derives it. | **Yes on any claim-bearing or behavior-bearing artifact; near-worthless on a change already proven by a grep or a green test the coordinator can see in the diff.** The irony worth recording: it was dropped from 35 of 40 tasks, and the cases where it was dropped were mostly the second kind — which is why nobody missed it, and why nobody noticed when it was missing from the first kind either. |
| **Design** (conditional, structure/approach only) | `task-execute-workflow.md:19-20`, `:56-57`; `task-verify-workflow.md:164-166` | The only reviewer with a whole-system remit: "separation of concerns; system-wide integrity (interface contracts, API compatibility, cross-doc consistency)". Everything else in `rn` reviews one artifact against one task. **Its record is the best of the four**: when `task-execute-workflow.md` and `task-verify-workflow.md` were split apart, Design caught the duplication on the spot — `.rn/20260625-rn-lean/checks/12.md` records "Flagged the ~110-line shared-header duplication as a standing drift risk against the repo's own anti-duplication principle — noted, not actioned … an already-decided tradeoff". No other axis mentioned it. | **Already conditional, and correctly so.** The gap that case exposes is not the review but the *disposition*: the finding was accepted as a tradeoff, and that acceptance lives only in a check file nothing reads. 131 lines are still duplicated with no sync rule anywhere. **A review only earns its cost if the disposition of its findings lands somewhere durable** — which is U1's problem, not Design's. |

**The shared problem.** All four are dispatched as fresh subagents that must read the artifact from
scratch, so on a one-line change four subagents are the entire cost of the task. `rn`'s only
conditionality is medium and structure/approach; it has no notion of size, and no rule permitting a
reviewer to be skipped. The result in practice was not proportionality but silent omission — planning
simply stopped writing the steps. **A rule that cannot be skipped legitimately gets skipped
illegitimately**, and that is the mechanism-shaped lesson for #2: the fix for an over-mandated step is
a stated condition, not a firmer instruction.

## The other unconditional steps

| Step | Mandated at | What only this catches | Worth its cost? |
|---|---|---|---|
| Self-check | `task-execute-workflow.md:153-161` | The only per-criterion evidence written by whoever built the thing, and the only record of *how* the Method was applied (coverage figures, which claims were checked, where the flow was traced). | Yes as a **record**; weak as a **check** — it is written by the same agent that built the artifact, and 24 of 40 past files were left without a `Ready to check off` verdict with no consequence. Its value is entirely contingent on QA reading it, which `task-verify-workflow.md:156-159` forbids passing to the reviewer. |
| Coordinator reads the committed diff | `task-verify-workflow.md:139-146` | The only step that reads the actual artifact independently of anyone's account of it. Catches scope creep, stray staged files, a summary that does not match the diff, a regenerated file. It backs nine rows of the enforced set. | **Yes, always.** It is one `git show`, the cheapest step in the loop, and the most load-bearing. |
| Dispatch all deliverable work to the implementation expert | `task-execute-workflow.md:26` | Keeps the coordinator's context clear of build trial-and-error — a resource property, not a quality one. | Yes for context economy; it catches nothing, and nothing records whether it happened. |
| Capture the task's starting commit | `task-execute-workflow.md:175-176` | The only way `task-verify-workflow.md:144-145`'s cumulative diff spans multiple fix rounds. Without it, review sees the last round only. | Yes — free, and its loss silently narrows the one step that always earns its place. |
| Triage every finding to Valid/Invalid/Escalation | `task-verify-workflow.md:176-189` | The only step forcing a finding to a decision instead of a judgement call about whether to bother. The Invalid bar ("only when it rests on a factual error or falls outside a scope boundary written in the Completion criteria") is what stops findings being waved off. | Yes — it is the rule that makes the reviews consequential rather than advisory. |
| Record review verdicts into the check file | `task-verify-workflow.md:192` | The only durable trace that a review happened at all. Everything else about the review chain is prompt-only. | **Yes, and it is currently the weakest link that could most cheaply become the strongest** — it is the one artifact that could make U1's 26 unenforced rows visible. |
| Check off steering + the single completion marker | `task-verify-workflow.md:208-214` | The session's actual state. Feeds `up`'s resume, the status block, and "the next unchecked task". | Yes — this is `rn`'s state machine; without it a resumed session redoes or skips work. |
| Advance immediately, no per-task gate | `task-verify-workflow.md:215-217` | Keeps the user out of per-task decisions, which is the plugin's whole premise. | Yes; it costs nothing and is what the three-gate design buys. |
| Session-status block at every user stop | `status-display.md:3-5` | The only thing that tells the user where the session stands without opening `steering.md`. | Yes on a stop; it is the user's only continuous view, and the user is mechanism C. |
| Version check in all five skills | `on/SKILL.md:15` and siblings | In principle, drift between a session and the installed plugin. | **No, as built.** It has never fired: 6 of 8 sessions carry no stamp to compare, `on`'s copy is documented as unreachable, and the missing-line case is undefined. It is four lines of ceremony in five files. |
| Evaluation sign-off always last | `planning-workflow.md:37` | That the goal is confirmed met before the session closes — the only step that checks the Acceptance criteria at all. | Yes, and it is the one planning rule with a real backstop (`task-verify-workflow.md:219-222`). |
| Pre-persist self-check that the last task is Evaluation sign-off | `planning-workflow.md:38` | Would catch the omission at authoring time rather than at session end. | Yes in principle; unenforced in fact (row 95), and it covers only this one task — the Design sign-off, the review steps, and the criteria phrasing get no equivalent. **The cheapest generalization available to #2 is to widen this step, since it is already the right shape: a check at authoring time on the artifact planning just wrote.** |
| Draft PR with a single-link body | `planning-workflow.md:44` | Puts the plan in front of the user in rendered form and creates the session's one review surface, on which mechanism C depends entirely. | Yes — every "visible on breach" verdict in this inventory that names the user ultimately resolves to this PR. |
