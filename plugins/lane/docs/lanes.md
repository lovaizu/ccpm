# lane's lanes

Each lane lane can lay, under the action it watches, so your AI can tell which lanes to propose for
your plugin's steps and you can tell what each hook tells your subagent; and the proposal your AI
writes them in.

The sentence is what the step says, and what the hook tells the subagent on a drift. What the lane
takes goes where the sentence shows `<...>`. The hook tells the sentence when the subagent does what
the last column says.

What a lane takes is fixed in the step, such as `CHANGELOG.md`, or given for each run, written
`{<name>}`. A thing given for each run is the value under that name that the values port reads in
what the subagent is given: the prompt of the Agent call that started it, and each message a
SendMessage call sent to it after, the later over the earlier. So the hook holds a file added to the run while the
subagent works, as by an answer, from then on. The sentence `Write only {work}.` holds a subagent to
the files and folders its run's `work` names, whichever they are. A value given as `null` is the
caller saying there is none: each lane taking that name lets the call or the end through on that
run, with nothing told. A thing taken holds any text, a comma among the rest.

Claude Code hands a subagent's start no prompt, so lane keeps the prompt of each Agent call
starting a subagent of your plugin as the call is made, and gives it to the next run of that
subagent that starts. Where two such calls with differing prompts wait for their starts, a run
cannot tell its own until its call comes back with the run's `agentId`, and each lane taking a
value of it is an error meanwhile. A SendMessage call counts where its `to` is the run's
`agentId`.

| Action | Lane | Sentence | Told when the subagent |
|---|---|---|---|
| read | read_only | Read only `<input>`. | reads anything else |
| read | read_whole | Read `<input>` to its end. | gives its result with a part of it unread |
| write | write_only | Write only `<output>`. | writes anything else |
| write | in_form | Write `<output>` in the form of `<form>`. | writes it out of that form |
| run | run_only | Run only `<commands>`. | runs any other command |
| run | hold | Run `<commands>` only with the person's approval. | runs one of them, which Claude Code puts to the person |
| test | test_after | After changing `<output>`, pass `<test>`. | gives its result with a change not yet passed |
| follow | follow_routes | Start each subagent you are told to start, until you are told to start no more. | starts another subagent, or ends while a start is due |
| end | end_when | End only once `<output>` is made. | gives its result before |
| end | every_item | Answer every item of `<input>`. | gives its result with an item unanswered |

A subagent with rules reads files with Read and Grep, writes them with Write and Edit, and runs a
command with Bash only where a run_only, hold or test_after lane names it, or its result command
does. lane matches a command whole, as the step writes it, and reads no part of it. A command in any
other words is stopped and told the sentence and, on the next line, the commands it may run.

hold does not stop the command: lane answers Claude Code to ask the person, and Claude Code shows
its permission prompt with the sentence, even under `bypassPermissions`. In `claude -p` no one can
be asked, so Claude Code refuses the command.

The lanes of the end, read_whole, test_after, end_when and every_item, are checked as the subagent
gives its result, so `lay.py write` gives a subagent with one of them a result command on its last
step, `done` where no route names it. The guard checks them as the subagent runs that command, from
the calls it kept, and stops the command with each lane's sentence and, on the next line, what is
missing. It holds each in_form output there to its form again too, as a command its lanes name may
have written it. The result script is given no run's ID, so it checks the result alone, as
[the routes](routes.md#how-a-subagent-gives-its-result) say.

in_form takes the form by the path the subagent reads it by, as
`${CLAUDE_PLUGIN_ROOT}/<path in the plugin>`. The form is one of two kinds:

- a `.json` JSON Schema of the keywords Anthropic's structured outputs accept, which in_form holds
  a JSON output to, or each line of a `.jsonl` one;
- a `.md` Markdown template, whose headings and frontmatter keys in_form holds a Markdown output
  to.

read_only lets the subagent read, beside its inputs, the form each of its in_form lanes names: its
step tells it to write in that form, and the form, a file of your plugin, holds nothing of the
project's work.

read_only and write_only each take a file or a folder, and a folder lets the subagent read or write
anything under it. test_after's output may be a folder too, and a change of any file under it is a
change of the output. read_only and write_only check the path that Read, Grep, Write or Edit is
given, a Grep given none reading the folder it runs in; a command a run_only lane names reads and
writes what it does unchecked, so name only commands whose reads and writes you accept.

read_whole counts a file read to its end where the Read calls of the subagent, by their `offset`
and `limit`, have covered every line of it, a Read with no `limit` covering the 2000 lines the Read
tool reads by default. test_after counts a test passed where the test's command
came back without an error, and the output changes after it where a Write or Edit of a file under it
came later.

follow_routes takes nothing. `lay.py write` lays it from your proposal's routes on the
orchestrator's step, and lane tells the orchestrator each start, as [the routes](routes.md) say.

every_item reads its input's items at the items port, as the ports below say. It counts an item
answered where its ID stands as a word of its own in a file the subagent wrote in this run other
than the input, so `B-1` is answered by neither `B-12`, `B-1.2` nor `AB-1`. An item with no ID is
not counted, as no text tells an answer to it from any other.

## The proposal

Your AI writes the lanes it proposes as one JSON file, has `lay.py print` show them as they will be
laid, and once it approves them has `lay.py write` lay them from the same file, held to this JSON
Schema:

```json
{"type": "object", "required": ["plugin"], "additionalProperties": false,
 "anyOf": [{"required": ["subagents"]}, {"required": ["routes"]}],
 "properties": {
  "plugin": {"type": "string", "description": "your plugin's folder"},
  "routes": {"type": "object", "description": "your subagents' routes, as docs/routes.md gives them"},
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
        "lane": {"enum": ["read_only", "read_whole", "write_only", "in_form", "run_only",
                          "hold", "test_after", "end_when", "every_item"]},
        "takes": {"type": "array", "items": {"type": "string"}},
        "adapter": {"type": "string", "description": "hooks/adapters/<port>-<name>.py"}}}}}}}}}}}}
```

- A lane goes only on a sentence whose drift shows in a tool call or in how the subagent ends, and
  only where the step alone is not sure to hold.

  What the subagent only weighs no hook sees.
- A lane's `takes` are its things in the order of its places under
  [What each lane is given](#what-each-lane-is-given), one in each place but the last, which takes
  the rest, each written as the step writes it, a script or a command word for word. So in_form
  takes its output and then its forms, and test_after its output and then its tests.
- An adapter is named only where your text is in another form than lane's, as the ports below say.
- Routes are written under `routes`, held to the JSON Schema [the routes](routes.md#the-routes)
  give, and laid as a follow_routes lane on the orchestrator's step and a result command on the last
  step of each subagent they name. A proposal may hold routes alone, with no `subagents`.
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
| values | `{"texts": ["<the prompt>", "<each message sent after>", ...]}`, in the order they were sent | `{"values": {"<name>": ["<text>", ...]}}` or `{"values": {"<name>": null}}` | the JSON objects the texts hold, the whole text or each line that is one, the later over the earlier; a list for each of its texts, a text for itself, `null` for itself |
| items | `{"input": "<path>", "text": "<its text>"}` | `{"items": ["<ID>", ...]}` | each top-level item of a Markdown list beginning with an ID, such as `B-1`, `R33` or `KR1.1`, in bold, code or brackets or not |

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
  }
}
```

## What each lane is given

The guard first holds the event to the form Claude Code hands it, and `hooks/lanes.json` to the
form `lay.py write` writes it in. Then, before any lane's check, it holds what each lane is given to
the lane's IN, a JSON Schema. A lane is given two things:

- the texts put in each place of its sentence, with each `{<name>}` given for the run put in and
  its empty texts left out, one or more in each place;
- where its check rests on what the subagent did before, the calls the guard kept of it, where a
  call counts once it has come back, and a call a hook stopped is left out.

The layer holds a proposal's takes to the same IN, so a wrong take shows when the lanes are laid,
not on a run.

Anything not as these say is an error, not a drift. Errors include a value not given or given
empty, or of a run that cannot tell its prompt; an adapter failing, giving no answer in time or
answering out of its port; the event or `hooks/lanes.json` not as Claude Code and `lay.py write`
write them; a step no longer saying its lane's sentence; and a thing a lane takes that `lay.py write` would now refuse,
such as in_form's form gone. On an error the guard stops the call, or keeps the subagent going once
as it ends, and tells it and you

```
<plugin>: lane cannot check <lane> on step <n> of <subagent>: <what is wrong>. Ask the main conversation for the fix: <who must fix it>. Go on with the rest of your work meanwhile.
```

or, where the event or `hooks/lanes.json` is what is wrong, so no lane of the subagent is known,

```
<plugin>: lane cannot check the lanes of <subagent>: <what is wrong>. Ask the main conversation for the fix: <who must fix it>. Go on with the rest of your work meanwhile.
```

and, where the hook's command does not name your plugin as `lay.py write` writes it, so your plugin
is not known, the same headed `lane:` and naming `the lanes of this hook`.

The IN of a lane, `<place>` standing for each of its places below, and `calls` required only where
it rests on the calls kept:

```json
{
  "type": "object",
  "required": ["takes", "calls"],
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
    "calls": {"type": "array"}
  }
}
```

| Lane | Places | Rests on the calls kept |
|---|---|---|
| read_only | `input` | no |
| read_whole | `input` | yes |
| write_only | `output` | no |
| in_form | `output`, `form` | no |
| run_only | `commands` | no |
| hold | `commands` | no |
| test_after | `output`, `test` | yes |
| follow_routes | none | yes |
| end_when | `output` | no |
| every_item | `input` | yes |

## A subagent's part

Where your subagent's file is its entry, its frontmatter and a body naming its part, such as

```markdown
Your steps are in `${CLAUDE_PLUGIN_ROOT}/prompts/writer.md`, given to you as you start. Take them on what you are given.
```

its steps are those of the part, the one file under your plugin's `prompts/` the body names in
backticks. `lay.py print` shows the part's steps, `lay.py write` writes each lane's sentence into
them, and the guard reads them there. Where a body names no such file, or more than one, lane reads
the steps from the subagent's file itself.

Subagents whose entries name one part share its steps, and the part carries one set of sentences.
So `lay.py print` refuses a proposal where subagents sharing a part would lay different lanes on a
step of it, those it gives and those laid before alike, and names them and the step.

Once lanes are laid in the subagent, the guard gives it the part whole as it starts, through the
SubagentStart hook's `additionalContext`, with your plugin's folder put in place of
`${CLAUDE_PLUGIN_ROOT}`, as Claude Code does in the entry's body. So the subagent has its steps
before its first call, and no lane is needed for reading them. The part not there is an error,
which the guard tells in the form `<plugin>: lane cannot check the lanes of <subagent>: <what is
wrong>.` above.
