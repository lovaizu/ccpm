# ux

## Goal

The developer builds what the product's users want.

## Template

[ux-template.md](ux-template.md)

## Example

[ux-example.md](ux-example.md)

## User benefits

- **Q1** (Roles, OKRs): Listing whom to build for, does the developer find every role that comes to the product with a want of its own, each with an objective for it?
- **Q2** (Roles, OKRs): Reading an objective, does the developer see which role it is for and what that role gets from the product?
- **Q3** (OKRs): Weighing a piece of work, does the developer see which one objective it brings closer, or that it brings none closer?
- **Q4** (OKRs): After a change, does the developer see from the key results whether to keep it?
- **Q5** (Roles, OKRs, Scenarios): Following a scenario, does the developer see, exchange by exchange, how its role goes from asking the product to having what its objective says?
- **Q6** (Scenarios): Meeting a point off the main path, does the developer see what the role does there and what it then has?
- **Q7** (the whole): Changing how the product works inside while its roles see the same, does the developer find the UX still true?

## Practices

### Q1: Listing whom to build for, does the developer find every role that comes to the product with a want of its own, each with an objective for it?

**Thinking**: Cut the roles by the want each brings to the product, not by what kind of thing takes them, and give each role the objective of its want, as a want with no objective is never built.

**Steps**

1. Where two roles want the same, merge them.

**Grounds**

- [Writing Effective Use Cases](https://web.archive.org/web/20210301131704id_/https://www.infor.uva.es/~mlaguna/is1/materiales/BookDraft1.pdf), Cockburn, draft for Addison-Wesley, 1999: "Brainstorm all the actors, human and non, who have an operational goal against the system."
- [Define Your Market](https://strategyn.com/jobs-to-be-done/jobs-to-be-done-playbook/define-your-market/), Ulwick, strategyn.com, 2021: "Products don’t have jobs-to-be-done—people do."
- [Barbara Minto: “MECE: I invented it, so I get to say how to pronounce it”](https://karriere.mckinsey.de/alumni/news-and-events/global-news/alumni-news/barbara-minto-mece-i-invented-it-so-i-get-to-say-how-to-pronounce-it), McKinsey & Company, karriere.mckinsey.de, 2018: "The concept required the groups of ideas to be MECE—divided pieces that were mutually exclusive of each other and collectively exhaustive in terms of the whole."

### Q2: Reading an objective, does the developer see which role it is for and what that role gets from the product?

**Thinking**: Write each objective as the progress its role is trying to make, in one sentence on one line: the role as its subject, then a verb, its object and the context it is done in, and no feature of the product, as an objective said from the product's side can be met while the role gains nothing.

**Steps**

1. Where the product could do all the sentence says while the role is no better off, rewrite it around what the role gains.

**Grounds**

- [Jobs to Be Done Theory](https://www.christenseninstitute.org/theory/jobs-to-be-done/), Clayton Christensen Institute, christenseninstitute.org, 2024: "Everyone has Jobs to Be Done in their lives—the progress they’re trying to make as they strive toward a goal or aspiration within particular circumstances."
- [Jobs to Be Done (JTBD): The Original Framework by Tony Ulwick](https://strategyn.com/jobs-to-be-done/), Anderson, strategyn.com, 2024: "Identify who is executing the job and define the core functional job in a single, solution-free statement."
- [Define Your Market](https://strategyn.com/jobs-to-be-done/jobs-to-be-done-playbook/define-your-market/), Ulwick, strategyn.com, 2021: "The product will help the group of people: [verb] + [object] + [contextual clarifier]"
- [Google's OKR Playbook](https://www.whatmatters.com/resources/google-okr-playbook), Google, whatmatters.com, no date: "Could the OKR get a 1.0 under reasonable circumstances — without providing direct enduser or economic benefit? If so, then reword the OKR to focus on the tangible benefit."
- [Google's OKR Playbook](https://www.whatmatters.com/resources/google-okr-playbook), Google, whatmatters.com, no date: "If your Objective doesn’t fit on one line, it probably isn’t crisp enough."

### Q3: Weighing a piece of work, does the developer see which one objective it brings closer, or that it brings none closer?

**Thinking**: Cut the objectives so that each piece of work brings exactly one of them closer, as a gain under two objectives leaves the developer unable to tell which the work serves.

**Steps**

1. Where one piece of work would bring two objectives closer, merge them.
2. Where an objective holds gains that pieces of work bring closer apart, split it.
3. Name, for each change planned or recently made that alters what a role gets, the one objective it brings closer.

**Grounds**

- [Set goals with OKRs](https://rework.withgoogle.com/en/guides/set-goals-with-okrs), Google re:Work, rework.withgoogle.com, 2016: "Once the organization knows what it’s focused on and how it will measure success, it can become easier for individuals to connect their projects with the organizational objectives."
- [Set goals with OKRs](https://rework.withgoogle.com/en/guides/set-goals-with-okrs), Google re:Work, rework.withgoogle.com, 2016: "Do the team priorities connect to any of the organizational key results?"

### Q4: After a change, does the developer see from the key results whether to keep it?

**Thinking**: Give each objective two key results that count what its role does or feels, KR.1 how well the role gets what the objective says and KR.2 the lead time to having it, with KR.2 bettered only while KR.1 does not get worse, as a result had fast but not well is no gain.

**Steps**

1. List how success or failure would show in what the role does or feels, such as giving up, undoing a result or working around the product.
2. Make each key result a share, an average per user, a count or a time, and name what it is counted out of.
3. Where both key results could get better while the role still does not get what the objective says, rework them.

**Grounds**

- [Measuring the User Experience on a Large Scale: User-Centered Metrics for Web Applications](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/36299.pdf), Rodden, Hutchinson and Fu, CHI, 2010: "Next, think about how success or failure in the goals might manifest itself in user behavior or attitudes. What actions would indicate the goal had been met?"
- [Measuring the User Experience on a Large Scale: User-Centered Metrics for Web Applications](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/36299.pdf), Rodden, Hutchinson and Fu, CHI, 2010: "Sometimes failure is easier to identify than success"
- [Measuring the User Experience on a Large Scale: User-Centered Metrics for Web Applications](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/36299.pdf), Rodden, Hutchinson and Fu, CHI, 2010: "Choose signals that are sensitive and specific to the goal – they should move only when the user experience is better or worse, not for other, unrelated reasons."
- [Measuring the User Experience on a Large Scale: User-Centered Metrics for Web Applications](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/36299.pdf), Rodden, Hutchinson and Fu, CHI, 2010: "Raw counts will go up as your user base grows, and need to be normalized; ratios, percentages, or averages per user are often more useful."
- [Google's OKR Playbook](https://www.whatmatters.com/resources/google-okr-playbook), Google, whatmatters.com, no date: "Make sure the metrics are unambiguous. If you say “1 million users,” is that all-time users or seven-day actives?"
- ['Improving ratings': audit in the British University system](https://gwern.net/doc/statistics/decision/1997-strathern.pdf), Strathern, European Review, 1997: "When a measure becomes a target, it ceases to be a good measure."
- [Google's OKR Playbook](https://www.whatmatters.com/resources/google-okr-playbook), Google, whatmatters.com, no date: "Is it reasonably possible to score 1.0 on all the Key Results, but still not achieve the intent of the Objective? If so, add or rework the Key Results until their successful completion guarantees that the Objective is also successfully completed."
- [Pairing Quantity and Quality Key Results: What are Some Examples?](https://www.whatmatters.com/faqs/quantity-quality-key-results-pairing-examples), Gil, whatmatters.com, no date: "In High Output Management, Andy Grove describes pairing Key Results as measuring “both effect and counter-effect.”"
- [Pairing Quantity and Quality Key Results: What are Some Examples?](https://www.whatmatters.com/faqs/quantity-quality-key-results-pairing-examples), Gil, whatmatters.com, no date: "This OKR anticipates that reducing pit stop time can lead to cutting corners or at the very least unintentional mistakes as the team speeds up their work."

### Q5: Following a scenario, does the developer see, exchange by exchange, how its role goes from asking the product to having what its objective says?

**Thinking**: Write for each objective one run of the main path, the one most of its role take, from the role's request to the gain that ends it, as the exchanges among the roles, the product and those outside it, as the main path is what most of the role meet.

**Steps**

1. Name each scenario by its objective's ID and a short active verb phrase saying how the role reaches it.
2. Write each exchange as one message, from the one who takes it to the one it acts on, saying what it passes, checks or changes.
3. Where a part repeats, mark it as a loop with its condition.
4. Read the scenario from start to end: the first message is the role's request, the last gives the role the end, and each moves toward it.

**Grounds**

- [Basic Use Case Template](https://web.archive.org/web/20160810073041/http://alistair.cockburn.us/Basic+use+case+template), Cockburn, Humans and Technology, 1998: "Use Case: <number> <the name should be the goal as a short active verb phrase>"
- [Basic Use Case Template](https://web.archive.org/web/20160810073041/http://alistair.cockburn.us/Basic+use+case+template), Cockburn, Humans and Technology, 1998: "<put here the steps of the scenario from trigger to goal delivery, and any cleanup after>"
- [Basic Use Case Template](https://web.archive.org/web/20160810073041/http://alistair.cockburn.us/Basic+use+case+template), Cockburn, Humans and Technology, 1998: "Trigger: <the action upon the system that starts the use case, may be time event>"
- [Writing Effective Use Cases](https://web.archive.org/web/20210301131704id_/https://www.infor.uva.es/~mlaguna/is1/materiales/BookDraft1.pdf), Cockburn, draft for Addison-Wesley, 1999: "The main success scenario is the most common, or perhaps easiest to understand, scenario."
- [Writing Effective Use Cases](https://web.archive.org/web/20210301131704id_/https://www.infor.uva.es/~mlaguna/is1/materiales/BookDraft1.pdf), Cockburn, draft for Addison-Wesley, 1999: "Write each sentence as a goal succeeding, distinctly moving the process forward. Write: "At some time, ActorA kicks ActorB with some information", or "System verifies validation conditions are met", or "System updates its state", or "ActorA has ActorB kick ActorC"."
- [Sequence diagrams](https://mermaid.js.org/syntax/sequenceDiagram.html), Mermaid, mermaid.js.org, no date: "It is possible to express loops in a sequence diagram."
- [Writing Effective Use Cases](https://web.archive.org/web/20210301131704id_/https://www.infor.uva.es/~mlaguna/is1/materiales/BookDraft1.pdf), Cockburn, draft for Addison-Wesley, 1999: "Does it run from trigger to delivery of the success end condition?"
- [Unified Modeling Language 2.5.1](https://www.omg.org/spec/UML/2.5.1/PDF), OMG, UML 2.5.1, 2017: "An Actor models a type of role played by an entity that interacts with the subjects of its associated UseCases (e.g., by exchanging signals and data). Actors may represent roles played by human users, external hardware, or other systems."

### Q6: Meeting a point off the main path, does the developer see what the role does there and what it then has?

**Thinking**: Write under each scenario each point where the role leaves the main path, such as a run that stops or a fault of the product, with what the role does there and what it then has, as the developer otherwise builds the main path alone and leaves the role with nothing off it.

**Steps**

1. Where the role gives up partway, say what it is left with.

**Grounds**

- [Basic Use Case Template](https://web.archive.org/web/20160810073041/http://alistair.cockburn.us/Basic+use+case+template), Cockburn, Humans and Technology, 1998: "<put here there extensions, one at a time, each refering to the step of the main scenario>"
- [Basic Use Case Template](https://web.archive.org/web/20160810073041/http://alistair.cockburn.us/Basic+use+case+template), Cockburn, Humans and Technology, 1998: "Failed End Condition: <the state of the world if goal abandoned>"

### Q7: Changing how the product works inside while its roles see the same, does the developer find the UX still true?

**Thinking**: Say only what the roles mean to do, see and receive, and nothing of how the product works inside, as any design that gives them the same then leaves the UX true.

**Steps**

1. Pick one change the design could make while the roles see the same, and flag each line that would have to change.
2. Rewrite each flagged line by what the role does, sees or receives, or leave it to the document that describes the inside, such as the architecture.

**Grounds**

- [Writing Effective Use Cases](https://web.archive.org/web/20210301131704id_/https://www.infor.uva.es/~mlaguna/is1/materiales/BookDraft1.pdf), Cockburn, draft for Addison-Wesley, 1999: "For computer systems, it is rare that we open up the black box."
- [Writing Effective Use Cases](https://web.archive.org/web/20210301131704id_/https://www.infor.uva.es/~mlaguna/is1/materiales/BookDraft1.pdf), Cockburn, draft for Addison-Wesley, 1999: "Show the intent of the actor, what it/they want and get accomplished in that step."
- [Deriving Specifications from Requirements: An Example](https://www.pamelazave.com/turnstile.pdf), Jackson and Zave, ICSE, 1995: "The requirement is concerned entirely with the environment, where the effects and benefits of the machine will be felt and assessed: the machine is purely a means to the end of achieving the required effect in the environment."
