# `meta`

## Goal

The generator can make deliverables with which their role achieves its purpose.

## Template

[template.json](template.json)

## Intents

| ID | About | Question |
| --- | --- | --- |
| Q1 | goal | Reading the goal, does the generator see the one end the deliverable's role is after, so that it can tell for each part, and in each case no practice foresaw, whether what it makes serves that end? |
| Q2 | intents | Choosing the questions, does the generator ask where makers of the kind fail the role, as deliverables made without the best practice show and the field's sources name, so that the evaluator checks the failures that matter and not a list kept for completeness? |
| Q3 | intents | Judging a deliverable by a question, does the evaluator reach the verdict that someone who knows the role's work would reach, so that a pass means the role gets what it's after and not that the words are there? |
| Q4 | template, parts | Filling in the template, or making each part, does the generator know what each holds and what its reader uses it for, so that the deliverable holds what its role uses and nothing more? |
| Q5 | inputs, preconditions | Ordering the work, does the planner find the kinds a deliverable of the kind is made from and those whose deliverables must pass before it's made, so that no deliverable is made before what it stands on? |
| Q6 | practices | Reading a practice, does the generator meet the ways the field has established for the case and when each fits, under the names the field knows them by and with the sources they rest on, so that it brings the field's knowledge to any deliverable of the kind, whatever its language and tools, and not one maker's reasoning? |
| Q7 | practices | Following a practice, does the generator see what the deliverable must be and why, where the practice applies and where it doesn't, and what it costs, so that it follows the practice where it holds and sets it aside where it doesn't? |
| Q8 | practices | Following a practice's steps, does the generator meet a step only where skipping it or doing it out of order breaks the deliverable, each with the call that shows it done, so that a guard holds what must hold and the generator's judgment shapes the rest? |
| Q9 | example | Reading the examples, does the generator see what the template's slots or the parts become in deliverables that differ from one another, so that it takes the intent and not one product's particulars? |
| Q10 | the whole | Using deliverables made by the best practice for cases held back from its making, does the role achieve its purpose? |

## Practices

### Q1

Reading the goal, does the generator see the one end the deliverable's role is after, so that it can tell for each part, and in each case no practice foresaw, whether what it makes serves that end?

**Name**

Intent

**Thinking**

Write the end the deliverable's role is after as one sentence, with the role as its subject. Leave out what the deliverable holds, how the role reaches the end, and how the end would show, as a deliverable can hold each of these and still miss the end. Ask why of each draft until no further end shows. The generator and the evaluator weigh every other part against this sentence. A generator that knows the end the rules serve can tell where a practice holds in a case its maker didn't foresee, and where it no longer serves.

**Applies**

Every best practice, as each kind serves one end of one role.

**Excludes**

The goal doesn't say how to reach the end or how to check it. The practices say how, and the questions check it.

**Cost**

A sentence that holds only the end is harder to write than a list of contents, and it takes several drafts.

**Sources**

- [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html)
- [Gamma et al. 1994, as Wikipedia's Software design pattern sums it up](https://en.wikipedia.org/wiki/Software_design_pattern), secondary, as the maker read only a summary of it

### Q2

Choosing the questions, does the generator ask where makers of the kind fail the role, as deliverables made without the best practice show and the field's sources name, so that the evaluator checks the failures that matter and not a list kept for completeness?

**Name**

Killer items

**Thinking**

Before you write a question, make real deliverables of the kind without the best practice, and keep each way they fail their role. Add the failures that the field's sources name for the kind. Write a question for each failure that matters, and none for a section where makers don't fail, as a checklist works when it holds the items most often missed and most dangerous to skip, and a long list imposed for completeness showed no effect. The WHO's checklist of 19 such items, said aloud at three points of an operation, went with a fall in deaths from 1.5% to 0.8% across eight hospitals. Merge two questions that fail the same deliverables for the same reason. Revise the questions once you've read many real deliverables, as reading them shows criteria that no one could name before.

**Applies**

Choosing a kind's questions, and revising them after a trial.

**Excludes**

A fault a script finds, such as a file out of its schema, needs no question. Leave it to the script.

**Cost**

The runs without the best practice take time before any writing starts. A failure that no run showed and no source named goes unasked until a trial finds it, and Q10 then adds its question.

**Sources**

- [Gawande's Read-Do and Do-Confirm checklists, as Sketchplanations sums them up](https://sketchplanations.com/read-do-do-confirm-checklists), secondary, as the maker read only a summary of it
- [Gawande, The Checklist Manifesto, as Steve Grossi sums it up](https://www.stevegrossi.com/on/the-checklist-manifesto), secondary, as the maker read only a summary of it
- [Haynes et al., A Surgical Safety Checklist to Reduce Morbidity and Mortality in a Global Population, NEJM 2009](https://dash.harvard.edu/server/api/core/bitstreams/c5287a52-75bc-4131-9262-4c598fcde8cc/content)
- [Urbach et al. 2014 in the New England Journal of Medicine, as HospiMedica reports it](https://www.hospimedica.com/surgical-techniques/articles/294752136/surgical-checklists-less-effective-than-previously-assumed.html), secondary, as the maker read only a summary of it
- [Bosk et al. 2009 in The Lancet, as ScienceDaily reports it](https://www.sciencedaily.com/releases/2009/09/090916092657.htm), secondary, as the maker read only a summary of it
- [Anthropic, Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Anthropic, skill-creator](https://raw.githubusercontent.com/anthropics/skills/main/skills/skill-creator/SKILL.md)
- [Shankar et al., Who Validates the Validators?](https://arxiv.org/abs/2404.12272)

### Q3

Judging a deliverable by a question, does the evaluator reach the verdict that someone who knows the role's work would reach, so that a pass means the role gets what it's after and not that the words are there?

**Name**

LLM-as-a-judge calibration, also known as inter-rater agreement

**Thinking**

Write each question as the moment the role uses the deliverable, what it needs there, and what it's after in that, in a clause that opens with "so that" and names that end. Leave the clause out only where what the role needs is the goal itself. Ask it for yes or no, as a vague or scaled question gives verdicts that differ from run to run and that no one can act on. Use a question once an evaluator judges it right on several kept deliverables whose answer someone who knows the role's work has given, with both passes and fails among them. Count how many of the passes and how many of the fails it got right, as agreement on one deliverable, or on a set of passes alone, shows nothing. Keep those deliverables and their answers beside the best practice, such as in a folder of cases, so that you judge each change to a question on them again. Judge with a model other than the one that made the deliverable, and let it answer that it can't tell.

**Applies**

Every question an evaluator judges, before the first run that rests on its verdict, and again after each change to it.

**Excludes**

A check that a script makes needs no calibration, as it judges the same way each time. Where no one who knows the role's work can give the answer for a kept deliverable, you can't calibrate the question yet. Ask the user.

**Cost**

Each question needs kept deliverables with known answers, both passes and fails, before it's used, and someone who knows the work to give those answers.

**Sources**

- [Anthropic, Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Anthropic, Develop tests](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [Husain, Creating a LLM-as-a-Judge](https://hamel.dev/blog/posts/llm-judge/)
- [McHugh, Interrater reliability: the kappa statistic, Biochemia Medica 2012](https://pmc.ncbi.nlm.nih.gov/articles/PMC3900052/)
- [Zheng et al., Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685)

### Q4

Filling in the template, or making each part, does the generator know what each holds and what its reader uses it for, so that the deliverable holds what its role uses and nothing more?

**Name**

Template, also known as Mandatory Elements Present

**Thinking**

Give a template where the kind's deliverable is one document, and name its parts where it's a set of files of a known form, such as code or a prompt, as those files' own form already lays them out and a template would only copy it. A template holds a section for each thing the role uses toward the goal, fixed text for what every deliverable of the kind shares, and a slot for the rest. Keep a section only where the role would fall short of the goal without it, as an AI writes past what a deliverable needs when it's only told not to, and the template leaves it no room. After each section, write a note saying of each slot what it holds, what its reader uses it for, and whether it's optional, marked so that a tool finds any note the generator leaves in a deliverable. rn's tools find a note by `DELETE_TEMPLATE_COMMENT`, so the marker is part of the template's form: a GitHub note whose first line opens with `DELETE_TEMPLATE_COMMENT:` in Markdown, and a key of that name in JSON. Where the deliverable has a schema of its own, such as a JSON Schema, make the schema the template and write each note in its field's description, as a second note beside the schema drifts from it. Write each slot so that its format shows it, such as `` `<name>` `` in Markdown, which drops a bare `<name>` as an HTML tag. Draw a figure in place of prose wherever one can say it, in a format the deliverable's readers see drawn, such as Mermaid for a sequence or SVG for any other, with a skeleton beside the template that shows the layout by the slots' names, such as `images/template-<name>.svg`. Give each part an id and what the role needs of it.

**Applies**

Every kind: a template where its deliverable is one document, and parts where it's a set of files of a known form.

**Excludes**

A best practice never gives both, as each would claim the deliverable's form and they'd drift apart.

**Cost**

A template fixes the order of sections, so a deliverable that would read better in another order waits for the template to change.

**Sources**

- [Nygard, Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [MADR](https://adr.github.io/madr/)
- [Meszaros and Doble, A Pattern Language for Pattern Writing](https://www.hillside.net/index.php/a-pattern-language-for-pattern-writing)
- [Anthropic, Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

### Q5

Ordering the work, does the planner find the kinds a deliverable of the kind is made from and those whose deliverables must pass before it's made, so that no deliverable is made before what it stands on?

**Name**

Related patterns, also known as pattern language

**Thinking**

Name in `inputs` each kind whose deliverables a deliverable of this kind is made from, and in `preconditions` each kind whose deliverables must pass before one of this kind is made, each by the name of its best practice's folder. The plan holds each deliverable's own inputs and preconditions to these kinds, and orders it after them. A kind left out lets a deliverable be made on what isn't there yet. A kind named without need holds the deliverable back.

**Applies**

Every kind. Each list is empty where the kind takes none.

**Excludes**

The lists name kinds, not files. The plan names the deliverables that a given deliverable takes.

**Cost**

A deliverable of the kind can't start before the kinds it names, so a wrong entry delays every deliverable of the kind.

**Sources**

- [Alexander et al., A Pattern Language, pattern 159](https://www.patternlanguage.com/apl/aplsample/apl159/apl159.htm)
- [Alexander 1977, as Wikipedia's Pattern language sums it up](https://en.wikipedia.org/wiki/Pattern_language), secondary, as the maker read only a summary of it
- [Gamma et al. 1994, as Wikipedia's Software design pattern sums it up](https://en.wikipedia.org/wiki/Software_design_pattern), secondary, as the maker read only a summary of it

### Q6

Reading a practice, does the generator meet the ways the field has established for the case and when each fits, under the names the field knows them by and with the sources they rest on, so that it brings the field's knowledge to any deliverable of the kind, whatever its language and tools, and not one maker's reasoning?

**Name**

Evidence-based software engineering, also known as multivocal literature review

**Thinking**

Turn each failure a question asks of into a question that the field can answer. Search the field's primary sources and its established guides for the way it handles that case: standards, the guides of a tool's makers, books, and papers, ahead of blogs. Weigh each source by its authority, its method, and whether its claims rest on data. Where sources disagree, look first for a difference of context that explains it, and state the practice with that context. Otherwise take the side of the stronger evidence, and write which side you took and why. Stop once new sources add no new finding. State the practice for any language and tool the kind is made with, and name one only as an example, as a practice tied to one language fails a deliverable made in another. Give the intent, the ways the field has established for it, when each fits, and what each costs, such as McCabe's limit of 10 for a function's complexity, and leave to the plan the way, the tool, the file, and the threshold for each deliverable's case, as only the case shows which fits, and a practice that fixes one binds every case to it. Name a repository's own machinery, such as its scripts, only as an example. Keep the facts of what the kind is about, such as the documented behavior of the platform a plugin runs on, as those are the field's and no choice. Call the practice by the name the field knows it by, such as information hiding or Given-When-Then, and list the other names it goes by, as a name brings the field's knowledge to a reader who knows it. Put the name beside what the role needs of it, as no study shows that a name alone serves a model better than the idea said plainly. Name each source read, and mark one where only a summary of it was read. A practice reasoned out alone misses what the field already knows.

**Applies**

Every practice.

**Excludes**

A convention of the tools that run or check the best practice, such as the marker of a template's note, has those tools as its source, as no field holds it. A choice for one deliverable's case, such as a tool or a limit a project sets, goes in the plan as that deliverable's decision, not in the practice.

**Cost**

Research takes longer than reasoning a practice out, and the maker weighs each source's authority before using it. The plan then decides for each deliverable what the practice leaves open.

**Sources**

- [Durham, Evidence-Based Software Engineering](https://ebse.webspace.durham.ac.uk/)
- [Garousi, Felderer and Mäntylä, Guidelines for including grey literature and conducting multivocal literature reviews in software engineering](https://arxiv.org/abs/1707.02553)
- [GRADE Handbook](https://gdt.gradepro.org/app/handbook/handbook.html)
- [AGREE II Users Manual and 23-item Instrument](https://www.agreetrust.org/wp-content/uploads/2017/12/AGREE-II-Users-Manual-and-23-item-Instrument-2009-Update-2017.pdf)
- [Google eng-practices, The Standard of Code Review](https://google.github.io/eng-practices/review/reviewer/standard.html)
- [Anthropic, Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Meszaros and Doble, A Pattern Language for Pattern Writing](https://www.hillside.net/index.php/a-pattern-language-for-pattern-writing)

### Q7

Following a practice, does the generator see what the deliverable must be and why, where the practice applies and where it doesn't, and what it costs, so that it follows the practice where it holds and sets it aside where it doesn't?

**Name**

Visible forces, also known as Pros, Cons, and Decision

**Thinking**

Write first what the deliverable must be for the question's role, and why the role needs it so, in short sentences and in plain words, with no capitals that demand. Then write where the practice applies and where it doesn't, with what to do there instead, and what following it costs. A generator that knows why, and where a practice stops, finds its own way where the case differs, and sets the practice aside where it no longer serves the goal. Keep only what the generator lacks. Leave out what a capable model already knows, such as what a test is, as each needless sentence costs reading and hides what matters.

**Applies**

Every practice.

**Excludes**

A template's notes say only what a slot holds and what its reader uses it for, as the practice behind them already says why.

**Cost**

A practice takes longer to write and to read than a bare rule. Lead with what the deliverable must be, so that a reader can stop there.

**Sources**

- [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Meszaros and Doble, A Pattern Language for Pattern Writing](https://www.hillside.net/index.php/a-pattern-language-for-pattern-writing)
- [Gamma et al. 1994, as Wikipedia's Software design pattern sums it up](https://en.wikipedia.org/wiki/Software_design_pattern), secondary, as the maker read only a summary of it
- [Anthropic, Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Anthropic, skill-creator](https://raw.githubusercontent.com/anthropics/skills/main/skills/skill-creator/SKILL.md)
- [Anthropic, Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

### Q8

Following a practice's steps, does the generator meet a step only where skipping it or doing it out of order breaks the deliverable, each with the call that shows it done, so that a guard holds what must hold and the generator's judgment shapes the rest?

**Name**

Degrees of freedom

**Thinking**

Give a step only where skipping it or doing it out of order breaks the deliverable, such as running the tests before the code changes. Say everything else in the thinking, and leave the way to the generator, as a model that holds the intent often reasons past a hand-written plan, and the evaluator judges what was made, not the path. Give each step its trace, the call that shows it done, in the form the guard reads, as a guard holds a step only by a call it can match. In rn's form, the trace takes `run` for a command run, matched whole, `read` for a file read to its end, or `write` for a file made. Write each take as the step writes it, with a value the role's start gives as `{<name>}`, such as `{deliverable}`, a whole take for a file or one word of a command. For `run` and `write`, give more than one take where any of them shows the step done, and for `read`, each file the step reads whole. Order the steps as their calls come, as a guard, such as Lane, holds the role to each step by its trace, in the steps' order, and holds its end until each trace comes back.

**Applies**

An action whose skipping or order breaks the deliverable, and that a call shows on every run.

**Excludes**

An action of a case, which only some runs take, and a judgment, which no call shows, are no steps: a trace on either would stop the runs that rightly don't make it. Say them in the thinking, and the evaluator checks them.

**Cost**

A guard holds the role's end until each trace comes back, so a step given without need holds every run to it.

**Sources**

- [Anthropic, Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Anthropic, Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Anthropic, Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Lane, The lanes](../../../../lane/docs/lanes.md)

### Q9

Reading the examples, does the generator see what the template's slots or the parts become in deliverables that differ from one another, so that it takes the intent and not one product's particulars?

**Name**

Diverse, canonical examples

**Thinking**

Make deliverables of the kind by the template and the practices, pass each by the questions, and name them in `example`: one file, or a folder of several. Choose them to differ where the kind allows, in product, size, and shape, so that the generator sees what stays the same across them, which is the intent, and doesn't copy one product's content. Where a deliverable lies elsewhere for its own reader, such as a product vision in the developers' folder, name its path in `source`, and have a tool copy it with its figures beside the best practice, such as rn's `practices.py example`, as a copy made by hand drifts from the deliverable, and a symbolic link shows as a line of text where a host doesn't follow it, such as GitHub. Give no example until a deliverable of the kind passes, as one made to another form teaches that form.

**Applies**

Every kind, once a deliverable of it passes.

**Excludes**

Where the kind has one deliverable alone, such as a repository's one product vision, the example is that one, as the kind allows no other.

**Cost**

Each example is a whole deliverable to make and pass, and you make each again when the best practice changes.

**Sources**

- [Anthropic, Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Anthropic, Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Moher et al., Guidance for Developers of Health Research Reporting Guidelines, PLoS Medicine 2010](https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.1000217)

### Q10

Using deliverables made by the best practice for cases held back from its making, does the role achieve its purpose?

**Name**

Pilot testing, also known as evaluations first

**Thinking**

Hold back some real cases of the kind from the making, as you write the best practice to close the shortfalls of the cases you make it from, and only cases it hasn't met show whether it holds beyond them. Have a fresh generator, with the best practice alone, make a deliverable for each case held back, on each model that runs it. Have the role, or an AI holding what the role wants, use each deliverable for the goal. Check that the generator used the best practice as meant, not only that it had it. Read the deliverables and the verdicts, not only their counts. Trace each shortfall to the goal, a question, or a practice, and mend it there. Then judge the mended best practice again on the kept cases and on new ones held back.

**Applies**

Every best practice before its first use, and again after each change to it.

**Excludes**

A trial shows whether the whole works. It doesn't show whether each question judges right, which the kept deliverables of Q3 show.

**Cost**

Cases held back can't shape the best practice, so the maker needs more real cases than it writes from, and each trial runs a generator and the role on each.

**Sources**

- [Anthropic, Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Anthropic, Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [World Health Organization, safe surgery tools and resources](https://www.who.int/teams/integrated-health-services/patient-safety/research/safe-surgery/tool-and-resources)
- [Moher et al., Guidance for Developers of Health Research Reporting Guidelines, PLoS Medicine 2010](https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.1000217)
- [Urbach et al. 2014 in the New England Journal of Medicine, as HospiMedica reports it](https://www.hospimedica.com/surgical-techniques/articles/294752136/surgical-checklists-less-effective-than-previously-assumed.html), secondary, as the maker read only a summary of it
- [Bosk et al. 2009 in The Lancet, as ScienceDaily reports it](https://www.sciencedaily.com/releases/2009/09/090916092657.htm), secondary, as the maker read only a summary of it
