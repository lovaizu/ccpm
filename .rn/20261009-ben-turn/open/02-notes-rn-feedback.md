# Feedback for rn: hold the ideal before acting

## Problem

Work on ben and turn kept turning into patches. Redoing it did not bring the documents closer to
what they should be, and tokens ran out on it. In one session (2026-10-10) the conductor:

- asked the user to approve an outline that the purpose already settled;
- took every "not written" in the first users' reports as something to add, and so wrote
  specifications into the designs (a hook runs the check, result headings, the scene file format,
  how time is counted);
- wrote a guess as fact ("an agent cannot call another agent"; the official docs say it can, three
  layers deep);
- ran the first users four times, fixing between runs.

The user judged the result unusable, since work done the wrong way hides traps, and it was reverted
to c0d8098 (6d00fdb).

Root cause: the conductor held no picture of what the deliverable should be as its own measure, and
treated whatever arrived (an instruction, a report, a remark) as items to clear. Clearing items looks
like progress, but nothing asked whether the deliverable came closer to what it should be. A
procedure added to stop this comes from the same root and is one more patch.

## Hypothesis

Before any work on a deliverable, the conductor defines what it should be, and judges every input
against that, doing only what brings the deliverable closer:

- In the README, who gets what (the benefits) is defined first. They are the ideal, and they agree
  with the plan's attractive quality.
- In the design, the principles are defined next: what must always hold for each benefit to reach the
  user, and why.
- Usage, features and record forms are derived from these. A sentence that traces to neither a
  decision nor the purpose is left to the implementation if a principle settles it, and goes to the
  user if it needs a new decision.
- A first user reads each document once. Each finding is judged against the document's aim: missing
  the aim means fixing the decision or principle it comes from; what a principle settles is not
  fixed.

For rn: the conductor's first move on a deliverable is to state its ideal from the README's benefits,
and every later judgment is made against it.

## Result

Not yet: ben and turn are to be redone this way, starting with the README benefits checked against
A1 to A3 and the user's decisions gathered from the conversation records. What to look at: whether
the documents come closer to A1 to A3 without patches, how many times first users had to read, and
whether the designs hold no specification.
