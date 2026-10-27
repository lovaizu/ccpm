# Calling turn

What a step of your plugin gives turn and what it gets back, so the step's text can be written to
call it: the checklist, the CCS, the call, the questions, a stop and the result.

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
the work and the AI that reads it each run that, so a gap one finds is not a difference in what each
chose to run.

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

Called again with the same call, a run that stopped goes on from where it stopped. Stop a run with
TaskStop.

## Questions and answers

What only the user can decide comes to the calling AI as a message, each question with the answer
turn recommends and the items it settles: a point the CCS leaves open, met before or while the work
is made, or a gap the AI that made the work holds outside the purpose and the AI that reads it still
holds:

```json
{"questions": [{"question": "...", "recommended": "...",
                "items": [{"checklist": "...", "item": "B-5"}]}]}
```

Put each to the user, keep the answer where the CCS names it, such as its decisions file, adding to
the CCS any file the answer brings, and send the answer to turn in plain words; the run goes on
with it from where it stood, taking in the files the CCS names then.

## A stop for what lies outside the work

Where an AI of the run cannot go on for what lies outside the work, such as a tool missing, a
permission not given or a network blocked, the run stops with no way round it and turn returns:

```json
{"stopped": {"tried": "...", "confirmed": "...", "not_confirmed": "...", "needs": "..."}}
```

Put what it needs to the user; once it is there, call turn again with the same call, and the run
goes on where it stopped.

## The result

```json
{"work": ["README.md"],
 "items": [{"checklist": "checklists/readme.md", "item": "B-2",
            "good": "...", "lines": ["<path>:<from>-<to>"]},
           {"checklist": "checklists/readme.md", "item": "B-3",
            "parts": [{"part": "<path>:<from>-<to>", "good": "...",
                       "lines": ["<path>:<from>-<to>"]}]}],
 "chosen": [{"chosen": "...", "why": "..."}]}
```

- `items`: each item's Good with the lines of the work that give it; an item whose Scope is
  `each part` gives them under `parts`, one for every part of the work, its lines inside that
  part.
- `chosen`: each choice the work rests on that the CCS and the files it names leave open, made by
  the AI that made it, with why; `[]` where none. Show them to the user, as no one asked them.
