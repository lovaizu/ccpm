# `design-tree`

## Goal tree

- The maker builds every deliverable that the user's goal needs, each after what it needs and from settled decisions, and the user knows where the work stands.
  - **C1** The design tree holds every deliverable that the goal needs, each after the deliverables it needs.
    - **N1** Does the goal state, in one sentence, what the user is trying to achieve? (goal)
    - **N2** Does the tree hold every deliverable that the goal needs? (deliverables)
    - **N3** Does each deliverable name its kind: the best practice of the field's established way of making it, or `specific` where the deliverable is this product's alone? (deliverables)
    - **N4** Does each deliverable name the deliverables it takes content from and those that must pass before it starts, and come after all of them? (deliverables)
  - **C2** The maker builds each deliverable from settled decisions, and asks the user only what's theirs to decide.
    - **N5** Does each deliverable hold the decisions and the open points for each necessary condition of its best practice? (deliverables)
    - **N6** Does each decision say who settled it? (deliverables)
  - **C3** The maker and the user see where the work stands, and pick it up from there.
    - **N7** Does each deliverable's name say what it brings toward the goal? (deliverables)
    - **N8** Does each deliverable show its status and which necessary conditions it meets? (deliverables)
  - **C4** The design tree stays true as the work changes it.
    - **N9** After a change to a node, does every node that the change touches agree with it? (goal, deliverables)
    - **N10** Does the tree hold only what holds now? (goal, deliverables)

## Template

[design-tree.schema.json](design-tree.schema.json)

## Practices

### N1

Does the goal state, in one sentence, what the user is trying to achieve?

Every deliverable in the design tree is there to serve the goal, so the goal decides what goes in and what stays out, and shows the user that the work is after what they want.

1. *While deciding.* Open the user's request, the words they gave, and write what they're trying to achieve as one sentence with the user as its subject.
2. *While deciding.* Ask why that matters to the user, and again of each answer, until the answer names no deliverable while the work can still make it true. That last answer is the goal, such as `The user gets from rn each deliverable they mean` from a request to rebuild rn.
3. *While deciding.* Put the sentence to the user to confirm, beside the words of the request it came from, and write it as they confirm it, since only the user knows what they're after.
4. *While deciding.* Write `user` in `by` once they confirm it.
5. *While making.* For each deliverable, name the part of the goal's sentence it helps make true, and drop a deliverable for which you can name none.

### N2

Does the tree hold every deliverable that the goal needs?

A deliverable left out shows up only when the work reaches it, and the work stops there. The items follow a [work breakdown structure](https://en.wikipedia.org/wiki/Work_breakdown_structure), which practitioners build down from the end objective until the parts together hold all of the work.

1. *While deciding.* Open the goal and the user's request, and list each deliverable that the user holds or uses once the goal holds, such as a plugin with its README. Keep one only where the goal fails without it, and ask the user about one you can't tell.
2. *While deciding.* List the folders of `${CLAUDE_PLUGIN_ROOT}/domain/best-practices/`, and for each deliverable, open `best-practice.json` of the folder whose goal names the deliverable's people and what they do with it, such as `readme` for a README. That folder is the deliverable's kind, which N3.1 writes. A deliverable that no folder's goal fits takes its kind at N3.2 or N3.3.
3. *While deciding.* For each deliverable, list each kind that `inputs` and `preconditions` of the best practice you opened for it name, or, where you opened none, each deliverable whose decisions it carries out, such as the architecture whose user story an integration test checks.
4. *While deciding.* For each kind listed, search the repository for a file of that kind for the same product, such as `dev/rn/product-vision.md` for rn's README. Take the file where the user's request leaves what it says as it is. Add a deliverable at the file's path where the request changes what it must say, such as a product vision whose roles a new kind of user widens, and add a deliverable of that kind at a new path where no such file exists. Repeat N2.3 and this item for each deliverable you add, until one takes nothing.
5. *While deciding.* Break each deliverable down until it's a work package: a part that ends at a check showing, on its own, that the people the goal serves get a part of what it promises them, such as one integration test for each user story of an architecture in place of one test of the whole plugin. A larger part leaves its maker to settle at once what no one checks between, and a smaller one passes checks that show nothing toward the goal.

### N3

Does each deliverable name its kind: the best practice of the field's established way of making it, or `specific` where the deliverable is this product's alone?

A deliverable of a kind that every product shares has a way of making it that the field has settled, and its best practice brings that way to the maker. A deliverable of this product alone has no such way, and a best practice made for it would only restate the product's own decisions, so a check judges it instead.

1. *While deciding.* Write as each deliverable's kind the folder whose best practice you opened for it at N2.2. Where a deliverable holds parts of several such kinds, its kind is the one whose best practice names the others for those parts.
2. *While deciding.* Where no folder fits, search the field's guides and handbooks for how to make the deliverable. Where guides written for different products give the same steps, as they do for a changelog, put a deliverable that makes its best practice, of the kind `meta`, at the top level before the first deliverable of that kind.
3. *While deciding.* Where no such guides agree, give the deliverable the kind `specific`, such as a file that keeps a run's state, a file of the product's own specification, an integration test of its architecture, or an end-to-end test, and name in `check` the check that judges it, such as the test that passes once the deliverable exists.

### N4

Does each deliverable name the deliverables it takes content from and those that must pass before it starts, and come after all of them?

A deliverable started before its inputs rests on a guess, and its maker does the work again once they arrive. The items follow the [precedence diagram](https://en.wikipedia.org/wiki/Precedence_diagram_method) of scheduling, which lists each activity's predecessors before it orders the activities.

1. *While deciding.* For each deliverable of a best practice's kind, write in its `inputs` the path of each file you took or deliverable you added at N2.4 for a kind that the best practice's `inputs` name, and in its `preconditions` the path of each one for a kind that its `preconditions` name, such as `dev/rn/product-vision.md` in the inputs of rn's README. Use paths, not kinds, since deliverables of one kind can serve different products.
2. *While deciding.* For a `specific` deliverable, write in `inputs` the path of each deliverable whose decisions it carries out, such as the architecture whose user story an integration test checks, and in `preconditions` the path of each deliverable it runs, such as the parts that the test calls.
3. *While deciding.* Put in the preconditions of each integration test the unit-tested parts it runs, and in those of each end-to-end (E2E) test the integration tests of the parts it runs, since a higher level finds a fault later, at a higher cost.
4. *While deciding.* Where other deliverables' results rest on a check, such as a script that CI runs on them, put in their preconditions the check with a test that shows it failing on a case it must catch, since a check never seen failing may pass anything.
5. *While making.* Write the deliverables in the order of the work: first each that names no deliverable of the tree in its inputs and preconditions, then each whose named deliverables all come before it, until you've placed each.
6. *While making.* After each change, run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py write {run} {deliverable} '<ground>'`, where `{run}` is the run's folder, `.rn/<yyyymmdd>-<goal>`, `{deliverable}` is the design tree's path in it, and `<ground>` is why the change decides as it does, as N6.2 says. It gives 1 with each deliverable before one it takes from or waits for, each path that's neither a deliverable nor a file, and each two deliverables at one path, and leaves the run's tree as it was, so fix each fault it names and run it again. It gives 0 once it has committed the tree with `<ground>` as the commit message, and prints `changed`, `touched`, and `doing` as JSON.
7. *While making.* Check that a later deliverable names each research deliverable in its inputs, and that a later deliverable has the kind that each meta deliverable makes, and drop one that none uses, since `tree.py write` doesn't check these.

### N5

Does each deliverable hold the decisions and the open points for each necessary condition of its best practice?

The maker builds a deliverable from the decisions that answer its best practice's conditions, and the user answers only the points that are theirs, each once its grounds exist. The items follow [grilling](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md), which asks only the decisions whose prerequisites are settled, one at a time with a recommendation, looks facts up itself, and leaves decisions to the user.

1. *While deciding.* For each deliverable of a best practice's kind, open `${CLAUDE_PLUGIN_ROOT}/domain/best-practices/<kind>/best-practice.json`, and write under the deliverable each necessary condition's ID, in that best practice's order, with `good` false.
2. *While deciding.* For each condition, take each `decide` item of its practice, and write the point it settles as a decision's `about`, in a few words, such as `the roles` from the item of a product vision that names who hires the product. Where an item settles nothing for this deliverable, such as one whose case doesn't hold, write no point for it.
3. *While deciding.* For a `specific` deliverable, write as its decisions each point that its check needs settled, such as which user story an integration test runs and what it shows.
4. *While deciding.* Leave a point's `decided` null while a deliverable of the tree that it takes from isn't done, such as a README's people before the product vision is done, and put it to no one until then, since an answer given before its grounds exist rests on a guess.
5. *While deciding.* Where a fact would settle a point, search the repository and the public documentation of what the point is about, and settle the point where a source states the fact.
6. *While deciding.* Where no source states the fact but a trial or a longer search can find it, such as how the host behaves in a case its documentation doesn't state, add a research deliverable: of the kind `specific`, at `{run}/research/<question>.md`, named by what the deliverable that holds the point can decide once it's done, with `each question has an answer that names its source, a page a reader can open or a command with what it printed` as its check.
7. *While deciding.* Write as the research deliverable's decisions the question it answers, as a question with one answer, and the point it serves, by the deliverable's path, the condition's ID, and the point's `about`, such as `plugins/rn/README.md N3: the install command`.
8. *While deciding.* Write the research deliverable's path in the `inputs` of the deliverable that holds the point, and leave the point's `decided` null until the research deliverable is done.
9. *While deciding.* Settle each point where the user's words, the goal, the deliverables done, and the best practice leave one answer, or answers that differ only in how the work is done, not in what the user gets.
10. *While deciding.* Put each point still open to the user, one in each message, with your recommendation and its ground, where the answers left differ in what the user gets, such as which people a product serves, and leave its `decided` null until they answer.
11. *While making.* When a deliverable becomes done, take each null point of the later deliverables that takes from it, and settle it or put it to the user as this practice's decide items say.

### N6

Does each decision say who settled it?

The user checks, on each sign-off, the decisions taken without asking them, and finds the grounds of each in git.

1. *While deciding.* Write in `by` who settled each decision: `user` where the user said or confirmed it, `research` where a source found it, `reasoning` where the goal and the best practices leave one answer, and `maker` where the maker chose among answers that differ only in how it makes its own deliverable.
2. *While making.* Write the grounds of each decision that a change makes, the point and why it holds, as `<ground>` of `tree.py write`, which commits the change with it as the commit message, and keep them out of the tree, so that the user finds them in git.

### N7

Does each deliverable's name say what it brings toward the goal?

The user reads the design tree to see where the work stands and what comes next, without opening each deliverable.

1. *While deciding.* As you add each deliverable, write as its name what holds toward the goal once it exists, with the people who gain it as its subject, such as `A newcomer decides from the README alone whether rn fits their work` in place of `rn's README`.
2. *While deciding.* Leave out its path and its kind, which have fields of their own.

### N8

Does each deliverable show its status and which necessary conditions it meets?

Whoever picks up the work goes on from where it stopped, without reading back through what came before.

1. *While making.* Keep each deliverable's status: `open` as you add it, `doing` once its turn has come, which `tree.py write` marks, and `done` once each `good` it holds is true.
2. *While making.* Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py round {run} <path>`, with `<path>` the deliverable's `path` in the tree. It prints as JSON the deliverable's last round, the generator's making of it and the judging of that by one evaluator for each group of its best practice's conditions, with each evaluator's answers: `good` with each condition good and the lines that meet it, and `more` with each condition not yet good and its `good_when`, what its people get once it's good. It gives 1 where the deliverable has had no round.
3. *While making.* Set a condition's `good` true only once you answer its question yes against the deliverable as it stands: where `good` of the last round names it, read the lines it gives in the deliverable, and where no round has judged it, read the deliverable for the lines that meet it. Leave it false where `more` names it.
4. *While making.* Set a condition's `good` back to false when a decision that answers it changes.
5. *While making.* Set a `specific` deliverable's `good` true only once its `check` passes when you run it.

### N9

After a change to a node, does every node that the change touches agree with it?

A node that a change touches, left unread, goes on saying what held before, and the next role builds on it.

1. *While making.* After each change to a node, list the nodes it touches: each node up to the goal, the later decisions of the same deliverable, and each deliverable that names the changed one in its inputs or preconditions or that it names there. `tree.py write` prints this list as `touched`.
2. *While making.* Read each node on the list beside the change. It holds where it names no path, kind, or decision that the change replaced or dropped, and rests on nothing that the change made false. Rewrite each other node in the same change, such as a README's decision on its people after the product vision's roles change.
3. *While making.* List the nodes again for each node you rewrote, until a pass rewrites nothing.

### N10

Does the tree hold only what holds now?

A reader acts on what the design tree says, and reads any history in it as part of the current decision, while git keeps how each point came about.

1. *While making.* Write a changed decision over its old text, with no note of what it said before.
2. *While making.* Keep one line for a deliverable that's done: its name, path, kind, and status.
3. *While making.* Once each point that a research deliverable serves holds its answer, drop the research deliverable, and its path from the `inputs` that name it, since the decisions hold what it found and the run's folder keeps the file.
