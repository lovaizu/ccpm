# `meta`

## Goal tree

- A generator that follows a best practice produces deliverables that serve their users' purpose.
  - **C1** The necessary conditions cover what users need from the deliverable.
    - **N1** Does the goal state, in one sentence, who uses the deliverable and what purpose it serves for them? (goal)
    - **N2** Do the critical success factors name the few things that must all hold for the users to reach the goal? (critical_success_factors)
    - **N3** Does each necessary condition ask, as a yes-or-no question, whether the deliverable holds a state that its factor needs? (necessary_conditions)
    - **N7** Does following the best practice put into the deliverable only the vital few, the things without which its users fail their goal? (the whole)
  - **C2** The generator meets every necessary condition in every deliverable.
    - **N4** Does the template place each necessary condition in a section, and give each slot a note on what it holds and in what form? (template)
    - **N5** Does each practice give the way of thinking that produces its condition's state: the decisions in order, the question at each, and the criteria for choosing, taken from an established method? (why, items)
  - **C3** Each deliverable stays consistent with the deliverables it builds on and the deliverables built on it.
    - **N6** Does the best practice name the kinds of deliverable that this kind builds on, with a condition that carries each of their vital few that its users need, and the kinds that must pass before work on it starts? (inputs, preconditions)

## Template

[template.json](template.json)

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

1. *While deciding.* Derive the factors from the goal: ask what must go right for the users to reach it, or they fail.
2. *While deciding.* Write each answer as a state in one sentence.
3. *While deciding.* Merge two states that fail together.
4. *While deciding.* For necessity, ask of each factor: if it failed, would the users still reach the goal? If they would, drop it.
5. *While deciding.* For sufficiency, walk through the users' use of the deliverable, from the moment they first meet it to the moment they reach the goal. At each moment, ask whether the users could still stop or go wrong there while every factor holds. If they could, find the missing factor.

### N3

Does each necessary condition ask, as a yes-or-no question, whether the deliverable holds a state that its factor needs?

The conditions are what the generator meets and the evaluator checks, so each must be a state that someone reading only the deliverable can confirm. The method is the goal tree of William Dettmer's The Logical Thinking Process, which breaks a goal into its critical success factors and each factor into the necessary conditions that make it true.

1. *While deciding.* For each factor, ask how the deliverable makes it true.
2. *While deciding.* Write each answer, a state of the deliverable, as a yes-or-no question about the deliverable, under its factor.
3. *While deciding.* Judge each condition by three tests. It's checkable: two readers of the deliverable give the same answer. It's about the deliverable, not about how someone made it. It's necessary: if the answer were no, its factor would fail.
4. *While deciding.* If a condition needs several states of its own, make it a factor.
5. *While deciding.* If a condition only says how to meet another condition, move it into that condition's practice.
6. *While making.* Read a deliverable that meets every condition as its users would. If it still fails them, find the level that caused it, whether the goal, a factor, a condition, or a practice, and rebuild that level from the level it serves.

### N4

Does the template place each necessary condition in a section, and give each slot a note on what it holds and in what form?

The template makes every deliverable of the kind hold each condition in the same place and the same form, so that no run has to invent the structure. The method is the consistency and labeling principles of Robert Horn's Information Mapping, in Mapping Hypertext: like content takes like terms, format, and order, and each unit takes a label that says what it holds.

1. *While deciding.* In a template in JSON, each key that holds content, at any depth, is a section. If the deliverable has a JSON Schema of its own, such as the design tree, use the schema as the template: its fields are the sections, and the description of each field is its note.
2. *While deciding.* Order the sections as the users need them, from the first thing they look for to the last.
3. *While deciding.* Place each condition in the section where the users need it, and name that section in the condition's `about`.
4. *While deciding.* For each piece of text, ask whether every deliverable of the kind says it the same way. If it does, write it as fixed text. If it differs, make it a slot.
5. *While deciding.* For each slot, choose the form that keeps the content the same shape across deliverables, such as one sentence, a list of commands, or a table with fixed columns. Each run fills a slot without a form in its own way.
6. *While deciding.* Where a slot's practice calls for a figure, choose a text format that shows each change in a diff, such as Mermaid for a sequence or SVG for other figures.
7. *While making.* Mark each slot so that the reader can tell it from fixed text and the rendered page still shows it, such as `` `<name>` `` in Markdown.
8. *While making.* After each section, write one note that says, for each slot, what it holds, the form it takes, whether it's optional, and, for a figure, where the deliverable keeps its own.
9. *While making.* Start each note with a marker by which the generator finds and deletes it, in the form the deliverable's format allows, such as a note block in Markdown or a key in JSON.
10. *While making.* Where a slot holds a figure, put a skeleton of the figure in the template, labeled with the names of its slots.

### N5

Does each practice give the way of thinking that produces its condition's state: the decisions in order, the question at each, and the criteria for choosing, taken from an established method?

A practice is the only place where the generator learns how to meet a condition well, so it gives the way of thinking that produces the condition's state, not a description of the state. The method is the systematic approach to problem solving of Jeroen van Merriënboer's four-component instructional design model, in Ten Steps to Complex Learning: the phases that a competent performer goes through on a task, each with the rules of thumb that help in it.

1. *While deciding.* Find by research the method that the field has established for the condition's state, and take its core steps as they apply to this deliverable, since a name alone doesn't tell the generator what to do.
2. *While making.* Write in `why`, in one or two sentences, what the condition gives the users, and the method's name and source.
3. *While making.* List the items in the order the generator takes them: each decision, with the question to ask and the criterion for choosing where there are options in the same item, then each step, and last, only where the condition's own question doesn't already say how to check it, how to check the result from the users' side, such as asking whether a newcomer can say the point back.
4. *While making.* Make each item one thing to take, since a role names each item it took by its ID, its condition's ID and its place, such as N6.2, and a check finds one left out.
5. *While making.* Give a trace to each item that every run takes and a tool call shows: a command it runs, a file it reads in full, or a file it writes. An item with a trace takes its place by its call, among the decisions or steps whose content it supplies, such as the read of an input just before the decision that takes from it, since a checker such as Lane checks each item by its trace in the order of the calls, and the evaluator checks what the judgments made.
6. *While making.* Mark each item `decide` where the maker takes it while it settles the work's decisions, and `make` where it takes it while it makes the deliverable. No `decide` item follows a `make` item, since the maker settles the decisions before it makes the deliverable.
7. *While making.* Where the generator must find the content before it writes it, such as the users of a product vision, say what the content serves, how to derive it from that, and when to ask the user.
8. *While making.* Write each reason and each way to find the content in the item that uses it, and the form of each slot in the template's note, so that each fact stands in one place.
9. *While making.* Name a language or a tool only as an example, so that each deliverable's plan chooses its own.

### N6

Does the best practice name the kinds of deliverable that this kind builds on, with a condition that carries each of their vital few that its users need, and the kinds that must pass before work on it starts?

A deliverable must say what the deliverables it builds on say, and the deliverables built on it must follow it. The method is requirements traceability, which Orlena Gotel and Anthony Finkelstein, in An Analysis of the Requirements Traceability Problem, define as following each requirement both backward to its source and forward to what carries it.

1. *While deciding.* To find the inputs, ask of each part of the deliverable where its content comes from. Each kind of deliverable that supplies content is an input, such as the product vision for a README.
2. *While deciding.* To find the preconditions, ask what must hold before work on the deliverable can start, such as an agreed product vision.
3. *While deciding.* Go the other way, from each input to the deliverable, since a deliverable that drops what it rests on fails its users while every part it holds is sound: take the input's vital few, such as the concept and the key results of a product vision, and ask which of them the deliverable's users need.
4. *While deciding.* For each of those vital few that the users need, decide which part of the deliverable carries it.
5. *While deciding.* Make sure a condition asks for each of those vital few, such as a README showing what the key results promise.
6. *While making.* List the inputs in `inputs` and the preconditions in `preconditions`, each by the folder name of its best practice.
7. *While making.* Leave out the kinds built on this kind, since their best practices name it in `inputs`, and listing them here as well would write the same fact twice.
8. *While making.* Leave out the paths of the inputs, since the plan holds the paths of each deliverable's inputs and orders the deliverable after them.
9. *While making.* When a deliverable changes, find the deliverables built on it and update them in the same change.
10. *While making.* When an input changes, check the deliverable against it again.

### N7

Does following the best practice put into the deliverable only the vital few, the things without which its users fail their goal?

A deliverable that holds the trivial many beside the vital few buries what its users need, and each round of work adds more. The method is Joseph Juran's Pareto principle, in his Quality Control Handbook, which names the few causes that decide most of a result the vital few.

1. *While deciding.* Make each level of the best practice the vital few of the level it serves: the goal names the one purpose, the factors the few things that purpose can't go without, and each condition the state that a factor needs.
2. *While deciding.* Derive each practice's items from what its condition serves, such as a README's problems from the product vision's objectives and their key results, since a practice that collects every thing of a kind and then keeps some, such as every problem readers have, fills the deliverable with the many.
3. *While making.* Never add a question or a check for fewness. It adds findings of its own, and the few follow from the build.
