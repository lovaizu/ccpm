# Where the work stands

turn was discarded whole and restarted from what its README promises, settled with the user one
point at a time. The user approved `turn/README.md` on 2026-10-11 (5392664 onward, last 9378fad).

Next:

1. Write `dev/turn/design.md` from the README, with `writ/references/essentials/doc.md` and
   `design.md` open, and `.claude/rules/plugin.md` §1 (simplest mechanism, no special paths).
2. Have it read once by a first user who does not know the discussion; settle findings at their
   root.
3. The user signs off the design; only then the prompts, scripts and tests, derived from it.

Agreed for the design (2026-10-11): its principles start from how the orchestrator uses the agents to bring the work to where the receiver can really use it. What the work
should be is written in the CCS by the plugin (receiver, acceptance, use, viewpoints); turn neither
makes nor changes it, and returns to the caller when it is not enough to judge by. The first user and the
learner only report what they did and what happened; the evaluator alone gives each point a Good or
More, laying it beside what the CCS says the work should be and checking it against the work and the
facts (conversation records, git), a Good as hard as a More, the learner's cause included. What is
fixed is the cause of a stumble, and the work is remade from it, never patched spot by spot; the
README says so (no "その場で直す"); the deliverable is called "deliverable" in English, kind `deliverable` included. The first user uses the work as the receiver would: it is told only
the work, who the receiver is and what they use it for, never the acceptance or the talk, and uses it
in a fresh-clone temporary copy, so that where it stumbles is where the receiver would. What is left after a turn is the returned CCS
and the work alone; the next turn starts from them, never from records or memory, and the CCS
received is never rewritten. These five are the design's principles.

Since 2026-10-11 the documents are written in English from the start, and the roles are named
orchestrator (turn's main conversation; calls the agents and passes on what they return, reads no
content), generator, first user, learner and evaluator (the only one that decides, checking each
report on the facts; split from the orchestrator so the orchestrator's conversation stays small).
`episodic_trace` kinds follow: `generator-1`, `first-user-1`, `learner-1`, `evaluator-1`. The README
needs the user's look again before the design sign-off.

Carry over: converse in plain everyday Japanese; never use 「得られること」「得るもの」 or "UX" as a
name or in conversation; one name per thing (the record is "CCS").
