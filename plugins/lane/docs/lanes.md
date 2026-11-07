# lane's lanes

This page gives each lane that lane can lay, under the action it watches, and the proposal your AI
writes them in. With it, your AI can tell which lanes to propose for your plugin's steps, and you
can tell what lane's check tells your subagent.

The sentence is what the step says. The check tells the subagent the sentence on a drift, that is,
when the subagent does what the last column says. What the lane takes goes where the sentence shows
`<...>`.

A newer lane may word a sentence it lays in other words. `lay.py up` and `lay.py write` then put
the new words in place of the old ones that lane laid in your steps, and leave every other word as
it was. The check tells the sentence in the new words, so it stops each call of a subagent whose
step still says the old ones. Words that lane never laid are yours, and lane leaves them.

What a lane takes is either fixed in the step, such as `CHANGELOG.md`, or given for each start of
the subagent, written `{<name>}`. A thing given for each start may be a whole take, or, in a
command, a part of it, as below. It is the value under that name that the values port reads in
what the subagent is given: the prompt of the Agent call that started it, and each message a
SendMessage call sent to it after, the later over the earlier. So the check holds a file added to
the start while the subagent works, as by an answer, from then on. The sentence `Write only {work}.`
holds a subagent to the files and folders its start's `work` names, whichever they are. A value
given as `null` is the caller saying there is none: each lane taking that name lets the call or the
end through on that start, with nothing told. A thing taken holds any text, a comma among the
rest.

Each subagent with lanes, or that routes name, sets `background: true` in its frontmatter.
`lay.py print` refuses a proposal where one does not. Claude Code then runs it in the background
however it is started ([background](https://code.claude.com/docs/en/sub-agents)), and the Agent
call that starts it comes back at once with the `agentId` of that start. lane keeps the call's
prompt under that ID as the call comes back. So lane holds each of many starts of one subagent at
once to its own values. A subagent starts a moment before its call comes back. So a call it makes
that needs a value waits up to 3 seconds for the Agent call to come back, and is an error where it
has not come back by then. A SendMessage call counts where its `to` is the start's `agentId`.
Within a run of your skill, lane stops one that the main conversation sends to a start that ended
with no result, as [the routes](routes.md#how-a-subagent-gives-its-result) say.

| Action | Lane | Sentence | Told when the subagent |
|---|---|---|---|
| read | read_only | Read only `<input>`. | reads anything else |
| read | read_whole | Read `<input>` to its end. | makes the trace of a later step first, or gives its result with a part of it unread, as its trace kind holds it |
| write | write_only | Write only `<output>`. | writes anything else |
| write | write_step | Make `<output>`. | makes the trace of a later step first, or gives its result before, as its trace kind holds it |
| write | in_form | Write `<output>` in the form of `<form>`. | writes it out of that form |
| write | edit_only | Once `<output>` is made, change it only with Edit. | writes it whole with Write once it is there, or with NotebookEdit |
| run | run_only | Run only `<commands>`. | runs any other command |
| run | run_step | Run `<commands>`. | makes the trace of a later step first, or gives its result before, as its trace kind holds it |
| run | hold | Run `<commands>` only with the person's approval. | runs one of them, which Claude Code puts to the person |
| test | test_after | After changing `<output>`, pass `<test>`. | gives its result with a change not yet passed |
| follow | follow_routes | Start each subagent you are told to start, until you are told to start no more. | starts another subagent, or ends while a start is due |
| end | end_when | End only once `<output>` is made. | gives its result before |
| end | every_item | Answer every item of `<input>`. | gives its result with an item unanswered |

A subagent with lanes reads files with Read and Grep, and writes them with Write and Edit. A
subagent with a run_only lane runs a command with Bash only where a run_only, hold or test_after
lane names it, or its result command does. lane matches a command whole, as the step writes it, and
reads no part of it. lane stops a command in any other words, and tells the subagent the sentence
and, on the next line, the commands it may run. A subagent with no run_only lane runs any command,
but a held one goes to the person, and a run of its result script on a result it may not give is
stopped with the sentence of its last step and the commands it gives its results by.

Only the main conversation starts a subagent of your plugin. lane stops a subagent with lanes, or
that your routes name, as it starts one with the Agent tool, or a subagent or a dependency's skill
that your routes name, and tells it

```
<plugin>: Start no subagent of this plugin: only the main conversation starts one, with what the plugin gives it. Reply with what you would pass on, and end.
```

A subagent that starts another passes on what it chooses, not what your plugin gives that start.

For each subagent with a run_only lane, `lay.py print` lists the commands it may run, on the line
`commands`. Where a step of such a subagent names in backticks a command that it may not run,
`lay.py print` says so beside that step's number, such as
``step 3  names `git status`, which writer may not run``. Add the command to a run_only lane before
you approve, or the check stops it on every run.

A command may be one that a skill of a dependency names. A dependency is a plugin that your plugin
declares in the `dependencies` of its own `.claude-plugin/plugin.json`
([dependencies](https://code.claude.com/docs/en/plugins/dependencies)). The skill names its script
by its own `${CLAUDE_PLUGIN_ROOT}`, which Claude Code fills with the folder it installed the
dependency in. No hook of Claude Code's is told that folder. So a run_only, hold or test_after lane writes the
folder as `${dependency:<name>}`, the dependency's name as your manifest declares it, such as
`python3 ${dependency:checker}/scripts/check.py CHANGELOG.md`. lane takes that part as any folder,
from the root, that holds `.claude-plugin/plugin.json` whose `name` is that dependency, and matches
the rest of the command whole. It reads the dependency from your plugin's own manifest alone, not
from a marketplace's entry. `lay.py print` refuses a lane that names a dependency the manifest
does not declare, or that names one in a place other than a command. lane tells a stopped subagent,
on the line after the commands it may run, what `${dependency:<name>}` stands for.

A command of a run_only, hold or test_after lane may hold a value given for the start as one part,
written `{<name>}` with no `$` before it, its name of letters, digits, `_` and `-`, such as `python3
${CLAUDE_PLUGIN_ROOT}/scripts/check.py {file}`. lane matches the rest whole. It matches that part to
each text of the start's own value of the name, put in as one word of the shell: as it is, where it
holds no other character than a letter, a digit or one of `@%+=:,./-_`, and in single quotes
otherwise, as Python's `shlex.quote` gives it. So the start given `{"file": "my notes.json"}` runs
`python3 <your plugin's folder>/scripts/check.py 'my notes.json'`. No value adds a word to the
command, such as by a blank or a `;`, or stands for anything but itself. lane tells a stopped
subagent, on the line after the sentence, each command it may run with its value put in. Braces that
name no value, as in `find . -exec ls {} +` or `${HOME}`, are the command's own. `lay.py print`
refuses a value held as a part of any take but a command, as lane matches only a command by its
parts.

hold does not stop the command: lane answers Claude Code to ask the person, and Claude Code shows
its permission prompt with the sentence, even under `bypassPermissions`. In `claude -p` no one can
be asked, so Claude Code refuses the command.

read_whole, write_step and run_step are of the trace kind: each names the call that shows its step
done, a file read to its end, a file made, or a command run, in this start. lane holds a subagent's
steps in their order by these traces, and never by what a file says:

- A step list is the numbered list of the subagent's steps, or a list your steps adapter gives, as
  [the ports](#the-ports) say. The step due in a list is the first whose traces haven't all come
  back. A step with no lane of the trace kind is passed over, as no call shows it done.
- lane stops a call that is the trace of a later step of a list while its step due isn't done, and
  tells the subagent what the step due says and, on the next line, what of its trace is missing.
  Steps of two lists have no order between them.
- lane stops the subagent's result command while any step's trace hasn't come back, and tells the
  first such step the same way.
- Lay a trace only on a step that every run takes. A step that some runs rightly leave out, such as
  one for a case that doesn't always come up, carries no trace, or those runs would be stopped.

run_step's commands are commands the subagent may run, beside those of its run_only lanes.

lane checks the lanes of the end, test_after, end_when and every_item, and each trace, as the
subagent gives its result. So `lay.py write` gives a subagent with one of them a result command on
its last step, with the result `done` where no route names it. The guard, the check script that lane's hooks
run, checks them as the subagent runs that command, from the calls it kept. It stops the command
with each lane's sentence and, on the next line, what is missing. It holds each in_form output there
to its form again too, as a command its lanes name may have written it. The result script is given
no start's ID, so it checks only the result, as [the
routes](routes.md#how-a-subagent-gives-its-result) say.

in_form takes the form by the path the subagent reads it by, as
`${CLAUDE_PLUGIN_ROOT}/<path in the plugin>`. The form is one of two kinds:

- a `.json` JSON Schema of the keywords Anthropic's structured outputs accept, which in_form holds
  a JSON output to, or each line of a `.jsonl` one;
- a `.md` Markdown template, whose headings and frontmatter keys in_form holds a Markdown output
  to.

read_only lets the subagent read, beside its inputs, the form each of its in_form lanes names: its
step tells it to write in that form, and the form, a file of your plugin, holds nothing of the
project's work. It lets the subagent read its own part too, the file its steps lie in, which lane
gives it whole as it starts: reading what it was given breaks no rule.

read_only and write_only each take a file or a folder, and a folder lets the subagent read or write
anything under it. A path of read_only, write_only or read_whole may begin with
`${CLAUDE_PLUGIN_ROOT}`, such as `${CLAUDE_PLUGIN_ROOT}/core/domain/how.md`, and lane puts your
plugin's folder in for it, as it does in a command, so a step can name a file of your plugin by
the path the subagent reads it by. test_after's output may be a folder too, and a change of any
file under it is a change of the output. read_only and write_only check the path that Read, Grep,
Write or Edit is given, a Grep given none reading the folder it runs in. A command a run_only lane
names reads and writes what it does unchecked, so name only commands whose reads and writes you
accept.

edit_only lets a Write make its output while the output is not there, and lets only Edit change it
once it is. Claude Code lets an Edit go only after a Read of the file, so the subagent sees what it
changes, while a Write puts a whole new text in place of one it need not have read. Take it for a
file whose shape the subagent must see each time it changes a part, such as a tree whose nesting
holds what each part serves. A command that writes the output is stopped only where a run_only
lane holds the subagent, which then runs only the commands its lanes name, so lay one beside
edit_only. An output may be a folder, under which edit_only holds each
file alike.

read_whole counts a file read to its end where the Read calls of the subagent, by their `offset`
and `limit`, have covered every line of it, a Read with no `limit` covering the 2000 lines the Read
tool reads by default. test_after counts a test passed where the test's command came back without
an error. It counts the output changed after the test where a Write or Edit of a file under it came
later.

follow_routes takes nothing. `lay.py write` lays it from your proposal's routes on the step of
the skill they start from, and lane tells the main conversation each start, as
[the routes](routes.md) say.

every_item reads its input's items at the items port, as the ports below say. Its adapter is given
the start's values too, so it can read the items from where your plugin keeps them, such as the
nodes that the change a start names touches in a design tree. every_item counts an item answered
where its ID stands as a word of its own in a file that the subagent wrote in this start, other than
the input, so `B-1` is answered by neither `B-12`, `B-1.2` nor `AB-1`. A change to the input restarts
the count: only a file written after the subagent's last change of the input answers, as the change
may have changed the items. every_item does not
count an item with no ID, as no text tells an answer to it from any other.

## The proposal

Your AI writes the lanes it proposes in one JSON file. It has `lay.py print` show them as they
will be laid, and once it approves them, has `lay.py write` lay them from the same file. The file
is held to this JSON Schema:

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
    "steps_adapter": {"type": "string", "description": "hooks/adapters/steps-<name>.py"},
    "results": {"type": "array", "minItems": 1, "items": {"type": "string", "pattern": "^[a-z][a-z0-9_-]*$"},
                "description": "the results it gives where no route is from it, as a plugin that uses yours routes them"},
    "steps": {"type": "array", "items": {
     "type": "object", "required": ["step", "lanes"], "additionalProperties": false,
     "properties": {
      "step": {"type": "integer", "description": "its number in the subagent's Steps"},
      "lanes": {"type": "array", "minItems": 1, "items": {
       "type": "object", "required": ["lane", "takes"], "additionalProperties": false,
       "properties": {
        "lane": {"enum": ["read_only", "read_whole", "write_only", "write_step", "in_form", "edit_only",
                          "run_only", "run_step", "hold", "test_after", "end_when", "every_item"]},
        "takes": {"type": "array", "items": {"type": "string"}},
        "adapter": {"type": "string", "description": "hooks/adapters/<port>-<name>.py"}}}}}}}}}}}}
```

- A lane goes only on a sentence whose drift shows in a tool call or in how the subagent ends, and
  only where the step alone is not sure to hold.

  No hook sees what the subagent only weighs.
- A lane's `takes` are its things in the order of its places under
  [What each lane is given](#what-each-lane-is-given). Each place takes one, and the last takes the
  rest. Write each as the step writes it, a script or a command word for word. So in_form
  takes its output and then its forms, and test_after its output and then its tests.
- An adapter is named only where your text is in another form than lane's, as the ports below say.
- `steps_adapter` names the adapter of the steps port, where a subagent's steps aren't a numbered
  list of its own, such as the practices of the intents it carries out, read from your best
  practices given the start's values. Each step list it gives is held in its order, as the lanes of
  the trace kind say, beside the numbered list of the subagent's file. A subagent with a steps
  adapter may give `steps` as an empty list.
- `results` names the results a subagent gives where no route of your plugin is from it, such as
  `["asks", "done"]` for a subagent that ends to wait for an answer or with its work done. A plugin
  that depends on yours can then route it by those results, as
  [the routes](routes.md#a-subagent-of-a-dependency) say. `lay.py write` lays the result command of
  each on its last step, in place of `done`. `lay.py print` refuses `results` on a subagent your
  routes are from, as the routes give its results.
- Your AI writes routes under `routes`, held to the JSON Schema
  [the routes](routes.md#the-routes) give. `lay.py write` lays them as a follow_routes lane on the
  skill's step and a result command on the last step of each subagent they name. A
  proposal may hold routes alone, with no `subagents`.
- Once written, a subagent the proposal gives has the proposal's lanes alone. So put in each lane
  that `lay.py up` says was laid in it before and that you keep, as `lay.py up` says the lane.

  `lay.py write` removes from its step the sentence of each lane left out.
- Keep the proposal as `.lane/<yyyymmdd>-<plugin>/<plugin>.json` at the root of the repository
  your plugin is in, the nearest folder above it holding `.git`, or your plugin's folder where none
  does, and its adapters beside it.

  Your AI reads and writes them with its tools, and Claude Code lets it do so without asking only
  inside the folder it works in. `lay.py write` removes them, and their folder, once it has written
  them into your plugin.

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
| steps | `{"values": {<the start's values>}}` | `{"lists": [{"list": "<name>", "steps": [{"says": "<what the step says>", "lanes": [{"lane": "<a lane of the trace kind>", "takes": ["<text>", ...]}]}, ...]}, ...]}` | none: only an adapter reads it |
| items | `{"input": "<path>", "text": "<its text>", "values": {<the start's values>}}` | `{"items": ["<ID>", ...]}` | each top-level item of a Markdown list beginning with an ID, such as `B-1`, `R33` or `KR1.1`, in bold, code or brackets or not, the values unread |

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
    "in": {"type": "object", "required": ["input", "text", "values"], "additionalProperties": false,
           "properties": {"input": {"type": "string"}, "text": {"type": "string"},
                          "values": {"type": "object",
                                     "additionalProperties": {"type": ["array", "null"], "items": {"type": "string"}}}}},
    "out": {"type": "object", "required": ["items"], "additionalProperties": false,
            "properties": {"items": {"type": "array", "items": {"type": "string"}}}}
  },
  "steps": {
    "in": {"type": "object", "required": ["values"], "additionalProperties": false,
           "properties": {"values": {"type": "object",
                                     "additionalProperties": {"type": ["array", "null"], "items": {"type": "string"}}}}},
    "out": {"type": "object", "required": ["lists"], "additionalProperties": false,
            "properties": {"lists": {"type": "array", "items": {
             "type": "object", "required": ["list", "steps"], "additionalProperties": false,
             "properties": {"list": {"type": "string"}, "steps": {"type": "array", "items": {
              "type": "object", "required": ["says", "lanes"], "additionalProperties": false,
              "properties": {"says": {"type": "string"}, "lanes": {"type": "array", "items": {
               "type": "object", "required": ["lane", "takes"], "additionalProperties": false,
               "properties": {"lane": {"enum": ["read_whole", "run_step", "write_step"]},
                              "takes": {"type": "array", "items": {"type": "string"}, "minItems": 1}}}}}}}}}}}}
  }
}
```

## What each lane is given

The guard first holds the event to the form Claude Code hands it, and `hooks/lanes.json` to the
form `lay.py write` writes it in, its routes to the order of results `lay.py print` asks of them,
as [the routes](routes.md#runs-at-once) say. Then, before any lane's check, it holds what each lane
is given to the lane's IN, a JSON Schema. A lane is given two things:

- the texts put in each place of its sentence, with each `{<name>}` given for the start put in and
  its empty texts left out, one or more in each place;
- where its check rests on what the subagent did before, the calls the guard kept of it, where a
  call counts once it has come back, and a call the check stopped is left out.

`lay.py` holds a proposal's takes to the same IN, so a wrong take shows when the lanes are laid,
not on a run.

Anything not as these say is an error, not a drift. Errors include a value not given or given
empty, or of a start that has not come back with its `agentId` within 3 seconds; an adapter
failing, giving no answer in time or answering out of its port; the event or `hooks/lanes.json` not
as Claude Code and `lay.py write` write them; a subagent's file no longer setting
`background: true`; a step no longer saying its lane's sentence; and a thing a lane takes that
`lay.py write` would now refuse, such as in_form's form gone. On an error the guard stops the
call, or keeps the subagent going once as it ends, and tells it and you

```
<plugin>: lane cannot check <lane> on step <n> of <subagent>: <what is wrong>. Ask the main conversation for the fix: <who must fix it>. Go on with the rest of your work meanwhile.
```

or, where the event, `hooks/lanes.json` or the subagent's file is what is wrong, so no lane of the
subagent can be checked,

```
<plugin>: lane cannot check the lanes of <subagent>: <what is wrong>. Ask the main conversation for the fix: <who must fix it>. Go on with the rest of your work meanwhile.
```

and, where the hook's command does not name your plugin as `lay.py write` writes it, so your plugin
is not known, the same headed `lane:` and naming `the lanes of this hook`.

Within a run of your skill, where lane cannot check the run, such as the routes laid or a start's
record, it tells the main conversation, and you beside it,

```
<plugin>: lane cannot check the routes of <skill>: <what is wrong>. Tell the user: <who must fix it>.
```

as the main conversation is the one that tells you. Where the skill's step no longer says the
routes' sentence, it names `follow_routes on step <n> of <skill>` in place of the routes, and no run
begins.

Here is the IN of a lane. `<place>` stands for each of its places below, and `calls` is required
only where the lane rests on the calls kept:

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
| write_step | `output` | yes |
| in_form | `output`, `form` | no |
| edit_only | `output` | no |
| run_only | `commands` | no |
| run_step | `commands` | yes |
| hold | `commands` | no |
| test_after | `output`, `test` | yes |
| follow_routes | none | yes |
| end_when | `output` | no |
| every_item | `input` | yes |

## A subagent's part

Your subagent's file may be only its entry: its frontmatter and a body naming its part, such as

```markdown
Your part is in `${CLAUDE_PLUGIN_ROOT}/domain/writer.md`, given to you as you start. Take it on what you're given.
```

Then its steps are those of the part: the one Markdown file under your plugin's `domain/` that the
body names in backticks, where [the plugin best
practice](../../rn/domain/best-practices/plugin/best-practice.md#q1) keeps the work's knowledge.
The part's name need not be the subagent's. lane also reads a part under `prompts/` or
`core/roles/`, where plugins laid before kept theirs. Move such a part to `domain/` when you next
lay the plugin's lanes. `lay.py print` shows the part's steps, `lay.py write`
writes each lane's sentence into them, and the guard reads them there. Where a body names no such
file, or more than one, lane reads the steps from the subagent's file itself.

Subagents whose entries name one part share its steps, and the part carries one set of sentences.
So `lay.py print` refuses a proposal where subagents sharing a part would lay different lanes on a
step of it, those it gives and those laid before alike, and names them and the step.

Once lanes are laid in the subagent, the guard gives it the part whole as it starts, through the
SubagentStart hook's `additionalContext`, with your plugin's folder put in place of
`${CLAUDE_PLUGIN_ROOT}`, as Claude Code does in the entry's body. Beside the part, it gives each
sentence that no step says, as where the part holds no numbered list, such as the result command
of its last step, and the step lists that its steps adapter gives. Claude Code 2.1.317 sends
SubagentStart before the Agent call that started the subagent comes back with its prompt. So the
guard gives those step lists only where the prompt is kept already. It holds the steps in their
order either way. So the subagent has its steps
before its first call, and no lane is needed for reading them. Where the part is missing, that is
an error, and the guard tells it in the form
`<plugin>: lane cannot check the lanes of <subagent>: <what is wrong>.` above.
