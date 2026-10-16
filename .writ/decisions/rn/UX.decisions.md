# rn's UX

## ux

### B-1: The users and their goals
- Whoever has Claude Code do work in a git repository on GitHub that takes days, and wants to spend
  their time deciding rather than watching: from their rough words, what they really wanted reaches
  them as a pull request ready to merge.

### B-2: The scenes to the goal
Before each work is made, the plan, the UX, the README, the design and each task's result, rn and
the user settle it the same way: rn goes down every point the work's checklists leave to decide,
those others rest on first, and confirms each with the user one point per message, with what it
looked up and the answer it recommends, the points it could look up included. What is settled goes
to turn as the decisions the work is made from.
1. The user starts with `/rn:up <what they want>`; the plan is settled so, made, and rn stops at the
   plan sign-off.
2. At each sign-off the user checks only that the work is as settled, and what changed while it was
   made; `/rn:ty` approves, `/rn:gm <feedback>` asks for a change they do not agree with.
3. The UX, the README and the design are settled and made the same way, and stop at the design
   sign-off.
4. rn carries out the tasks; the user does not watch, and is called only for a point only they can
   decide, settled the same way.
5. The finished product is used as the user would use it, and rn stops at the deliverable sign-off;
   on `/rn:ty` the pull request is marked ready, and the merge is the user's.
6. Wherever the user stops, `/rn:up` in a fresh conversation goes on from there.
