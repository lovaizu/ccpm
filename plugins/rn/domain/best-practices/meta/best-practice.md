# `meta`

## Goal

A generator that follows a best practice produces deliverables that serve their users' purpose.

## Template

[template.json](template.json)

## Example

[../readme/best-practice.json](../readme/best-practice.json)

## Critical success factors

| ID | Factor |
| --- | --- |
| C1 | The necessary conditions cover what users need from the deliverable. |
| C2 | The generator meets every necessary condition in every deliverable. |
| C3 | Each deliverable stays consistent with the deliverables it builds on and the deliverables built on it. |

## Necessary conditions

| ID | Factor | Condition | Sections |
| --- | --- | --- | --- |
| N1 | C1 | Does the goal state, in one sentence, who uses the deliverable and what purpose it serves for them? | goal |
| N2 | C1 | Do the critical success factors name the few things that must all hold for the users to reach the goal? | critical_success_factors |
| N3 | C1 | Does each necessary condition ask, as a yes-or-no question, whether the deliverable holds a state that its factor needs? | necessary_conditions |
| N4 | C2 | Does the template give each necessary condition a section, and each slot a note on what it holds and in what form? | template |
| N5 | C2 | Does each practice say what the deliverable must be, why, and which established method achieves it? | practices |
| N6 | C2 | Does the example show a finished deliverable of the kind that meets every necessary condition? | example, source |
| N7 | C3 | Does the best practice name the kinds of deliverable that this kind builds on, and the kinds that must pass before work on it starts? | inputs, preconditions |

## Practices

### N1

Does the goal state, in one sentence, who uses the deliverable and what purpose it serves for them?

**Thinking**

Write the goal as one sentence whose subject is the deliverable's users. Name the users and what they achieve with the deliverable. The factors and the conditions all derive from this sentence, so it states the purpose itself, not a means to it.

**Steps**

1. Ask why of the sentence until the answer is the purpose itself.

### N2

Do the critical success factors name the few things that must all hold for the users to reach the goal?

**Thinking**

A critical success factor is one of the few things that must go right for the users to reach the goal, as John Rockart defined the term. Write each factor as a state, in one sentence. Together, the factors are sufficient: when all of them hold, the users reach the goal. Keep only the vital few, in Joseph Juran's term, so that each condition serves one of them.

**Steps**

1. Walk through how the users use the deliverable, one step at a time, and name what must go right at each step.
2. Check that the goal follows when every factor holds. If it doesn't, a factor is missing.

### N3

Does each necessary condition ask, as a yes-or-no question, whether the deliverable holds a state that its factor needs?

**Thinking**

A necessary condition is a state of the deliverable that a factor needs, as in a goal tree. Write each as a yes-or-no question about the deliverable, and name the factor it serves in `csf`. The generator meets each condition by its practice, and the evaluator checks each by its question.

**Steps**

1. For each factor, list each state of the deliverable that it needs.
2. If a deliverable that meets every condition still fails its users, find the level that caused it, whether the goal, a factor, a condition, or a practice, and fix it there.
3. To improve a best practice, start from the conditions that use has confirmed, and add what research shows.

### N4

Does the template give each necessary condition a section, and each slot a note on what it holds and in what form?

**Thinking**

The template is the skeleton of the deliverable. Each section holds one or more conditions, and each condition names its sections in `about`. Slots hold what changes from one deliverable to the next, and fixed text holds what every deliverable of the kind shares.

**Steps**

1. Mark each slot so that the reader can tell it from fixed text and the rendered page still shows it, such as `` `<name>` `` in Markdown.
2. After each section, write one note that says, for each slot, what it holds, the form it takes, and whether it's optional. Start the note with a marker by which the generator finds and deletes it, in the form the deliverable's format allows, such as a note block in Markdown or a key in JSON.
3. If the deliverable has a JSON Schema of its own, such as the design tree, use the schema as the template: its top-level fields are the sections, and the description of each field is its note.
4. Where a figure explains a slot better than words, draw it in a text format that shows each change in a diff, such as Mermaid for a sequence, SVG for other figures, or a table. Put a skeleton of each figure in the template, labeled with the names of its slots, and say in the note where the deliverable keeps its own.

### N5

Does each practice say what the deliverable must be, why, and which established method achieves it?

**Thinking**

Each condition has one practice. The practice first says what the deliverable must be to meet the condition, and why its users need that. With the reason, the generator can meet the condition in cases the template doesn't cover. The practice then names the method the field has established for it, found by research, with its source, such as single responsibility or Given-When-Then. The name carries the field's knowledge. Where the field has several methods, give each with when it fits. Name a language or a tool only as an example, so that each deliverable's plan chooses its own. The reasons and the way to find the content go in the practice, and the form of each slot goes in the template's note, so that each fact stands in one place.

**Steps**

1. Add a step only where a generator that understands the intent still needs to know how, such as a format to keep or a place to look. Say what the step achieves.
2. Give a trace to each step that every run takes and a tool call shows: a command it runs, a file it reads in full, or a file it writes. Order the steps as their calls come, because a checker such as Lane checks each step by its trace in that order. The evaluator checks the steps that are judgments.
3. Where the generator must find the content before it writes it, such as the users of a product vision, say where to look, how to find all of it, and when to ask the user.

### N6

Does the example show a finished deliverable of the kind that meets every necessary condition?

**Thinking**

The example is the product's own deliverable of the kind, made from its design tree with the template and the practices, and checked against every condition. Name its file in `example`. One finished deliverable shows what each section becomes.

**Steps**

1. If the deliverable lives elsewhere for its own readers, such as a product vision in the developers' folder, put its path in `source`, and copy it and its figures next to the best practice with a script, such as ccpm's `dev/scripts/practices.py example`, so that the copy stays the same as the original.

### N7

Does the best practice name the kinds of deliverable that this kind builds on, and the kinds that must pass before work on it starts?

**Thinking**

List in `inputs` each kind of deliverable that this kind builds on, and in `preconditions` each kind that must pass before work on it starts, each by the folder name of its best practice. The deliverables built on this kind are those whose best practices name it in `inputs`. Listing them here as well would write the same fact twice. The plan holds the paths of each deliverable's inputs and orders the deliverable after them.

**Steps**

1. When a deliverable changes, find the deliverables built on it and update them in the same change.
2. When an input changes, check the deliverable against it again.
