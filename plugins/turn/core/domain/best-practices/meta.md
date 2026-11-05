# meta

## Goal

The generator can make deliverables with which their role achieves its purpose.

## Template

[meta-template.json](meta-template.json)

## Example

[ux.json](ux.json)

## User benefits

- **Q1** (goal): Reading the goal, does the generator see the one thing the deliverable's role achieves with it?
- **Q2** (template): Filling in the template, does the generator know what to write in each section and in what order, with no room for more?
- **Q3** (goal, template): Setting the template against the goal, does the generator find each section the goal needs, and none it does not?
- **Q4** (user_benefits): Judging a deliverable by a question, does the evaluator tell whether the role gets what it needs from the sections the question is about?
- **Q5** (template, user_benefits): Going through the template, does the generator find a question for each section, each dependency among sections and the whole?
- **Q6** (practices): Following a practice, does the generator make what its question asks for?
- **Q7** (user_benefits, practices): Going through the questions in order, does the generator find a practice for each?
- **Q8** (example): Reading the example, does the generator see what the template's slots become in one deliverable?
- **Q9** (the whole): Using a deliverable made by the best practice and passed, does its role achieve its purpose?

## Practices

### Q1: Reading the goal, does the generator see the one thing the deliverable's role achieves with it?

**Thinking**: Write what the deliverable's role is trying to get done as one sentence with the role as its subject, and nothing of what the deliverable holds or how it is made, as each section serves that.

**Steps**

1. Where two readers would name two achievements from it, keep the one the other serves.

**Grounds**

- [The Goal Question Metric Approach](https://www.cs.umd.edu/~mvz/handouts/gqm.pdf), Basili, Caldiera and Rombach, Encyclopedia of Software Engineering, 1994: "A goal is defined for an object, for a variety of reasons, with respect to various models of quality, from various points of view, relative to a particular environment."
- [Jobs to Be Done (JTBD): The Original Framework by Tony Ulwick](https://strategyn.com/jobs-to-be-done/), Strategyn, strategyn.com, 2024: "Identify who is executing the job and define the core functional job in a single, solution-free statement."

### Q2: Filling in the template, does the generator know what to write in each section and in what order, with no room for more?

**Thinking**: Write the template anew from the goal and from what good deliverables of the kind hold that their role uses toward it, as an AI writes past what a deliverable needs when only told not to.

**Steps**

1. Where what the good deliverables hold is one way of doing it, such as a place, a file or a name, keep what the role gets from it instead.
2. Write as fixed text what is the same in every deliverable of the kind, and a slot `<name>` for the rest.
3. After each section, write one comment saying only what each slot holds and whether it is optional.
4. Open the template with the comment "Delete every comment once the document is written."
5. Where the deliverable is JSON, write each comment as a `$comment` key.
6. Draw a sequence in Mermaid and any other figure in SVG, and write a table in Markdown.
7. Name the template's file in `template`.

**Grounds**

- [Using Rubrics to Promote Thinking and Learning](https://ascd.org/el/articles/using-rubrics-to-promote-thinking-and-learning), Andrade, Educational Leadership, 2000: "Look at models. Review examples of good and poor work on a project like the one your students are about to undertake."
- [The Good Docs Project templates](https://gitlab.com/tgdp/templates/-/raw/main/README.md), The Good Docs Project, gitlab.com, no date: "The template file is the raw template for the content type. It provides a rough outline of the suggested content and a few embedded writing tips for how to fill in the different sections of the template."
- [The Good Docs Project templates](https://gitlab.com/tgdp/templates/-/raw/main/README.md), The Good Docs Project, gitlab.com, no date: "This guide provides a deeper explanation of how to fill in the template."
- [Download arc42](https://arc42.org/download), arc42, arc42.org, no date: "Plain gives you the bare structure."
- [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5), Anthropic, platform.claude.com, no date: "files that Claude Opus 5 writes to disk (reports, Markdown documents, summaries) are often longer than on prior models."

### Q3: Setting the template against the goal, does the generator find each section the goal needs, and none it does not?

**Thinking**: Cut each section the role could do without toward the goal, and add what a deliverable with every section would still lack when it fails its role, as each section is there because the goal needs it.

**Steps**

1. Repeat until no such deliverable can be imagined.

**Grounds**

- [The Goal Question Metric Approach](https://www.cs.umd.edu/~mvz/handouts/gqm.pdf), Basili, Caldiera and Rombach, Encyclopedia of Software Engineering, 1994: "This means that measurement must be defined in a top-down fashion."
- [The Logic and Methodology of Checklists](https://wmich.edu/sites/default/files/attachments/u350/2014/logic%26methodology_dec07.pdf), Scriven, Western Michigan University, 2007: "Then one tries to construct hypothetical cases in which an entity has all the properties in the proposed comlist but still lacks something that would be required or important in order to justify an assignment of merit."
- [The Logic and Methodology of Checklists](https://wmich.edu/sites/default/files/attachments/u350/2014/logic%26methodology_dec07.pdf), Scriven, Western Michigan University, 2007: "The list should be concise (to assist its mnemonic function); i.e., it should contain no superfluous criteria."

### Q4: Judging a deliverable by a question, does the evaluator tell whether the role gets what it needs from the sections the question is about?

**Thinking**: Ask whether the role, at the moment it uses the sections, gets what it needs from them toward the goal, as a question that asks for a sign of good work can be met in its words while the role goes without.

**Steps**

1. Have two evaluators judge one real deliverable by the question, and rewrite it where they differ.

**Grounds**

- [The Logic and Methodology of Checklists](https://wmich.edu/sites/default/files/attachments/u350/2014/logic%26methodology_dec07.pdf), Scriven, Western Michigan University, 2007: "The checkpoints should refer to criteria and not mere indicators"
- [The Logic and Methodology of Checklists](https://wmich.edu/sites/default/files/attachments/u350/2014/logic%26methodology_dec07.pdf), Scriven, Western Michigan University, 2007: "indicators are easily corrupted, and once it becomes known that they are being used as an indicator for something important in an evaluation, people are very ingenious about faking the score on them"
- [What's Wrong—and What's Right—with Rubrics](https://ascd.org/el/articles/whats-wrong-and-whats-right-with-rubrics), Popham, Educational Leadership, 1997: "In essence, these overly general criteria allow both teachers and students to conclude that really good student responses to the task are, well, really good."
- [Using LLM-as-a-Judge For Evaluation: A Complete Guide](https://hamel.dev/blog/posts/llm-judge/), Husain, hamel.dev, 2024: "You need to be able to say “this interaction passed because…” and “this interaction failed because…”."
- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), Anthropic, anthropic.com, 2026: "A good task is one where two domain experts would independently reach the same pass/fail verdict."

### Q5: Going through the template, does the generator find a question for each section, each dependency among sections and the whole?

**Thinking**: Give each section, each dependency among sections and the whole a question, and add one that fails each deliverable that would pass them all and still fail its role, as the questions are complete only when none such is left.

**Steps**

1. Where two questions would fail the same deliverables for the same reason, merge them, but keep a key one on its own.
2. Judge real deliverables that their role found short, and where one passes, add or mend the question that should have failed it.

**Grounds**

- [The Logic and Methodology of Checklists](https://wmich.edu/sites/default/files/attachments/u350/2014/logic%26methodology_dec07.pdf), Scriven, Western Michigan University, 2007: "The list should be complete (no significant omissions)."
- [The Logic and Methodology of Checklists](https://wmich.edu/sites/default/files/attachments/u350/2014/logic%26methodology_dec07.pdf), Scriven, Western Michigan University, 2007: "The items should be contiguous, i.e., nonoverlapping"
- [Using Rubrics to Promote Thinking and Learning](https://ascd.org/el/articles/using-rubrics-to-promote-thinking-and-learning), Andrade, Educational Leadership, 2000: "After class, take time to combine criteria. Avoid creating categories that are too big, and don't bury criteria that you want to emphasize."
- [Key Evaluation Checklist](https://wmich.edu/sites/default/files/attachments/u350/2014/key%20evaluation%20checklist.pdf), Scriven, Western Michigan University, 2007: "We can describe this as a case where they failed to clear a holistic (or overall) bar that was implicit in this example, but can often be made explicit through dialog."
- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), Anthropic, anthropic.com, 2026: "Converting user-reported failures into test cases ensures your suite reflects actual usage"

### Q6: Following a practice, does the generator make what its question asks for?

**Thinking**: Take the way from where good deliverables have met the question before, and write it as one action of the generator, as a way that has worked is likelier to work again than one made up.

**Steps**

1. Write a step only for what the thinking alone does not lead the generator to, one action each, in order.
2. Where a step or a source names one way of doing it, such as a place, a file or a tool, write what that way achieves instead.
3. Quote as grounds the sources' words from the pages opened.
4. Make one real deliverable by the practice, judge it by the question, and mend the practice where the answer stays no.

**Grounds**

- [Key Evaluation Checklist](https://wmich.edu/sites/default/files/attachments/u350/2014/key%20evaluation%20checklist.pdf), Scriven, Western Michigan University, 2007: "This is an iterative checklist, not a one-shot checklist."

### Q7: Going through the questions in order, does the generator find a practice for each?

**Thinking**: Order the questions so that each comes before those that build on it, and give each one practice in that order, as the generator then meets no question with nothing to go by.

### Q8: Reading the example, does the generator see what the template's slots become in one deliverable?

**Thinking**: Make the product's own deliverable of the kind from its design tree by the template and the practices, pass it by the questions, and name its file in `example`, as one finished deliverable shows what the comments alone do not.

**Grounds**

- [The Good Docs Project templates](https://gitlab.com/tgdp/templates/-/raw/main/README.md), The Good Docs Project, gitlab.com, no date: "See an example of the template in action in our model documentation project: The Chronologue."

### Q9: Using a deliverable made by the best practice and passed, does its role achieve its purpose?

**Thinking**: Have the role, or an AI holding what it wants, use the example for the goal, and set its verdict against the evaluator's, as only a deliverable made and used shows whether the whole works.

**Steps**

1. Trace each difference to the goal, the template, a question or a practice, and mend it there.
2. Go through again with the next real deliverable.

**Grounds**

- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), Anthropic, anthropic.com, 2026: "LLM-as-judge graders should be closely calibrated with human experts"
- [Who Validates the Validators?](https://arxiv.org/abs/2404.12272), Shankar et al., arXiv, 2024: "users need criteria to grade outputs, but grading outputs helps users define criteria."
- [Using LLM-as-a-Judge For Evaluation: A Complete Guide](https://hamel.dev/blog/posts/llm-judge/), Husain, hamel.dev, 2024: "You cannot write a good judge prompt until you’ve seen the data."
