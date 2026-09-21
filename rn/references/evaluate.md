# Evaluate

Has a result judged by someone other than its author, against a few named questions about whether
it does its job — not whether a step ran. Read by Judging the plan in `steering.md` (kind Plan) and
by `task.md` (kinds Design, Deliverable, Session). Steps 1, 4 and 5 are the caller's; 2 and 3 are
what the evaluator is asked to do.

## Steps

1. **Caller — give the judgment to someone who did not build the thing, so the verdict is not
   colored by the builder's account.** Dispatch `Agent` with `model: opus` and no conversation
   history — a fresh one every round, so the judge of a fix is never the author of the finding.
   Hand it, and only this:
   - `steering.md` in full — the Goal, Success criteria, Rules, Assumptions and tasks are the whole
     contract; a decision about scope that is not in it is not a decision;
   - which task, when the artifact is one task's result or design;
   - the artifact — a path or a commit range;
   - the kind and all of that kind's questions below, every round;
   - a scratch directory outside the repository to work in, which it removes before returning,
     leaving the repository's working tree as it found it;
   - a verdict file — a path outside the repository where it writes its verdict, the same text
     it returns, so the caller can pass it on without retyping a word;
   - the language to answer in — the one `steering.md` is written in.

   Never the author's account, never what to excuse or where not to look, never an earlier
   verdict or what was fixed since; earlier evaluations on the PR are not evidence either — the
   evaluator judges the thing itself.

2. **Evaluator — answer only the questions for the artifact's kind, so the judgment is about the
   job the artifact has to do.** Each level is judged against the one above it: Success criteria
   against the Goal, a task's Objective against the Goal, a task's Success criteria against its
   Objective. Run or read the thing itself; a report of it is not evidence.

   **Plan** (`steering.md`)
   - P1 — If every Success criterion held, would the Goal be achieved — nothing missing, nothing
     extra?
   - P2 — Does each task's Objective serve a Success criterion, and do the tasks together, in the
     order their Prerequisites allow, reach all of them?
   - P3 — If a task's Success criteria held, would its Objective be achieved, and can each be
     checked with evidence?
   - P4 — Does every criterion, at both levels, survive a change of means — is it a state of the
     world, not an artifact or a step?
   - P5 — Is each Assumption a checked fact or a named assumption, and is none of them work still
     to do or a decision not yet made?
   - Migration (a migrated plan only) — Is every task, check-off, `State` fact and pending item of
     the old file present in the new one? The migration's own rule says what changes by design
     and is not a loss: unchecked steps that only ran the old `rn`'s review and its process files
     are dropped, and a check-off the commit log proves is added.

   **Design** (the approach, written before build)
   - D1 — Does it reach the Goal — can each Success criterion be traced to the part of the design
     that produces it?
   - D2 — Does every part earn its place — for each, what fails if it is removed? Nothing is there
     without a reason.
   - D3 — Where a choice existed, is it made, with its why recorded against the Goal — nothing left
     for the builder to guess, and a later change can be judged against it?

   **Deliverable** (one task's result)
   - E1 — Is the task's Objective achieved — judged on the thing itself, run or read, with each
     Success criterion holding on evidence a reader can check?
   - E2 — Is there nothing beyond the Objective — no added scope, no residue, nothing done "in
     case"?
   - E3 — Is the whole still sound — what worked before still works, and what was touched reads as
     one piece with what was there?

   **Session** (the finished work, at "Evaluation sign-off")
   - S1 — Does every Success criterion hold on the real artifacts, with evidence?
   - S2 — Read the Goal as the user wrote it: is it achieved — or did the criteria miss something
     the work exposed?
   - S3 — Has the session left only `steering.md` and the deliverable — in the tree and outside it?

3. **Evaluator — return one line per question and one overall verdict, so the caller can act
   without re-reading the artifact.** Each line: OK or NG, then the evidence. Then the overall
   verdict. Written to the verdict file, headed `## Evaluation — {kind}[ — task #N] — {short
   commit}`, and returned as the final message.

4. **Caller — put every round's verdict where the user reviews, so it is read in rendered form,
   as returned, and stays addressable.** A line without evidence is not a verdict: send it back
   before anything else. Then post the verdict file itself — `gh pr comment --body-file` on the
   session PR — and read the posted comment back against the file before going on; then remove
   the file. Every round is posted, an NG as much as an OK, and never retyped — the user reads the
   verdict, not the conductor's paraphrase of it. With no PR, print the file in full in the
   conversation instead.

5. **Caller — act on the verdict; what follows an NG — a fix, a retry, a stop — is the caller's
   decision, and so is its limit.** Wherever a gate is then presented, `State`'s `Pending` names
   the commit this verdict judged and where the verdict is, so a later conversation knows what
   was judged.
