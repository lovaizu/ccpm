# What lane's design says

## Concept, agreed with the user (2026-10-23)

- User: an AI building a Claude Code plugin.
- Purpose: that plugin's subagents, on every run, notice when they drift from a step and are told
  the right step, without the building AI writing the checks.
- Concept: `lane:up` reads the plugin's steps and lays, on each step that alone is not sure to hold
  and whose drift shows in a tool call, a lane: the step's sentence with a hook; on every run the
  guard notices a drifting call and tells the sentence again, so the AI finds its way back itself.
- The AI that calls `lane:up` answers its points and approves its proposal itself; no person takes
  part.
- lane's own principles: (1) the AI is made to notice its drift from a step and is told the step
  again, so it finds its way back itself; (2) a lane is a sentence of a step together with the hook
  that notices a drift from it.

- lane is lanes alone, a step with its hook: no flow, no recorder, no run state; turn keeps its own
  flow, rn uses none and holds its steering's form by a hook of its own; a flow is built only if
  rn's trials show the need (the user, 2026-10-22).

The design is read by whoever builds or changes lane; it is built on dev/architecture.md and brings
about lane/README.md and dev/lane/ux.md, both agreed.

## design

### B-1: The stories
- As the README and the UX give them: the builder asks Claude, which starts `lane:up`; `lane:up`
  asks one point at a time through the calling AI, proposes, and on OK has the steps and the hooks
  written; run again where an older copy is, it brings it up; a drift is stopped with the
  sentence; without Python 3.9 or later the hooks stop the calls they watch.

### B-2, B-3: The components and how they work
- `lane:up` is the orchestrator, a subagent the calling AI starts, messaging the agent the caller
  names (`main` from the main conversation); it reads and proposes itself and starts no subagents,
  so the README says only that Claude starts it from a conversation or a subagent (the user,
  2026-10-21).
- The hearing shows the builder each fact found that the lanes rest on, one at a time, to confirm,
  as well as each point only the builder decides (dev/architecture.md, Hearing).
- What the builder approved is written by a script, word for word, not by an AI.
- lane lays lanes on a plugin's subagents alone; their hooks go into the plugin's
  `hooks/hooks.json`, one entry acting only in its subagent by the event's `agent_type`, as Claude
  Code ignores `hooks` in a plugin subagent's file and a tool event's matcher filters by tool.
- lane's code goes into `<plugin>/hooks/lane/`: a relative link in a plugin of the ccpm
  marketplace, a copy with its VERSION elsewhere, brought up by the next `/lane:up`.
- The code reads every tool call as begin, read, write, run, test, hand on, wait or end, and holds
  it to the 12 lanes: start_with, read_only, read_whole, write_only, in_form, hands_off,
  test_after, as_printed, follow_next, wait_for, end_when, every_item.
- A lane on the order of steps reads what the subagent did before from that subagent's own record
  (`agent_transcript_path`), as turn's hooks do; the earlier decision against reading a transcript
  was about telling which skill runs, and does not bear on this.
- A check reads the forms the steps tell and the AI writes, not every way the shell has; what must
  hold whatever the AI writes is held by branch protection, the sandbox or permission rules
  (lane/README.md, Why lane).
- Each lane's sentence is made from the lane's wording in the README's Lanes with what the lane
  takes put in; the layer writes it into the step, the hook names the step, the lane and what it
  takes, and the guard makes the same sentence when it stops a call and finds it in the step, so
  the two cannot differ and no sentence is written twice (lane/README.md, Why lane: "Each hook
  tells the step's own sentence").
- The 12 lanes, each with its wording, what it takes and when it stops a call, are the table the
  user agreed (2026-10-21), which the README's Lanes gives as one table with an action column
  (the user, 2026-10-22).
- The code shared by rn and turn now, `common/hooks/hook.py` (the entry every hook runs) and
  `common/hooks/shell.py` (how a hook reads a command), moves into lane's code, cut to the usual
  forms; `common/` and `dev/common/` go, `dev/common/testing.py` going to `dev/lane/testing.py`,
  from which rn's and turn's tests import it, as their code takes lane's and `dev/check.sh` fails
  on a copy (the user, 2026-10-21); rn and turn then take lane's code by the same link as any ccpm
  plugin.
- Without python3 3.9 or later, each hook stops the call it checks with exit 2 and asks for Python
  to be installed, rather than letting it through.

### B-8 to B-15: Verification
- The checklist template's `Flow:` and `Content:` stay as they are beside the component flow: they
  name what is checked, and a word met in two places is not renamed for that alone (the user,
  2026-10-21).
- Each unit's flow with unittest and Hypothesis in `dev/lane/tests/`, 100% lines and branches by
  `dev/check.sh` and no surviving mutant by `dev/mutate.sh`; the agents' flow on stand-ins, their
  content on real plugins (the README's `notes`, turn's agents), on the model users run, judged from
  every JSONL; trials in `lovaizu/playground`, one at a time, removed after.

## Where the 12 lanes were drawn from (agreed 2026-10-21)

| Lane | Where it was drawn from |
|---|---|
| start_with | turn's roles run `turn.py given` first |
| read_only | turn's first user reads `{work}`, `{has}` and `{checklists}` alone |
| read_whole | turn's roles read their inputs whole |
| write_only | turn's generator writes `{work}` alone |
| in_form | turn's replies; rn's `steering.md` |
| hands_off | no commit or push in turn's roles |
| test_after | turn's generator passes the work's checks after changing it |
| as_printed | turn's prompts handed on as `turn.py` printed them; lane:up's proposal |
| follow_next | turn's roles started in the order `turn.py` prints |
| wait_for | lane:up writes the proposal only on the builder's OK |
| end_when | turn's result made before ending |
| every_item | turn's evaluator answers every item of `{checklists}` |

rn runs its steps in the main conversation, where a hook cannot tell which step runs; its
`steering.md` is told by its place, `.rn/*/steering.md`, so its form is held there, and its
sign-off by `/rn:ty`, which the AI cannot call.

