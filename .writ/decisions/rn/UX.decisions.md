# rn's UX

## ux

### B-1: The users and their goals
- G1: Whoever wants to hand a whole piece of work to an agent: they ask for it without preparing
  anything and only answer what they are asked, and their purpose is achieved.

### B-2 (key results)
They stand from the highest priority: the user's time is never saved by a deliverable that misses
their purpose, since what is sent back then is made again after all of it is built.
- KR1.1: The points the user sends back at the deliverable sign-off; fewer is better, and none once
  the goal is reached.
  At the plan and design sign-offs the user decides; a point sent back at the deliverable is where
  the finished work misses the purpose they agreed, and it is made again after all is built.
- KR1.2: The time the user spends from asking to their purpose achieved: answering, checking at the
  sign-offs, sending back and doing anything by hand; shorter is better, and once the goal is
  reached only answering what the user alone can decide is left.
  The goal is asking without preparing and only answering; every other minute is the user's work.

### B-2: The scenes to the goal
1. The user starts with `/rn:up <what they want>`. rn confirms each point to decide, one per
   message, with what it looked up and the answer it recommends, the points it could look up
   included, since a point decided unasked is made again when it is wrong. Each message shows the
   points to decide, the settled ones with their outcome and the current one marked; for the
   current one, the conclusion, its grounds, and the options, the recommended one first, each with
   its trade-off and whether it can be undone; and one question on that point alone, answered by
   the option's letter or in the user's own words. Answers to the user's questions and what rn
   fixed on its own come first, apart from the points. The goal and the
   acceptance criteria, each with an ID, go into the plan, which rn puts on a draft pull request
   of its own branch, and rn stops at the plan sign-off.
2. At a sign-off the user reads the proposal and answers `/rn:ty` to approve or
   `/rn:gm <feedback>` to ask for a change. On `/rn:gm`, rn keeps the feedback and stops, so the
   conversation can be cleared; going on, it finds the point behind the words that it took wrong
   or did not ask, confirms it the same way, makes the work again, and stops at the same sign-off
   with what changed since the last proposal.
3. The documents the purpose needs, such as the UX, the README and the design, are settled and made
   the same way, and rn stops at the design sign-off.
4. rn carries out tasks, each naming the acceptance criteria it serves and checked against them;
   the user does not watch, and is called only for a point only they can decide, confirmed the same
   way.
5. The finished work is used as the user would use it, for each acceptance criterion, and rn stops
   at the deliverable sign-off; on `/rn:ty`, rn confirms, one point at a time, what the session
   learned that would make later work better, each with what happened and the addition to the
   user's checklists it recommends, and whether a fault of rn's own goes to rn as an issue; the
   additions the user takes go into the same pull request. Then the pull request is marked ready,
   and the merge is the user's.
6. Wherever the user stops, `/rn:up` in a fresh conversation goes on from there.

Each work is made with rn's checklist for its kind and the user's addition to it, at
`.rn/checklists/<kind>.md` in their repository, which holds only what it adds; a kind rn has no
checklist for gets one made there. rn's own checklists are not changed in place, since they sit
outside git on the user's machine and an update of rn replaces them.

### B-3: The benefits
- The user asks without preparing: rough words are enough, and rn finds the points to decide and
  comes to confirm them.
- The user's purpose is achieved by answering alone: each point is confirmed and each task traced
  to the acceptance criteria, so making a finished work again becomes rare.
- At each sign-off the user decides from the proposal alone: what they are shown has been read and
  used in its receiver's place by an AI that did not make it, so they need not read it all again.
- Work that takes days goes on from wherever the user stopped.
- What was decided, and why, stays: the README and the design in the product, and what the
  documents do not keep, the options weighed with their reasons and each feedback with its answer,
  in the commit messages rn writes, so the next work, or a teammate, starts from it.
- What a session learned is confirmed with the user one point at a time, and what they add to their
  checklists makes every later work better.
