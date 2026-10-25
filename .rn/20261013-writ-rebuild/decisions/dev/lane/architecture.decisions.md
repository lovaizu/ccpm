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
- As the README and the UX give them: the building AI starts `lane:up`; `lane:up` sends it every
  open point in one reply, proposes, and on its OK has the steps and the hooks written; run again where an older copy is, it brings it up; a drift is stopped with the
  sentence; without Python 3.9 or later the hooks stop the calls they watch.

### B-2, B-3: The components and how they work
- `lane:up` is the orchestrator, a subagent the building AI starts, its points given as its reply
  and the answers sent to its agent ID; it reads and proposes itself and starts no subagents (the
  user, 2026-10-21).
- The hearing shows the building AI, in one reply, each fact found that the lanes rest on, to
  confirm, as well as each point it decides (dev/architecture.md, Hearing; the user, 2026-10-23).
- What the building AI approved is written by a script, word for word, not by an AI.
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
| wait_for | lane:up writes the proposal only on the building AI's OK |
| end_when | turn's result made before ending |
| every_item | turn's evaluator answers every item of `{checklists}` |

rn runs its steps in the main conversation, where a hook cannot tell which step runs; its
`steering.md` is told by its place, `.rn/*/steering.md`, so its form is held there, and its
sign-off by `/rn:ty`, which the AI cannot call.


## Moved out of the architecture, for tests and steps (2026-10-23)

- [test: layer] Bringing an older copy up, a lane the current version no longer lays, or lays taking other things, is left out of its hook and becomes a point to the building AI, to lay again or leave out; kept in the hook, the guard could not read it and would let every call it watches through, and left out unsaid, an approved lane would be gone with no one told.
- [step: lane:up] It gives, in one reply, every point the files leave open as a question with its recommendation, and every fact it found with where it found it, then in one reply more those an answer opens, until no point is left; a fact found is shown too, since the proposal rests on it, and a fact read otherwise is assumed in the caller's place (dev/architecture.md, Hearing until nothing is left to decide).
- [step: lane:up] With every point settled, it keeps its proposal in a file, has the layer print it and gives that print as its reply: for each subagent step, the lanes it would lay, each under its action, with the step as it would read and its hooks; a change asked goes back to it, which changes the file and gives the print again; the print is what is approved, so no AI retells it.
- [step: lane:up] Where the building AI wants no lanes at all, it removes the proposal and writes nothing.
- [test: layer] Once approved, the layer writes the proposal from the same file word for word into the plugin, with lane's code, and checks that the plugin loads; a plugin that does not load fails for every user.
- [test: layer] The layer removes the proposal file once it is written.
- [test: guard] The guard reads each tool call as one action, begin, read, write, run, test, hand on, wait or end, a command that writes a file being a write of it too, against that subagent's lanes alone, and on a drift stops the call and tells `<plugin>: <sentence>`.
- [test: guard] A lane on the order of steps, such as reading an input whole before writing, is held from what the subagent has done since it started.
- [test: guard] A lane on how the subagent ends, test_after, end_when, every_item, or as_printed on its last reply, is held as it is about to end, from what it has done since it started and its last reply; on a drift the guard keeps it going with `<plugin>: <sentence>`, and told once, a subagent that answers in words alone, with no call since, is let end; it is told, not trapped, or a subagent that cannot keep the lane would be kept going for good and its reply never reach the one who started it.
- [test: guard] The guard answers Claude Code in its JSON output on exit 0: a call stopped by `permissionDecision: "deny"` with the sentence as its reason, the subagent kept going at SubagentStop by `decision: "block"` with the sentence as its reason, which Claude Code gives it as its next instruction, and what the user is told as `systemMessage`; one form at every boundary lane defines (the user, 2026-10-25).
- [test: guard] At SubagentStop the guard reads the last reply from the event, and from the record whether the subagent has answered in words alone since it was told; the event shows only that a stop hook has kept it going once.
- [test: guard] A thing given for each run, written `{<name>}`, is the value under that name in the JSON the subagent starts from: its prompt where it is a JSON object, and each JSON object a script laid by start_with prints, the later over the earlier; a list stands for each of its texts; the guard puts the run's value in before the lane's check and tells the sentence as the step says it, with the value on the next line; a value not given, or given empty, is an error, as below.
- [test: layer] Laying again, the layer takes out of each step the sentence of each lane the subagent's hook held there before and the new proposal no longer lays, the rest of the step as it was, and its print shows each step so; a sentence left behind would hold the subagent to what no hook keeps.
- [test: layer] A lane may hold more than its sentence shows, such as the commands wait_for holds back until the approval; the layer's print shows them beside the hook, so the building AI approves every thing a hook holds and the subagent is told only what its step says.
- [test: guard] Where the step a hook holds no longer has the lane's sentence, word for word with a line break read as a space, the guard stops the call and says to have `lane:up` run again; the step was changed since the lane was laid, and a lane kept on a sentence that is gone holds the subagent to what its step no longer says.
- [test: Python check] Where `python3` is missing or older than 3.9, each hook command writes `<plugin>: install Python 3.9 or later, run as python3, for its hooks to run` and exits 2 on a tool call and 1 at a subagent's end, on an event of its subagent alone, found in the event's text by the shell; letting the call through would leave it unkept with no one told, and a subagent cannot install Python, so kept going it would only be asked again.
- [test: layer] Into a copy of lane's code alone the layer writes `VERSION`, one line holding the version it reads from lane's `plugin.json`, by which the next run tells an older copy.
- [test: guard] Each of the lanes is one file in `lanes/` holding its check and its wording, and a test holds the README's Lanes to those wordings, so the table and the code cannot differ.
- [test: layer] A lane's hook entry has as its matcher the tools that subagent's lanes watch, or at SubagentStop the subagent, and a timeout of 10; its command runs the Python check, then `pretooluse.py` or `subagentstop.py` with `<plugin>:<subagent>` alone, the guard reading that subagent's lanes from `hooks/lanes.json`, written in the proposal's shape, so what was approved is what is read and a thing taken holds a comma; a tool event's matcher filters by tool alone.
- [test: layer] The layer leaves every other entry of the plugin's `hooks/hooks.json` as it was.
- [test: guard] A step that says `git commit` is held against `git commit`, `git -C notes commit` or `cd notes && git commit`, but not against `g=git; $g commit`; these are the forms the steps tell and the AI writes.
- [test: guard] A script or command a lane takes is read as the step writes it, such as `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/prepare.py" given`, by the same reading as a call's words: python3 or sh before it left out, and its path in the plugin matched by the end of the call's.
- [step: lane:up] It takes a script or command a lane takes from the step word for word.
- [test: guard] in_form's `<form>` is a file of the plugin, named in the step as `${CLAUDE_PLUGIN_ROOT}/<path in the plugin>`: a JSON Schema, in the keywords Anthropic's structured outputs accept, for JSON or JSONL, or a Markdown template, for its frontmatter keys and headings; Claude Code puts the plugin's folder in, so the subagent finds the form wherever the plugin is installed and does not take it for where to write.
- [test: layer] The layer refuses a schema with any keyword beyond those structured outputs accept; a keyword read past would let through, unseen, what the building AI meant to stop.
- [test: guard] read_only lets the subagent read, beside its inputs, the form each of its in_form lanes names, found in `hooks/hooks.json`, as are the scripts its start_with runs; a lane's check is given only what that lane takes.
- [test: guard] in_form holds a write of the output to its form before it is made, by Write's content or by Edit's result, and stops a command writing the output, as its text cannot be read before it runs; after the sentence it tells the first point the text is out by, as one point at a time is what the subagent puts right and the sentence first keeps it on its step.
- [test: guard] The end lanes count only what this run did: test_after a run of the test after the last change to the output, ending with the test's own exit; end_when an output this run wrote that is there; every_item each item of the input as the items port reads it, answered by its ID in the last reply or in a file written this run; a failure hidden by a command after the test, a file left from an earlier run, or an item with no ID to tell its answer by would let the subagent end with its work undone.
- [test: guard] as_printed and follow_next hold every other hand-on or call once their command has printed, until the print is handed on word for word, or the move it prints, as the move port reads it, by default one tool call as a JSON line `{"tool": ..., "input": {...}}` last in the output, is made; wait_for holds its commands until a message with the approval reaches the subagent after it last asked, by SendMessage or by a reply that ended its turn; a hand-on is an Agent call's prompt, a SendMessage's message or the subagent's reply; the move printed as the tool call itself is a form general to any plugin.
- [test: guard] In a subagent's record, the calls of one reply are written once their hooks have run, so a lane on the order of steps reads the replies before; a reply that ended the turn is the entry whose `stop_reason` is `end_turn`; one a stop hook kept going reached no one and is left out, as is a call a hook stopped, which never ran; so a call sent in the same reply as the move a lane waits on is held once, and passes when sent again.
- [test: layer] `lane:up` is held by lanes of its own, laid by the layer: as_printed on handing on the layer's print, and wait_for on writing it before the approval; on lane itself the layer leaves lane's code as it is; these keep what the building AI approves the print, and nothing written before it, and what `lane:up` reads and writes is in the plugin it is given, which differs on each run, so no lane names it.
- [test: guard] Each lane checks only what lanes.md defines it to take and knows no plugin's form; where a check reads a plugin's text it reads it at a port lanes.md defines with its JSON in and out, the values a subagent started from, the items of an input and the move a script printed, in the one form lanes.md gives, or by the plugin's adapter, a Python 3 command `lane:up` writes into `hooks/adapters/` with the cases it must give, run by the layer on each case before writing and by the guard at the port, its failure or a wrong answer an error; a new form is the plugin's adapter, never a new version of lane (the user, 2026-10-25: lane works on the IN it defines; ports and adapters, as git's textconv)
- [test: guard] The guard checks what each lane is given against the lane's IN, a JSON Schema lanes.md defines, before any check runs: the event, the lanes laid, the run's values, an adapter's answer and the record a lane rests on; what is not as its IN says is an error, not a drift: the call stopped, or the end kept going once, with `<plugin>: lane cannot check <lane> on step <n> of <subagent>: <what is wrong>.` and who must fix it, the user told the same; nothing is let through unchecked, as a drift is the subagent's to put right and an error the plugin's, which a pass would hide (the user, 2026-10-25: 'チェックできない、エラーだよね'; validated at the entry as an application does)
