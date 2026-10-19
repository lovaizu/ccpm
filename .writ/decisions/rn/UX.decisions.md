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
   included, since a point decided unasked is made again when it is wrong. The goal and the
   acceptance criteria, each with an ID, go into the plan, and rn stops at the plan sign-off.
2. At a sign-off the user reads the proposal and answers `/rn:ty` to approve or
   `/rn:gm <feedback>` to ask for a change.
3. The documents the purpose needs, such as the UX, the README and the design, are settled and made
   the same way, and rn stops at the design sign-off.
4. rn carries out tasks, each naming the acceptance criteria it serves and checked against them;
   the user does not watch, and is called only for a point only they can decide, confirmed the same
   way.
5. The finished work is used as the user would use it, for each acceptance criterion, and rn stops
   at the deliverable sign-off; on `/rn:ty` the pull request is marked ready, and the merge is the
   user's.
6. Wherever the user stops, `/rn:up` in a fresh conversation goes on from there.

### B-3: The benefits
- What the user gets is what they really wanted, not what their first words said, and going back
  over finished work becomes far rarer, since every point is settled with them before a work is
  made.
- Each work reaches the user only after it has been read and used in its receiver's place.
- At each sign-off the user checks only that the work is as settled and what changed while it was
  made, without reading it all again.
- Work that takes days goes on from wherever the user stopped.
- What was decided, and why, stays: the README and the design in the product, each decision and
  what became of each finding in the record and the commits, so the next work, or a teammate,
  starts from it.
- What a session learned is put to the user one point at a time, and what they add to their
  checklists makes every later work better.
