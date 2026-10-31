# Calling turn

What a step of your plugin gives turn and what it gets back, so you can write the step's text to
call it: the checklist, the CCS, the call, the questions and the result.

## The checklist

turn reads an item as a heading of the third level whose text begins with its ID, capitals, a
hyphen and a number, then a colon:

```markdown
### Q-1: Whether the project is for them

On opening it, can the reader tell whether the project is for them?
```

Headings in the frontmatter or in a code fence are not items. turn stops the run on a checklist
with no item, saying what to fix.

turn's AIs answer each item at the lines of the work that give it. An item your call asks of each
part is answered in every part of the work on its own. In Markdown, the title and opening are one
part, and each section under a heading of the second level is another; any other file is one part.
A folder of the work is each file in it, at any depth, each split the same way; a file that is not
text has no part.

## The CCS

A CCS is a JSON object of parts, each a list of entries, each entry one kind and its value as text,
the shape [ACC](https://arxiv.org/abs/2601.11653) gives an AI's state. The parts and the kinds are
your plugin's names, and the call says which kinds hold what turn needs.

turn's AI that makes the work reads the CCS and each file or folder that an entry names and that is
there. The AI that reads the work in the receiver's place reads only the work, what the receiver
has and the checklists.

## The call

Start the `turn:up` agent in the background with the call as JSON, from the main conversation or
from an agent it started:

```json
{"ccs": "<path>", "result": "<path>",
 "kind": {"work": "<kind>", "checklist": "<kind>", "receiver": "<kind>",
          "use": "<kind>", "has": "<kind>", "each": "<kind>"},
 "test": "<command> or null"}
```

- `ccs`: the CCS; `result`: where turn writes the result.
- `kind`: the kind in the CCS of each of these:
  - `work`: the files or folders the work is. turn's AI that makes the work writes only within
    them, and in a folder chooses each file, its name and what it holds;
  - `checklist`: its checklists;
  - `receiver`: its receiver, the one it is for;
  - `use`: what the receiver uses it for;
  - `has`: what the receiver has with it, such as `.` for the whole repository;
  - `each`: the items asked of each part, each as `<checklist path> <ID>`, such as
    `checklists/readme.md Q-3`.

  Each kind but `each` needs at least one entry. Give no entry of `each` where no item is asked of
  each part. Once the run is going, `has` may have none, as where an answer moves all the receiver
  has into the work.
- `test`: the one command that checks the work, such as `sh dev/check.sh`, joining every check into
  one; `null` where the work has none.

You stop a run with TaskStop. Called again with the same call, turn goes on from what the run had
made: the work at its paths, and its AIs' last replies, which it keeps in `.turn/` at the top of
your repository.

## Questions and answers

What only the user can decide comes to the main conversation as a message from turn's AI that makes
the work, whether the calling AI is the main conversation or an agent below it. That AI sends it as
soon as it meets it, before or while it makes the work: a point the CCS leaves open, a file the work
needs out of the files and folders the CCS names, or something outside the work, such as a tool
missing or a permission not given. Each message is one question, with the answer recommended and
the items that wait on it:

```json
{"question": "...", "recommended": "<the answer recommended, and why, in one sentence>",
 "items": [{"checklist": "...", "item": "Q-5"}]}
```

Put it to the user, and keep the answer where the CCS names it, such as its decisions file. Add to
the CCS any file the answer brings. Then send the answer in plain words with SendMessage to the
agent that asked, by the ID shown with its message. That agent takes in the files the CCS names
then, and makes what waited on the answer; it makes the rest of the work meanwhile.

## The result

```json
{"work": ["README.md"],
 "items": [{"checklist": "checklists/readme.md", "item": "Q-2",
            "lines": ["<path>:<from>-<to>"]}],
 "left": [{"checklist": "checklists/readme.md", "item": "Q-4", "need": "..."}],
 "chosen": [{"chosen": "...", "why": "..."}]}
```

- `work`: each file of the work, by your names: each file the CCS names, and each file in a folder
  it names, by the path from that folder.
- `items`: each item with the lines of the work that give its Good, as the AI that read the work
  in its receiver's place gave them. An item asked of each part has at least one range in every
  part of the work, each inside one part.
- `left`: each item that AI found no Good for once the two AIs had mended the work as far as they
  could, with what the receiver would need to get it, in one sentence; `[]` where none. The work
  is mostly made by then, so make each yourself, asking the user only what is theirs to decide.
- `chosen`: each choice the work rests on that the CCS and the files it names leave open, which the
  AI that made the work made itself, with why; `[]` where none. Show them to the user, as no one
  asked them.
