Serves: A2, A3, M8

This session and the split-pith session (PR #40, now at its design stage) both change how rn checks
its work: PR #40 moves rn's first user and its checks into a new plugin, pith, and this session
changes what those checks return to you (#46), how rn waits for them (#44), and when it calls `writ`
(#39). Built side by side, one would be built again on top of the other. Which should go first?

- This session first (recommended): rn becomes usable sooner, and PR #40 is carried on with an rn
  that no longer has these faults; PR #40 meanwhile pauses, and redoes its rn part on the result.
  It costs PR #40 the rn part of its design, which is not yet written.
- PR #40 first: rn's checks are rebuilt only once, already on pith; this session waits until PR #40
  is merged, while PR #40 runs on rn as it is today, with these faults.
- One session for both: nothing is built twice, but the session grows to two goals and is the
  slowest to give you anything.
