# rn — design notes

The intent behind the rn procedures. **Not read at runtime** — the skill and reference files are pure
procedure; this file is for whoever maintains them and needs to judge whether a step is still right
when requirements change. One note per step or decision, keyed to the procedure it explains.

## on (`/rn:on` — start)

- **Every user touchpoint is a proposal (one recommended option, plain language)** — because a
  one-click confirmation costs the user less than an open-ended question that makes them do the
  framing.
- **Step 1 restates the goal as faithful intent, no added scope** — because the restatement is the
  contract the user approves in PR review; inventing scope makes them approve work they never asked
  for.
- **Step 2 derives the slug from branch / issue / goal, reusing the branch name** — because the
  situation already names the work, and aligning slug with the PR branch keeps them from drifting.
- **Step 3 reads the template before filling** — because the template is the source of per-section
  structure; filling from memory drifts from it.
- **Step 4 decomposes by working backward from the acceptance criteria** — because starting from the
  end state yields tasks that provably reach it, not a forward guess that may miss.
- **Step 5's PR body is a single steering link, never duplicated plan content** — because the plan
  lives in steering.md; copying it into the body only drifts, and a branch-ref blob link tracks the
  latest plan through review.
- **Step 5 uses a draft PR as the review surface, with an approval gate** — because the steering is
  too long to review in the console; the PR renders it, later tasks add commits to it, and executing
  before approval risks building the wrong thing.
- **Step 6 reads task-workflow.md before executing task #1** — because that reference defines how a
  task is run, keeping execution consistent with the rest of rn.

## dn (`/rn:dn` — suspend)

- **Step 1 fallback searches commit history** — a suspend may run in a fresh conversation that never
  saw the path; the `Status: paused` marker distinguishes a suspended session from a finished one.
- **Step 3 caps `Notes` to a bounded forward pointer** — a suspend has to survive a new conversation
  and a context compaction, and `/rn:up` resumes from `Notes` alone, so it must hold what a resume
  needs: branch/PR, next concrete action, open blockers, user-deferred paths. But the per-resume cost
  is the *narrative* `dn` re-writes each cycle, which `git log` already holds; capping `Notes` to the
  forward pointer keeps the resume working while stopping per-resume bloat from returning.
- **Step 4 forbids `complete task #` in the message** — that exact substring is the single
  task-completion marker `/rn:up` matches in `git log`; a suspend is not a completion. (`wip:` flags
  an unfinished task for the reader.)
- **Step 5 never deletes an untracked file** — a misclassified delete destroys user work
  irreversibly; gitignore is reversible and enough to get the tree clean, so deletion is only ever the
  user's explicit choice.
- **Step 5 gitignores recurring artifacts instead of removing them** — a rule hides the path from
  `git status` and stops it re-dirtying the tree on a later run, without touching the file.
- **Step 5 records the literal `git status --porcelain` string** — step 7 matches a remaining path
  against `Notes`; a paraphrase would not match.
- **Step 6 makes one commit and never force-pushes** — keeps the branch history clean and
  recoverable, reviewed by the user on the PR.
- **Step 7 is a single forward pass, never a retry loop** — `/rn:dn` exists to cross the context
  boundary and let the user leave, so the verify step must terminate unconditionally. A retry that
  re-fixes a just-written gitignore rule was dropped: step 5 has no guidance to write a *better* rule
  the second time, so a retry falls through to "record as deferred" anyway — identical to one pass,
  minus the correction-marker bookkeeping. Any path still present is recorded user-deferred and the
  suspend completes; it never wedges on a departing user.
- **Step 8 reports the push's status** — a failed push must be surfaced so the user knows the commits
  are local-only and whether work is safe.

## up (`/rn:up` — resume)

- **Step 1 waits for confirmation before touching a dirty tree** — the user's uncommitted work may be
  intentional; a resume must not silently destroy or commit it.
- **Step 2 keeps only paths that still exist on disk, ranking `Status: paused` above recency** — git
  history lists steering.md files that may since have moved or been deleted; the paused one is the
  session a resume is meant to pick up, and recency is only the tiebreaker.
- **Step 3 reads `State`** — `State` is the handoff record `/rn:dn` wrote so `/rn:up` can resume
  without the original conversation.
- **Step 4 matches commits by `complete task #{id}`** — the commit log is the source of truth for
  what is actually done versus what the file claims.
- **Step 5 adapts the approach rather than dropping a blocked task** — the goal is fixed; a blocker
  changes the means, not the objective.
- **Step 6 retires shipped decisions, then resets `State`** — steering is a forward contract for the
  remaining work, not the session's archive. A decision whose every `Governs` task is checked off and
  shipped is no longer needed to finish, and its "why" is preserved in the recording commit + PR, so
  retiring it on ship loses nothing while stopping `Decisions` from accumulating shipped-work
  decisions across repeated `/rn:up`/`/rn:dn` cycles. The `Governs` field makes retirement a
  mechanical check (structure, not a remembered rule); a `Governs: —` decision is cross-cutting and
  kept for the session's life. A decision with no `Governs` field (written before the field existed)
  defaults to keep for back-compat, since retiring it would lose it from the live file.
- **Step 6 collapses a shipped task to a one-line `SHIPPED` pointer, rather than deleting it** —
  `Tasks` is the largest section, and once a task ships its full Steps / Completion criteria are dead
  weight that `/rn:up`/`/rn:dn` would otherwise carry across every cycle. A shipped decision is
  *deleted* because it is pure rationale, fully recoverable from the recording commit + PR; a shipped
  task is *collapsed*, not deleted, because the `Tasks` section is a map other tasks index into —
  numbering must stay stable so a later `Prerequisites: #N` still resolves, and a resuming agent needs
  an at-a-glance sense of what is already done. The one-liner keeps both (the number and a name) while
  the body, recoverable from the `complete task #{id}` commit it cites, is dropped. The trigger reuses
  Lever A's two-part shipped test (box checked AND marker in `git log`) so collapse and decision-retire
  run off one mechanical check in the same reconcile pass.
- **Step 6 resets `State` to the placeholder and commits** — once reconciled, the stale resume state
  is consumed; clearing it stops a later resume acting on outdated notes.
- **Step 7 executes via task-workflow.md** — `/rn:up` only restores position; the actual execution
  defers to the canonical workflow so behavior matches a normal run.

## task-workflow (the per-task execution loop)

- **Coordinator never touches the deliverable or its git history; writes directly only steering.md and
  checks/{task-id}.md** — the split line is "does it carry exploration or trial-and-error," not "does
  it write to the repo." Keeping an expert's trial-and-error inside the subagent keeps the
  coordinator's context light; steering.md and recorded verdicts carry no trial-and-error to isolate.
- **Coordinator stays on as reviewer rather than fully delegating** — that keeps a place for the user
  to step in at every task boundary.
- **One task = one completion marker, on the post-approval check-off commit** — deliverable commits
  accumulate freely, so pinning the single `complete task #{id}` substring to the check-off commit
  guarantees exactly one marker per task for `/rn:up` to reconcile against `git log`.
- **Work-order carries everything the expert needs and only that** — the expert has no conversation
  history.
- **Method: write the test first (code)** — the work is a hypothesis; it is not done until its tests
  pass.
- **Never `git add -A`/`.` when staging the deliverable** — it would sweep the check-file ledger into
  a plain deliverable commit and break "the check file is the coordinator's ledger."
- **cannot-push / cannot-commit fallbacks are git mechanics only** — subagent commit/push is verified
  available, so these are last-resort paths for capability-less environments; the content always stays
  the expert's, never authored, amended, or regenerated by the coordinator.
- **Return only a compact summary** — the diff is on disk for the coordinator to read; only the
  summary should enter the coordinator's context.
- **Capture the starting commit once, never re-capture on fix rounds** — it stays anchored at the
  task's original start so `git diff <start>..HEAD` keeps spanning every round's commits.
- **Coordinator reads the committed diff itself** — its own look at the artifact, independent of the
  expert's account.
- **Review experts are independent subagents with neutral framing; never pass the self-check file,
  expert summary, or your own verdict** — independence is the safeguard against bias; passing the
  Completion criteria verbatim is required and is not leading, but your assessment of whether they are
  met is withheld so the evidence decides.
- **Triage against the proper-form bar: Valid → implementation expert; Invalid → cite; User's call
  only when genuinely theirs** — the artifact has a proper form (correct, clear, consistent) the
  coordinator can judge against; don't swallow feedback wholesale, and don't bounce a decidable call
  for lack of a standard. "It's minor, so I'll just ask" is not a reason. Every deliverable-touching
  fix is the expert's because every line and its history is the expert's.
- **Re-run the originating expert plus any dimension a fix could regress; cap at 3 iterations** — a
  fix can reshape a dimension another expert already cleared; the cap bounds rework, then escalates
  unresolved NGs to user review.
- **User review on the PR; do not proceed without approval** — the PR renders diffs and long documents
  properly, and the gate keeps the user in the loop at every task boundary.
- **Check-file column ownership is disjoint, committed by the coordinator** — the expert never
  touching the review-verdict sections means a re-dispatched expert on a fix round cannot clobber
  verdicts the coordinator already recorded.

## steering-template (the steering.md structure + fill rules)

- **Copy the template block verbatim; keep the blank lines between fields** — `/rn:on` copies it
  as-is, and without the blank lines Markdown collapses `Purpose` / `Prerequisites` / `Steps` /
  `Completion criteria` onto one line.
- **Acceptance criteria written exhaustively, never sampled, across goal alignment and quality** — the
  complete set defines scope (in/out); a result can meet the goal yet be low-quality or vice versa, so
  both axes must be judged.
- **Assumptions separate facts from assumptions and flag unverified ones** — an assumption that proves
  false changes the plan, so the reader must know which statements are load-bearing guesses.
- **Tasks are flat (#1, #2, …), no phases or phase-level gates** — each task's own verify steps (QA /
  expert / user review) are its gate; phase grouping only duplicates that.
- **Completion criteria state outcomes/end-state only, third-party verifiable, no vague terms** — a
  criterion naming an action/review/gate or using words like "appropriate"/"correct" cannot be checked
  independently; actions/reviews/gates live in Steps as `- [ ]` so their status stays trackable.
- **Completion criteria are framed as two questions a third party answers with grounds, not that an
  output was produced** — "outcomes/end-state only" was being read as "the artifact exists" (e.g.
  "DESIGN.md exists"), which passes while the goal is unmet. Each criterion must let a third party
  answer two questions: ① is the objective achieved? (the objective met, not the output produced — a
  contrast example pins this down: "the residue no longer keeps the tree dirty", not "the file
  exists"; this subsumes the intended behavior being observably present) and ② are new problems
  absent? (the representative failure modes named and required absent). Two questions beat the earlier
  three lenses because they pair confirmation with falsification — a tighter frame that is harder to
  game than a checklist of three positive lenses, since ② actively hunts for what the change broke.
  The grounds are mandatory because they turn an assertion ("the behavior occurs") into a checkable
  claim (the evidence that shows it occurs). Crucially the grounds live in the verification — the
  `checks/{task-id}.md` Evidence columns recorded at self-check and review — not in the criterion
  text; writing the grounds into the criterion would smuggle a means (how it is checked) into a bar
  that should state only the end (means-vs-end anti-pattern). This keeps the criteria a real review
  bar consistent with `task-workflow`'s use of them, while retaining the three existing constraints
  (third-party verifiable, no vague terms, end-state not actions).
- **Decisions keep Rationale (judgment) separate from Evidence (facts) and Sources** — mixing
  reasoning with facts hides which part is opinion and which is verifiable.
- **`Decisions` is a live working set with a `Governs` field, and `State → Notes` is a forward
  pointer** — the structure itself encodes the non-accumulation property: `Governs` ties each decision
  to the tasks it serves so `/rn:up` can retire it once they ship, and a `Notes` capped to the forward
  pointer keeps `git log` as the narrative. Putting both in the template means a writer meets the rule
  by filling the structure, not by remembering a convention.
- **`Tasks` carries the same non-accumulation note: a shipped task collapses to a one-line `SHIPPED`
  pointer** — the parenthetical on the `Tasks` section documents that `/rn:up` replaces a shipped
  task's whole block with `### #N: … — SHIPPED (#N in <sha>)`, parallel to the Decisions/Notes note,
  so the encoding lives where the writer reads it. The note states the number is preserved because the
  section is a map other tasks reference by `#N`; that is the structural reason a task collapses where
  a decision deletes.
- **State `Status` is `paused` only while suspended, else `not suspended`** — `paused` is the signal
  `/rn:up` and `/rn:dn` search for, so only a genuinely suspended session must read it.
