# `meta`

## Goal

The generator can make deliverables with which their role achieves its purpose.

## Template

[template.json](template.json)

## Example

[../product-vision/best-practice.json](../product-vision/best-practice.json)

## Vital few

| ID | About | Question |
| --- | --- | --- |
| Q1 | goal, vital_few | Making or judging a deliverable, do the generator and the evaluator know the end its role is after and the few things that decide whether the role reaches it, so that every part of the deliverable carries one of them? |
| Q2 | template | Filling in the template, does the generator find a slot for each vital one and the form its sentences take, so that the deliverable holds the vital few? |
| Q3 | practices | Making each vital one, does the generator grasp its intent and the field's established way to make it, so that it makes it in any case, the same way on every run? |
| Q4 | inputs, preconditions | Starting a deliverable, does the generator know the kinds it makes the deliverable from and the kinds that must pass first, so that it makes the deliverable on what's there? |
| Q5 | example, source | Reading the example, does the generator see what the template's slots become in one deliverable, so that it fills its own to the same intent? |

## Practices

### Q1

Making or judging a deliverable, do the generator and the evaluator know the end its role is after and the few things that decide whether the role reaches it, so that every part of the deliverable carries one of them?

**Thinking**

The goal is the one end the role is after, in one sentence with the role as its subject. The vital few are the things that decide whether the role reaches it, as Juran's Pareto principle names them: with each one in place the role reaches its end, and with one missing it falls short. Each one is a question of the moment the role uses it, what the role gets there, and what it's after in that, and the evaluator confirms that the role gets it.

**Steps**

1. Write the goal, and ask why of each part of it until the end itself shows.
2. Walk through the role's use of the deliverable toward the goal, one moment at a time, and name at each moment what decides whether the role reaches the goal.
3. Write each one as the question of its moment, with a "so that" clause where what the role gets differs from the goal.
4. To better a best practice, start from the vital few its use has confirmed, and take in what research shows.
5. Where a deliverable in use falls short of its role, mend the vital one that caused it.

### Q2

Filling in the template, does the generator find a slot for each vital one and the form its sentences take, so that the deliverable holds the vital few?

**Thinking**

The template holds one slot for each vital one, with the form its sentences take, such as one rule and one why, and fixed text for what every deliverable of the kind shares. The generator fills each slot with what this deliverable needs for that vital one.

**Steps**

1. Mark each slot so that its reader can tell it from fixed text and the page that shows it keeps it, such as `` `<name>` `` in Markdown.
2. After each section, write one note that says for each slot what it holds, what its reader uses it for, and whether it's optional. Open the note with a marker by which the generator finds and deletes it, and write it in the form the deliverable's format holds, such as a comment in Markdown or a key in JSON.
3. Where the deliverable has a JSON Schema of its own, such as the design tree, make the schema the template, its top fields the sections, and each slot's note the description of its field.
4. Give a slot a figure wherever a figure says it, drawn as text that shows each change in a diff, such as Mermaid for a sequence, SVG for any other figure, and a table. Give each figure a skeleton in the template that shows its layout by the slots' names, and say in the note where the deliverable puts its own.

### Q3

Making each vital one, does the generator grasp its intent and the field's established way to make it, so that it makes it in any case, the same way on every run?

**Thinking**

Each vital one has one practice. It says first, in short sentences, what the deliverable must be to give the role that vital one, and why the role needs it so, so that the generator finds its way in any case. It then gives the way the field has established for that, found by research, by its established name and with its source, such as single responsibility or Given-When-Then, so that the name carries the field's knowledge to the generator. It names a language or a tool as an example, and gives each established way with when it fits, so that each deliverable's plan picks the way and the tool.

**Steps**

1. Add a step where a generator that holds the intent still needs to know how, such as a format to keep or a place to look, and say what the step achieves.
2. Give each step that every run makes and a call shows its trace: a command it runs, a file it reads to its end, or a file it makes. Order the steps as their calls come, as a checker such as Lane holds the role to each step by its trace, in that order. The evaluator checks a step that's a judgment.
3. Where the generator finds the content before it writes it, such as the roles of a product vision, say what to look at, how to find all of it, and when to ask the user.

### Q4

Starting a deliverable, does the generator know the kinds it makes the deliverable from and the kinds that must pass first, so that it makes the deliverable on what's there?

**Thinking**

Inputs name each kind whose deliverables the generator makes a deliverable of this kind from, and preconditions each kind whose deliverables pass before it makes one, each by the name of its best practice's folder. The plan then holds each deliverable's own paths to them, and orders it after them.

### Q5

Reading the example, does the generator see what the template's slots become in one deliverable, so that it fills its own to the same intent?

**Thinking**

Make the product's own deliverable of the kind from its design tree by the template and the practices, confirm in it each vital one, and name its file in `example`, as one finished deliverable shows what the slots become.

**Steps**

1. Where the deliverable lies elsewhere for its own reader, such as a product vision in the developers' folder, name its path in `source`, and copy it with its figures beside the best practice by a script, such as ccpm's `dev/scripts/practices.py example`, so that the copy stays the same as the deliverable.
