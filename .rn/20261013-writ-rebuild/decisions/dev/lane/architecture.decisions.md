# What lane's design says

## Concept, agreed with the user (2026-10-23)

- User: an AI building a Claude Code plugin.
- Purpose: that plugin's subagents, on every run, notice when they drift from a step and are told
  the right step, without the building AI writing the checks.
- Concept: the building AI proposes, on each step of its plugin that alone is not sure to hold and
  whose drift shows in a tool call, a lane: the step's sentence with a hook, and lane's layer lays it;
  on every run the guard notices a drifting call and tells the sentence again, so the AI finds its
  way back itself.
- The building AI writes the proposal, has `lay.py print` show it and approves it itself, running
  `lay.py write`; no person takes part. lane has no agent of its own: `lane:up` is deleted, lane
  being used for now by turn and rn inside ccpm (the maintainer, 2026-10-25).
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
- As the README and the UX give them: the building AI writes the proposal, has `lay.py print` show
  it, and on its approval has `lay.py write` write the steps and the hooks; `lay.py up`, run where
  an older copy is, brings it up; a drift is stopped with the sentence; without Python 3.9 or later
  the hooks stop the calls they watch.

### B-2, B-3: The components and how they work
- What the building AI approved is written by a script, word for word, not by an AI.
- lane lays lanes on a plugin's subagents alone; their hooks go into the plugin's
  `hooks/hooks.json`, one entry acting only in its subagent by the event's `agent_type`, as Claude
  Code ignores `hooks` in a plugin subagent's file and a tool event's matcher filters by tool.
- lane's code goes into `<plugin>/hooks/lane/`: a relative link in a plugin of the ccpm
  marketplace, a copy with its VERSION elsewhere, brought up by `lay.py up`.
- The code reads every tool call as begin, read, write, run, test, hand on, follow, wait or end,
  and holds it to the 12 lanes: start_with, read_only, read_whole, write_only, in_form, hands_off,
  test_after, as_printed, follow_next, wait_for, end_when, every_item.
- A lane on the order of steps reads what the subagent did before from that subagent's own record
  (`agent_transcript_path`), as turn's hooks do, and from the calls `called.py` keeps of it as they
  come back, until the record holds them; the earlier decision against reading a transcript
  was about telling which skill runs, and does not bear on this.
- A check reads the forms the steps tell and the AI writes, not every way the shell has; what must
  hold whatever the AI writes is held by branch protection, the sandbox or permission rules
  (lane/README.md, Why lane).
- Each lane's sentence is made from the lane's wording in docs/lanes.md with what the lane takes
  put in; the layer writes it into the step, `hooks/lanes.json` holds the step, the lane and what it
  takes, and the guard makes the same sentence when it stops a call and finds it in the step, so
  the two cannot differ and no sentence is written twice (lane/README.md, Why lane:
  "Told the step's own sentence, the AI goes back to the step").
- The 12 lanes, each with its wording, what it takes and when it stops a call, are the table the
  user agreed (2026-10-21), which docs/lanes.md gives as one table with an action column (the
  user, 2026-10-22).
- The code shared by rn and turn now, `common/hooks/hook.py` (the entry every hook runs) and
  `common/hooks/shell.py` (how a hook reads a command), moves into lane's code, cut to the usual
  forms; `common/` and `dev/common/` go, `dev/common/testing.py` going to `dev/lane/testing.py`,
  from which rn's and turn's tests import it, as their code takes lane's and `dev/check.sh` fails
  on a copy (the user, 2026-10-21); rn and turn then take lane's code by the same link as any ccpm
  plugin.
- Without python3 3.9 or later, each hook stops the call it checks and asks for Python to be
  installed, rather than letting it through, in Claude Code's JSON output on exit 0.

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
| wait_for | lane:up writes the proposal only on the building AI's OK |
| end_when | turn's result made before ending |
| every_item | turn's evaluator answers every item of `{checklists}` |

rn runs its steps in the main conversation, where a hook cannot tell which step runs; its
`steering.md` is told by its place, `.rn/*/steering.md`, so its form is held there, and its
sign-off by `/rn:ty`, which the AI cannot call.


## Moved out of the architecture, for tests and steps (2026-10-23)

- [test: layer] Bringing an older copy up, a lane the current version no longer lays, or lays taking other things, is left out of its hook and said to the building AI, to propose another lane that keeps its step or leave out; kept in the hook, the guard could not read it and would let every call it watches through, and left out unsaid, an approved lane would be gone with no one told.
- [test: layer] The building AI keeps its proposal in a file and has the layer print it: for each subagent step, the lanes it would lay, each under its action, with the step as it would read and its hooks; the print is what is approved, so no AI retells it.
- [test: layer] Once approved, the layer writes the proposal from the same file word for word into the plugin, with lane's code, and checks that the plugin loads; a plugin that does not load fails for every user.
- [test: layer] The layer removes the proposal file once it is written.
- [test: guard] The guard reads each tool call as one action, begin, read, write, run, test, hand on, follow, wait or end, a command that writes a file being a write of it too, against that subagent's lanes alone, and on a drift stops the call and tells `<plugin>: <sentence>`.
- [test: guard] A lane on the order of steps, such as reading an input whole before writing, is held from what the subagent has done since it started.
- [test: guard] A lane on how the subagent ends, test_after, end_when, every_item, or as_printed on its last reply, is held as it is about to end, from what it has done since it started and its last reply; on a drift the guard keeps it going with `<plugin>: <sentence>`, and told once, a subagent that answers in words alone, with no call since, is let end; it is told, not trapped, or a subagent that cannot keep the lane would be kept going for good and its reply never reach the one who started it.
- [test: guard] The guard answers Claude Code in its JSON output on exit 0: a call stopped by `permissionDecision: "deny"` with the sentence as its reason, the subagent kept going at SubagentStop by `decision: "block"` with the sentence as its reason, which Claude Code gives it as its next instruction, and what the user is told as `systemMessage`; one form at every boundary lane defines (the user, 2026-10-25).
- [test: guard] At SubagentStop the guard reads the last reply from the event, and from the record whether the subagent has answered in words alone since it was told; the event shows only that a stop hook has kept it going once.
- [test: guard] A thing given for each run, written `{<name>}`, is the value under that name in the JSON the subagent starts from: its prompt where it is a JSON object, and each JSON object a script laid by start_with prints, the later over the earlier; a list stands for each of its texts; the guard puts the run's value in before the lane's check and tells the sentence as the step says it, with the value on the next line; a value given as null is the caller saying there is none, and rests the lane on that run, the call or the end let through with nothing told (the maintainer, 2026-10-25); a value not given, or given empty, is an error, as below.
- [test: layer] Laying again, the layer takes out of each step the sentence of each lane the subagent's hook held there before and the new proposal no longer lays, the rest of the step as it was, and its print shows each step so; a sentence left behind would hold the subagent to what no hook keeps.
- [test: layer] A lane may hold more than its sentence shows, such as the commands wait_for holds back until the approval; the layer's print shows them beside the hook, so the building AI approves every thing a hook holds and the subagent is told only what its step says.
- [test: guard] Where the step a hook holds no longer has the lane's sentence, word for word with a line break read as a space, the guard stops the call and says the plugin's maker must lay its lanes again with `lay.py write`; the step was changed since the lane was laid, and a lane kept on a sentence that is gone holds the subagent to what its step no longer says.
- [test: Python check] Where `python3` is missing or older than 3.9, each hook command answers `<plugin>: install Python 3.9 or later, run as python3, for its hooks to run` in Claude Code's JSON output on exit 0, the call denied on a tool call and the user told by `systemMessage` at a subagent's end, letting it end, on an event of its subagent alone, found in the event's text by the shell; letting the call through would leave it unkept with no one told, and a subagent cannot install Python, so kept going it would only be asked again.
- [test: layer] Into a copy of lane's code alone the layer writes `VERSION`, one line holding the version it reads from lane's `plugin.json`, by which the next run tells an older copy.
- [test: guard] Each of the lanes is one file in `lanes/` holding its check and its wording, and a test holds docs/lanes.md's table to those wordings, so the table and the code cannot differ.
- [test: layer] A lane's hook entry has as its matcher the tools that subagent's lanes watch, or at SubagentStop the subagent, and a timeout of 10; its command runs the Python check, then `pretooluse.py` or `subagentstop.py` with `<plugin>:<subagent>` alone; beside them each subagent with lanes has a PostToolUse and a PostToolUseFailure entry matching every tool, whose command lets every event through where Python is missing and runs `posttooluse.py` or `posttoolusefailure.py`, keeping each call as it comes back; the guard reading that subagent's lanes from `hooks/lanes.json`, written in the proposal's shape, so what was approved is what is read and a thing taken holds a comma; a tool event's matcher filters by tool alone.
- [test: layer] The layer leaves every other entry of the plugin's `hooks/hooks.json` as it was.
- [test: guard] A step that says `git commit` is held against `git commit`, `git -C notes commit` or `cd notes && git commit`, but not against `g=git; $g commit`; these are the forms the steps tell and the AI writes.
- [test: guard] A script or command a lane takes is read as the step writes it, such as `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/prepare.py" given`, by the same reading as a call's words: python3 or sh before it left out, and its path in the plugin matched by the end of the call's.
- [docs: lanes.md] The building AI writes a script or command a lane takes in the proposal as the step writes it, word for word.
- [test: guard] in_form's `<form>` is a file of the plugin, named in the step as `${CLAUDE_PLUGIN_ROOT}/<path in the plugin>`: a JSON Schema, in the keywords Anthropic's structured outputs accept, for JSON or JSONL, or a Markdown template, for its frontmatter keys and headings; Claude Code puts the plugin's folder in, so the subagent finds the form wherever the plugin is installed and does not take it for where to write.
- [test: layer] The layer refuses a schema with any keyword beyond those structured outputs accept; a keyword read past would let through, unseen, what the building AI meant to stop.
- [test: guard] read_only lets the subagent read, beside its inputs, the form each of its in_form lanes names, found in `hooks/lanes.json`, as are the scripts its start_with runs; a lane's check is given only what that lane takes.
- [test: guard] in_form holds a write of the output to its form before it is made, by Write's content or by Edit's result, and stops a command writing the output, as its text cannot be read before it runs; after the sentence it tells the first point the text is out by, as one point at a time is what the subagent puts right and the sentence first keeps it on its step.
- [test: guard] The end lanes count only what this run did: test_after a run of the test after the last change to the output, ending with the test's own exit; end_when an output this run wrote that is there; every_item each item of the input as the items port reads it, answered by its ID in the last reply or in a file written this run; a failure hidden by a command after the test, a file left from an earlier run, or an item with no ID to tell its answer by would let the subagent end with its work undone.
- [test: guard] as_printed and follow_next hold every other hand-on or call once their command has printed, until the print is handed on word for word, or the move it prints, as the move port reads it, by default one tool call as a JSON line `{"tool": ..., "input": {...}}` last in the output, is made; wait_for holds its commands until a message with the approval reaches the subagent after it last asked, by SendMessage or by a reply that ended its turn; a hand-on is an Agent call's prompt, a SendMessage's message or the subagent's reply; the move printed as the tool call itself is a form general to any plugin.
- [test: guard] In a subagent's record, the calls of one reply are written once their hooks have run, so a lane on the order of steps reads the replies before; a reply that ended the turn is the entry whose `stop_reason` is `end_turn`; one a stop hook kept going reached no one and is left out, as is a call a hook stopped, which never ran; the calls of the reply being handed are read from those `called.py` keeps as each comes back, so a call sent in the same reply as the move a lane waits on passes the first time.
- [test: layer] On lane itself the layer leaves lane's code as it is, so a run on lane's folder never takes out the code it runs on.
- [test: guard] Each lane checks only what lanes.md defines it to take and knows no plugin's form; where a check reads a plugin's text it reads it at a port lanes.md defines with its JSON in and out, the values a subagent started from, the items of an input and the move a script printed, in the one form lanes.md gives, or by the plugin's adapter, a Python 3 command the building AI writes, with the cases it must give, and the layer writes into `hooks/adapters/`, run by the layer on each case before writing and by the guard at the port, its failure or a wrong answer an error; a new form is the plugin's adapter, never a new version of lane (the user, 2026-10-25: lane works on the IN it defines; ports and adapters, as git's textconv)
- [test: guard] The guard checks what each lane is given against the lane's IN, a JSON Schema lanes.md defines, before any check runs: the event, the lanes laid, the run's values, an adapter's answer and the record a lane rests on; what is not as its IN says is an error, not a drift: the call stopped, or the end kept going once, with `<plugin>: lane cannot check <lane> on step <n> of <subagent>: <what is wrong>.` and who must fix it, the user told the same; nothing is let through unchecked, as a drift is the subagent's to put right and an error the plugin's, which a pass would hide (the user, 2026-10-25: 'チェックできない、エラーだよね'; validated at the entry as an application does)
