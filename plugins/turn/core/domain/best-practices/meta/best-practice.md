# meta

## Goal

The generator can make deliverables with which their role achieves its purpose.

## Template

[template.json](template.json)

## Example

[../product-vision-board/best-practice.json](../product-vision-board/best-practice.json)

## User benefits

- **Q1** (goal): Reading the goal, does the generator see the one thing the deliverable's role achieves with it?
- **Q2** (template): Filling in the template, does the generator know what to write in each section and in what order, with no room for more?
- **Q3** (goal, template): Setting the template against the goal, does the generator find each section the goal needs, and none it does not?
- **Q4** (user_benefits): Judging a deliverable by a question, does the evaluator tell whether the role gets what it needs from the sections the question is about?
- **Q5** (template, user_benefits): Going through the template, does the generator find a question for each section, each dependency among sections and the whole?
- **Q6** (practices): Following a practice, does the generator make what its question asks for?
- **Q7** (user_benefits, practices): Going through the questions in order, does the generator find a practice for each?
- **Q8** (example, source): Reading the example, does the generator see what the template's slots become in one deliverable?
- **Q9** (the whole): Using a deliverable made by the best practice and passed, does its role achieve its purpose?

## Practices

### Q1: Reading the goal, does the generator see the one thing the deliverable's role achieves with it?

**Thinking**: Write what the deliverable's role is trying to get done as one sentence with the role as its subject, and nothing of what the deliverable holds or how it is made, as each section serves that.

**Steps**

1. Where two readers would name two achievements from it, keep the one the other serves.

### Q2: Filling in the template, does the generator know what to write in each section and in what order, with no room for more?

**Thinking**: Write the template anew from the goal and from what good deliverables of the kind hold that their role uses toward it, as an AI writes past what a deliverable needs when only told not to.

**Steps**

1. Where what the good deliverables hold is one way of doing it, such as a place, a file or a name, keep what the role gets from it instead.
2. Write as fixed text what is the same in every deliverable of the kind, and a slot `` `<name>` `` for the rest, marked as code, as a bare `<name>` is dropped as an HTML tag where the template is shown.
3. After each section, write one GitHub note whose first line is `DELETE_TEMPLATE_COMMENT:`, saying only what each slot holds and whether it is optional, as the reader of the template then sees it, and the generator finds and deletes each note by its marker.
4. Where the deliverable is JSON, write each note as a key `DELETE_TEMPLATE_COMMENT`, as JSON holds no comment.
5. Give the content found by digging a slot for its intent and why alone, in the fewest words, and a figure in place of prose wherever a figure can say it.
6. Draw a sequence in Mermaid, and any other figure in SVG, a table among them, as a table stands in for prose.
7. Give each SVG figure of the template a skeleton of its own beside it, `images/template-<name>.svg`, that shows the figure's layout by the slots' names, give it an alt text with no slot, and say in the section's note where the deliverable puts its own figure, as a figure the template names but does not hold shows broken, and the example's figure shows one product's content in place of the layout.
8. Name the template's file in `template`.

### Q3: Setting the template against the goal, does the generator find each section the goal needs, and none it does not?

**Thinking**: Cut each section the role could do without toward the goal, and add what a deliverable with every section would still lack when it fails its role, as each section is there because the goal needs it.

**Steps**

1. Repeat until no such deliverable can be imagined.

### Q4: Judging a deliverable by a question, does the evaluator tell whether the role gets what it needs from the sections the question is about?

**Thinking**: Ask whether the role, at the moment it uses the sections, gets what it needs from them toward the goal, as a question that asks for a sign of good work can be met in its words while the role goes without.

**Steps**

1. Have two evaluators judge one real deliverable by the question, and rewrite it where they differ.

### Q5: Going through the template, does the generator find a question for each section, each dependency among sections and the whole?

**Thinking**: Give each section, each dependency among sections and the whole a question, and add one that fails each deliverable that would pass them all and still fail its role, as the questions are complete only when none such is left.

**Steps**

1. Where two questions would fail the same deliverables for the same reason, merge them, but keep a key one on its own.
2. Dig each question until it shows the idea the role must grasp, and ask whether the role grasps it, so that the template gives it a figure.
3. Judge real deliverables that their role found short, and where one passes, add or mend the question that should have failed it.

### Q6: Following a practice, does the generator make what its question asks for?

**Thinking**: Take the way from where good deliverables have met the question before, and write it as one action of the generator, as a way that has worked is likelier to work again than one made up.

**Steps**

1. Write a step only for what the thinking alone does not lead the generator to, one action each, in order.
2. Where the content must be found before it is written, such as the roles of a product vision board, say what to look at, how to find all of it, and when to ask the user.
3. Where a step or a source names one way of doing it, such as a place, a file or a tool, write what that way achieves instead.
4. Make one real deliverable by the practice, judge it by the question, and mend the practice where the answer stays no.

### Q7: Going through the questions in order, does the generator find a practice for each?

**Thinking**: Order the questions so that each comes before those that build on it, and give each one practice in that order, as the generator then meets no question with nothing to go by.

### Q8: Reading the example, does the generator see what the template's slots become in one deliverable?

**Thinking**: Make the product's own deliverable of the kind from its design tree by the template and the practices, pass it by the questions, and name its file in `example`, as one finished deliverable shows what the comments alone do not.

**Steps**

1. Where the deliverable lies elsewhere for its own reader, such as a product vision board in the developers' folder, name its path in `source` and copy it with its figures beside the best practice by `plan.py example`, as a copy made by hand drifts from the deliverable, and a symbolic link shows as a line of text on GitHub and on Windows.

### Q9: Using a deliverable made by the best practice and passed, does its role achieve its purpose?

**Thinking**: Have the role, or an AI holding what it wants, use the example for the goal, and set its verdict against the evaluator's, as only a deliverable made and used shows whether the whole works.

**Steps**

1. Trace each difference to the goal, the template, a question or a practice, and mend it there.
2. Go through again with the next real deliverable.
