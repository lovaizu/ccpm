# What a turn run spends, set to what its purpose needs

The user agreed these intents (2026-10-27), after acceptance run 3 (folder
/tmp/rn/20261027-acceptance-5180ibfe) took 3 h 50 min and about $76 for 3½ of 6 tasks of a
250-line tool, nearly all inside turn. Each is fixed where its cause lies, then the acceptance run
shows whether it improved.

1. The generator's self-check: per item, whether it passes and its evidence, the command run and
   what it printed or the lines, in short; only the items sent back are written again.
2. The orchestrator's moves number what the run needs, about eight for two rounds; the user is told
   only at a role's start and end, a question and the result.
3. Only what the user alone can decide is asked; a technical choice the generator settles and names
   as chosen. Once answered, turn goes on where it stood, a CCS added to not starting it again; rn
   does not commit and push at each answer.
4. Maker and reader meet: a code work's project has a formatter, a linter and a type checker, and
   what a machine can see is left to them; the reader finds Good by whether the receiver can use the
   work, sending back only a gap that hinders that use; per item, what is run and how far is the same
   for the generator and the first user.
5. The generator and the first user, holding the same purpose, settle a gap by messages: the first
   user says the gap and how it hinders the purpose, the generator mends it or says why it lies
   outside the purpose.
6. Every check tells "could not check" apart from "no problem": it ends in no problem, a problem
   found, or could not check with why; for each way it can fail to check, what should then happen
   is decided beforehand and tested, so no case is met unconsidered. This holds for hooks (a
   script that fails or times out, a command not parsed), tests (a skip is no pass), CI (a job
   not run), a reader (a command that did not run gives no Good) and the trial tools.

7. Where what keeps the work from going on lies outside it, such as the environment, a permission
   or a missing tool, the run stops without a way round and tells its caller what was tried, what
   was confirmed and what was not, and what it needs (agreed 2026-10-27).
8. An acceptance test shows, beside how close the purpose came, the time and the tokens a run took,
   which the maintainer judges by feel against the size of the work, kept so that runs can be
   compared as they gather (the user's view, 2026-10-27).

Intents 1 to 8 are general to every plugin and go into dev/architecture.md's principles; lane,
turn and rn apply them.

Decided by the assistant from these and turn's purpose:

- turn's Principle 4 is kept for the first reading alone: the first user reads the work without the
  generator's claim, as the receiver it stands in for has none; after a gap is found, the two talk as
  intent 5 says.
- Principle 6 is kept by writing each answer to a file before the next move; the push waits for the
  step's end, as going on from a stop needs the file, not the push.
- The exchange of intent 5 goes through the flow, the orchestrator holding the run (Principle 1),
  one exchange counted as one move; the first user judges only by whether the receiver can use the
  work, and a gap still disputed after one exchange is a question of the purpose, put to the user.
- turn starts over on an added CCS only because lane fixes a run's files at the role's start; lane
  takes a run's files from later messages too, so the run goes on.
- `turn.py next` waits for a role's end itself, so a wait is one move, not repeated polls.
- The orchestrator's check of the CCS before any work goes: the generator asks at its step 3, before
  making, what only the user can decide.
- The hunting form is fixed at its root, the template of rn/checklists/checklist.md, then each
  checklist; code.md B-6 has the generator decide and name a survivor kept, not ask the user.
- rn's own step lines follow the same rule as turn's: a step's start and end, a question, a result.
- Hooks: lay.py writes `"onFailure": "block"` on every command hook it lays (Claude Code v2.1.295+),
  so a hook that fails or times out stops the call; a command lane cannot parse is told as could not
  check, not let through.

Where each intent lands, as found before any fix: audits/run-cost-impact.md.
