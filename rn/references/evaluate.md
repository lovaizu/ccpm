# Evaluate

Has a result judged by someone other than its author, against a few named questions about whether
it does its job — not whether a step ran. Read by Judging the plan in `steering.md` (kind Plan) and
by `task.md` (kinds Design, Deliverable, Session). What follows an NG — a fix, a retry, a stop —
and its limit are the caller's; a stop at the limit shows the last verdict, and the count starts
again from the user's answer.

Every round's verdict is a file in the session's own directory,
`.rn/{yyyymmdd}-{slug}/evaluations/{NN}-{kind}[-task-{N}].md`, where `{NN}` is the next unused
number there — `01-plan.md`, `02-plan.md` for its re-judge, `03-design-task-2.md`, and so on. The
file is committed and pushed, so the user reads every round rendered on the PR beside the diff it
judged, an NG as much as an OK, and a round closes on a commit rather than on anything posted. The
directory is removed when "Evaluation sign-off" is approved, so the session still leaves only
`steering.md` and the deliverable.

## Steps

1. **Caller — put the round on record before it starts, so a conversation that ends mid-round
   leaves a verdict to find, not a stale one to trust.** Work out the verdict file's path by the
   rule above. Write in `State`'s `Pending` what is being judged, the commit it stands at (`HEAD`
   before this record commit), and that path; commit and push. A round's entry is closed only by
   the commit of its written verdict, never by the next round — an unfinished round stays on record
   until step 5 closes it.

2. **Caller — give the judgment to someone who did not build the thing, so the verdict is not
   colored by the builder's account.** Dispatch `Agent` with `model: opus` and no conversation
   history — a fresh one every round, so the judge of a fix is never the author of the finding.
   Hand it this and nothing else — not the builder's account, not what to excuse, not an earlier
   verdict:
   - `steering.md` in full — the whole contract, scope decisions included;
   - which task, when the artifact is one task's result or design;
   - the artifact — a path or a commit range — and that it is the only thing to read;
   - the kind and all of that kind's questions below, every round;
   - a scratch directory outside the repository to work in, removed before it returns, so the only
     thing it leaves behind is the verdict file;
   - the verdict file's path, where it writes the verdict it returns, so the caller can commit it
     without retyping a word;
   - the language to answer in — the one `steering.md` is written in.

3. **Evaluator — answer only the questions for the artifact's kind, so the judgment is about the
   job the artifact has to do.** Each level is judged against the one above it: Success criteria
   against the Goal, a task's Objective against the Goal, a task's Success criteria against its
   Objective. Run or read the thing itself.

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
     the old file present in the new one? By design, and not a loss: unchecked steps that only ran
     the old `rn`'s own review and its process files are dropped, and a check-off the commit log
     proves is added.

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
   - S3 — Has the session left only `steering.md`, its `evaluations/` and the deliverable — in the
     tree and outside it?

4. **Evaluator — return one line per question and one overall verdict, so the caller can act
   without re-reading the artifact.** Each line: OK or NG, then the evidence. Then the overall
   verdict. Written to the verdict file, headed `# Evaluation — {kind}[ — task #N] — {short
   commit}`, and returned as the final message.

5. **Caller — commit the verdict as the evaluator wrote it, so the user reads it rendered next to
   what it judged and it stays addressable.** A line without evidence is not a verdict: send it
   back first. Then compare the file to what was returned, commit it alone as
   `docs: evaluation {NN} — {kind}[ — task #N] — {OK|NG}`, push, and write that commit into the
   round's `Pending` entry as where the verdict is. The file stays until the session closes.
