# ux

## Goal

Whoever builds or changes the product, a person or an AI, makes it give its users what they come for.

## Parts

- **okrs**: The objectives, each with its key results, and a note that key results have no target values, because a measure made a target stops being a good measure (Goodhart's law), so they serve to judge how close the objective is.
  - **objective**: Each objective, with an ID the rest of the document points to: one short sentence of what a user gets from the product, with the user as its subject.
  - **key-result**: Under each objective, two key results, each with an ID the rest of the document points to and the direction that is better: first how well the user gets what the objective says, then the lead time from when the user needs it, on their request or on an event, to having it. The first comes first: lead time is shortened only by changes that keep how well.
- **scenarios**: The participants, then one scenario for each objective.
  - **participants**: Before the scenarios, in one place: each participant and whether it is a person, an AI or a script.
  - **scenario**: For one objective, named by its ID and a short name for how the user reaches it: the main path from when the user first needs it, on their request or on an event, to reaching it, laid out so the reader follows who does what, in order.

## Benefits

- **Q1** (objective): Reading an objective, does the builder know which user the product is for and what that user gets from it?
- **Q2** (okrs): Weighing a piece of work, can the builder tell which one objective it brings closer?
- **Q3** (objective, key-result): After a change, can the builder tell from the key results whether users came closer to the objective?
- **Q4** (key-result): Weighing a change that shortens the lead time, can the builder tell whether it keeps how well the user gets what the objective says?
- **Q5** (objective, scenarios): For each objective, can the builder follow, step by step, how its user goes from when they first need it to having what the objective says?
- **Q6** (participants, scenario): Building a step of a scenario, can the builder tell whether it waits for a person, is taken by an AI, or runs as a script?
- **Q7** (the whole): Can the builder change how the product works inside, while its users see the same, and leave the document as it is?

## Practices

### Q1: Reading an objective, does the builder know which user the product is for and what that user gets from it?

**Thinking**: An objective is the progress one user is trying to make, said from where they stand, not what the product does.

**Steps**

1. List each one who comes to the product with a goal of their own, a person or an AI, by the role they play.
2. Write each one's objective as one sentence that fits on one line: that user as its subject, then a verb, its object and the context it is done in, with no feature or mechanism of the product.
3. Ask whether the product could do all the sentence says while that user is no better off; if so, rewrite the sentence around what the user gains.

**Grounds**

- [Jobs to Be Done Theory](https://www.christenseninstitute.org/theory/jobs-to-be-done/), Clayton Christensen Institute, christenseninstitute.org, 2024: "Everyone has Jobs to Be Done in their lives—the progress they’re trying to make as they strive toward a goal or aspiration within particular circumstances."
- [Writing Effective Use Cases](https://web.archive.org/web/20210301131704id_/https://www.infor.uva.es/~mlaguna/is1/materiales/BookDraft1.pdf), Cockburn, draft in preparation for Addison-Wesley, 1999, The one page Summary: "Brainstorm all the actors, human and non, who have an operational goal against the system."
- [Define Your Market](https://strategyn.com/jobs-to-be-done/jobs-to-be-done-playbook/define-your-market/), Ulwick, Jobs-to-be-Done Playbook, strategyn.com, 2021: "Products don’t have jobs-to-be-done—people do."
- [Jobs to Be Done (JTBD): The Original Framework by Tony Ulwick](https://strategyn.com/jobs-to-be-done/), Strategyn (Tiffany Anderson), strategyn.com, 2024: "Identify who is executing the job and define the core functional job in a single, solution-free statement."
- [Define Your Market](https://strategyn.com/jobs-to-be-done/jobs-to-be-done-playbook/define-your-market/), Ulwick, Jobs-to-be-Done Playbook, strategyn.com, 2021: "The product will help the group of people: [verb] + [object] + [contextual clarifier]"
- [Google's OKR Playbook](https://www.whatmatters.com/resources/google-okr-playbook), Google, whatmatters.com, no date: "Could the OKR get a 1.0 under reasonable circumstances — without providing direct enduser or economic benefit? If so, then reword the OKR to focus on the tangible benefit."
- [Google's OKR Playbook](https://www.whatmatters.com/resources/google-okr-playbook), Google, whatmatters.com, no date: "If your Objective doesn’t fit on one line, it probably isn’t crisp enough."

### Q2: Weighing a piece of work, can the builder tell which one objective it brings closer?

**Thinking**: Objectives are cut so that each piece of work brings one of them closer, no gain is written twice, and none is left out.

**Steps**

1. List each user and what each gets from the product, and give each pair one objective; merge objectives that one piece of work would bring closer together, and split an objective that holds gains a piece of work could bring closer apart, until each piece of work brings exactly one closer.
2. Take each change planned or recently made that alters what a user gets, and name the one objective it brings closer.

**Grounds**

- [Barbara Minto: “MECE: I invented it, so I get to say how to pronounce it”](https://karriere.mckinsey.de/alumni/news-and-events/global-news/alumni-news/barbara-minto-mece-i-invented-it-so-i-get-to-say-how-to-pronounce-it), McKinsey & Company, alumni news, 2018: "The concept required the groups of ideas to be MECE—divided pieces that were mutually exclusive of each other and collectively exhaustive in terms of the whole."
- [Set goals with OKRs](https://rework.withgoogle.com/en/guides/set-goals-with-okrs), Google re:Work, rework.withgoogle.com, 2016: "Once the organization knows what it’s focused on and how it will measure success, it can become easier for individuals to connect their projects with the organizational objectives."
- [Set goals with OKRs](https://rework.withgoogle.com/en/guides/set-goals-with-okrs), Google re:Work, rework.withgoogle.com, 2016: "Do the team priorities connect to any of the organizational key results?"

### Q3: After a change, can the builder tell from the key results whether users came closer to the objective?

**Thinking**: A key result counts what users do or feel as they come closer to the objective, so it cannot get better while they get nothing more.

**Steps**

1. For the objective, list how success or failure would show in what the user does or feels, such as giving up, undoing a result or working around the product.
2. Turn the signs kept into two measures, each a share, an average per user, a count or a time, and name what it is counted out of: one of how well the user gets what the objective says, and the lead time from when the user needs it, on their request or on an event, to having it.
3. Ask whether all the objective's key results could get better while the user still does not get what the objective says; if so, add or rework key results until they could not.

**Grounds**

- [Measuring the User Experience on a Large Scale: User-Centered Metrics for Web Applications](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/36299.pdf), Rodden, Hutchinson and Fu, CHI 2010: "Next, think about how success or failure in the goals might manifest itself in user behavior or attitudes. What actions would indicate the goal had been met?"
- [Measuring the User Experience on a Large Scale: User-Centered Metrics for Web Applications](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/36299.pdf), Rodden, Hutchinson and Fu, CHI 2010: "Sometimes failure is easier to identify than success"
- [Measuring the User Experience on a Large Scale: User-Centered Metrics for Web Applications](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/36299.pdf), Rodden, Hutchinson and Fu, CHI 2010: "Choose signals that are sensitive and specific to the goal – they should move only when the user experience is better or worse, not for other, unrelated reasons."
- [Google's OKR Playbook](https://www.whatmatters.com/resources/google-okr-playbook), Google, whatmatters.com, no date: "What matters isn’t the launch, but its impact."
- [Measuring the User Experience on a Large Scale: User-Centered Metrics for Web Applications](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/36299.pdf), Rodden, Hutchinson and Fu, CHI 2010: "Raw counts will go up as your user base grows, and need to be normalized; ratios, percentages, or averages per user are often more useful."
- [Google's OKR Playbook](https://www.whatmatters.com/resources/google-okr-playbook), Google, whatmatters.com, no date: "Make sure the metrics are unambiguous. If you say “1 million users,” is that all-time users or seven-day actives?"
- ['Improving ratings': audit in the British University system](https://gwern.net/doc/statistics/decision/1997-strathern.pdf), Strathern, European Review 5(3), 1997, p. 308: "When a measure becomes a target, it ceases to be a good measure."
- [Google's OKR Playbook](https://www.whatmatters.com/resources/google-okr-playbook), Google, whatmatters.com, no date: "Is it reasonably possible to score 1.0 on all the Key Results, but still not achieve the intent of the Objective? If so, add or rework the Key Results until their successful completion guarantees that the Objective is also successfully completed."

### Q4: Weighing a change that shortens the lead time, can the builder tell whether it keeps how well the user gets what the objective says?

**Thinking**: Quality first, then lead time: each stage from the user's need to the result, such as asking, deciding, making and redoing, is made shorter only where the result stays as good, since a result had fast but not well is no gain.

**Steps**

1. Imagine the change, and ask whether it could make the first key result worse.
2. Keep it only where it could not.

**Grounds**

- [Google's OKR Playbook](https://www.whatmatters.com/resources/google-okr-playbook), Google, whatmatters.com, no date: "Well done OKRs are a motivational management tool that helps make it clear to teams what’s important, what to optimize, and what tradeoffs to make during their day-to-day work."
- [Risk-Aware Product Decisions in A/B Tests with Multiple Metrics](https://engineering.atspotify.com/2024/03/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics), Schultzberg, Ankargren and Frånberg, engineering.atspotify.com, 2024: "Clearly, this rule is insufficient when, for example, metrics move in conflicting directions."
- [Pairing Quantity and Quality Key Results: What are Some Examples?](https://www.whatmatters.com/faqs/quantity-quality-key-results-pairing-examples), Gil, whatmatters.com, no date: "In High Output Management, Andy Grove describes pairing Key Results as measuring “both effect and counter-effect.”"
- [Pairing Quantity and Quality Key Results: What are Some Examples?](https://www.whatmatters.com/faqs/quantity-quality-key-results-pairing-examples), Gil, whatmatters.com, no date: "This OKR anticipates that reducing pit stop time can lead to cutting corners or at the very least unintentional mistakes as the team speeds up their work."
- [Measuring the User Experience on a Large Scale: User-Centered Metrics for Web Applications](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/36299.pdf), Rodden, Hutchinson and Fu, CHI 2010: "Use the HEART framework to prompt articulation of goals (e.g. is it more important to attract new users, or to encourage existing users to become more engaged?)."
- [Risk-Aware Product Decisions in A/B Tests with Multiple Metrics](https://engineering.atspotify.com/2024/03/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics), Schultzberg, Ankargren and Frånberg, engineering.atspotify.com, 2024: "By articulating the heuristics that govern your decision-making process, you can design and analyze the experiment in a way that respects how you make decisions in the end."

### Q5: For each objective, can the builder follow, step by step, how its user goes from when they first need it to having what the objective says?

**Thinking**: A scenario is one run of the main path to the objective, the one most users take, from the request that starts it to the gain that ends it.

**Steps**

1. Name each scenario by its objective's ID and a short active verb phrase, the user its subject, saying how they reach it.
2. Write each step as one message, from the one who takes it to the one it acts on, saying what it passes, checks or changes, such as an arrow in a Mermaid sequence diagram.
3. Mark a part that repeats as a loop with its condition, holding each step that repeats.
4. Read the scenario from start to end: the first message is the user's request, the last gives the user the end, and each step moves toward it.

**Grounds**

- [Basic Use Case Template](https://web.archive.org/web/20160810073041/http://alistair.cockburn.us/Basic+use+case+template), Cockburn, HaT TR.96.03a, 1998: "Use Case: <number> <the name should be the goal as a short active verb phrase>"
- [Basic Use Case Template](https://web.archive.org/web/20160810073041/http://alistair.cockburn.us/Basic+use+case+template), Cockburn, HaT TR.96.03a, 1998: "<put here the steps of the scenario from trigger to goal delivery, and any cleanup after>"
- [Basic Use Case Template](https://web.archive.org/web/20160810073041/http://alistair.cockburn.us/Basic+use+case+template), Cockburn, HaT TR.96.03a, 1998: "Trigger: <the action upon the system that starts the use case, may be time event>"
- [Writing Effective Use Cases](https://web.archive.org/web/20210301131704id_/https://www.infor.uva.es/~mlaguna/is1/materiales/BookDraft1.pdf), Cockburn, draft in preparation for Addison-Wesley, 1999: "The main success scenario is the most common, or perhaps easiest to understand, scenario."
- [Writing Effective Use Cases](https://web.archive.org/web/20210301131704id_/https://www.infor.uva.es/~mlaguna/is1/materiales/BookDraft1.pdf), Cockburn, draft in preparation for Addison-Wesley, 1999: "Write each sentence as a goal succeeding, distinctly moving the process forward. Write: "At some time, ActorA kicks ActorB with some information", or "System verifies validation conditions are met", or "System updates its state", or "ActorA has ActorB kick ActorC"."
- [Sequence diagrams](https://mermaid.js.org/syntax/sequenceDiagram.html), Mermaid, mermaid.js.org: "It is possible to express loops in a sequence diagram."
- [Writing Effective Use Cases](https://web.archive.org/web/20210301131704id_/https://www.infor.uva.es/~mlaguna/is1/materiales/BookDraft1.pdf), Cockburn, draft in preparation for Addison-Wesley, 1999: "Does it run from trigger to delivery of the success end condition?"

### Q6: Building a step of a scenario, can the builder tell whether it waits for a person, is taken by an AI, or runs as a script?

**Thinking**: Each one that takes a step is named by its role and its kind, so the builder knows which step waits for a person and which runs without one.

**Steps**

1. In each scenario, name each participant it uses, with its kind, as the list of participants gives them, such as by declaring them at the start of a diagram.
2. Check each scenario: every message's sender and receiver is named there, and every name and kind is the one the list of participants gives.

**Grounds**

- [Unified Modeling Language 2.5.1](https://www.omg.org/spec/UML/2.5.1/PDF), OMG, 2017, chapter 18: "An Actor models a type of role played by an entity that interacts with the subjects of its associated UseCases (e.g., by exchanging signals and data). Actors may represent roles played by human users, external hardware, or other systems."
- [Writing Effective Use Cases](https://web.archive.org/web/20210301131704id_/https://www.infor.uva.es/~mlaguna/is1/materiales/BookDraft1.pdf), Cockburn, draft in preparation for Addison-Wesley, 1999: "An actor might be a person, a company or organization, a computer program or a computer system, hardware or software or both."
- [Sequence diagrams](https://mermaid.js.org/syntax/sequenceDiagram.html), Mermaid, mermaid.js.org: "The actor can have a convenient identifier and a descriptive label."
- [Writing Effective Use Cases](https://web.archive.org/web/20210301131704id_/https://www.infor.uva.es/~mlaguna/is1/materiales/BookDraft1.pdf), Cockburn, draft in preparation for Addison-Wesley, 1999: "Is it clear which actor is operating the goal (who is "kicking the ball?)"

### Q7: Can the builder change how the product works inside, while its users see the same, and leave the document as it is?

**Thinking**: The product is one closed box: the document says only what users mean to do, see and receive, so any design that gives them the same leaves it true.

**Steps**

1. Pick one change the design could make while users see the same, read every line, and flag each line that would have to change.
2. Rewrite each flagged line by what the user does, sees or receives, or leave it to the document that describes the design inside, such as the architecture document.

**Grounds**

- [Writing Effective Use Cases](https://web.archive.org/web/20210301131704id_/https://www.infor.uva.es/~mlaguna/is1/materiales/BookDraft1.pdf), Cockburn, draft in preparation for Addison-Wesley, 1999: "For computer systems, it is rare that we open up the black box."
- [Writing Effective Use Cases](https://web.archive.org/web/20210301131704id_/https://www.infor.uva.es/~mlaguna/is1/materiales/BookDraft1.pdf), Cockburn, draft in preparation for Addison-Wesley, 1999: "Show the intent of the actor, what it/they want and get accomplished in that step."
- [Deriving Specifications from Requirements: An Example](https://www.pamelazave.com/turnstile.pdf), Jackson and Zave, ICSE 1995: "The requirement is concerned entirely with the environment, where the effects and benefits of the machine will be felt and assessed: the machine is purely a means to the end of achieving the required effect in the environment."
