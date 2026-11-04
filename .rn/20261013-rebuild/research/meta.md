# Research: meta

Sources for the best practice of meta: how to build a best practice.
A best practice here is a standard, which a deliverable is judged by, and a practice, which it is built by.
Its users are the planner who builds it, the generator and the evaluator who use it, and in the end the user of each deliverable.
Every quote below was copied from the page at its URL, opened on 2026-11-02.
The sources already cited in meta.json's grounds are left out: Anthropic "Demystifying evals for AI agents", CheckEval (arXiv:2403.18771), Shankar et al. (arXiv:2404.12272) and Brookhart 2018.

## The standard starts from the goal and its user, top down

### Measurement is defined top down from goals

- Source: Victor R. Basili, Gianluigi Caldiera and H. Dieter Rombach, "The Goal Question Metric Approach", University of Maryland, PDF; the PDF prints no year.
- URL: https://www.cs.umd.edu/~mvz/handouts/gqm.pdf
- Quote:

  > This means that measurement must be defined in a top-down fashion. It must be focused, based on goals and models. A bottom-up approach will not work because there are many observable characteristics in software (e.g., time, number of defects, complexity, lines of code, severity of failures, effort, productivity, defect density), but which metrics one uses and how one interprets them it is not clear without the appropriate models and goals to define the context.

- What it says: what to check, and how to read the result, both come from the goal; a list of things one could check does not.

### Goal, then questions, then metrics

- Source: Victor R. Basili, Gianluigi Caldiera and H. Dieter Rombach, "The Goal Question Metric Approach", University of Maryland, PDF; the PDF prints no year.
- URL: https://www.cs.umd.edu/~mvz/handouts/gqm.pdf
- Quote:

  > A GQM model is a hierarchical structure (Figure 1) starting with a goal (specifying purpose of measurement, object to be measured, issue to be measured, and viewpoint from which the measure is taken). The goal is refined into several questions, such as the one in the example, that usually break down the issue into its major components. Each question is then refined into metrics, some of them objective such as the one in the example, some of them subjective.

- What it says: the standard is a tree, and each question is a component of the goal seen from a stated viewpoint.

### A goal names its purpose, object, quality and viewpoint

- Source: Victor R. Basili, Gianluigi Caldiera and H. Dieter Rombach, "The Goal Question Metric Approach", University of Maryland, PDF; the PDF prints no year.
- URL: https://www.cs.umd.edu/~mvz/handouts/gqm.pdf
- Quote:

  > A goal is defined for an object, for a variety of reasons, with respect to various models of quality, from various points of view, relative to a particular environment.

- What it says: a goal without its viewpoint, here the user, leaves the questions without a ground.

### Criteria come from what "a good X" means to an expert

- Source: Michael Scriven, "The Logic and Methodology of Checklists", Western Michigan University Evaluation Center, June 2000, revised October 2005 and December 2007.
- URL: https://wmich.edu/sites/default/files/attachments/u350/2014/logic%26methodology_dec07.pdf
- Quote:

  > The key question to ask is this: What properties are parts of the concept (the meaning) of “a good X,” for someone who is an expert on Xs.

- What it says: each criterion is derived from what makes this kind of thing good, not borrowed from a general list.

### A checklist rests on a theory of what the thing must do well

- Source: Michael Scriven, "The Logic and Methodology of Checklists", Western Michigan University Evaluation Center, 2000, revised 2007.
- URL: https://wmich.edu/sites/default/files/attachments/u350/2014/logic%26methodology_dec07.pdf
- Quote:

  > It’s not a theory about how watches work, but about what they need to do well in order to perform their defining function well. An evaluative theory of X is just the idea that a certain list is a comlist for X.

- What it says: the standard is a claim about the deliverable's function, and it can be argued and tested as one. (A "comlist" is Scriven's term for a checklist of criteria of merit.)

### Start from the people the thing affects and their needs

- Source: Michael Scriven, "Key Evaluation Checklist", Western Michigan University Evaluation Center, February 2007.
- URL: https://wmich.edu/sites/default/files/attachments/u350/2014/key%20evaluation%20checklist.pdf
- Quote:

  > Consumers comprise (i) the recipients/users of the services/products (i.e., the downstream direct impactees) PLUS (ii) the downstream indirect impactees (e.g., recipient’s family or coworkers, who are impacted via ripple effect).

- What it says: the user is named first, including those reached through the direct user, such as the caller of a subagent.

## Each check asks about the thing itself, not a sign of it

### Criteria, not indicators

- Source: Michael Scriven, "The Logic and Methodology of Checklists", Western Michigan University Evaluation Center, 2000, revised 2007.
- URL: https://wmich.edu/sites/default/files/attachments/u350/2014/logic%26methodology_dec07.pdf
- Quote:

  > 1. The checkpoints should refer to criteria and not mere indicators (explained below).

- What it says: a check asks whether the user gets what they need, not whether a feature often found in good work is present.

### Indicators are easily gamed

- Source: Michael Scriven, "The Logic and Methodology of Checklists", Western Michigan University Evaluation Center, 2000, revised 2007.
- URL: https://wmich.edu/sites/default/files/attachments/u350/2014/logic%26methodology_dec07.pdf
- Quote:

  > But keep in mind that indicators are easily corrupted, and once it becomes known that they are being used as an indicator for something important in an evaluation, people are very ingenious about faking the score on them; you can’t do this with a criterion of merit, since it’s valid by definition.

- What it says: a generator who knows the checks will meet a checked sign without meeting the need behind it.

### The test of the skill is not the skill

- Source: W. James Popham, "What's Wrong—and What's Right—with Rubrics", Educational Leadership, Vol. 55, No. 2, ASCD, 1997-10-01.
- URL: https://ascd.org/el/articles/whats-wrong-and-whats-right-with-rubrics
- Quote:

  > Teachers must keep in mind that performance tests represent skills. The tests are not the skills themselves.

- What it says: passing the checklist stands for fitness to the user's purpose and must not replace it.

### Task-specific criteria do not guide the maker

- Source: W. James Popham, "What's Wrong—and What's Right—with Rubrics", Educational Leadership, ASCD, 1997.
- URL: https://ascd.org/el/articles/whats-wrong-and-whats-right-with-rubrics
- Quote:

  > Teachers need evaluative criteria that capture the essential ingredients of the skill being measured, not the particular display of that skill applied to a specific task.

- What it says: a question tied to one example deliverable cannot guide the generator of the next one.

### Criteria so general that they say nothing

- Source: W. James Popham, "What's Wrong—and What's Right—with Rubrics", Educational Leadership, ASCD, 1997.
- URL: https://ascd.org/el/articles/whats-wrong-and-whats-right-with-rubrics
- Quote:

  > In essence, these overly general criteria allow both teachers and students to conclude that really good student responses to the task are, well, really good. And, of course, really bad student responses are—you guessed it—really bad.

- What it says: a question that only asks whether the work is good gives neither the generator nor the evaluator anything to act on.

## The list is complete, without overlap, clear, short and checkable

### Scriven's requirements for a checklist of criteria

- Source: Michael Scriven, "The Logic and Methodology of Checklists", Western Michigan University Evaluation Center, 2000, revised 2007.
- URL: https://wmich.edu/sites/default/files/attachments/u350/2014/logic%26methodology_dec07.pdf
- Quote:

  > 2. The list should be complete (no significant omissions). 3. The items should be contiguous, i.e., nonoverlapping (essential if the list is used for scoring).4 4. The criteria should be commensurable (explained below). And of course: 5. The criteria should be clear (a.k.a. comprehensible, applicable). 6. The list should be concise (to assist its mnemonic function); i.e., it should contain no superfluous criteria. 7. The criteria should be confirmable (e.g., measurable or reliably inferrable).

- What it says: these six, with "criteria, not indicators", are requirements on the checklist as a whole. (The "4" after "scoring)." is a footnote mark in the PDF.)

### A missing criterion lets a poor thing pass

- Source: Michael Scriven, "The Logic and Methodology of Checklists", Western Michigan University Evaluation Center, 2000, revised 2007.
- URL: https://wmich.edu/sites/default/files/attachments/u350/2014/logic%26methodology_dec07.pdf
- Quote:

  > For example, it is essential that it is complete or very close to complete, i.e., that it include every significant criterion of merit. Otherwise, something that scores well on it may in fact be quite inferior because of its poor performance on some missing but crucial dimension of merit.

- What it says: completeness matters because the evaluator judges by the standard alone.

### Overlapping criteria count one fault twice

- Source: Michael Scriven, "The Logic and Methodology of Checklists", Western Michigan University Evaluation Center, 2000, revised 2007.
- URL: https://wmich.edu/sites/default/files/attachments/u350/2014/logic%26methodology_dec07.pdf
- Quote:

  > Again, the criteria in a comlist should not overlap if it is to be used as a basis for scoring to avoid “double-counting” of the overlap area.

- What it says: each need is checked in one place.

### Validate the list by looking for a case it would wrongly pass

- Source: Michael Scriven, "The Logic and Methodology of Checklists", Western Michigan University Evaluation Center, 2000, revised 2007.
- URL: https://wmich.edu/sites/default/files/attachments/u350/2014/logic%26methodology_dec07.pdf
- Quote:

  > Then one tries to construct hypothetical cases in which an entity has all the properties in the proposed comlist but still lacks something that would be required or important in order to justify an assignment of merit.

- What it says: the planner tests the standard by inventing a deliverable that passes every check yet fails its user.

### Unpack criteria into subcriteria

- Source: Michael Scriven, "The Logic and Methodology of Checklists", Western Michigan University Evaluation Center, 2000, revised 2007.
- URL: https://wmich.edu/sites/default/files/attachments/u350/2014/logic%26methodology_dec07.pdf
- Quote:

  > The richness and value of a comlist is often greatly increased by unpacking some of the criteria. Doing so is still part of comlist development and often the hardest and most useful part.

- What it says: a criterion becomes usable when it is broken into parts the evaluator can check one by one.

### Group items by what the checklist is for

- Source: Michael Scriven, "The Logic and Methodology of Checklists", Western Michigan University Evaluation Center, 2000, revised 2007.
- URL: https://wmich.edu/sites/default/files/attachments/u350/2014/logic%26methodology_dec07.pdf
- Quote:

  > For example, in the laundry list itself, if the function is to control the actions of the laundry person, colored articles need to be listed separately from the white ones. But if the task is simply to make a record of what went to the laundry, the color of the shirts is irrelevant.

- What it says: the same items are divided differently for a generator's practice and for an evaluator's standard.

### Combine overlapping criteria, but do not bury the ones that matter

- Source: Heidi Goodrich Andrade, "Using Rubrics to Promote Thinking and Learning", Educational Leadership, Vol. 57, No. 5, ASCD, 2000-02-01. (The page shows no byline; the article cites the author's own studies as Andrade, 1999 and Goodrich, 1996.)
- URL: https://ascd.org/el/articles/using-rubrics-to-promote-thinking-and-learning
- Quote:

  > You are likely to end up with a long list of criteria, many of which may relate to one another or even overlap. After class, take time to combine criteria. Avoid creating categories that are too big, and don't bury criteria that you want to emphasize.

- What it says: merging removes overlap, and a key point keeps a question of its own.

### Few criteria, because long rubrics go unused

- Source: W. James Popham, "What's Wrong—and What's Right—with Rubrics", Educational Leadership, ASCD, 1997.
- URL: https://ascd.org/el/articles/whats-wrong-and-whats-right-with-rubrics
- Quote:

  > For openers, such a rubric would contain three to five evaluative criteria. It is tempting to lay out all of the possible criteria that could be used to judge students' responses; but rubric developers should remember that their efforts should guide teachers, not overwhelm them. In rubrics, less is more.

- What it says: the standard is sized for the person who must use it.

### Detail buys agreement but costs use

- Source: W. James Popham, "What's Wrong—and What's Right—with Rubrics", Educational Leadership, ASCD, 1997.
- URL: https://ascd.org/el/articles/whats-wrong-and-whats-right-with-rubrics
- Quote:

  > In general, the more detailed and constraining a rubric's scoring rules, the greater the likelihood of between-rater agreement.

- What it says: the same section asks whether to build short rubrics that are used or long ones that "won't be used", a trade-off the planner must decide.

## Each check gives a verdict that any judge would give

### Use pass or fail, with a written reason

- Source: Hamel Husain, "Creating a LLM-as-a-Judge That Drives Business Results", hamel.dev, 2024-10-29.
- URL: https://hamel.dev/blog/posts/llm-judge/
- Quote:

  > Forces Articulation of Expectations: When domain experts must decide if an interaction passes or fails, they are compelled to articulate their expectations clearly. This process uncovers nuances and unspoken assumptions about how the AI should behave.

- What it says: a yes-or-no check makes the planner say what is good enough.

### A score of 3 or 4 tells no one what to do

- Source: Hamel Husain, "Creating a LLM-as-a-Judge That Drives Business Results", hamel.dev, 2024-10-29.
- URL: https://hamel.dev/blog/posts/llm-judge/
- Quote:

  > It’s not actionable: People don’t know what to do with a 3 or 4. It’s not immediately obvious how this number is better than a 2. You need to be able to say “this interaction passed because…” and “this interaction failed because…”.

- What it says: the verdict carries its reason, so the generator knows what to fix.

### Uncalibrated scales are read differently by each judge

- Source: Hamel Husain, "Creating a LLM-as-a-Judge That Drives Business Results", hamel.dev, 2024-10-29.
- URL: https://hamel.dev/blog/posts/llm-judge/
- Quote:

  > Arbitrary Scoring Systems: Using uncalibrated scales (like 1-5) across multiple dimensions, where the difference between scores is unclear and subjective. What makes something a 3 versus a 4? Nobody knows, and different evaluators often interpret these scales differently.

- What it says: a check that two evaluators read differently gives two verdicts.

### LLM judges have known biases

- Source: Lianmin Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", arXiv:2306.05685, 2023.
- URL: https://arxiv.org/abs/2306.05685
- Quote:

  > We examine the usage and limitations of LLM-as-a-judge, including position, verbosity, and self-enhancement biases, as well as limited reasoning ability, and propose solutions to mitigate some of them.

- What it says: an AI evaluator may prefer the first or the longer answer, or its own; the same abstract reports "over 80% agreement" with human preferences for strong judges.

### Separate checks reduce the halo effect

- Source: Michael Scriven, "The Logic and Methodology of Checklists", Western Michigan University Evaluation Center, 2000, revised 2007.
- URL: https://wmich.edu/sites/default/files/attachments/u350/2014/logic%26methodology_dec07.pdf
- Quote:

  > Checklists in general, and particularly comlists, reduce the influence of the halo effect, i.e., the tendency to allow the presence of some highly valued feature to overinfluence one’s judgment of merit.

- What it says: one question per part keeps a strong part from hiding a weak one.

### Objective and subjective data differ by viewpoint

- Source: Victor R. Basili, Gianluigi Caldiera and H. Dieter Rombach, "The Goal Question Metric Approach", University of Maryland, PDF; the PDF prints no year.
- URL: https://www.cs.umd.edu/~mvz/handouts/gqm.pdf
- Quote:

  > Subjective: If they depend on both the object that is being measured and the viewpoint from which they are taken; E.g., readability of a text, level of user satisfaction.

- What it says: a check on whether the reader understands depends on who reads, so the check names its reader.

## Weights and minimum bars are set on purpose

### Bars are minimums that no other strength makes up for

- Source: Michael Scriven, "Key Evaluation Checklist", Western Michigan University Evaluation Center, February 2007.
- URL: https://wmich.edu/sites/default/files/attachments/u350/2014/key%20evaluation%20checklist.pdf
- Quote:

  > The “bars” are absolute minimum standards for acceptability, if any. That is, they are minima on a particular scale that must be “cleared” (exceeded) if the candidate is to be acceptable, no matter how well she or he scores on other scales.

- What it says: a deliverable that fails one essential check fails, whatever else it does well.

### A holistic bar can fail what clears every single bar

- Source: Michael Scriven, "Key Evaluation Checklist", Western Michigan University Evaluation Center, February 2007.
- URL: https://wmich.edu/sites/default/files/attachments/u350/2014/key%20evaluation%20checklist.pdf
- Quote:

  > We can describe this as a case where they failed to clear a holistic (or overall) bar that was implicit in this example, but can often be made explicit through dialog.

- What it says: a question on the whole catches what the part questions each let through.

### Keep equal weights unless the evidence is overwhelming

- Source: Michael Scriven, "The Logic and Methodology of Checklists", Western Michigan University Evaluation Center, 2000, revised 2007.
- URL: https://wmich.edu/sites/default/files/attachments/u350/2014/logic%26methodology_dec07.pdf
- Quote:

  > 1. Do not abandon equal weighting without overwhelming evidence.

- What it says: the same list warns "almost never go beyond the ratio of 2".

## The standard is drawn from real examples and revised

### Look at good and poor work first

- Source: Heidi Goodrich Andrade, "Using Rubrics to Promote Thinking and Learning", Educational Leadership, ASCD, 2000.
- URL: https://ascd.org/el/articles/using-rubrics-to-promote-thinking-and-learning
- Quote:

  > Look at models. Review examples of good and poor work on a project like the one your students are about to undertake.

- What it says: the steps that follow are "List criteria.", "Pack and unpack criteria.", "Create a draft rubric." and "Revise the draft."

### A judge prompt is written after seeing the data

- Source: Hamel Husain, "Creating a LLM-as-a-Judge That Drives Business Results", hamel.dev, 2024-10-29.
- URL: https://hamel.dev/blog/posts/llm-judge/
- Quote:

  > You cannot write a good judge prompt until you’ve seen the data.

- What it says: the questions of a standard come from real deliverables, not only from reasoning ahead of them.

### Go through the checklist more than once

- Source: Michael Scriven, "Key Evaluation Checklist", Western Michigan University Evaluation Center, February 2007.
- URL: https://wmich.edu/sites/default/files/attachments/u350/2014/key%20evaluation%20checklist.pdf
- Quote:

  > This is an iterative checklist, not a one-shot checklist. You should expect to go through it several times, even for design purposes, since discoveries or problems that come up under later checkpoints will often require modification of what was entered under earlier ones (and no rearrangement of the order will avoid this).

- What it says: the practice expects the generator to return to earlier parts when a later one changes them.

### Guidelines can conflict, so each states its reason

- Source: Asaf Degani and Earl L. Wiener, "Human Factors of Flight-Deck Checklists: The Normal Checklist", NASA Contractor Report 177549, May 1990.
- URL: https://ntrs.nasa.gov/api/citations/19910017830/downloads/19910017830.pdf
- Quote:

  > These considerations are not specifications, and some when applied individually may conflict. Therefore, each should be carefully evaluated for its relevance to operational constraints and the checklist philosophy-of-use in any specific airline operation. The section in the report which explains the rationale for each guideline is given in parenthesis.

- What it says: each guideline points to its rationale, so the user can judge a conflict.

### Say which guideline wins a conflict

- Source: Asaf Degani and Earl L. Wiener, "Human Factors of Flight-Deck Checklists: The Normal Checklist", NASA Contractor Report 177549, May 1990.
- URL: https://ntrs.nasa.gov/api/citations/19910017830/downloads/19910017830.pdf
- Quote:

  > We note that this guideline could be in conflict with Nos. (8) and (9) above. In most cases where this occurs, this guideline (10) should take precedence.

- What it says: where two rules can clash, the standard says which one holds.

## The checklist is used as meant, not ticked by rote

### Ticking without reading the meaning creates risk

- Source: Michael Scriven, "The Logic and Methodology of Checklists", Western Michigan University Evaluation Center, 2000, revised 2007.
- URL: https://wmich.edu/sites/default/files/attachments/u350/2014/logic%26methodology_dec07.pdf
- Quote:

  > Daniel Stufflebeam reports on a pilot whose considered judgment was that some pilots he had flown with had focused more on covering the preflight checklist in the sense of checking items off it, but not on the meaning of the checkpoints, thereby creating serious risks.

- What it says: a check without its why invites a yes given without looking.

### Responses given from memory, not from the state

- Source: Asaf Degani and Earl L. Wiener, "Human Factors of Flight-Deck Checklists: The Normal Checklist", NASA Contractor Report 177549, May 1990.
- URL: https://ntrs.nasa.gov/api/citations/19910017830/downloads/19910017830.pdf
- Quote:

  > The pilot would "run" the checklist, but the reply would be done from memory, and not based on the actual state of the item.

- What it says: the evaluator must look at the deliverable for each check, not answer from expectation.

### A response states the value seen, not "checked"

- Source: Asaf Degani and Earl L. Wiener, "Human Factors of Flight-Deck Checklists: The Normal Checklist", NASA Contractor Report 177549, May 1990.
- URL: https://ntrs.nasa.gov/api/citations/19910017830/downloads/19910017830.pdf
- Quote:

  > Checklist responses should portray the desired status or the value of the item being considered (not just "checked" or "set").

- What it says: a verdict cites what the evaluator saw, which makes a rote answer visible.

### Split a long checklist into chunks

- Source: Asaf Degani and Earl L. Wiener, "Human Factors of Flight-Deck Checklists: The Normal Checklist", NASA Contractor Report 177549, May 1990.
- URL: https://ntrs.nasa.gov/api/citations/19910017830/downloads/19910017830.pdf
- Quote:

  > A long checklist should be subdivided to smaller task-checklists or chunks that can be associated with systems and functions within the cockpit.

- What it says: the checks are grouped by the part of the deliverable they belong to.

### Put the most critical items first

- Source: Asaf Degani and Earl L. Wiener, "Human Factors of Flight-Deck Checklists: The Normal Checklist", NASA Contractor Report 177549, May 1990.
- URL: https://ntrs.nasa.gov/api/citations/19910017830/downloads/19910017830.pdf
- Quote:

  > The most critical items on the task-checklist should be listed as close as possible to the beginning of the task-checklist, in order to increase the likelihood of completing the task before interruptions may occur.

- What it says: order within the standard follows how much each check matters.

## Each decision keeps its reason with it

### Without the reason, a later reader can only accept or change blindly

- Source: Michael Nygard, "Documenting Architecture Decisions", Cognitect blog, 2011-11-15.
- URL: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- Quote:

  > One of the hardest things to track during the life of a project is the motivation behind certain decisions. A new person coming on to a project may be perplexed, baffled, delighted, or infuriated by some past decision. Without understanding the rationale or consequences, this person has only two choices:

- What it says: the two choices are "Blindly accept the decision." and "Blindly change it.", which is why each part of a standard carries its why.

### Too many unexplained decisions freeze the project

- Source: Michael Nygard, "Documenting Architecture Decisions", Cognitect blog, 2011-11-15.
- URL: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- Quote:

  > If the project accumulates too many decisions accepted without understanding, then the development team becomes afraid to change anything and the project collapses under its own weight.

- What it says: a standard whose questions lack reasons cannot be changed with confidence.

### List all consequences, not only the good ones

- Source: Michael Nygard, "Documenting Architecture Decisions", Cognitect blog, 2011-11-15.
- URL: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- Quote:

  > This section describes the resulting context, after applying the decision. All consequences should be listed here, not just the "positive" ones.

- What it says: a decision's record includes what it costs, so a later reader can weigh it.

### A reversed decision is kept and marked superseded

- Source: Michael Nygard, "Documenting Architecture Decisions", Cognitect blog, 2011-11-15.
- URL: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- Quote:

  > If a decision is reversed, we will keep the old one around, but mark it as superseded. (It's still relevant to know that it was the decision, but is no longer the decision.)

- What it says: this is one way to keep history; the repository's own rule keeps history in git instead.

### Small documents are read and kept up to date

- Source: Michael Nygard, "Documenting Architecture Decisions", Cognitect blog, 2011-11-15.
- URL: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- Quote:

  > Large documents are never kept up to date. Small, modular documents have at least a chance at being updated.

- What it says: a standard split into small parts, each with one question, can be mended part by part.

## Not found

- Michael Scriven, "Evaluation Thesaurus" (1991) and "The Logic of Criteria" (1959): I found no open copy and did not look further.
- Jonsson and Svingby (2007), "The use of scoring rubrics: Reliability, validity and educational consequences": the ScienceDirect page returned HTTP 403.
- Phillip Dawson, "Assessment rubrics: towards clearer and more replicable design, research and practice" (Assessment & Evaluation in Higher Education 42:3, 2017): the Deakin repository page returned HTTP 202 with no content, then 403.
- Werner Kunz and Horst Rittel, "Issues as Elements of Information Systems" (1970), the source of IBIS: I opened the eScholarship PDF, but it is a scanned image with no text layer, so I could not copy a quote.
- MacLean et al. (1991), "Questions, Options, and Criteria" (QOC) design rationale: I did not find an open copy.
- Gawande and Boorman, "A Checklist for Checklists" (Project Check): I found only secondary references and no live primary copy.
- The year of the GQM paper is not printed in the PDF I opened, so the entries leave it out.
