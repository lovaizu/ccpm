# `product-vision`

## Goal tree

- The developers build a product with which its users achieve their goals.
  - **C1** The developers know whom the product serves and what each of them is trying to achieve.
    - **N1** Does Roles list every kind of person who comes to the product with a goal of their own? (Roles)
    - **N2** Does each objective state, in one sentence, what one role is trying to achieve in their own work? (Objectives and key results)
    - **N3** Does the vision describe only what the users do and get, not how the product works inside? (the whole)
  - **C2** The developers can tell whether a change brings the users closer to their goals.
    - **N4** Does each objective have key results that measure how well and how fast its role achieves it, each with the direction that's better? (Objectives and key results)
    - **N5** Are the objectives distinct, so that each piece of work serves one of them? (Objectives and key results)
  - **C3** The developers know the one way by which the product brings its users to their goals, so that every choice leans toward it.
    - **N6** Does the concept state first the one way, as its maker means it, by which the product brings the users to their objectives, and then the ideas that keep this way holding at each moment of their use? (Concept)

## Template

[template.md](template.md)

## Practices

### N1

Does Roles list every kind of person who comes to the product with a goal of their own?

The developers build for the people Roles lists, so a missing role goes unserved, and two roles merged into one get a product that fits neither.

1. *While deciding.* Find the job that the product exists to do in the goal and the decisions of your cut, and, where the repository already holds the product, in its README. Write it in one sentence as what the product gets done for the people who come to it, such as `turns a request into a deliverable that the people it's for can use`. Where none of these says it, ask the user what the product gets done, and for whom.
2. *While deciding.* Name each kind of person who comes to the product for that job, by the job and not by a job title, such as `one who asks rn for a deliverable` in place of `developer`.
3. *While deciding.* Ask whether that job gets done only if someone else also does a job with the product, such as an administrator who sets it up on a shared server for a team. Name each such person as a role as well.
4. *While deciding.* For each person whose job the goal, the decisions, and what the product does leave unclear, ask the user `What does <person> come to the product to get done?`, with the job you'd guess as your recommendation.
5. *While deciding.* Split a role where two of its members would count different results as their job done, such as a guest who browses a shop and a member who buys from it.
6. *While deciding.* Name the role `user` where there's only one.
7. *While making.* Read Roles as a developer would, and check that each role has a job that no other role has. Where two roles share a job, merge them.

### N2

Does each objective state, in one sentence, what one role is trying to achieve in their own work?

The developers build toward the objectives, so each must name the end that a role reaches in their own work, and neither a feature nor a measure of that end.

1. *While deciding.* For each role, take its job from Roles and write it as the end the role reaches in their own work, in one sentence with the role as the subject, such as `the user gets each deliverable they mean`.
2. *While deciding.* Ask why that end matters to the role, and ask again of each answer, until the answer is something the role reaches in their own work and no longer something the product does, such as going on from `rn writes the README` to `the people the README is for decide on the product with it`.
3. *While deciding.* Write one objective for each distinct end, where two ends are distinct if a role can reach one without the other, such as a member who buys and an administrator who keeps the shop running.
4. *While making.* Read each objective with the product's name taken out. Where it then reads as a feature, such as `manage tasks in the app`, rewrite it as the end the role reaches, such as `the team finishes its work on time`.

### N3

Does the vision describe only what the users do and get, not how the product works inside?

The vision must stay true while the inside of the product changes, so it describes only what the users do and get, and leaves how the product does it to the architecture.

1. *While making.* For each sentence of the vision, ask whether it would change if the product's insides changed while the users saw the same. If it would, take it out, and where it carried something the users see, write that in its place, such as `answers within a second` in place of `keeps an index in memory`.

### N4

Does each objective have key results that measure how well and how fast its role achieves it, each with the direction that's better?

The developers keep a change only if it brings the users closer to their goals, so each objective needs measures that a developer reads after a change. Usability testers judge a change by the [success rate and the time on task](https://www.nngroup.com/articles/usability-metrics/) of each task the users do, and the two key results take these.

1. *While deciding.* For each objective, write the task its role does to reach it, from where they start to the result they keep, such as from the user's request to the deliverable they sign off.
2. *While deciding.* Make the first key result measure how well: the share of those tasks in which the role reaches the result. Where a run of the task shows the failures rather than the successes, such as a deliverable that its people can't use, measure the share that fails instead, such as `the share of the deliverables rn hands over that the people they're for couldn't use`.
3. *While deciding.* Make the second key result measure how fast: the time from the task's start to its result, the role's own time in it included, such as the time the user spends answering questions. Where that time depends mostly on things outside the product, such as the speed of the machine, count the role's own effort instead, such as the questions they answer.
4. *While deciding.* Give each key result the direction that's better, such as `Lower is better.`
5. *While deciding.* Rank the key results, how well before how fast, so that a developer keeps a change that improves one only if none ranked before it gets worse.
6. *While deciding.* Give no targets, since developers who aim at a number improve the number in place of the users' result.
7. *While making.* For each key result, write down what one end-to-end (E2E) run of the role's task would record that a developer counts the key result from, such as each deliverable that a judge marks unusable, or the times at which the task starts and ends. Where no record of such a run would show it, rewrite the key result.

### N5

Are the objectives distinct, so that each piece of work serves one of them?

The developers decide what to build by asking which objective a piece of work serves, which works only where each piece serves one objective.

1. *While deciding.* List each piece of work the product plans that the decisions of your cut name. Where the repository already holds the product, add each of its open issues and each feature its README names. Where none of these lists any work, ask the user what the product is to do next.
2. *While deciding.* For each piece of work, name the objective it serves, such as `O1` for `ask the user only what the best practice doesn't settle`.
3. *While deciding.* For each pair of objectives, ask whether a piece of work could serve one without the other. If no piece could, merge the two.
4. *While deciding.* For each piece that serves no objective, ask the user `Is <piece> not needed, or does it serve an end that no objective names?`, with the answer you'd give as your recommendation, and add the objective where it shows one missing.

### N6

Does the concept state first the one way, as its maker means it, by which the product brings the users to their objectives, and then the ideas that keep this way holding at each moment of their use?

The developers make many choices that no line of the vision names, and the concept lets each of them lean the same way, so that the users meet one product and not a set of parts that pull apart.

1. *While deciding.* Ask the user `How does the product bring its users to their objectives, and by which ideas?` before you write the concept, since the one way and the ideas that carry it out come from whoever conceived the product, and an analysis of what goes wrong today yields only a list of fixes with no center.
2. *While deciding.* Write the one way in one sentence as what the users see the product do, such as `rn works only on the vital few, the things that decide whether the people a deliverable is for can use it`.
3. *While deciding.* Write each idea the user gave, with what it gives the role toward the objective.
4. *While deciding.* List the moments of the users' use, from the moment they first meet the product to the moment they reach the objective, as a [customer journey map](https://www.nngroup.com/articles/journey-mapping-101/) does, such as the request, the goal confirmed, the questions answered, the plan signed off, and each deliverable signed off.
5. *While deciding.* At each moment, ask what keeps the one way holding there. Where no idea answers, propose one.
6. *While deciding.* For each idea you propose, ask the user `Does <idea> keep <the one way> holding at <moment>, as you mean it?`, and keep it only where they say yes.
7. *While deciding.* Drop each idea where taking it out leaves the one way holding at every moment.
8. *While making.* At each moment, take a design choice that no line of the vision names, such as whether to ask the user about a point the best practice settles, and decide it by the one way and its ideas. Where they don't decide it one way, rewrite the idea for that moment until they do.
