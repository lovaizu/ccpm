# Calling turn

What a step of your plugin gives turn and what it gets back, so the step's text can be written to
call it: the checklist, the CCS, the call, the questions and the result.

## The checklist

turn reads an item as a heading of the third level whose text begins with its ID, capitals, a
hyphen and a number, then a colon, followed by a blank line and the line saying where in the work
it is answered:

```markdown
### B-1: Who it is for

Scope: its part

On opening it, can the reader tell whether the project is for them?
```

- `Scope: its part`: answered at the lines that give it.
- `Scope: each part`: answered in every part of the work on its own: in Markdown, the title and
  opening as one part and each section under a heading of the second level as another; any other
  file whole.
- `Scope: whole`: answered of the work at once.

An item may say, on a line beginning `Tried by:`, what is run for it and how far; the AI that makes
the work and the AI that reads it each run that, so an item one finds without Good is not a
difference in what each chose to run.

Headings in the frontmatter or in a code fence are not items. A checklist with no item, or an item
without its `Scope` line, stops the run with what to fix.

## The CCS

A JSON object of parts, each a list of entries, each entry one kind and its value as text, the
shape [ACC](https://arxiv.org/abs/2601.11653) gives an AI's state. The parts and the kinds are your
plugin's names; the call says which kinds hold what turn needs. Each entry whose value is a file or
folder that is there is given to turn's agents to read.

## The call

Start the `turn:up` agent in the background with the call as JSON, from the main conversation or
from an agent it started:

```json
{"ccs": "<path>", "result": "<path>",
 "kind": {"work": "<kind>", "checklist": "<kind>", "receiver": "<kind>",
          "use": "<kind>", "has": "<kind>"},
 "test": "<command> or null"}
```

- `ccs`: the CCS; `result`: where turn writes the result.
- `kind`: the kind in the CCS of the files the work is, of its checklists, of its receiver, the one
  it is for, of what the receiver uses it for, and of what the receiver has with it, such as `.`
  for the whole repository. Each needs at least one entry.
- `test`: the one command that checks the work, such as `sh dev/check.sh`, joining every check into
  one; `null` where the work has none.

Stop a run with TaskStop. Called again with the same call, a run goes on from what it had made: the
work at its paths, and its agents' last replies, kept in `.turn/` at the top of your repository.

## Questions and answers

What only the user can decide comes to the main conversation as a message from turn's AI that makes
the work, whether the calling AI is the main conversation or an agent below it. It comes as soon as
that AI meets it, before or while the work is made: a point the CCS leaves open, a file the work
needs that the CCS does not name, or something outside the work, such as a tool missing or a
permission not given. Each message is one question, with the answer recommended and the items that
wait on it:

```json
{"question": "...", "recommended": "<the answer recommended, and why, in one sentence>",
 "items": [{"checklist": "...", "item": "B-5"}]}
```

Put it to the user, keep the answer where the CCS names it, such as its decisions file, adding to
the CCS any file the answer brings, and send the answer in plain words with SendMessage to the
agent that asked, by the ID shown with its message. It takes in the files the CCS names then, and
makes what waited on the answer; the rest of the work is made meanwhile.

## The result

```json
{"work": ["README.md"],
 "items": [{"checklist": "checklists/readme.md", "item": "B-2",
            "lines": ["<path>:<from>-<to>"]}],
 "left": [{"checklist": "checklists/readme.md", "item": "B-4", "need": "..."}],
 "chosen": [{"chosen": "...", "why": "..."}]}
```

- `items`: each item with the lines of the work that give its Good, as the AI that read the work
  in its receiver's place gave them; for an item whose Scope is `each part`, at least one range in
  every part of the work, each inside one part.
- `left`: each item that AI found no Good for once the work was mended as far as the two AIs
  could, with what the receiver would need to get it, in one sentence; `[]` where none. The work
  is mostly made by then, so make each yourself, asking the user only what is theirs to decide.
- `chosen`: each choice the work rests on that the CCS and the files it names leave open, made by
  the AI that made it, with why; `[]` where none. Show them to the user, as no one asked them.
