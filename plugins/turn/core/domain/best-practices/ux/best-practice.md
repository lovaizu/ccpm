# ux

## Goal

The developer builds what the product's users want.

## Template

[template.md](template.md)

## Example

[example.md](example.md), a copy of [../../../../../../dev/turn/ux.md](../../../../../../dev/turn/ux.md)

## User benefits

- **Q1** (Roles): Listing whom to build for, does the developer find every role that comes to the product with a want of its own?
- **Q2** (Roles, OKRs): Reading an objective, does the developer see what its role gets from the product?
- **Q3** (OKRs): Weighing a piece of work, does the developer see which one objective it brings closer, or that it brings none closer?
- **Q4** (OKRs): After a change, does the developer see from the key results whether to keep it?
- **Q5** (Roles, OKRs, Product): Weighing the product against what its roles do today, does the developer see why it meets each objective where that way does not?
- **Q6** (Roles, OKRs, Product, Scenarios): Following a scenario, does the developer see, exchange by exchange, how its role goes from asking the product to having what its objective says?
- **Q7** (the whole): Changing how the product works inside while its roles see the same, does the developer find the UX still true?

## Practices

### Q1: Listing whom to build for, does the developer find every role that comes to the product with a want of its own?

**Thinking**: Cut the roles by the want each brings to the product, not by what kind of thing takes them, as a role cut otherwise hides a want or splits one.

**Steps**

1. Walk through who uses the product, who runs it, who receives what it makes, who is affected by it, and each AI or system that calls it, over the product's whole life.
2. Where two roles want the same, merge them.
3. Where one role is left, name it the user, as a name made up for the only role tells the reader nothing more.
4. Ask the user who else comes to the product, and confirm with them each role the request does not show.

### Q2: Reading an objective, does the developer see what its role gets from the product?

**Thinking**: Give each role the objective of its want, written as the progress the role is trying to make, in one sentence on one line: the role as its subject, then a verb, its object and the context it is done in, and no feature of the product, as a want with no objective is never built, and an objective said from the product's side can be met while the role gains nothing.

**Steps**

1. Where a want is said as a feature, ask why it is needed until the answer is that without it the role's problem stays unsolved, and write that.
2. Take an objective from what the role has been seen to do, such as records of real use or complaints. Confirm with the user one that rests on what is only said or guessed.
3. Where the product could do all the sentence says while the role is no better off, rewrite it around what the role gains.

### Q3: Weighing a piece of work, does the developer see which one objective it brings closer, or that it brings none closer?

**Thinking**: Cut the objectives so that each piece of work brings exactly one of them closer, as a gain under two objectives leaves the developer unable to tell which the work serves.

**Steps**

1. Where one piece of work would bring two objectives closer, merge them.
2. Where an objective holds gains that pieces of work bring closer apart, split it.
3. Name, for each change planned or recently made that alters what a role gets, the one objective it brings closer.

### Q4: After a change, does the developer see from the key results whether to keep it?

**Thinking**: Give each objective two key results that count what its role does or feels, KR.1 how well the role gets what the objective says and KR.2 the lead time to having it, with KR.2 bettered only while KR.1 does not get worse, as a result had fast but not well is no gain.

**Steps**

1. List how success or failure would show in what the role does or feels, such as giving up, undoing a result or working around the product.
2. Make each key result a share, an average per user, a count or a time, and name what it is counted out of.
3. Where both key results could get better while the role still does not get what the objective says, rework them.

### Q5: Weighing the product against what its roles do today, does the developer see why it meets each objective where that way does not?

**Thinking**: Find with the user, by trying ideas together, the few that set the product apart from what its roles do today and make it meet each objective, drawing the user's own words out before offering any idea, as a concept cannot be read off facts: its maker finds it by trying ideas against the problem, and ideas an AI offers first crowd out the maker's own and come out alike.

**Steps**

1. Ask the user what the roles do today without the product and where that falls short of each objective. Say their words back to them and ask what else, before offering any idea.
2. Turn each shortfall into a question of how the product might meet the objective there, and let the user pick the ones to work on.
3. Ask the user for their ideas first. Then add ideas that differ from theirs and from one another, judging none yet.
4. Rate each idea against the roles' present way, better, the same or worse, for each objective. Combine and improve them, and let the user choose.
5. Argue against the ideas chosen, and write the riskiest assumption under them with how it would be checked.
6. Stop once at most five ideas stand out, each meets an objective, the present way they beat is named, and the riskiest assumption has its check. Otherwise go back to the first or the third step.
7. Keep, where the design is kept, each idea tried, whose it was, how it rated, and why it was kept, dropped or merged, in the user's words.

### Q6: Following a scenario, does the developer see, exchange by exchange, how its role goes from asking the product to having what its objective says?

**Thinking**: Write for each objective one run of the main path, the one most of its role take, from the role's request to the gain that ends it, as the exchanges among the roles, the product and those outside it, as the main path is what most of the role meet.

**Steps**

1. Name each scenario by its objective's ID and a short active verb phrase saying how the role reaches it.
2. Write each exchange as one message, from the one who takes it to the one it acts on, saying what it passes, checks or changes.
3. Where a part repeats, mark it as a loop with its condition.
4. Read the scenario from start to end: the first message is the role's request, the last gives the role the end, and each moves toward it.

### Q7: Changing how the product works inside while its roles see the same, does the developer find the UX still true?

**Thinking**: Say only what the roles mean to do, see and receive, and nothing of how the product works inside, as any design that gives them the same then leaves the UX true.

**Steps**

1. Pick one change the design could make while the roles see the same, and flag each line that would have to change.
2. Rewrite each flagged line by what the role does, sees or receives, or leave it to the document that describes the inside, such as the architecture.
