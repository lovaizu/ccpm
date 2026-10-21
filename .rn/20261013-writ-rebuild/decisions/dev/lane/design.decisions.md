# What lane's design says

- lane is lanes alone, a step with its hook: no flow, no recorder, no run state; turn keeps its own
  flow, rn uses none and holds its steering's form by a hook of its own; a flow is built only if
  rn's trials show the need (the user, 2026-10-22). Lines below on the flow, the recorder and a
  run's state are outdated by this and go when the design is remade.

The design is read by whoever builds or changes lane; it is built on dev/architecture.md and brings
about lane/README.md and dev/lane/ux.md, both agreed.

## design

### B-1: The stories
- As the README and the UX give them: the builder asks Claude, which starts `lane:up`; `lane:up`
  asks one point at a time through the calling AI, proposes, and on OK has the flow definition, the
  steps and the hooks written; run again where an older copy is, it brings it up; the flow refuses a
  move that breaks a rule and goes past a gate only on the caller's OK; a drift is stopped with the
  sentence; a run goes on in a new conversation; without Python 3.9 or later the flow and the hooks
  stop.

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
- Each lane's sentence is made from the lane's wording in `lanes.md` with what the lane takes put
  in; the layer writes it into the step, the hook names the step, the lane and what it takes, and
  the guard makes the same sentence when it stops a call and finds it in the step, so the two
  cannot differ and no sentence is written twice (lane/README.md, Why lane: "Each hook tells the
  step's own sentence").
- The 12 lanes, each with its wording, what it takes and when it stops a call, are the table the
  user agreed (2026-10-21), which `lanes.md` gives.
- The code shared by rn and turn now, `common/hooks/hook.py` (the entry every hook runs) and
  `common/hooks/shell.py` (how a hook reads a command), moves into lane's code, cut to the usual
  forms; `common/` and `dev/common/` go, `dev/common/testing.py` going to `dev/lane/testing.py`,
  from which rn's and turn's tests import it, as their code takes lane's and `dev/check.sh` fails
  on a copy (the user, 2026-10-21); rn and turn then take lane's code by the same link as any ccpm
  plugin.
- Without python3 3.9 or later, each hook stops the call it checks with exit 2 and asks for Python
  to be installed, rather than letting it through.

### B-2, B-3: The flow
- lane keeps the flow every ccpm plugin runs on (dev/architecture.md, The flow keeps the run); a
  plugin gives its own in one JSON file. lane defines the keys and what each does, never their
  values (the user, 2026-10-21):
  - `phases`, each with `name`; `each`, a `jq` path to the plan's items walked one by one; `type`,
    the type of work run on each item; `gate`, the caller's own action that alone lets the run go
    on, such as `rn:ty`; `done_when`, a `jq` condition on the state.
  - `types`, each a named list of steps, such as rn's `make`: turn, then record, then a gate.
  - For rn, as an example: hearing done when no point is left; plan, gated; design, each document
    made, gated; tasks, each task made, done when the pull request's checks pass; deliverable,
    gated.
- The plan is data in the state, written by the orchestrator; each change keeps its reason; the
  goal and the acceptance criteria, once approved, change only with the caller's approval again.
- The flow refuses a move that breaks a rule, keeps a limit on making a work again, and records
  each approval from the caller's own action.
- A run's state is `state.json` in the folder of that piece of work in the user's repository, its
  name and form the same for every plugin, given by lane; the orchestrator names the folder on its
  first call to the flow: rn `.rn/<case>/`, turn the CCS's folder, lane:up `.lane/<plugin>/`; not
  `${CLAUDE_PLUGIN_DATA}`, which stays on one machine, as a run is to go on from another
  conversation or machine (the user, 2026-10-21).
- A plugin's flow definition is `<plugin>/flows/<orchestrator>.json`, one per orchestrator; the
  orchestrator's steps run `flow.py` with `${CLAUDE_PLUGIN_ROOT}` written in, as a Bash call gets
  no plugin variables (plugins-reference, Where each variable resolves).
- The recorder, lane's hooks on AskUserQuestion in the main conversation, refuses a question whose
  `answers` is filled, records the chosen label into the state of the work folder the question
  names, and refuses a tool call that writes a run's state; the shape of PostToolUse's
  `tool_response` is undocumented, so it is taken from a real interactive run.
- The flow judges only the moves the orchestrator tells it; no hook calls it for the orchestrator
  (the user, 2026-10-21). A hook in the main conversation cannot tell the run's moves from other
  work there, and AI-DLC's hooks that do (core/hooks/aidlc-continue-workflow.ts,
  aidlc-plan-approval-guard.ts) take every move as the run's while one is open; turn's twelve
  recorded runs told turn.py before each of their 90 role moves.

### B-8 to B-15: Verification
- The checklist template's `Flow:` and `Content:` stay as they are beside the component flow: they
  name what is checked, and a word met in two places is not renamed for that alone (the user,
  2026-10-21).
- Each unit's flow with unittest and Hypothesis in `dev/lane/tests/`, 100% lines and branches by
  `dev/check.sh` and no surviving mutant by `dev/mutate.sh`; the agents' flow on stand-ins, their
  content on real plugins (the README's `notes`, turn's agents), on the model users run, judged from
  every JSONL; trials in `lovaizu/playground`, one at a time, removed after.
