# Evaluate

Judges a result against a few named questions, by someone other than its author. Read by `on`
(kind Plan) and `task.md` (kind Design / Deliverable / Session).

## Steps

1. **Launch a subagent with no memory of how the artifact was built, so the verdict isn't colored
   by the author's account.** Dispatch `Agent` with no `model` override, so it runs on the
   conversation's own model. Give it exactly: the session Goal, the artifact (a path or a commit
   range), its kind, and that kind's questions below. Never give it the author's summary or an
   expected verdict.

2. **Ask only the fixed questions for the artifact's kind.**

   **Plan** (`steering.md`):
   - P1 — If every Acceptance criterion held, would the Goal be achieved — nothing missing, nothing
     extra?
   - P2 — Does each criterion survive a change of means — is it a state of the world, not an
     artifact or a step?
   - P3 — Can each task's Completion criteria be checked by evidence, and do the tasks together
     reach the Acceptance criteria?

   **Design** (an approach written before build):
   - D1 — Does the approach reach the Goal within the stated Assumptions and Rules?
   - D2 — Is the why recorded, so a later change can be judged against it?
   - D3 — What would break it, and is that named together with what catches it?

   **Deliverable** (one task's result):
   - E1 — Does it do what the task's Purpose says — judged on the thing itself (run it, read it),
     not the record of steps?
   - E2 — Does each Completion criterion hold, with evidence a reader can check?
   - E3 — Is anything that worked before now broken?

   **Session** (the last task, on the real artifacts):
   - Every Acceptance criterion, OK/NG with grounds.

3. **Require one line per question plus one overall verdict, so the caller can act without
   re-reading the artifact.** OK/NG with the evidence for each question, then a single overall
   verdict.

4. **Post the verdict where the user reviews, not into the conversation.** `gh pr comment` on the
   session PR, headed by what was evaluated and the commit.

5. **Leave the retry decision to the caller, so this file stays the same whether it's the first pass
   or the third.** This file only produces the verdict; the NG-fix cycle and its 3-round cap live in
   `task.md`, which invoked it.
