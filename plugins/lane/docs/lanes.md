# lane's lanes

Each lane lane can lay, under the action it watches, so your AI can tell which lanes to propose for
your plugin's steps and you can tell what each hook tells your subagent; and the proposal your AI
writes them in.

The sentence is what the step says, and what the hook tells the subagent on a drift. What the lane
takes goes where the sentence shows `<...>`. The hook tells the sentence when the subagent does what
the last column says.

What a lane takes is fixed in the step, such as `CHANGELOG.md`, or given for each run, written
`{<name>}`. A thing given for each run is the value under that name that the values port reads in
what the subagent is given: its prompt, what the script it first runs prints, and each message sent
to it after, the later over the earlier. So the hook holds a file added to the run while the
subagent works, as by an answer, from then on. The sentence `Write only {work}.` holds a subagent to
the files and folders its run's `work` names, whichever they are. A value given as `null` is the
caller saying there is none: each lane taking that name lets the call or the end through on that
run, with nothing told. A thing taken holds any text, a comma among the rest.

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

wait_for takes, after the approval, each command it holds back, as the step writes it. Its
sentence shows the approval alone.

in_form takes the form by the path the subagent reads it by: as
`${CLAUDE_PLUGIN_ROOT}/<path in the plugin>`, or by a name the subagent's entry says lies there, as
[a subagent's part](#a-subagents-part) says. The form is one of two kinds:

- a `.json` JSON Schema of the keywords Anthropic's structured outputs accept, which in_form holds
  a JSON output to, or each line of a `.jsonl` one;
- a `.md` Markdown template, whose headings and frontmatter keys in_form holds a Markdown output
  to.

read_only lets the subagent read, beside its inputs, the form each of its in_form lanes names: its
step tells it to write in that form, and the form, a file of your plugin, holds nothing of the
project's work.

read_only and write_only each take a file or a folder, and a folder lets the subagent read or write
anything under it. test_after's output may be a folder too, and a change of any file under it is a
change of the output. read_only and write_only tell which file a command reads or writes by the words naming it. Some
words do not settle which file they name: one holding `$` or a backquote, or a relative path after a
`cd` whose folder the words do not settle. The hook cannot tell whether such a file is an input or
an output, so it stops the call as one lane could not check. It tells the subagent the sentence and,
on the next line, that lane cannot tell which file is named there, and to name each file by its
path, without `$`, a backquote or a `cd` lane cannot follow. write_only lets a command write out of
the folder the subagent works in, as one throwing its output away in `/dev/null`, only where the
words settle that the file is out of it.

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
- A lane's `takes` are its things in the order of its places under
  [What each lane is given](#what-each-lane-is-given), each written as the step writes it, a script
  or a command word for word.
- An adapter is named only where your text is in another form than lane's, as the ports below say.
- A subagent the proposal gives has, once it is written, the proposal's lanes alone. Put in each
  lane that `lay.py up` says was laid before in it and that you keep, as `lay.py up` says the lane.

  `lay.py write` takes the sentence of each lane left out out of its step.
- Keep the proposal as `.lane/<yyyymmdd>-<plugin>/<plugin>.json` at the root of the repository
  your plugin is in, the nearest folder above it holding `.git`, or your plugin's folder where none
  does, and its adapters beside it.

  Your AI reads and writes them with its tools, and Claude Code lets it do so without asking only
  inside the folder it works in; `lay.py write` removes them, and their folder, once they are
  written into your plugin.

## The ports

Where a lane reads your plugin's text, it reads it at a port: given JSON, the port gives back JSON,
each held to the JSON Schema below. lane reads one form at each port. Where your text is in another
form, your plugin has an adapter for it:

- The adapter is a Python 3 script. It is given the port's JSON on stdin and prints the port's JSON
  on stdout.
- Beside it, `<port>-<name>.json` holds the cases it must give: a list of
  `{"given": <the port's JSON in>, "gives": <the port's JSON out>}`, at least one for each form the
  text takes and one that gives nothing.
- The adapter is part of the proposal. Your AI keeps it as `<plugin>/adapters/<port>-<name>.py` in
  the folder the proposal is in, and names it by its path in your plugin,
  `hooks/adapters/<port>-<name>.py`. It names it on the lane reading the port, or, for the values
  port, on the subagent, as every lane of the subagent reads its values.
- `lay.py print` runs the adapter on each of its cases before it prints the proposal, and shows the
  adapter in the print. `lay.py write` writes it with its cases into your plugin's
  `hooks/adapters/` once your AI approves it.
- `lay.py` and the guard run the adapter with `CLAUDE_PLUGIN_ROOT` set to your plugin's folder,
  beside the proposal as in your plugin, so it finds your plugin's other files from there.
- On a run, the guard runs the adapter within the hook's time. An adapter failing, giving no answer
  in time or answering out of its port is an error, as below.

| Port | Given | Gives | lane's form |
|---|---|---|---|
| values | `{"texts": ["<the prompt>", "<each print of a start_with script or message sent after>", ...]}`, in the order the subagent's record holds them | `{"values": {"<name>": ["<text>", ...]}}` or `{"values": {"<name>": null}}` | the JSON objects the texts hold, the whole text or each line that is one, the later over the earlier; a list for each of its texts, a text for itself, `null` for itself |
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

The guard first holds the event to the form Claude Code hands it, and `hooks/lanes.json` to the
form `lay.py write` writes it in. Then, before any lane's check, it holds what each lane is given to
the lane's IN, a JSON Schema. A lane is given two things:

- the texts put in each place of its sentence, with each `{<name>}` given for the run put in and
  its empty texts left out, one or more in each place;
- where its check rests on what the subagent did before, its record, where a call counts once it
  has come back, and a call a hook stopped is left out.

The layer holds a proposal's takes to the same IN, so a wrong take shows when the lanes are laid,
not on a run.

Anything not as these say is an error, not a drift. Errors include a value not given or given
empty; an adapter failing, giving no answer in time or answering out of its port; the record not
found; the event or `hooks/lanes.json` not as Claude Code and `lay.py write` write them; a step no
longer saying its lane's sentence; and a thing a lane takes that `lay.py write` would now refuse,
such as in_form's form gone. On an error the guard stops the call, or keeps the subagent going once
as it ends, and tells it and you

```
<plugin>: lane cannot check <lane> on step <n> of <subagent>: <what is wrong>. Ask the main conversation for the fix: <who must fix it>. Go on with the rest of your work meanwhile.
```

or, where the event or `hooks/lanes.json` is what is wrong, so no lane of the subagent is known,

```
<plugin>: lane cannot check the lanes of <subagent>: <what is wrong>. Ask the main conversation for the fix: <who must fix it>. Go on with the rest of your work meanwhile.
```

and, where the hook's command does not name the subagent as `lay.py write` writes it, so neither
your plugin nor the subagent is known, the same headed `lane:` and naming `the lanes of this hook`.

The guard holds a lane taking a value given for the run once the script start_with runs first has
run and come back, as the value comes with what the script prints. Until then start_with holds the
subagent, and the guard lets through the call that runs the script.

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

## A subagent's part

Where your subagent's file is its entry, its frontmatter and a body having it read its part first,
such as

```markdown
Read `${CLAUDE_PLUGIN_ROOT}/prompts/writer.md` whole first, and take its steps on what you are given.
```

its steps are those of the part, the one file under your plugin's `prompts/` the body names in
backticks. `lay.py print` shows the part's steps, `lay.py write` writes each lane's sentence into
them, and the guard reads them there. Where a body names no such file, or more than one, lane reads
the steps from the subagent's file itself.

Claude Code puts your plugin's folder in for `${CLAUDE_PLUGIN_ROOT}` in the entry's body alone, not
in the part the subagent reads, so the part names each script, file or folder by its name alone,
and the body says where each lies, before the sentence naming the part, as
`` `<name>` below is `<what it stands for>` ``, such as

```markdown
`writer.py` below is `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/writer.py"`, run from where you start.
`entry.json` below is `${CLAUDE_PLUGIN_ROOT}/forms/entry.json`.
```

A lane takes the name as the step says it, as in `` First run `writer.py start`. ``, and its
sentence shows it so. Where a thing it takes begins with a name the body binds, the guard and the
layer read the name as the body says it stands for. So start_with holds the subagent to run the
script where the body says it lies, and in_form reads the form there.

Once lanes are laid in the subagent, the guard holds it to read the part whole before anything
else, with nothing in the proposal for it, as the sentence is the entry's and not a step's. The
guard lets a Read of the part go on, without holding its lanes on it. It stops any other call made
before the part is read to its end, and tells the subagent the entry's sentence, headed by your
plugin's name, as start_with and read_whole tell theirs. The part not there, or the subagent's
record not found, is an error, which the guard tells in the form
`<plugin>: lane cannot check the lanes of <subagent>: <what is wrong>.` above.
