# lane's lanes

Each lane lane can lay, under the action it watches, so your AI can tell which lanes to propose for
your plugin's steps and you can tell what each hook tells your subagent; and the proposal your AI
writes them in.

The sentence is what the step says and what the subagent is told on a drift, with what the lane
takes put in where it shows `<...>`; the hook tells it when the subagent does what the last column
says.

What a lane takes is fixed in the step, such as `CHANGELOG.md`, or given for each run, written
`{<name>}`: the value under that name the values port reads in what the subagent starts from, its
prompt and what the script it first runs prints. The sentence `Write only {work}.` holds a subagent
to the files its run's `work` names, whichever they are. A value given as `null` is the caller
saying there is none: each lane taking that name lets the call or the end through on that run, with
nothing told. A thing taken holds any text, a comma among the rest.

| Action | Lane | Sentence | Told when the subagent |
|---|---|---|---|
| begin | start_with | First run `<script>`. | begins with anything else |
| read | read_only | Read only `<input>`. | reads anything else |
| read | read_whole | Read `<input>` to its end. | leaves a part of it unread |
| write | write_only | Write only `<output>`. | writes anything else |
| write | in_form | Write `<output>` in the form of `<form>`. | writes it out of that form |
| run | hands_off | Do not run `<commands>`. | runs one of them |
| test | test_after | After changing `<output>`, pass `<test>`. | ends with a change not yet passed |
| hand on | as_printed | Hand on `<command>` as it is. | does anything else first |
| follow | follow_next | Take the next move `<script>` printed. | does anything else first |
| wait | wait_for | Do not go on until `<approval>`. | runs a command it holds back without it |
| end | end_when | End only once `<output>` is made. | ends before |
| end | every_item | Answer every item of `<input>`. | leaves an item unanswered |

wait_for takes, after the approval, each command it holds back, as the step writes it; its sentence
shows the approval alone. in_form takes the form as `${CLAUDE_PLUGIN_ROOT}/<path in the plugin>`,
the path the subagent reads it by: a `.json` JSON Schema of the keywords Anthropic's structured
outputs accept, which a JSON output, or each line of a `.jsonl` one, is held to, or a `.md`
Markdown template, whose headings and frontmatter keys a Markdown output is held to.

read_only lets the subagent read, beside its inputs, the form each of its in_form lanes names: its
step tells it to write in that form, and the form, a file of your plugin, holds nothing of the
project's work.

every_item reads its input's items at the items port, and follow_next the move your script printed
at the move port, as the ports below say.

## The proposal

Your AI writes the lanes it proposes as one JSON file, has `lay.py print` show them as they will be
laid, and once it approves them has `lay.py write` lay them from the same file, held to this JSON
Schema:

```json
{"type": "object", "required": ["plugin", "subagents"], "additionalProperties": false,
 "properties": {
  "plugin": {"type": "string", "description": "your plugin's folder"},
  "subagents": {"type": "array", "minItems": 1, "items": {
   "type": "object", "required": ["name", "steps"], "additionalProperties": false,
   "properties": {
    "name": {"type": "string", "description": "the subagent, as its file's name: field"},
    "adapter": {"type": "string", "description": "hooks/adapters/values-<name>.py"},
    "steps": {"type": "array", "minItems": 1, "items": {
     "type": "object", "required": ["step", "lanes"], "additionalProperties": false,
     "properties": {
      "step": {"type": "integer", "description": "its number in the subagent's Steps"},
      "lanes": {"type": "array", "minItems": 1, "items": {
       "type": "object", "required": ["lane", "takes"], "additionalProperties": false,
       "properties": {
        "lane": {"enum": ["start_with", "read_only", "read_whole", "write_only", "in_form",
                          "hands_off", "test_after", "as_printed", "follow_next", "wait_for",
                          "end_when", "every_item"]},
        "takes": {"type": "array", "items": {"type": "string"}},
        "adapter": {"type": "string", "description": "hooks/adapters/<port>-<name>.py"}}}}}}}}}}}}
```

- A lane goes only on a sentence whose drift shows in a tool call or in how the subagent ends, and
  only where the step alone is not sure to hold.

  What the subagent only weighs no hook sees.
- A lane's `takes` are its things in the order of its places under What each lane is given, each
  written as the step writes it, a script or a command word for word.
- An adapter is named only where your text is in another form than lane's, as the ports below say.
- A subagent the proposal gives has, once it is written, the proposal's lanes alone: put in each
  lane `lay.py up` says was laid before in it that you keep, as it says the lane.

  The sentence of each lane left out is taken out of its step.
- Keep the proposal as `.lane/<yyyymmdd>-<plugin>/<plugin>.json` at the root of the repository
  your plugin is in, the nearest folder above it holding `.git`, or your plugin's folder where none
  does, and its adapters beside it.

  Your AI reads and writes them with its tools, and Claude Code lets it do so without asking only
  inside the folder it works in; `lay.py write` removes them, and their folder, once they are
  written into your plugin.

## The ports

Where a lane reads your plugin's text, it reads it at a port: given JSON, the port gives back JSON,
each held to the JSON Schema below. lane reads one form at each port; where your text is in another,
your plugin has an adapter for it, a Python 3 script given the port's JSON on stdin and printing the
port's JSON on stdout, with the cases it must give, `<port>-<name>.json`, a list of
`{"given": <the port's JSON in>, "gives": <the port's JSON out>}`, at least one for each form the
text takes and one that gives nothing. An adapter is part of the proposal: kept beside it, as
`<plugin>/adapters/<port>-<name>.py` in the folder the proposal is in, it is named by its path in
your plugin, `hooks/adapters/<port>-<name>.py`, on the lane reading the port, or, for the values
port, on the subagent, as every lane of the subagent reads its values; it is run on each of its
cases before the proposal is printed, shown in the print, and written into your plugin's
`hooks/adapters/` with its cases once approved. On a run the guard runs it within the hook's time,
and an adapter failing, giving no answer in time or answering out of its port is an error, as below.

| Port | Given | Gives | lane's form |
|---|---|---|---|
| values | `{"texts": ["<the prompt>", "<each print of a start_with script>"]}` | `{"values": {"<name>": ["<text>", ...]}}` or `{"values": {"<name>": null}}` | the JSON objects the texts hold, the whole text or each line that is one, the later over the earlier; a list for each of its texts, a text for itself, `null` for itself |
| items | `{"input": "<path>", "text": "<its text>"}` | `{"items": ["<ID>", ...]}` | each top-level item of a Markdown list beginning with an ID, such as `B-1`, `R33` or `KR1.1`, in bold, code or brackets or not |
| move | `{"output": "<what the script printed>"}` | `{"move": {"tool": "...", "input": {...}}}` or `{"move": null}` | the tool call itself, one JSON line `{"tool": ..., "input": {...}}` last in the output |

The ports' JSON Schemas:

```json
{
  "values": {
    "in": {"type": "object", "required": ["texts"], "additionalProperties": false,
           "properties": {"texts": {"type": "array", "items": {"type": "string"}}}},
    "out": {"type": "object", "required": ["values"], "additionalProperties": false,
            "properties": {"values": {"type": "object",
                                      "additionalProperties": {"type": ["array", "null"], "items": {"type": "string"}}}}}
  },
  "items": {
    "in": {"type": "object", "required": ["input", "text"], "additionalProperties": false,
           "properties": {"input": {"type": "string"}, "text": {"type": "string"}}},
    "out": {"type": "object", "required": ["items"], "additionalProperties": false,
            "properties": {"items": {"type": "array", "items": {"type": "string"}}}}
  },
  "move": {
    "in": {"type": "object", "required": ["output"], "additionalProperties": false,
           "properties": {"output": {"type": "string"}}},
    "out": {"type": "object", "required": ["move"], "additionalProperties": false,
            "properties": {"move": {"anyOf": [
              {"type": "null"},
              {"type": "object", "required": ["tool", "input"], "additionalProperties": false,
               "properties": {"tool": {"type": "string"}, "input": {"type": "object"}}}]}}}
  }
}
```

## What each lane is given

The guard first holds the event to the form Claude Code hands it and `hooks/lanes.json` to the form
`lay.py write` writes it in; then, before any lane's check, what each lane is given to the lane's
IN, a JSON Schema: the texts put in each place of its sentence, with each `{<name>}` given for the
run put in, its empty texts left out, one or more in each place; and, where its check rests on what
the subagent did before, its record, where a call counts once it has come back, a call a hook
stopped left out. The layer holds a proposal's takes to the same IN, so a wrong
take shows when the lanes are laid, not on a run. Anything not as these say, a value not given or
given empty, an adapter failing, giving no answer in time or answering out of its port, the record
not found, the event or `hooks/lanes.json` not as Claude Code and `lay.py write` write them, a step
no longer saying its lane's sentence, or a thing a lane takes that `lay.py write` would now refuse,
such as in_form's form gone, is an error, not a drift: the call is stopped, or the subagent kept
going once as it ends, and it and you are told

```
<plugin>: lane cannot check <lane> on step <n> of <subagent>: <what is wrong>. Stop here and reply that <who must fix it>.
```

or, where the event or `hooks/lanes.json` is what is wrong, so no lane of the subagent is known,

```
<plugin>: lane cannot check the lanes of <subagent>: <what is wrong>. Stop here and reply that <who must fix it>.
```

and, where the hook's command does not name the subagent as `lay.py write` writes it, so neither
your plugin nor the subagent is known, the same headed `lane:` and naming `the lanes of this hook`.

A lane taking a value given for the run is held once the script start_with runs first has run and
come back, as the value comes with what it prints; until then start_with holds the subagent, the
call that runs the script let through.

The IN of a lane, `<place>` standing for each of its places below, and `record` required only where
it rests on the record:

```json
{
  "type": "object",
  "required": ["takes", "record"],
  "additionalProperties": false,
  "properties": {
    "takes": {
      "type": "object",
      "required": ["<place>"],
      "additionalProperties": false,
      "properties": {
        "<place>": {"type": "array", "items": {"type": "string"}, "minItems": 1}
      }
    },
    "record": {"type": "array"}
  }
}
```

| Lane | Places | Rests on the record |
|---|---|---|
| start_with | `script` | yes |
| read_only | `input` | no |
| read_whole | `input` | yes |
| write_only | `output` | no |
| in_form | `output`, `form` | no |
| hands_off | `commands` | no |
| test_after | `output`, `test` | yes |
| as_printed | `command` | yes |
| follow_next | `script` | yes |
| wait_for | `approval`, `held` | yes |
| end_when | `output` | yes |
| every_item | `input` | yes |

`held` is the commands wait_for holds back.
