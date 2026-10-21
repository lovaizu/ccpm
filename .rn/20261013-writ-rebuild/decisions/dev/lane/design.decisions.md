# What lane's design says

The design is read by whoever builds or changes lane; it is built on dev/architecture.md and brings
about lane/README.md and dev/lane/ux.md, both agreed.

## design

### B-1: The stories
- As the README and the UX give them: `/lane:up` asks one point at a time, proposes, and on OK
  writes the steps and the hooks; run again where an older copy is, it brings it up; a drift is
  stopped with the sentence; without Python 3.9 or later the hooks stop the calls they watch.

### B-2, B-3: The components and how they work
- `/lane:up` is a plugin job under dev/architecture.md: a front skill that only talks, an
  orchestrator agent that does what the flow prints, a flow script keeping the run in a JSON state
  file, and roles that are agents of their own.
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

### B-8 to B-15: Verification
- Each unit's flow with unittest and Hypothesis in `dev/lane/tests/`, 100% lines and branches by
  `dev/check.sh` and no surviving mutant by `dev/mutate.sh`; the agents' flow on stand-ins, their
  content on real plugins (the README's `notes`, turn's agents), on the model users run, judged from
  every JSONL; trials in `lovaizu/playground`, one at a time, removed after.
