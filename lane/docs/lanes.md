# lane's lanes

Each lane lane can lay, under the action it watches, so you can tell what `lane:up` proposes for
your plugin's steps and what each hook tells your subagent.

The sentence is what the step says and what the subagent is told on a drift, with what the lane
takes put in where it shows `<...>`; the hook tells it when the subagent does what the last column
says.

What a lane takes is fixed in the step, such as `CHANGELOG.md`, or given for each run, written
`{<name>}`: the value under that name in the JSON the subagent starts from, its prompt or what the
script it first runs prints. The sentence `Write only {work}.` holds a subagent to the files its
run's `work` names, whichever they are.

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

follow_next reads the next move your script prints as the tool call itself, one JSON line
`{"tool": ..., "input": {...}}` last in its output; a script printing its move in a form of its own
gets no follow_next.

## What each lane is given

Before any lane's check, the guard holds what each lane is given to the lane's IN, a JSON Schema:
the texts put in each place of its sentence, with each `{<name>}` given for the run put in, one or
more in each place; and, where its check rests on what the subagent did before, its record. The
layer holds a proposal's takes to the same IN, so a wrong take shows when the lanes are laid, not on
a run. Anything not as its IN says, a value not given or given empty, the record not found, the
event or `hooks/lanes.json` not as Claude Code and `lane:up` write them, or a step no longer saying
its lane's sentence, is an error, not a drift: the call is stopped, or the subagent kept going once
as it ends, and it and you are told

```
<plugin>: lane cannot check <lane> on step <n> of <subagent>: <what is wrong>. Stop here and reply that <who must fix it>.
```

A lane taking a value given for the run is held once the script start_with runs first has run, as
the value comes with what it prints; until then start_with holds the subagent.

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
