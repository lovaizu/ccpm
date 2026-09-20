# Evaluate

Has a result judged by someone other than its author, against a few named questions about whether
it does its job — not whether a step ran. Read by `/rn:on` (kind Plan) and by `task.md` (kinds
Design, Deliverable, Session).

## Steps

1. **Give the judgment to someone who did not build the thing, so the verdict is not colored by
   the builder's account.** Dispatch `Agent` with `model: opus` and no conversation history. Hand it
   exactly: the session Goal, the artifact (a path or a commit range), its kind, and that kind's
   questions below. Never the author's summary, never the verdict you expect.

2. **Ask only the questions for the artifact's kind, so the judgment is about the job the artifact
   has to do.**

   **Plan** (`steering.md`)
   - P1 — If every Acceptance criterion held, would the Goal be achieved — nothing missing, nothing
     extra?
   - P2 — Does each criterion survive a change of means — is it a state of the world, not an
     artifact or a step?
   - P3 — Can each task's Completion criteria be checked with evidence, and do the tasks together
     reach the Acceptance criteria?

   **Design** (an approach written before build)
   - D1 — Does the approach reach the Goal within the stated Assumptions and Rules?
   - D2 — Is the why recorded, so a later change can be judged against it?
   - D3 — What would break it, and is that named together with what catches it?

   **Deliverable** (one task's result)
   - E1 — Does it do what the task's Purpose says — judged on the thing itself, run or read, not on
     the record of steps?
   - E2 — Does each Completion criterion hold, with evidence a reader can check?
   - E3 — Is anything that worked before now broken?

   **Session** (the finished work, at "Evaluation sign-off")
   - Every Acceptance criterion in `steering.md`, OK or NG with grounds, on the real artifacts.

3. **Require one line per question and one overall verdict, so the caller can act without
   re-reading the artifact.** Each line: OK or NG, then the evidence. Then the overall verdict.

4. **Put the verdict where the user reviews, so it is read in rendered form and stays
   addressable.** `gh pr comment` on the session PR, headed by what was evaluated and the commit.
   With no PR (creation failed), report it in the conversation instead.

5. **Return the verdict to the caller, so this file reads the same on the first pass and the
   third.** Retrying and its three-round limit belong to `task.md`.
