# `meta`

## Goal

The generator makes deliverables with which their role achieves its purpose.

## Template

[template.json](template.json)

## Example

[../product-vision/best-practice.json](../product-vision/best-practice.json)

## Critical success factors

| ID | Factor |
| --- | --- |
| C1 | The generator and the evaluator know what the deliverable achieves and what decides it. |
| C2 | The generator meets each necessary condition the same way on every run. |
| C3 | The generator makes the deliverable once what it takes is there. |

## Necessary conditions

| ID | Factor | About | Question |
| --- | --- | --- | --- |
| Q1 | C1 | goal | Starting a deliverable, does the generator know in one sentence the end its role is after, so that it knows what the deliverable achieves? |
| Q2 | C1 | critical_success_factors | Starting a deliverable, does the generator know the few things that must go right for the role to reach that end, so that it knows what decides the deliverable? |
| Q3 | C1 | necessary_conditions | Making or judging a deliverable, do the generator and the evaluator know, each as a question, the states of the deliverable that each critical success factor needs, so that both know what decides it? |
| Q4 | C2 | template | Filling in the template, does the generator find for each necessary condition its section and the form its sentences take, so that it meets the condition the same way on every run? |
| Q5 | C2 | practices | Meeting a necessary condition, does the generator grasp its intent and the field's established way, so that it meets the condition the same way on every run? |
| Q6 | C2 | example, source | Reading the example, does the generator see what the template's sections become in one deliverable, so that it meets each condition the same way on every run? |
| Q7 | C3 | inputs, preconditions | Starting a deliverable, does the generator know the kinds it makes the deliverable from and the kinds that must pass first, so that it makes the deliverable once what it takes is there? |

## Practices

### Q1

Starting a deliverable, does the generator know in one sentence the end its role is after, so that it knows what the deliverable achieves?

**Thinking**

Write the end the role is after as one sentence, with the role as its subject.

**Steps**

1. Ask why of each part of the sentence until the end itself shows.

### Q2

Starting a deliverable, does the generator know the few things that must go right for the role to reach that end, so that it knows what decides the deliverable?

**Thinking**

The critical success factors are the few things that must go right for the role to reach its end, as John Rockart named them: with each one in place, the role reaches its end. Each level of a best practice holds the vital few of the level it serves, as Juran's Pareto principle names them: the critical success factors hold what the goal needs, and the necessary conditions what each factor needs. Write each factor as one sentence that states it.

**Steps**

1. Walk through the role's use of the deliverable toward the goal, one moment at a time, and name what must go right at each.

### Q3

Making or judging a deliverable, do the generator and the evaluator know, each as a question, the states of the deliverable that each critical success factor needs, so that both know what decides it?

**Thinking**

Each necessary condition is a state of the deliverable that its critical success factor needs, as a goal tree names it. Write each as a question of the moment the role uses it, what the role gets there, and the factor it serves, in a "so that" clause. The evaluator confirms each condition, and its practice makes it.

**Steps**

1. For each critical success factor, name each state of the deliverable it needs.
2. To better a best practice, start from the conditions its use has confirmed, and take in what research shows.
3. Where a deliverable in use falls short of its role, mend the level that caused it: the goal, a critical success factor, a necessary condition, or its practice.

### Q4

Filling in the template, does the generator find for each necessary condition its section and the form its sentences take, so that it meets the condition the same way on every run?

**Thinking**

The template holds each necessary condition in a section, with the form its sentences take, such as one rule and one why, and fixed text for what every deliverable of the kind shares. Each section holds one or more conditions, and each condition names its sections in `about`.

**Steps**

1. Mark each slot so that its reader can tell it from fixed text and the page that shows it keeps it, such as `` `<name>` `` in Markdown.
2. After each section, write one note that says for each slot what it holds, what its reader uses it for, and whether it's optional. Open the note with a marker by which the generator finds and deletes it, and write it in the form the deliverable's format holds, such as a comment in Markdown or a key in JSON.
3. Where the deliverable has a JSON Schema of its own, such as the design tree, make the schema the template, its top fields the sections, and each slot's note the description of its field.
4. Give a slot a figure wherever a figure says it, drawn as text that shows each change in a diff, such as Mermaid for a sequence, SVG for any other figure, and a table. Give each figure a skeleton in the template that shows its layout by the slots' names, and say in the note where the deliverable puts its own.

### Q5

Meeting a necessary condition, does the generator grasp its intent and the field's established way, so that it meets the condition the same way on every run?

**Thinking**

Each necessary condition has one practice. It says first, in short sentences, what the deliverable must be to meet that condition, and why the role needs it so, so that the generator finds its way in any case. It then gives the way the field has established for that, found by research, by its established name and with its source, such as single responsibility or Given-When-Then, so that the name carries the field's knowledge to the generator. It names a language or a tool as an example, and gives each established way with when it fits, so that each deliverable's plan picks the way and the tool.

**Steps**

1. Add a step where a generator that holds the intent still needs to know how, such as a format to keep or a place to look, and say what the step achieves.
2. Give each step that every run makes and a call shows its trace: a command it runs, a file it reads to its end, or a file it makes. Order the steps as their calls come, as a checker such as Lane holds the role to each step by its trace, in that order. The evaluator checks a step that's a judgment.
3. Where the generator finds the content before it writes it, such as the roles of a product vision, say what to look at, how to find all of it, and when to ask the user.

### Q6

Reading the example, does the generator see what the template's sections become in one deliverable, so that it meets each condition the same way on every run?

**Thinking**

Make the product's own deliverable of the kind from its design tree by the template and the practices, confirm in it each necessary condition, and name its file in `example`, as one finished deliverable shows what the sections become.

**Steps**

1. Where the deliverable lies elsewhere for its own reader, such as a product vision in the developers' folder, name its path in `source`, and copy it with its figures beside the best practice by a script, such as ccpm's `dev/scripts/practices.py example`, so that the copy stays the same as the deliverable.

### Q7

Starting a deliverable, does the generator know the kinds it makes the deliverable from and the kinds that must pass first, so that it makes the deliverable once what it takes is there?

**Thinking**

Inputs name each kind whose deliverables the generator makes a deliverable of this kind from, and preconditions each kind whose deliverables pass before it makes one, each by the name of its best practice's folder. The plan then holds each deliverable's own paths to them, and orders it after them.
