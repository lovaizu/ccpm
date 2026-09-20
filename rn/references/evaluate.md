# Evaluate

Has a result judged by someone other than its author, against a few named questions about whether
it does its job — not whether a step ran. Read by `/rn:on` (kind Plan), by the migration in
`steering.md` (kind Plan with its Migration line), and by `task.md` (kinds Design, Deliverable,
Session).

## Steps

1. **Give the judgment to someone who did not build the thing, so the verdict is not colored by
   the builder's account.** Dispatch `Agent` with `model: opus` and no conversation history. Hand
   it what the questions need and nothing that answers them: the session Goal and Success
   criteria; for a task, its Objective and Success criteria; the artifact (a path or a commit
   range); its kind and that kind's questions below; a scratch directory outside the repository to
   work in, which it removes before returning. Never the author's summary, never the verdict you
   expect.

2. **Ask only the questions for the artifact's kind, so the judgment is about the job the artifact
   has to do.** Each level is judged against the one above it: Success criteria against the Goal, a
   task's Objective against the Goal, a task's Success criteria against its Objective.

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
     the old file present in the new one?

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

3. **Require one line per question and one overall verdict, so the caller can act without
   re-reading the artifact.** Each line: OK or NG, then the evidence. Then the overall verdict.

4. **Put the verdict where the user reviews, so it is read in rendered form and stays
   addressable.** `gh pr comment` on the session PR, headed by what was evaluated and the commit.
   With no PR, report it in the conversation instead.

5. **Return the verdict to the caller, so what follows an NG — a fix, a retry, a stop — is the
   caller's decision.** The retry and its limit live where this file is called from.
