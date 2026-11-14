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
2. *While deciding.* Name each kind of person who comes to the product for that job by the part of it they come to get done, not by a job title, such as `one who asks rn for a deliverable` in place of `developer`.
3. *While deciding.* Ask whether that job gets done only if someone else also does a job with the product, such as an administrator who sets it up on a shared server for a team. Name each such person as a role as well.
4. *While deciding.* For each person whose job the goal, the decisions, and what the product does leave unclear, ask the user `What does <person> come to the product to get done?`, with the job you'd guess as your recommendation.
5. *While deciding.* Split a role where two of its members would count different results as their job done, such as a guest who browses a shop and a member who buys from it.
6. *While deciding.* Merge two roles where their members would count the same result as their job done, such as a new customer and a returning customer who both buy from a shop.
7. *While deciding.* Name the role `user` where there's only one.

### N2

Does each objective state, in one sentence, what one role is trying to achieve in their own work?

The developers build toward the objectives, so each must name the end that a role reaches in their own work, and neither a feature nor a measure of that end.

1. *While deciding.* For each role, take its job from Roles and write it in one sentence with the role as the subject, such as `the user has rn write the README`.
2. *While deciding.* Ask yourself why the role wants what that sentence says, answer from the goal and the decisions of your cut and from Roles, and write the answer as a sentence in the same form. Ask why of that answer in turn, and stop at the first sentence, N2.1's own included, that the role reaches in their own work and that no longer names what the product does, such as going on from `the user has rn write the README` to `the people the README is for decide on the product with it`. Where an answer names two results, such as `the shop takes every order and no customer's data leaks`, go on from each on its own. Where your cut and Roles don't give the answer, ask the user `Why does <role> want <sentence>?`, with the answer you'd guess as your recommendation.
3. *While deciding.* Write one objective for each end that N2.2 reached. Where a role can't reach one of its ends without another, write the two as one objective, and keep them apart where it can reach one without the other, such as an administrator's `the shop takes every order` and `no customer's data leaks`, since a shop can take every order while its data leaks.
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

1. *While deciding.* Once each role has its objectives, and before you write any key result, list each piece of work the product plans that the decisions of your cut name. Where the repository already holds the product, add each of its open issues and each feature its README names. Where none of these lists any work, ask the user what the product is to do next.
2. *While deciding.* For each piece of work, name each objective it serves, such as `O1` for `ask the user only what the best practice doesn't settle`.
3. *While deciding.* For each pair of objectives of one role, look at the pieces that N5.2 named either of them for. Where there are such pieces and each names both, merge the two into one objective, and name it in place of either wherever a piece names one of them. Leave two objectives of different roles apart, since each objective states what one role is trying to achieve.
4. *While deciding.* For each piece that still names more than one objective, split it into parts that each serve one, such as `search and checkout` into `search` for the guest's objective and `checkout` for the member's. Where it doesn't split, name only the objective whose role would miss it most, such as the guest's for a faster first page, which a guest meets on every visit and a member once before checkout.
5. *While deciding.* For each piece that serves no objective, ask the user `Is <piece> not needed, or does it serve an end that no objective names?`, with the answer you'd give as your recommendation, and add the objective where it shows one missing.

### N6

Does the concept state first the one way, as its maker means it, by which the product brings the users to their objectives, and then the ideas that keep this way holding at each moment of their use?

The developers make many choices that no line of the vision names, and the concept lets each of them lean the same way, so that the users meet one product and not a set of parts that pull apart.

1. *While deciding.* Ask the user `How does the product bring its users to their objectives, and by which ideas?` before you write the concept, since the one way and the ideas that carry it out come from whoever conceived the product, and an analysis of what goes wrong today yields only a list of fixes with no center.
2. *While deciding.* Write the one way in one sentence as what the users see the product do, such as `rn works only on the vital few, the things that decide whether the people a deliverable is for can use it`.
3. *While deciding.* Write each idea the user gave, with what it gives the role toward the objective.
4. *While deciding.* Take each task that N4.1 wrote, from where its role starts to the result they keep, and list the moments of that use in order, as a [customer journey map](https://www.nngroup.com/articles/journey-mapping-101/) does, starting where the role first meets the product, such as the request, the goal confirmed, the questions answered, the plan signed off, and each deliverable signed off.
5. *While deciding.* At each moment, ask what keeps the one way holding there. Where no idea answers, propose one.
6. *While deciding.* At each moment, take from the pieces of work that N5.1 listed each one that the role meets there, and from it each choice that its developers must make between ways that the role would meet differently and that no line of the vision decides, such as whether to ask the user about a point the best practice settles. Where no piece falls at a moment, take the choice that a developer who builds that moment makes first, such as what the role sees while they wait.
7. *While deciding.* Decide each choice that N6.6 took by the one way and its ideas. Where they don't decide it one way, rewrite the idea for that moment until they do.
8. *While deciding.* For each idea you proposed or rewrote, ask the user `Does <idea> keep <the one way> holding at <moment>, as you mean it?`, and keep it only where they say yes.
9. *While deciding.* Drop each idea where taking it out leaves the one way holding at every moment.
