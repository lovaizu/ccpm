# Where the work stands

turn was discarded whole and restarted from what its README promises, settled with the user one
point at a time. The user approved `turn/README.md` on 2026-10-11 (5392664 onward, last 9378fad).

Next:

1. Done: `dev/turn/design.md` written from the README with the essentials open, and read once by a
   first user (2026-10-11); its findings settled at their root.
2. Done: the user looked at the README and signed off the design (2026-10-11).
3. After sign-off: task #6, the prompts, scripts and tests, derived from the design; prompts through
   writ's `prompt.md` before any trial. `dev/turn/README.md` is written once tests and trials exist.
   In progress (2026-10-11): built test-first from here on (rule added): scripts `check.py`,
   `tryout.py`, `trace.py`, `assemble.py` with tests (CI 100%); prompts `skills/up/SKILL.md` and
   `agents/{generator,first-user,learner,evaluator}.md`; a trial plugin and fixture in
   `dev/turn/trials/`. One full trial ran (scratchpad trial-1): the flow worked and returned
   `ask the user`, then a contradiction between the example's acceptance ("without asking anyone")
   and asking Sato for the token; the receiver run passed. b564b05 patched the prompts from that
   trial before the way of checking was settled.
   Stopped there. The user asked what checking turn should look like. Proposed ideal, not yet
   agreed: each quality is checked where it is decided, as cheaply as shows it: scripts by unit
   tests; the orchestrator's flow with mock agents over every branch; each agent's prompt alone
   with set inputs (`prompt.md`); the README's promises by one real trial at the end.
   Decided by the user (2026-10-11): checking in four levels; design section 4 now has the prompt
   checks and the orchestrator's flow with stand-in agents, before the trials.
   Decided by the user (2026-10-11): only b564b05 is taken back; scripts, prompts and the trial
   plugin stay, and the prompts go through the new checks.
   Decided by the user (2026-10-11): the README has no console example (one call, CCS in and out).
   A lacking viewpoint is added where it is missing, in any plugin: writ's prompt.md now asks how
   the AI gets from a problem to what it changes (#53 notes it); turn's prompts were read against
   it and the evaluator's rule now holds wherever the cause acts.
   Done (2026-10-11, afe0d15): each agent's prompt run alone with prompt.md (runs kept in the
   session scratchpad, not in the repository). The evaluator now decides from the records; the
   generator marks what is not known where it is needed. Let go, as the loop catches them: the
   generator naming a stand-in beside "not known yet", its claims of checks it did not run, the
   learner adding advice, the first user testing error lines beyond the guide, and a remake whose
   edit failed going to the caller.
   Done (2026-10-11): README's CCS example says "following the guide alone".
   Done (2026-10-11): the orchestrator's flow with stand-in agents (`dev/turn/trials/flow.py`), all
   five ways a round can end gave the expected `next`, agents, no commit, no copy left, the CCS
   received unchanged, the acceptance never told to the first user. Every run fumbled reading the
   CCS by hand; decided by the user (2026-10-11): the steps that need no judgment are one script,
   `turn/scripts/up.py` (start, copy, round, end), so the orchestrator only calls the agents and
   that script. Rerun on all five: as expected, and the orchestrator ran nothing but up.py.
   Decided by the user (2026-10-11): no made-up trial. turn is checked by making pith, writ and rn
   through it, one at a time; the user starts a session for each and this session sends it the
   work and decides turn's fixes from the records (the one who works does not judge turn). Design
   section 4 says so; `run.py`, its fixture and setup-plugin are gone. The whole flow is a trial
   instead: `dev/turn/trials/flow.py` with the note plugin and stand-in agents (ask, answer, stop,
   carry on in another clone, done); it passed on the first run, about 3 minutes.
   Decided by the user (2026-10-11), replacing the per-item entries: the aim is that every agent
   really opens the deliverable and the records and decides from facts, which asking in words does
   not get. So each agent's own record is checked when it tries to finish (a SubagentStop hook in
   turn's hooks/hooks.json, matched by `^turn:<agent>$`; plugin agents cannot hold hooks; a block
   keeps the same agent running with the reason), what must not be done is stopped as it is tried
   (PreToolUse), no agent reads a record or the CCS itself: a script writes the generator's and the
   first user's steps and what the deliverable should be into files read whole with Read (checked by
   the lines read), the first user's prompt is checked to hold no acceptance, and each cause and ending names the steps and deliverable lines it rests on, every
   error step named by some ending. The evidence file keeps the steps and the endings with their
   grounds. Confirmed in code.claude.com/docs/en/hooks and /sub-agents. Design 2 "Checking that each
   agent did its job" and the README's evidence lines are rewritten; waiting for the user's look.
   Signed off by the user (2026-10-11), then built test-first (f72b6c6, 09f3049; CI passes, 100%):
   steps.py (records → numbered steps), should.md written at start, the work folder named by session
   (`turn-try-<session>`, found by the hooks), up.py `steps` and `round <work>`, the evidence file
   written at end, hooks in turn/hooks (pretooluse: first_user_place, generator_place, no_commit,
   handed; read_whole and grounds run before SubagentHandback and at SubagentStop), prompts updated.
   Found by an experiment (scratchpad hookexp, Claude Code 2.1.296): agents now hand back their report
   with SubagentHandback before they stop, so a SubagentStop block does nothing; refusing the
   SubagentHandback call in PreToolUse does keep the agent running. Design 2 says so (uncommitted
   line committed with this note).
   Flow trial flow-3 (scratchpad): 8 of 9 checks pass; "the agents are called in this order" fails
   because in round 2 the learner's stand-in command ran twice (learner-2, learner-3 in calls.jsonl).
   Not yet known whether one learner kept running by the hook ran it again or the orchestrator called
   two learners. Do not run unit tests while a flow trial runs (they make turn-try-* folders the
   trial counts).
   Next (start here): read every record of flow-3 from a list made first (both sessions and every
   agent under ~/.claude/projects/*flow-3*), checking above all that each agent was kept running until
   it had read what it must; then decide the cause of the double learner run; then put the changed
   prompts through writ's prompt.md; then the first real use (pith, writ or rn) in a session the user
   starts.
   Then: the user starts the session for the first of pith, writ and rn; this session sends it the
   work and judges turn from the records and the evidence.
4. Decided by the user (2026-10-11): turn is used in two ways. When each plugin runs, its skill hands
   each task to `turn:up`. When each plugin's documents and prompts are made, the builder hands that
   work to `turn:up`, with writ's essentials files as viewpoints. turn's first version is made by
   hand; once it passes its trial, pith, writ and rn are made through turn, and their calls to turn
   are built in the same work.

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
