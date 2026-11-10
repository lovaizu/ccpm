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
| N4 | C2 | Does the template place each necessary condition in a section, and give each slot a note on what it holds and in what form? | template |
| N5 | C2 | Does each practice give the way of thinking that produces its condition's state: the decisions in order, the question at each, and the criteria for choosing, taken from an established method? | practices |
| N6 | C2 | Does the example show a finished deliverable of the kind that meets every necessary condition? | example, source |
| N7 | C3 | Does the best practice name the kinds of deliverable that this kind builds on, with a condition that carries each of their vital few that its users need, and the kinds that must pass before work on it starts? | inputs, preconditions |
| N8 | C1 | Does following the best practice put into the deliverable only the vital few, the things without which its users fail their goal? | the whole |

## Practices

### N1

Does the goal state, in one sentence, who uses the deliverable and what purpose it serves for them?

Every later decision rests on the goal, so it must name the purpose the users have, not a means to it. The method is the why and how laddering of goal-oriented requirements engineering, as in Knowledge Acquisition in Automated Specification (KAOS) by Axel van Lamsweerde: asking why moves up toward the goal, and asking how moves down toward the means.

1. *While deciding.* Start from the people who use the deliverable, not from the deliverable: ask who reads or runs it, and what they're trying to get done when they do.
2. *While deciding.* Write one sentence with those people as the subject and what they achieve as the verb.
3. *While deciding.* Ask why that achievement matters to them, and repeat until the next answer goes beyond what the deliverable can affect. The last answer within its reach is the goal.
4. *While deciding.* If the sentence names a part of the deliverable, such as a section or a feature, it states a means. Ask why once more.
5. *While making.* Read the sentence without the deliverable's name in it. If it no longer says what the users achieve, rewrite it.

### N2

Do the critical success factors name the few things that must all hold for the users to reach the goal?

The factors decide where the generator spends its effort, so they must be the few things that the users can't reach the goal without, as John Rockart defined critical success factors, usually three to six. These are the vital few, in Joseph Juran's term.

1. *While deciding.* Derive the factors from the goal: ask what must go right for the users to reach it, or they fail. Write each answer as a state in one sentence, and merge two states that fail together.
2. *While deciding.* For necessity, ask of each factor: if it failed, would the users still reach the goal? If they would, drop it.
3. *While deciding.* For sufficiency, walk through the users' use of the deliverable, from the moment they first meet it to the moment they reach the goal. At each moment, ask whether the users could still stop or go wrong there while every factor holds. If they could, find the missing factor.

### N3

Does each necessary condition ask, as a yes-or-no question, whether the deliverable holds a state that its factor needs?

The conditions are what the generator meets and the evaluator checks, so each must be a state that someone reading only the deliverable can confirm. The method is the goal tree, which breaks each goal into the states that make it true.

1. *While deciding.* For each factor, ask how the deliverable makes it true. Write each answer, a state of the deliverable, as a yes-or-no question about the deliverable, and name its factor in `csf`.
2. *While deciding.* Judge each condition by three tests. It's checkable: two readers of the deliverable give the same answer. It's about the deliverable, not about how someone made it. It's necessary: if the answer were no, its factor would fail.
3. *While deciding.* If a condition needs several states of its own, make it a factor. If it only says how to meet another condition, move it into that condition's practice.
4. *While making.* If a deliverable that meets every condition still fails its users, find the level that caused it, whether the goal, a factor, a condition, or a practice, and rebuild that level from the level it serves.

### N4

Does the template place each necessary condition in a section, and give each slot a note on what it holds and in what form?

The template makes every deliverable of the kind hold each condition in the same place and the same form, so that no run has to invent the structure.

1. *While deciding.* Order the sections as the users need them, from the first thing they look for to the last.
2. *While deciding.* Place each condition in the section where the users need it, and name that section in the condition's `about`.
3. *While deciding.* For each piece of text, ask whether every deliverable of the kind says it the same way. If it does, write it as fixed text. If it differs, make it a slot.
4. *While deciding.* For each slot, choose the form that keeps the content the same shape across deliverables, such as one sentence, a list of commands, or a table with fixed columns. Each run fills a slot without a form in its own way.
5. *While making.* Mark each slot so that the reader can tell it from fixed text and the rendered page still shows it, such as `` `<name>` `` in Markdown.
6. *While making.* After each section, write one note that says, for each slot, what it holds, the form it takes, and whether it's optional. Start the note with a marker by which the generator finds and deletes it, in the form the deliverable's format allows, such as a note block in Markdown or a key in JSON.
7. *While making.* If the deliverable has a JSON Schema of its own, such as the design tree, use the schema as the template: its top-level fields are the sections, and the description of each field is its note.
8. *While making.* Where a slot's practice calls for a figure, draw it in a text format that shows each change in a diff, such as Mermaid for a sequence or SVG for other figures. Put a skeleton of the figure in the template, labeled with the names of its slots, and say in the note where the deliverable keeps its own.

### N5

Does each practice give the way of thinking that produces its condition's state: the decisions in order, the question at each, and the criteria for choosing, taken from an established method?

A practice is the only place where the generator learns how to meet a condition well, so it gives the way of thinking that produces the condition's state, not a description of the state. Its test: a generator that takes only this practice's items makes a deliverable that meets the condition every time.

1. *While deciding.* Find by research the method that the field has established for the condition's state. A name alone doesn't tell the generator what to do, so take the method's core steps as they apply to this deliverable.
2. *While deciding.* Write in `why` what the condition gives the users, and the method's name and source.
3. *While deciding.* Derive the items from what the condition gives the users, and list them in the order the generator takes them: each decision with the question to ask and the criterion for choosing where there are options, then each step, and last how to check the result from the users' side, such as asking whether a newcomer can say the point back. Make each item one thing to take, since a role names each item it took by its ID, its condition's ID and its place, such as N6.2, and a check finds one left out.
4. *While deciding.* Mark each item `decide` where the maker takes it while it settles the work's decisions, and `make` where it takes it while it makes the deliverable.
5. *While deciding.* Give a trace to each item that every run takes and a tool call shows: a command it runs, a file it reads in full, or a file it writes. Order the items as their calls come, because a checker such as Lane checks each item by its trace in that order. The evaluator checks what the judgments made.
6. *While deciding.* Where the generator must find the content before it writes it, such as the users of a product vision, say what the content serves, how to derive it from that, and when to ask the user.
7. *While making.* Write the reasons and the way to find the content in the practice, and the form of each slot in the template's note, so that each fact stands in one place. Name a language or a tool only as an example, so that each deliverable's plan chooses its own.

### N6

Does the example show a finished deliverable of the kind that meets every necessary condition?

The example shows the generator what following the best practice produces, which no description fully conveys.

1. *While making.* Make the example from the product's own design tree by taking the template and the practices exactly.
2. *While making.* Check it against every condition as its users would.
3. *While making.* Where it falls short, fix the practice or the template that produced the shortfall, and make the example again from them. A fix made only in the example would hide the fault in the best practice.
4. *While making.* Name the example's file in `example`.
5. *While making.* If the deliverable lives elsewhere for its own readers, such as a product vision in the developers' folder, name its path in the best practice's `source` field. Have a script, such as ccpm's `dev/scripts/practices.py example`, copy it and its figures next to the best practice, so that the copy matches the original each time the script runs.

### N7

Does the best practice name the kinds of deliverable that this kind builds on, with a condition that carries each of their vital few that its users need, and the kinds that must pass before work on it starts?

A deliverable must say what the deliverables it builds on say, and the deliverables built on it must follow it.

1. *While deciding.* To find the inputs, ask of each part of the deliverable where its content comes from. Each kind of deliverable that supplies content is an input, such as the product vision for a README.
2. *While deciding.* To find the preconditions, ask what must hold before work on the deliverable can start, such as an agreed product vision.
3. *While deciding.* Go the other way, from each input to the deliverable, since a deliverable that drops what it rests on fails its users while every part it holds is sound. For each input, take its vital few, such as the concept and the key results of a product vision, and ask which of them the deliverable's users need. For each one they need, decide which part of the deliverable carries it, and make sure a condition asks for it, such as a README showing what the key results promise.
4. *While making.* List the inputs in `inputs` and the preconditions in `preconditions`, each by the folder name of its best practice. The deliverables built on this kind are those whose best practices name it in `inputs`, so listing them here as well would write the same fact twice. The plan holds the paths of each deliverable's inputs, and orders the deliverable after them.
5. *While making.* When a deliverable changes, find the deliverables built on it and update them in the same change.
6. *While making.* When an input changes, check the deliverable against it again.

### N8

Does following the best practice put into the deliverable only the vital few, the things without which its users fail their goal?

A deliverable that holds the trivial many beside the vital few buries what its users need, and each round of work adds more. Joseph Juran named the few causes that decide most of a result the vital few. Get them by building, not by checking, since a check for fewness adds findings of its own.

1. *While deciding.* Make each level of the best practice the vital few of the level it serves: the goal names the one purpose, the factors the few things that purpose can't go without, and each condition the state that a factor needs.
2. *While deciding.* Derive each practice's items from what its condition serves, such as a README's problems from the product vision's objectives and their key results. A practice that collects every thing of a kind and then keeps some, such as every problem readers have, fills the deliverable with the many.
