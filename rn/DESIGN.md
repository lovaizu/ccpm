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
- **Step 3 puts resume context in `Notes`** — a suspend has to survive a new conversation and a
  context compaction; the next `/rn:up` resumes from `Notes` alone, so anything not written there is
  lost.
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
- **Steps 5–7 bound the gitignore retry per path and persist the marker in `Notes`** — `/rn:dn`
  exists to cross the context boundary, so the "retry a wrong rule at most once" bound must hold from
  persisted state, not agent memory; otherwise a compaction mid-suspend could let the verify loop
  re-fix the same path forever. Each path ends gitignored-away or recorded-deferred, so it terminates.
- **Step 6 makes one commit per pass and never force-pushes** — keeps the branch history clean and
  recoverable, reviewed by the user on the PR.
- **Step 7 reaches a terminal state, never wedges** — the user runs `/rn:dn` precisely to stop and
  leave; an unresolved path is recorded and the suspend completes rather than blocking on a departing
  user.
- **Step 8 reports the last push's status** — step 6 may run twice; a stale warning from an earlier
  pass would mislead the user about whether work is safe.

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
- **Decisions keep Rationale (judgment) separate from Evidence (facts) and Sources** — mixing
  reasoning with facts hides which part is opinion and which is verifiable.
- **State `Status` is `paused` only while suspended, else `not suspended`** — `paused` is the signal
  `/rn:up` and `/rn:dn` search for, so only a genuinely suspended session must read it.
